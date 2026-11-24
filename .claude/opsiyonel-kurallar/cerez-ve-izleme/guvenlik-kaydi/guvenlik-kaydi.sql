-- Güvenlik kaydı: giriş denemeleri, çıkış, parola işlemleri; IP, konum, işletim sistemi (PostgreSQL 14+).
-- Kural: .claude/opsiyonel-kurallar/cerez-ve-izleme.md
-- Projenin backend/ klasörüne kopyalanır ve bir göçte çalıştırılır (PARCALAR.md).
-- Yalnızca ekleme yapılır; UPDATE, DELETE ve TRUNCATE reddedilir. Hash zinciri yoktur:
-- giriş denemeleri çok hacimli olabilir ve zincir kilidi yavaşlatır. Başarılı giriş ve
-- parola değişikliği, denetim-kaydi kuralı açıksa ayrıca denetim kaydına da yazılır.

CREATE TABLE guvenlik_kaydi (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    zaman           timestamptz NOT NULL DEFAULT now(),
    -- giris.basarili, giris.basarisiz, giris.kilitlendi, cikis,
    -- parola.sifirlama_istendi, parola.degisti (proje yeni olay ekleyebilir)
    olay            text        NOT NULL,
    kullanici_id    text,
    denenen_kimlik  text,       -- maskelenmiş: a***@ornek.com
    ip              inet,
    ulke            text,       -- ISO kodu: TR
    sehir           text,
    user_agent      text,
    isletim_sistemi text,
    tarayici        text,
    cihaz           text        -- masaustu, mobil, tablet, bot
);

CREATE INDEX guvenlik_kaydi_zaman     ON guvenlik_kaydi (zaman);
CREATE INDEX guvenlik_kaydi_ip        ON guvenlik_kaydi (ip, zaman);
CREATE INDEX guvenlik_kaydi_kullanici ON guvenlik_kaydi (kullanici_id, zaman);
CREATE INDEX guvenlik_kaydi_olay      ON guvenlik_kaydi (olay, zaman);

-- Tek istisna: saklama süresi dolan kaydın kişisel verisini (ip, sehir, user_agent) BOŞALTMAK.
-- Başka hiçbir alan değişemez, boşaltılan alan yeniden doldurulamaz, satır silinemez.
CREATE FUNCTION guvenlik_kaydi_degismez() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'UPDATE'
       AND NEW.ip IS NULL AND NEW.sehir IS NULL AND NEW.user_agent IS NULL
       AND (NEW.id, NEW.zaman, NEW.olay, NEW.kullanici_id, NEW.denenen_kimlik, NEW.ulke,
            NEW.isletim_sistemi, NEW.tarayici, NEW.cihaz)
           IS NOT DISTINCT FROM
           (OLD.id, OLD.zaman, OLD.olay, OLD.kullanici_id, OLD.denenen_kimlik, OLD.ulke,
            OLD.isletim_sistemi, OLD.tarayici, OLD.cihaz)
    THEN
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'guvenlik_kaydi değiştirilemez ve silinemez (%); yalnızca guvenlik_kaydi_anonimlestir() kişisel veriyi boşaltabilir', TG_OP
        USING ERRCODE = 'insufficient_privilege';
END
$$;

CREATE TRIGGER guvenlik_kaydi_degismez
    BEFORE UPDATE OR DELETE ON guvenlik_kaydi
    FOR EACH ROW EXECUTE FUNCTION guvenlik_kaydi_degismez();

CREATE TRIGGER guvenlik_kaydi_bosaltilamaz
    BEFORE TRUNCATE ON guvenlik_kaydi
    FOR EACH STATEMENT EXECUTE FUNCTION guvenlik_kaydi_degismez();

-- Saklama süresi: süresi dolan kayıtlarda ip, sehir ve user_agent boşaltılır (anonimleştirme).
-- Olay, zaman, ülke, işletim sistemi, tarayıcı ve cihaz kalır; istatistik korunur.
-- Kullanım: SELECT guvenlik_kaydi_anonimlestir(730);  -- 730 günden eski kayıtlar
-- Günde bir zamanlanır (PARCALAR.md). denetim_kaydi tablosu varsa her çalışma oraya da yazılır.
CREATE FUNCTION guvenlik_kaydi_anonimlestir(gun integer) RETURNS integer
LANGUAGE plpgsql AS $$
DECLARE
    adet integer;
BEGIN
    IF gun IS NULL OR gun < 1 THEN
        RAISE EXCEPTION 'saklama süresi en az 1 gün olmalı';
    END IF;
    UPDATE guvenlik_kaydi
       SET ip = NULL, sehir = NULL, user_agent = NULL
     WHERE zaman < now() - make_interval(days => gun)
       AND (ip IS NOT NULL OR sehir IS NOT NULL OR user_agent IS NOT NULL);
    GET DIAGNOSTICS adet = ROW_COUNT;
    IF to_regclass('public.denetim_kaydi') IS NOT NULL THEN
        EXECUTE 'INSERT INTO denetim_kaydi (aktor_tipi, aktor_id, eylem, hedef_tipi, yeni, sonuc)
                 VALUES (''sistem'', ''guvenlik-kaydi-anonimlestirme'', ''guvenlik_kaydi.anonimlestirildi'',
                         ''guvenlik_kaydi'', $1, ''basarili'')'
        USING jsonb_build_object('adet', adet, 'gun', gun);
    END IF;
    RETURN adet;
END
$$;
