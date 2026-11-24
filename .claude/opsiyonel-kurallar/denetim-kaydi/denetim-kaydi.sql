-- Denetim kaydı: tablo, hash zinciri, değişmezlik ve doğrulama (PostgreSQL 14+).
-- Kural: .claude/opsiyonel-kurallar/denetim-kaydi.md
--
-- Bu dosya projenin backend/ klasörüne kopyalanır ve bir göç (migration) içinde olduğu gibi çalıştırılır
-- (.claude/ klasörü konteynerde yoktur):
--   laravel-next : backend/database/sql/denetim-kaydi.sql → DB::unprepared(file_get_contents(database_path('sql/denetim-kaydi.sql')))
--   fastapi-next : backend/alembic/sql/denetim-kaydi.sql   → await_only(op.get_bind().connection.driver_connection.execute(<dosya>.read_text()))
--                  (op.execute asyncpg ile çalışmaz: tek çağrıda birden çok komut kabul edilmez)
-- Göçün down/downgrade adımı bu tabloyu silmez.

-- 1. Tablo -------------------------------------------------------------------
-- sira, olusturuldu, onceki_hash ve hash alanlarını uygulama yazmaz; trigger yazar.

CREATE TABLE denetim_kaydi (
    id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sira              bigint      NOT NULL UNIQUE,
    olusturuldu       timestamptz NOT NULL,
    istek_id          text,
    aktor_tipi        text        NOT NULL CHECK (aktor_tipi IN ('kullanici', 'admin', 'sistem', 'misafir')),
    aktor_id          text,
    aktor_adi         text,
    adina_islem_yapan text,
    eylem             text        NOT NULL,
    hedef_tipi        text,
    hedef_id          text,
    eski              jsonb,
    yeni              jsonb,
    sonuc             text        NOT NULL CHECK (sonuc IN ('basarili', 'reddedildi', 'hata')),
    http              jsonb,
    onceki_hash       bytea,
    hash              bytea       NOT NULL
);

CREATE INDEX denetim_kaydi_hedef ON denetim_kaydi (hedef_tipi, hedef_id);
CREATE INDEX denetim_kaydi_aktor ON denetim_kaydi (aktor_tipi, aktor_id);
CREATE INDEX denetim_kaydi_eylem ON denetim_kaydi (eylem);
CREATE INDEX denetim_kaydi_zaman ON denetim_kaydi (olusturuldu);

-- 2. Hash'e giren içerik ------------------------------------------------------
-- Zaman UTC mikro saniye olarak girer; oturumun saat dilimi sonucu değiştirmez.
-- jsonb metni anahtar sırasından bağımsızdır; aynı kayıt her zaman aynı metni verir.

CREATE FUNCTION denetim_kaydi_icerik(k denetim_kaydi) RETURNS bytea
LANGUAGE sql IMMUTABLE AS $$
    SELECT convert_to(jsonb_build_object(
        'sira',              k.sira,
        'zaman_us',          (extract(epoch FROM k.olusturuldu) * 1000000)::bigint,
        'istek_id',          k.istek_id,
        'aktor_tipi',        k.aktor_tipi,
        'aktor_id',          k.aktor_id,
        'aktor_adi',         k.aktor_adi,
        'adina_islem_yapan', k.adina_islem_yapan,
        'eylem',             k.eylem,
        'hedef_tipi',        k.hedef_tipi,
        'hedef_id',          k.hedef_id,
        'eski',              k.eski,
        'yeni',              k.yeni,
        'sonuc',             k.sonuc,
        'http',              k.http
    )::text, 'UTF8')
$$;

-- 3. Hash zinciri -------------------------------------------------------------
-- Eklemeler bir kilitle sıraya girer; zincir sırası (sira) bu kilit altında atanır.
-- id kullanılmaz: eşzamanlı eklemelerde id sırası ile kayıt sırası farklılaşabilir.
-- Not: REPEATABLE READ veya SERIALIZABLE işlemde eşzamanlı ekleme sira çakışmasıyla
-- hata verir (UNIQUE); denetim kaydı READ COMMITTED (varsayılan) işlemde yazılır.

CREATE FUNCTION denetim_kaydi_zincir() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    son_sira bigint;
    son_hash bytea;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext('denetim_kaydi'));
    SELECT sira, hash INTO son_sira, son_hash
      FROM denetim_kaydi ORDER BY sira DESC LIMIT 1;
    NEW.sira        := coalesce(son_sira, 0) + 1;
    NEW.olusturuldu := clock_timestamp();
    NEW.onceki_hash := son_hash;
    NEW.hash        := sha256(coalesce(son_hash, ''::bytea) || denetim_kaydi_icerik(NEW));
    RETURN NEW;
END
$$;

CREATE TRIGGER denetim_kaydi_zincir
    BEFORE INSERT ON denetim_kaydi
    FOR EACH ROW EXECUTE FUNCTION denetim_kaydi_zincir();

-- 4. Değişmezlik --------------------------------------------------------------
-- UPDATE, DELETE ve TRUNCATE reddedilir. Tablonun sahibi trigger'ı kapatabilir;
-- bu yüzden asıl güvence hash zinciridir (5. bölüm) ve tablo sahibi ayrı bir roldür (6. bölüm).

CREATE FUNCTION denetim_kaydi_degismez() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'denetim_kaydi değiştirilemez ve silinemez (%)', TG_OP
        USING ERRCODE = 'insufficient_privilege';
END
$$;

CREATE TRIGGER denetim_kaydi_degismez
    BEFORE UPDATE OR DELETE ON denetim_kaydi
    FOR EACH ROW EXECUTE FUNCTION denetim_kaydi_degismez();

CREATE TRIGGER denetim_kaydi_bosaltilamaz
    BEFORE TRUNCATE ON denetim_kaydi
    FOR EACH STATEMENT EXECUTE FUNCTION denetim_kaydi_degismez();

-- 5. Doğrulama ----------------------------------------------------------------
-- Kullanım: SELECT * FROM denetim_kaydi_dogrula();
-- Boş sonuç: zincir sağlam. Satır dönerse ilk bozulan kayıt ve nedeni.
-- Sınır: zincirin SON kayıtları silinirse zincir bunu göremez. Bunun için son kaydın
-- sırası ve hash'i düzenli olarak veritabanı dışına yazılır (çapa):
--   SELECT sira, encode(hash, 'hex') FROM denetim_kaydi ORDER BY sira DESC LIMIT 1;

CREATE FUNCTION denetim_kaydi_dogrula()
RETURNS TABLE (bozuk_sira bigint, neden text)
LANGUAGE sql STABLE AS $$
    WITH z AS (
        SELECT k.sira, k.onceki_hash, k.hash,
               lag(k.sira) OVER w AS onceki_sira,
               lag(k.hash) OVER w AS beklenen_onceki,
               denetim_kaydi_icerik(k) AS icerik
          FROM denetim_kaydi k
        WINDOW w AS (ORDER BY k.sira)
    )
    SELECT sira,
           CASE
               WHEN onceki_sira IS NULL AND sira <> 1            THEN 'ilk kayıtlar eksik (silinmiş olabilir)'
               WHEN onceki_sira IS NOT NULL AND sira <> onceki_sira + 1 THEN 'sıra atlanmış (kayıt silinmiş olabilir)'
               WHEN onceki_hash IS DISTINCT FROM beklenen_onceki THEN 'önceki hash uyuşmuyor'
               ELSE 'kayıt içeriği değiştirilmiş'
           END
      FROM z
     WHERE (onceki_sira IS NULL AND sira <> 1)
        OR (onceki_sira IS NOT NULL AND sira <> onceki_sira + 1)
        OR onceki_hash IS DISTINCT FROM beklenen_onceki
        OR hash <> sha256(coalesce(onceki_hash, ''::bytea) || icerik)
     ORDER BY sira
$$;

-- 6. Ayrı roller (devreye alırken seçildiyse) ---------------------------------
-- Tablonun sahibi göçleri çalıştıran roldür; uygulamanın bağlandığı rol yalnızca
-- ekleyip okuyabilir. Böylece uygulama trigger'ı kapatamaz, tabloyu silemez.
-- <uygulama_rolu> projede gerçek rol adıyla değiştirilir.
--
-- REVOKE ALL ON denetim_kaydi FROM <uygulama_rolu>;
-- GRANT SELECT, INSERT ON denetim_kaydi TO <uygulama_rolu>;
-- GRANT EXECUTE ON FUNCTION denetim_kaydi_dogrula() TO <uygulama_rolu>;
