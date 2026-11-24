# Yedekleme

Bu isteğe bağlı bir kuraldır. `/kural ac yedekleme` ile açılınca `.claude/rules/` altına kopyalanır ve her oturumda geçerli olur. Hazır parçası `.claude/opsiyonel-kurallar/yedekleme/` klasöründedir; kurulumu `PARCALAR.md` dosyasında yazar.

Projenin verisi her gün yedeklenir, yedekler düzenli olarak geri yüklenerek sınanır. Açılmayan yedek, yedek sayılmaz.

## İlkeler

- **Canlıda yedek servisi çalışır.** Canlıya çıkan bir projede `yedek` servisi compose dosyasındadır ve `YEDEK_KLASORU` doludur.
- **Her döküm doğrulanır.** Okunamayan döküm yedek sayılmaz ve hata verir.
- **Geri yükleme sınaması:** her hafta son yedek geçici bir veritabanına yüklenir. Sonuç `geri-yukleme-sinamalari.log` dosyasına yazılır. Sınama başarısızsa bu bir teknik borçtur ve hemen açılır.
- **Saklama:** son `YEDEK_GUNLUK` günlük, son `YEDEK_HAFTALIK` haftalık, son `YEDEK_AYLIK` aylık yedek kalır. Saklama süresi dolunca silinen yalnızca eski **yedek dosyalarıdır**; veritabanına hiçbir zaman dokunulmaz.
- **Uzak kopya:** sunucu kaybolursa yerel yedek de gider. Uzak kopya (`RCLONE_HEDEF`) yoksa bu bir risk olarak teknik borçta yazılı durur. Uzak kopyada dosya silinmez; uzaktaki saklama süresi deponun kendi kuralıyla ayarlanır.
- **Gizlilik:** yedekler kişisel veri içerir. Yalnızca sahibinin okuyabileceği izinlerle yazılır, git'e girmez, herkese açık bir yere konmaz. Uzak depo erişim anahtarları yalnızca `.env` dosyasında durur.
- **Denetim kaydı çapası:** denetim-kaydi kuralı açıksa her yedekte zincirin son halkası (`sira` ve `hash`) `capa/` altına yazılır. Böylece zincirin son kayıtlarının silinmesi de fark edilir.

## Geri yükleme

- **Gerçek geri yükleme**, yani projenin veritabanının bir yedekle değiştirilmesi, veri kaybına yol açabilir. Claude bunu kendi başına yapmaz, önermez, komutunu çalıştırmaz.
- **Kullanıcı isterse:** önce o anki halin yedeği alınır. Hangi yedeğin hangi veritabanına yükleneceği kullanıcıya şıklı sorulur. Komut kullanıcıya gösterilir.
- **Geri yükleme sınaması** projenin veritabanına dokunmaz: yalnızca kendi açtığı geçici veritabanını kullanır ve sonunda kaldırır.

## Claude'un davranışı

- **Yeni veritabanı:** projeye yeni bir veritabanı veya veri deposu eklenirse (örneğin dosya yüklemeleri için bir hacim) yedek kapsamında olup olmadığı kontrol edilir. Kapsamda değilse teknik borç açılır.
  - `yedekle.sh` Postgres veritabanlarının hepsini alır.
  - Docker hacimlerindeki dosyaları (örneğin `backend-storage`) almaz; bu, yükleme yapan projelerde ayrıca ele alınır.
- **Silme yok:** yedek klasörünü, uzak depoyu veya yedek dosyalarını silen bir komut yazılmaz ve önerilmez. Saklama düzeni betiğin işidir.
- **Değişiklik:** yedek zamanlaması, saat dilimi veya saklama sayıları değişince yalnızca `.env` değerleri değişir; betik ve compose dosyası değiştirilmez.

## Diğer kurallarla bağ

- **denetim-kaydi:** açıksa her yedekte çapa yazılır; `docs/mantik/denetim-kaydi.md` dosyasındaki çapa kararı "yedek servisinin `capa/` klasörü" olarak güncellenir.
- **cerez-ve-izleme:** güvenlik kaydı aynı veritabanında olduğu için yedeğe girer; güvenlik kaydının saklama süresi yedek saklama süresiyle birlikte değerlendirilir.

## Devreye alma

`/kural ac yedekleme` şu soruları sorar ve cevapları projeye yazar:

1. **Yedek klasörü** (canlı sunucuda): örneğin `/yedekler/<proje>`. `.env` dosyasında `YEDEK_KLASORU`.
2. **Saklama:** önerilen 7 gün / 4 hafta / 6 ay. `.env` dosyasında `YEDEK_GUNLUK`, `YEDEK_HAFTALIK`, `YEDEK_AYLIK`.
3. **Yedek saati ve saat dilimi:** önerilen 03:30, Europe/Istanbul.
4. **Uzak kopya isteniyor mu?** Sağlayıcı (Backblaze B2, Cloudflare R2, Hetzner, MinIO, başka). Anahtarlar kullanıcı tarafından `.env` dosyasına yazılır; Claude değer yazmaz.
5. **Yerelde de yedek servisi olsun mu?** `profiles: ["yedek"]` ile; varsayılan olarak hayır.

Cevaplar `docs/proje/yigin.md` dosyasına yazılır. Claude `.env` dosyasına değer yazmaz (veri.md): `YEDEK_SAATI`, `YEDEK_SAAT_DILIMI`, `YEDEK_GUNLUK`, `YEDEK_HAFTALIK`, `YEDEK_AYLIK` boş kalırsa compose dosyasındaki varsayılanlar (03:30, Europe/Istanbul, 7/4/6) kullanılır. Varsayılandan farklı bir değer seçildiyse ya da `YEDEK_KLASORU` ve uzak depo anahtarları için, değeri kullanıcı `.env` dosyasına yazar; Claude yazılacak satırı gösterir.

## Kurulum sonrası TD

Parça kurulunca `/td` ile bir teknik borç açılır. Ad: `yedek doğrulama`. Durum: `açık`. Borç metni şunları ister:

- canlıda ilk yedeğin alındığı ve ilk geri yükleme sınamasının başarılı olduğu `geri-yukleme-sinamalari.log` dosyasında görülmeli;
- uzak kopya ayarlanmadıysa: sunucu kaybında yedeklerin de gideceği risk olarak yazılır;
- uzak depoda saklama kuralı (lifecycle) ayarlanmalı;
- dosya yüklemesi yapan projelerde Docker hacimlerinin yedeği ayrıca planlanmalı.

Borç, kullanıcı ilk sınamanın başarılı olduğunu söyleyene kadar açık kalır.
