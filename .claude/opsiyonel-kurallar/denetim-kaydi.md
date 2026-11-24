# Denetim kaydı

Bu isteğe bağlı bir kuraldır. `/kural ac denetim-kaydi` ile açılınca `.claude/rules/` altına kopyalanır ve her oturumda geçerli olur.

Kullanıcıların ve sistemin önemli işleri kaydedilir. Her kayıt şunları söyler:
- **kim:** aktör;
- **ne zaman:** zaman;
- **neyi:** hedef;
- **neyden neye:** eski ve yeni değer;
- **ne denedi, ne oldu:** eylem ve sonuç.

Kayıtlar geriye dönük tutulur. Değiştirilemez ve silinemez.

Giriş denemeleri, parola sıfırlama talepleri, IP ve konum bu kuralın konusu değildir; `cerez-ve-izleme` kuralıyla gelir. Bu kural açıkken de IP ve konum alanı eklenmez.

## Ne kaydedilir

1. **Kullanıcının iş olayları:** durum değiştiren her önemli iş. Örnekler: ayar değiştirme, abonelik satın alma, hesap kapatma, profil güncelleme, içerik silme.
2. **Yetkili kişinin işlemleri:** admin ve süperadmin bir şeyi değiştirdiğinde aktörün kimliği ve kullanıcı adı, hedef, eski ve yeni değer yazılır. Kullanıcı adı o anki haliyle saklanır; kullanıcı adını sonra değiştirse de kayıt değişmez.
3. **Sistem işleri:** kuyruk işi, zamanlanmış görev, webhook. Bunlarda aktör `sistem`, aktör kimliği işin kısa, kebab-case adıdır (örneğin `odeme-webhook`, `aidat-tahakkuk`). Laravel'de ve Celery'de aynı biçim kullanılır.
4. **HTTP istekleri:** durum değiştiren her istek (POST, PUT, PATCH, DELETE). Hassas veri okuyan GET istekleri de kaydedilir; örneğin bir adminin bir kullanıcının ayrıntılarını açması. Yazılanlar: yöntem, yol, maskelenmiş gövde (en çok 8 KB, fazlası kesilir), yanıt kodu, süre, istek kimliği.
5. **Başarısız denemeler:** yetkisiz, doğrulamadan geçmeyen veya hata veren durum değiştirme denemeleri de kaydedilir. `sonuc` alanı ne olduğunu söyler: `basarili`, `reddedildi` veya `hata`.

Okuma işlemleri (liste, sayfa görüntüleme) kaydedilmez. Hassas veri okuyan istekler bunun dışındadır.

## Kayıt alanları

| Alan | Anlamı |
|---|---|
| `sira` | Zincirdeki sıra. Veritabanı atar. |
| `olusturuldu` | Zaman, UTC. Veritabanı atar. |
| `istek_id` | Aynı isteğin bütün kayıtlarını birleştirir. |
| `aktor_tipi` | `kullanici`, `admin`, `sistem` veya `misafir` |
| `aktor_id`, `aktor_adi` | İşi yapanın kimliği ve o anki kullanıcı adı |
| `adina_islem_yapan` | Bir admin bir kullanıcının yerine işlem yaptığında (kullanıcı olarak giriş, impersonation) adminin kimliği. `aktor_*` alanları kullanıcıyı gösterir. |
| `eylem` | Noktayla ayrılmış ad: `abonelik.satin_alindi`, `kullanici.rol_degisti` |
| `hedef_tipi`, `hedef_id` | Değişen kayıt |
| `eski`, `yeni` | Değişen alanların önceki ve sonraki değeri (JSON). Yalnızca değişen alanlar yazılır. |
| `sonuc` | `basarili`, `reddedildi`, `hata` |
| `http` | Yöntem, yol, yanıt kodu, süre, maskelenmiş gövde (JSON) |
| `onceki_hash`, `hash` | Hash zinciri. Veritabanı atar. |

## Değişmezlik

Tablo, trigger'lar ve doğrulama sorgusu `.claude/opsiyonel-kurallar/denetim-kaydi/denetim-kaydi.sql` dosyasındadır. Bu dosya projede bir göç içinde olduğu gibi çalıştırılır. Dosya 2026-11-23 tarihinde Postgres 17'de denendi.

- **Değiştirme ve silme reddedilir:** veritabanı UPDATE, DELETE ve TRUNCATE işlemlerini reddeder. Kodda denetim kaydını değiştiren veya silen satır yazılmaz.
- **Hash zinciri:** her kayıt bir öncekinin hash'ini taşır. Hash'i veritabanı hesaplar; uygulama hash, sıra veya zaman vermez, verse de dikkate alınmaz.
- **Doğrulama:** `SELECT * FROM denetim_kaydi_dogrula();` boş dönerse zincir sağlamdır. Satır dönerse ilk bozulan kaydı ve nedenini gösterir.
- **Göçler:** denetim kaydı tablosuna yalnızca sütun ekleyebilir. Göçün geri alma adımı (down/downgrade) bu tabloyu silmez.
- **Tablo sahibi:** tablonun sahibi trigger'ı kapatabilir. Uygulamayla göçler aynı veritabanı rolünü kullanıyorsa trigger yalnızca kazara değişikliği engeller; kasıtlı bir müdahaleyi hash zinciri ortaya çıkarır. En güçlü düzen ayrı rollerdir: tablonun sahibi göç rolüdür, uygulama rolü yalnızca ekleyip okuyabilir (SQL dosyası, 6. bölüm).
- **Son kayıtlar:** zincirin son kayıtları silinirse zincir bunu göremez. Bunun için son kaydın sırası ve hash'i düzenli olarak veritabanı dışına yazılır (çapa). Nereye yazılacağı projede belirlenir.

## İşlem bütünlüğü

- **İş olayı kaydı** işin kendisiyle aynı veritabanı işleminde (transaction) yazılır. Kayıt yazılamazsa iş de geri alınır. Kayıt olmadan iş yapılmış sayılmaz.
- **HTTP istek kaydı** yanıt verildikten sonra yazılır. Yazılamazsa istek bozulmaz, ama hata uygulama günlüğüne düşer.
- **Yalıtım düzeyi:** denetim kaydı READ COMMITTED (varsayılan) işlemde yazılır. Daha sıkı bir yalıtım düzeyinde eşzamanlı yazımlar hata verir.

## Maskeleme

Kayda giren her istek gövdesi ve her `eski`/`yeni` değer maskelenir.

- **Değeri `***` yazılan alanlar:** adı `password`, `parola`, `token`, `secret`, `authorization`, `cookie`, `api_key` içeren alanlar; kart numarası, CVV ve IBAN.
- **Gövdesi hiç yazılmayan uç noktalar:** giriş, kayıt olma, parola sıfırlama gibi kimlik doğrulama uç noktaları. Yöntem, yol ve yanıt kodu yazılır.
- **Tek yer:** maskeleme kuralı kodda tek bir yerde durur; her çağrıda yeniden yazılmaz.

```text
kötü: {"email":"a@b.com","password":"Gizli123"}
iyi:  {"email":"a@b.com","password":"***"}
```

## Okuma

- Denetim kayıtlarını görmek ayrı bir yetki ister.
- Kayıtları açmak da hassas veri okumadır ve kaydedilir.
- Kayıtlar yalnızca okunabilir sunulur; arayüzde düzenleme veya silme düğmesi olmaz.

## Olay kataloğu

Kaydedilecek olaylar projede `docs/mantik/denetim-kaydi.md` dosyasında listelenir. Kural açılırken bu belge kullanıcıya sorularak açılır.

| Eylem | Ne zaman yazılır | Aktör | eski → yeni |
|---|---|---|---|
| `kullanici.olusturuldu` | Kayıt ol veya admin kullanıcı ekledi | kullanici / admin | — → e-posta, rol |
| `ayar.degisti` | Kullanıcı bir ayarı kaydetti | kullanici | yalnızca değişen ayarlar |
| `abonelik.satin_alindi` | Ödeme onaylandı | kullanici | — → paket, tutar, dönem |
| `abonelik.iptal_edildi` | Kullanıcı aboneliği iptal etti | kullanici | paket → durum, bitiş tarihi |
| `abonelik.yenilendi` | Ödeme sağlayıcısının webhook'u geldi | sistem (`odeme-webhook`) | bitiş tarihi → yeni bitiş tarihi |
| `hesap.kapatildi` | Kullanıcı hesabını kapattı | kullanici | durum: aktif → kapalı |
| `kullanici.rol_degisti` | Admin bir kullanıcının rolünü değiştirdi | admin | rol → rol |
| `kullanici.askiya_alindi` | Admin bir hesabı askıya aldı | admin | durum, neden |
| `kullanici.olarak_giris` | Admin bir kullanıcının hesabına geçti | admin; `adina_islem_yapan` dolu | — |
| `denetim_kaydi.goruntulendi` | Biri denetim kayıtlarını açtı | admin | filtreler |

Bu tablo **örnektir**, kullanıcıya olduğu gibi önerilmez. Kural açılırken ürüne (`docs/proje/hakkinda.md`) uyan olaylar önerilir: tablodaki genel olaylardan ürüne uyanlar ve ürüne özel olaylar (örneğin bir site yönetimi uygulamasında `aidat.tahakkuk_edildi`, `gider.dagitildi`). Abonelik gibi ürüne uymayan satırlar önerilmez.

## Claude'un davranışı

- **Yeni özellik:** durum değiştiren bir özellik yazmadan önce olay kataloğu okunur.
  - Olay katalogda varsa kodda kaydı yazılır.
  - Katalogda yoksa önce kataloğa eklenir (mantik-belgeleri kuralı), sonra koda yazılır.
- **Test:** her yeni olay için, işin sonunda doğru eylem, aktör ve eski/yeni değerle bir kaydın yazıldığını doğrulayan bir test yazılır. Test yazılamıyorsa teknik borç açılır (impact kuralı).
- **Silme yok:** denetim kaydını silen, değiştiren veya "temizleyen" bir komut, göç ya da öneri yazılmaz. Saklama süresi dolan kayıtlar için yalnızca kullanıcının kararıyla arşive taşıma yapılır.
- **Hassas veri yok:** kayıtlara parola, token veya tam kart numarası yazılmaz. Maskeleme atlanmaz.

## Yığına göre uygulama

Bu bölüm yol gösterir. Denenenler: SQL dosyası (Postgres 17) ve FastAPI göçündeki SQL yükleme yolu. Denenmeyenler: Laravel'deki `DB::unprepared` yüklemesi, servisler ve middleware'ler; bunlar ilk kullanımda denenir.

SQL dosyası her iki yığında da önce `backend/` altına kopyalanır. Konteynere yalnızca `./backend` bağlanır, canlı imaja da yalnızca `backend/` girer; `.claude/` klasörü konteynerde yoktur.

**laravel-next:**
- **Göç:** SQL dosyası `backend/database/sql/denetim-kaydi.sql` olarak kopyalanır; göçte `DB::unprepared(file_get_contents(database_path('sql/denetim-kaydi.sql')))` çalıştırılır.
- **Servis:** `App\Services\AuditLog::record(eylem, hedef, eski, yeni, sonuc)`. Aktörü `auth()->user()` ile, yerine işlem yapan admini oturumdan okur. İş olayında `DB::transaction` içinde çağrılır.
- **İstek kaydı:** bir middleware. Durum değiştiren istekler `terminate()` aşamasında, yani yanıttan sonra yazılır. Maskeleme bu middleware'de ve serviste ortak bir sınıfla yapılır.
- **Horizon işleri ve zamanlanmış görevler:** aktör `sistem`; aktör kimliği işin kısa adıdır (Kural: "Sistem işleri"). İş sınıfı varsa kısa adı kebab-case yazılır: `AidatTahakkukJob` → `aidat-tahakkuk`.

**fastapi-next:**
- **Göç:** SQL dosyası `backend/alembic/sql/denetim-kaydi.sql` olarak kopyalanır. asyncpg tek çağrıda birden çok komutu kabul etmediği için `op.execute(...)` ve `exec_driver_sql(...)` **çalışmaz** ("cannot insert multiple commands"; 2026-11-23 tarihinde SQLAlchemy 2.1.9 ve asyncpg 0.32.0 ile denendi). Çalışan yol, dosyayı doğrudan asyncpg bağlantısına vermektir:

  ```python
  from pathlib import Path
  from alembic import op
  from sqlalchemy.util import await_only

  def upgrade() -> None:
      sql = (Path(__file__).parents[1] / "sql" / "denetim-kaydi.sql").read_text()
      await_only(op.get_bind().connection.driver_connection.execute(sql))

  def downgrade() -> None:
      pass  # denetim kaydı tablosu silinmez
  ```
- **Yardımcı:** `app/audit.py` içinde `async def kaydet(session, eylem, ...)`. İş olayında aynı `AsyncSession` ve aynı işlem içinde çağrılır.
- **İstek kaydı:** bir middleware veya `BackgroundTask` ile yanıttan sonra yazılır.
- **Celery görevleri:** aktör `sistem`, aktör kimliği görevin adıdır.
- **API sürümü:** denetim kaydı uç noktaları `/api/v1/...` altında yalnızca okuma yapar.

## Diğer kurallarla bağ

- **cerez-ve-izleme:** açıksa olay kataloğuna şu olaylar eklenir: `giris.basarili`, `parola.degisti`, `cerez.onay_degisti`. Güvenlik kaydındaki ayrıntılar (IP, cihaz) denetim kaydına kopyalanmaz.
- **yedekleme:** açıksa çapa yedek servisinin `capa/` klasörüne yazılır; `docs/mantik/denetim-kaydi.md` dosyasındaki çapa kararı buna göre güncellenir.

## Devreye alma

`/kural ac denetim-kaydi` şu soruları sorar ve cevapları projeye yazar:

1. **Saklama süresi:** süresiz mi, belirli bir süre mi? Cevap `docs/proje/yigin.md` dosyasına yazılır. Süre dolunca silme yok; arşive taşıma kullanıcı kararıyla yapılır.
2. **Aktörler:** projede admin veya süperadmin var mı? Admin bir kullanıcının yerine işlem yapabiliyor mu? Cevap `docs/mantik/denetim-kaydi.md` dosyasının "Kararlar" bölümüne yazılır.
3. **İlk olay kataloğu:** ürüne göre önerilen olaylar listelenir, kullanıcı seçer. Ardından `docs/mantik/denetim-kaydi.md` açılır.
4. **Veritabanı rolleri:** göç ve uygulama için ayrı roller mi (önerilen), tek rol mü? Cevap `docs/proje/yigin.md` dosyasına yazılır; ayrı roller seçildiyse rol adları da.
5. **Çapa:** son hash nereye yazılsın? Şimdilik yok, bir dosya veya harici bir servis. Cevap `docs/mantik/denetim-kaydi.md` dosyasının "Kararlar" bölümüne yazılır. yedekleme kuralı açıksa çapa yedek servisinin `capa/` klasörüne yazılır ve bu cevap kendiliğinden öyle olur.
