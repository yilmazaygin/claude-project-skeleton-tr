# Yedekleme: hazır parça

`/kural ac yedekleme` bu dosyayı izler. Tek parça vardır: `yedek` servisi. laravel-next ve fastapi-next için aynıdır. `<proje>` proje adıdır.

## Ne yapar

- **Her gün `YEDEK_SAATI` saatinde:**
  1. projenin bütün veritabanları (`umami` dahil, `postgres` ve `testing` hariç) `pg_dump -Fc` ile alınır;
  2. her döküm `pg_restore --list` ile doğrulanır;
  3. dökümler `gunluk/`, `haftalik/` (pazar) ve `aylik/` (ayın 1'i) klasörlerine yazılır;
  4. saklama uygulanır: son `YEDEK_GUNLUK` günlük, son `YEDEK_HAFTALIK` haftalık, son `YEDEK_AYLIK` aylık yedek kalır;
  5. denetim kaydı varsa son hash `capa/` altına yazılır;
  6. `RCLONE_HEDEF` doluysa her şey uzak depoya kopyalanır.
- **Her pazar, yedekten bir saat sonra:** geri yükleme sınaması yapılır. Son yedek geçici bir veritabanına yüklenir, sonuç `geri-yukleme-sinamalari.log` dosyasına yazılır.
- **İzinler:** yedek dosyaları kişisel veri içerir; yalnızca sahibinin okuyabileceği izinlerle (`umask 077`) yazılır.

## Kurulum

1. **Dosyaları kopyala:** `yedekleme/docker/yedek/` → proje kökünde `docker/yedek/`:
   - `Dockerfile`
   - `baslat.sh`
   - `yedekle.sh`
   - `geri-yukle-sina.sh`
2. **`compose.live.yaml`:** şu servis `db` servisinden hemen önce eklenir:

   ```yaml
   yedek:
     container_name: <proje>-yedek
     build:
       context: .
       dockerfile: docker/yedek/Dockerfile
     init: true
     restart: unless-stopped
     # postgres imajı veri klasörünü VOLUME tanımlar; tmpfs olmadan her açılışta boş bir adsız hacim kalır.
     tmpfs:
       - /var/lib/postgresql/data
     environment:
       PGHOST: db
       PGUSER: ${DB_USERNAME}
       PGPASSWORD: ${DB_PASSWORD}
       PGDATABASE: ${DB_DATABASE}
       TZ: ${YEDEK_SAAT_DILIMI:-Europe/Istanbul}
       YEDEK_SAATI: ${YEDEK_SAATI:-03:30}
       YEDEK_GUNLUK: ${YEDEK_GUNLUK:-7}
       YEDEK_HAFTALIK: ${YEDEK_HAFTALIK:-4}
       YEDEK_AYLIK: ${YEDEK_AYLIK:-6}
       RCLONE_HEDEF: ${RCLONE_HEDEF:-}
       RCLONE_CONFIG_UZAK_TYPE: s3
       RCLONE_CONFIG_UZAK_PROVIDER: ${RCLONE_UZAK_SAGLAYICI:-Other}
       RCLONE_CONFIG_UZAK_ENDPOINT: ${RCLONE_UZAK_ADRES:-}
       RCLONE_CONFIG_UZAK_REGION: ${RCLONE_UZAK_BOLGE:-}
       RCLONE_CONFIG_UZAK_ACCESS_KEY_ID: ${RCLONE_UZAK_ERISIM_ANAHTARI:-}
       RCLONE_CONFIG_UZAK_SECRET_ACCESS_KEY: ${RCLONE_UZAK_GIZLI_ANAHTAR:-}
     volumes:
       - ${YEDEK_KLASORU:?YEDEK_KLASORU .env içinde sunucudaki yedek klasörüyle doldurulmalı}:/yedekler
     depends_on:
       db:
         condition: service_healthy
   ```

   - Saat dilimi `.env` dosyasındaki `YEDEK_SAAT_DILIMI` ile değişir (boşsa Europe/Istanbul).
   - Uzak depo adı her zaman `uzak` olur. `RCLONE_HEDEF` değeri `uzak:<kova>/<proje>` biçimindedir.

3. **`compose.local.yaml` (isteğe bağlı):** aynı servis eklenir, şu farklarla:
   - `restart` satırı olmaz;
   - `profiles: ["yedek"]` eklenir; böylece `make up` ile açılmaz;
   - hacim satırı `${YEDEK_KLASORU:-./.dev/yedekler}:/yedekler` olur. `.dev/` zaten git'e girmez.

   Elle çalıştırma: `docker compose -f compose.local.yaml --profile yedek run --rm --entrypoint yedekle.sh yedek`.
4. **Anahtarlar:** `.env` ve `.env.example` dosyalarına aynı sırayla eklenir:
   - `YEDEK_KLASORU`, `YEDEK_SAATI`, `YEDEK_SAAT_DILIMI`, `YEDEK_GUNLUK`, `YEDEK_HAFTALIK`, `YEDEK_AYLIK`;
   - `RCLONE_HEDEF`, `RCLONE_UZAK_SAGLAYICI`, `RCLONE_UZAK_ADRES`, `RCLONE_UZAK_BOLGE`, `RCLONE_UZAK_ERISIM_ANAHTARI`, `RCLONE_UZAK_GIZLI_ANAHTAR`.

   Erişim anahtarları gizlidir; yalnızca `.env` dosyasına yazılır.
5. **Sunucuda:** yedek klasörü bir kez açılır (örneğin `/yedekler/<proje>`). Diskte yer olduğu kontrol edilir.

## Elle komutlar (canlı)

- **Hemen yedek al:** `docker compose -f compose.live.yaml exec yedek yedekle.sh`
- **Geri yükleme sınaması:** `docker compose -f compose.live.yaml exec yedek geri-yukle-sina.sh`
- **Yedekleri listele:** `docker compose -f compose.live.yaml exec yedek ls -lh /yedekler/gunluk`

**Gerçek geri yükleme**, yani projenin veritabanının yedekle değiştirilmesi, veri kaybına yol açabilir. Bu yüzden betiği yoktur ve Claude bunu kendi başına yapmaz. Kullanıcı kararıyla, önce o anki halin yedeği alınarak, `pg_restore` ile elle yapılır.

## Uzak kopya

- `rclone copy` kullanılır: uzak depoda dosya **silinmez**. Bu sayede yerel klasör yanlışlıkla boşalsa bile uzak kopya korunur.
- Uzaktaki saklama süresi deponun kendi kuralıyla ayarlanır (S3 lifecycle; örneğin 180 günden eski nesneleri sil).
- S3 uyumlu sağlayıcılar: Backblaze B2, Cloudflare R2, Hetzner Object Storage, MinIO. `RCLONE_UZAK_SAGLAYICI` değeri rclone'un sağlayıcı adıdır (`Cloudflare`, `Minio`, `Other` …).

## Deneme durumu (2026-11-23)

laravel-next test projesinde, yerel compose dosyasına `profiles: ["yedek"]` ile eklenerek denendi.

**Denenenler:**
- **Yedek alma:** iki veritabanı (`deneme`, `umami`) alındı; `testing` atlandı. Her döküm doğrulandı.
- **İzinler:** dosyalar `600`, klasörler `700` izinle yazıldı.
- **Çapa:** denetim kaydı tablosu varken son `sira` ve `hash` `capa/` altına yazıldı.
- **Uzak kopya:** rclone'un yerel dosya hedefiyle denendi (gerçek bir S3 deposu yok).
- **Saklama:** `YEDEK_GUNLUK=3` ile denendi. Klasörde 6 dosya vardı (5 sahte eski dosya ve 1 gerçek yedek); yeni yedekle 7 oldu. En yeni 3'ü kaldı, 4'ü silindi.
- **Geri yükleme sınaması:** son yedek geçici veritabanına yüklendi (10 tablo), geçici veritabanı kaldırıldı.
- **Zamanlanmış kip:**
  - crontab ve ortam dosyası (izin 600) kuruldu;
  - **gerçek crond** belirlenen dakikada yedeği aldı.

**Testte bulunan ve düzeltilen hata:** crond işleri boş bir ortamla çalıştırır. Betikte `PATH` ayarı yokken `psql: not found` ile düşüyordu; yani gece yedekleri sessizce alınmayacaktı. İki betiğe de `PATH` eklendi; ardından gerçek cron çalışması doğrulandı.

**Denenmeyenler:**
- gerçek bir S3 uyumlu depoya kopyalama;
- haftalık ve aylık klasöre kopyalama (pazar ve ayın 1'i koşulları; kod yolu günlükle aynı);
- canlı compose dosyasında çalışma (servis tanımı aynıdır, yalnızca `restart` ve hacim yolu farklıdır).
