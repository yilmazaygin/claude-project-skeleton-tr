# Çerez ve izleme: hazır parçalar

`/kural ac cerez-ve-izleme` bu dosyayı izler. Yalnızca kullanıcının seçtiği parçalar kurulur. Yollar `.claude/opsiyonel-kurallar/cerez-ve-izleme/` klasörüne göredir. `NN` proje numarasıdır, `<proje>` proje adıdır.

| Parça | Ne kurar | Gerektirdiği |
|---|---|---|
| `cerez-onayi` | Banner, onay çerezi, onaya bağlı betik yükleme, "Çerez ayarları" linki | — |
| `ga4` | Google Analytics 4, Consent Mode v2 | `cerez-onayi` |
| `umami` | Proje başına Umami servisi ve izleme betiği | `cerez-onayi` |
| `guvenlik-kaydi` | Giriş denemeleri, çıkış ve parola işlemleri; IP, ülke, şehir, işletim sistemi, tarayıcı | — |

`ga4` veya `umami` seçilip `cerez-onayi` seçilmediyse bu söylenir ve `cerez-onayi` de eklenir.

Herhangi bir parça kurulduktan sonra kuraldaki "Kurulum sonrası TD" açılır.

---

## cerez-onayi

1. **Dosyaları kopyala:** `cerez-onayi/src/` içindekiler `frontend/src/` altına:
   - `lib/cerez-onayi.ts`
   - `lib/use-cerez-onayi.ts`
   - `components/CerezBanner.tsx`
   - `components/OnayliBetik.tsx`
   - `components/CerezAyarlariLinki.tsx`
2. **`frontend/src/app/layout.tsx`:** `<body>` içinin en sonuna `<CerezBanner />` eklenir. Alt bilgiye `<CerezAyarlariLinki />` konur.
3. **Çerez politikası sayfası:** banner varsayılan olarak `/cerez-politikasi` adresine link verir. Sayfa yoksa bu, TD'de bir madde olarak yazılır.
4. **Onay kaydı** (denetim-kaydi açıksa zorunlu, kapalıysa "Devreye alma" sorusuna göre): `.env` dosyasına `NEXT_PUBLIC_CEREZ_ONAY_KAYDI=` anahtarı eklenir; değeri `/api/cerez-onayi` olur. Canlı compose dosyasında frontend'in `build.args` bölümüne aynı anahtar eklenir. Backend'de uç nokta açılır:
   - **laravel-next** (`routes/api.php`): `Route::post('/cerez-onayi', ...)`. Gövde doğrulanır (`tercih`, `analitik`, `pazarlama` boolean). denetim-kaydi açıksa `cerez.onay_degisti` olayı yazılır. Yanıt `204`.
   - **fastapi-next** (`app/api/v1/`): `POST /api/v1/cerez-onayi`. Bu durumda `NEXT_PUBLIC_CEREZ_ONAY_KAYDI` değeri `/api/v1/cerez-onayi` olur.
5. **Testler:** `cerez-onayi/src/lib/cerez-onayi.test.ts` (onay mantığı, 8 test) ve `cerez-onayi/src/components/CerezBanner.test.tsx` (banner'a tıklama, 4 test) `frontend/src/` altındaki aynı yerlere kopyalanır; Vitest ile çalışır (HAZIR.md → Frontend testleri). e2e eki varsa `cerez-onayi/e2e/cerez-banner.spec.ts` → `frontend/e2e/`: gerçek tarayıcıda Reddet/Kabul et ve onaya bağlı gtag yüklemesi (3 test).
6. **Yeni betik eklemek:** zorunlu olmayan her betik `<OnayliBetik kategori="analitik|pazarlama|tercih" ... />` ile eklenir; doğrudan `<Script>` yazılmaz.

## ga4

1. **Dosyayı kopyala:** `ga4/src/components/GoogleAnalytics.tsx` → `frontend/src/components/`.
2. **`layout.tsx`:** `<body>` içine `<GoogleAnalytics />` eklenir.
3. **Anahtar:** `.env` ve `.env.example` dosyalarına `NEXT_PUBLIC_GA_ID=` eklenir (değer `G-XXXXXXX`, kullanıcı doldurur).
4. **Canlı compose:** frontend servisine şu blok eklenir:

   ```yaml
   build:
     args:
       NEXT_PUBLIC_GA_ID: ${NEXT_PUBLIC_GA_ID:-}
   ```

5. **Çerez listesi:** `_ga` ve `_ga_<kimlik>` çerezleri analitik kategorisine yazılır (2 yıl, Google). Reklam izinleri pazarlama onayına bağlıdır.

## umami

1. **Compose servisleri:** iki compose dosyasına aşağıdaki iki servis eklenir. Umami projenin Postgres'inde ayrı bir `umami` veritabanı kullanır. Veritabanını tek seferlik `umami-db-hazirla` servisi açar; veritabanı zaten varsa dokunmaz.

   **`compose.local.yaml`:**

   ```yaml
   umami-db-hazirla:
     container_name: <proje>-umami-db-hazirla
     image: postgres:17-alpine
     # postgres imajı veri klasörünü VOLUME tanımlar; tmpfs olmadan her açılışta boş bir adsız hacim kalır.
     tmpfs:
       - /var/lib/postgresql/data
     environment:
       PGHOST: db
       PGUSER: ${DB_USERNAME}
       PGPASSWORD: ${DB_PASSWORD}
       PGDATABASE: ${DB_DATABASE}
     command: ["sh", "-c", "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='umami'\" | grep -q 1 || psql -c 'CREATE DATABASE umami'"]
     depends_on:
       db:
         condition: service_healthy

   umami:
     container_name: <proje>-umami
     image: ghcr.io/umami-software/umami:3.5.0
     init: true
     environment:
       DATABASE_URL: postgresql://${DB_USERNAME}:${DB_PASSWORD}@db:5432/umami
       APP_SECRET: ${UMAMI_APP_SECRET:?UMAMI_APP_SECRET .env içinde doldurulmalı}
       DISABLE_TELEMETRY: "1"
     depends_on:
       umami-db-hazirla:
         condition: service_completed_successfully
     labels:
       - traefik.enable=true
       - traefik.http.routers.<proje>-umami.rule=Host(`umami.localhost`)
       - traefik.http.routers.<proje>-umami.entrypoints=web
       - traefik.http.services.<proje>-umami.loadbalancer.server.port=3000
   ```

   **`compose.live.yaml`:** aynı iki servis eklenir, şu farklarla:
   - `umami` servisine `restart: unless-stopped`;
   - `umami-db-hazirla` servisindeki `tmpfs` satırı canlıda da kalır;
   - yönlendirme kuralı `Host(\`${UMAMI_DOMAIN:-umami.invalid}\`)`: `UMAMI_DOMAIN` boşsa yönlendirme etkisizdir;
   - frontend servisinin `build.args` bölümüne `NEXT_PUBLIC_UMAMI_URL: ${NEXT_PUBLIC_UMAMI_URL:-}` ve `NEXT_PUBLIC_UMAMI_WEBSITE_ID: ${NEXT_PUBLIC_UMAMI_WEBSITE_ID:-}`.

2. **Anahtarlar:** `.env` ve `.env.example` dosyalarına aynı sırayla eklenir:
   - `UMAMI_APP_SECRET`: uzun, rastgele bir değer;
   - `UMAMI_DOMAIN`: yalnızca canlıda;
   - `NEXT_PUBLIC_UMAMI_URL`: yerelde `http://umami.localhost:80NN`;
   - `NEXT_PUBLIC_UMAMI_WEBSITE_ID`: Umami'de site eklenince verilen kimlik.

   **Parola uyarısı:** `DB_PASSWORD` içinde `@ : / ? #` gibi karakterler varsa `DATABASE_URL` bozulur. Bu durumda Umami için ayrı, URL'de güvenli bir parola kullanılır.
3. **Dosyayı kopyala:** `umami/src/components/UmamiBetigi.tsx` → `frontend/src/components/`. `layout.tsx` içinde `<body>` içine `<UmamiBetigi />` eklenir.
4. **İlk giriş:** Umami'nin varsayılan kullanıcısı `admin`, parolası `umami`. **İlk girişte parola hemen değiştirilir.** Bu adım TD'ye de yazılır. Ardından Umami'de site eklenir ve verilen kimlik `NEXT_PUBLIC_UMAMI_WEBSITE_ID` anahtarına yazılır.
5. **NPM:** canlıda `UMAMI_DOMAIN` için ayrı bir proxy host tanımlanır: `UMAMI_DOMAIN` → `<proje>-traefik:80`.

## guvenlik-kaydi

**Ortak:**
- `guvenlik-kaydi/guvenlik-kaydi.sql`: tablo; yalnızca ekleme yapılabilir.
- **IP güvenilirliği:** ziyaretçi `X-Forwarded-For` başlığını kendisi uydurabilir. Bu yüzden yalnızca Docker iç ağlarındaki vekillere güvenilir, `*` kullanılmaz. Başlık sağdan sola okunur, iç ağ dışındaki ilk adres ziyaretçidir. Testte `'*'` ile Laravel uydurulan adresi gerçek IP sandı; iç ağ aralıklarıyla gerçek adresi buldu.
- **GeoIP:** DB-IP Lite (CC BY 4.0). Sitede "IP Geolocation by DB-IP" bağlantısıyla kaynak gösterilir (https://db-ip.com). Bu madde TD'ye yazılır.

**laravel-next:**

1. **SQL dosyası:** `guvenlik-kaydi.sql` → `backend/database/sql/guvenlik-kaydi.sql`.
2. **Göç:** `php artisan make:migration create_guvenlik_kaydi` ile açılır. `up()` içinde `DB::unprepared(file_get_contents(database_path('sql/guvenlik-kaydi.sql')));`. `down()` boş kalır, tablo silinmez.
3. **Kod:** `guvenlik-kaydi/laravel/app/` içindekiler `backend/app/` altına kopyalanır:
   - `Security/GuvenlikKaydi.php`
   - `Security/GeoIp.php`
   - `Security/UserAgent.php`
   - `Console/Commands/GeoIpIndir.php`
4. **Olay aboneliği:** `app/Providers/AppServiceProvider.php` içindeki `boot()` metoduna `\Illuminate\Support\Facades\Event::subscribe(\App\Security\GuvenlikKaydi::class);` eklenir.
5. **Paket:** `docker compose -f compose.local.yaml exec backend composer require geoip2/geoip2` (2026-11-23 tarihinde v3.5.0 kuruldu ve denendi).
6. **`bootstrap/app.php`:** `trustProxies` satırının iç ağ aralıklarını kullandığı kontrol edilir (laravel-next HAZIR.md bunu böyle kurar). Eski bir kurulumda `'*'` varsa şununla değiştirilir:

   ```php
   $middleware->trustProxies(at: ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '127.0.0.1']);
   ```

7. **Anonimleştirme:** scheduler eki varsa `routes/console.php` içine eklenir:

   ```php
   Schedule::call(fn () => \Illuminate\Support\Facades\DB::select('SELECT guvenlik_kaydi_anonimlestir(?)', [(int) env('GUVENLIK_KAYDI_SAKLAMA_GUN', 730)]))->dailyAt('04:30');
   ```

   `.env` ve `.env.example` dosyalarına `GUVENLIK_KAYDI_SAKLAMA_GUN=` eklenir (boşsa 730). Scheduler eki yoksa bu bir TD olarak yazılır: süre dolan kişisel veri boşaltılmaz.
8. **GeoIP dosyası:** `docker compose -f compose.local.yaml exec backend php artisan geoip:indir`. Scheduler eki varsa `routes/console.php` içine `Schedule::command('geoip:indir')->monthlyOn(3, '04:00');` eklenir. Canlıda dosya `backend-storage` hacminde durur. İlk deploy'dan sonra komut bir kez elle çalıştırılır.
9. **Göçü uygula:** `php artisan migrate`.

**fastapi-next:**

1. **SQL dosyası:** `guvenlik-kaydi.sql` → `backend/alembic/sql/guvenlik-kaydi.sql`. Göç, denetim-kaydi kuralındaki `await_only` yöntemiyle yazılır; asyncpg `op.execute` ile birden çok komutu kabul etmez.
2. **Kod:** `guvenlik-kaydi/fastapi/app/guvenlik.py` ve `geoip_indir.py` → `backend/app/`. Giriş ve parola uç noktaları `await guvenlik.kaydet(session, "giris.basarisiz", request, denenen_kimlik=...)` çağırır.
3. **Paket:** `backend/requirements.txt` dosyasına `maxminddb==3.3.0` eklenir (2026-11-23 tarihinde pip'in çözdüğü ve denenen sürüm) ve imaj yeniden build edilir.
4. **Git:** `backend/.gitignore` dosyasına `data/geoip/` eklenir.
5. **Canlı compose:** backend servisine (veya `x-backend` bloğuna) `volumes: [backend-geoip:/app/data/geoip]` eklenir; `backend-geoip` hacmi de en alttaki `volumes` listesine.
6. **Anonimleştirme:** queue ve scheduler ekleri varsa `app/worker.py` içindeki `beat_schedule` sözlüğüne günlük bir görev eklenir; görev `SELECT guvenlik_kaydi_anonimlestir(:gun)` çalıştırır (`gun` = `GUVENLIK_KAYDI_SAKLAMA_GUN`, boşsa 730). `.env` ve `.env.example` dosyalarına `GUVENLIK_KAYDI_SAKLAMA_GUN=` eklenir. Ekler yoksa bu bir TD olarak yazılır.
7. **GeoIP dosyası:** `docker compose -f compose.local.yaml exec backend python -m app.geoip_indir`. Queue ve scheduler ekleri varsa `beat_schedule` içine `app.geoip_indir.gorev` ayda bir eklenir.

---

## Deneme durumu (2026-11-23)

Dört parça laravel-next üzerinde, yerelde ve canlıda bu dosyadaki adımlarla kuruldu ve denendi. `guvenlik-kaydi` fastapi-next için ayrıca denendi.

**Denenenler:**
- **cerez-onayi:** onay mantığı Node 24 ile 8 birim testinden geçti (kabul, ret, kısmi onay, çerez biçimi, bozuk ya da hileli değer, geri çekme). Next.js 16 build'i geçti. Onaysız sayfa HTML'inde GA4 ve Umami betiği yok; "Çerez ayarları" linki var.
- **ga4:** canlı imajda `NEXT_PUBLIC_GA_ID` koda gömüldü. Onaysız HTML'de gtag yok.
- **umami:**
  - `umami` veritabanı tek seferlik servisle açıldı;
  - yerelde ve canlıda giriş sayfası ve `script.js` 200 döndü;
  - API ile site eklendi; bir sayfa görüntüleme kaydedildi (1 görüntüleme, 1 ziyaretçi);
  - Umami veritabanında IP sütunu yok.

  Canlıda ilk açılışta Umami kendi göçlerini uygularken birkaç saniye 502 verir.
- **guvenlik-kaydi (laravel-next):**
  - başarısız giriş, başarılı giriş ve çıkış olayları yazıldı;
  - e-posta maskelendi; işletim sistemi, tarayıcı ve cihaz doğru bulundu;
  - DB-IP indirildi (121 MB, yaklaşık 1 dakika); 8.8.8.8 → US;
  - NPM zinciri taklit edilerek uydurulan IP'nin atlandığı görüldü; Next.js proxy'si üzerinden de;
  - değiştirme ve silme reddedildi;
  - canlıda `www-data` kullanıcısıyla GeoIP indirmesi ve kayıt yazımı çalıştı.
- **guvenlik-kaydi (fastapi-next):** IP zinciri, konum, işletim sistemi ve maskeleme kontrolleri ve kayıt yazımı geçti. Tablo `await_only` ile kuruldu, silme reddedildi.

**Sonradan denenenler (2026-11-23):** banner'a tıklama Vitest + Testing Library ile (4 test) ve gerçek Chromium'da Playwright ile (3 test) denendi ve geçti: Reddet, Ayarlar, Kabul et, onay sonrası gtag yüklemesi, geri çekmede sayfa yenilenmesi ve gtag'in kalkması.

**Anonimleştirme (2026-11-23):** SQL fonksiyonu Postgres 17'de denendi: 730 günden eski kayıtta `ip`, `sehir`, `user_agent` boşaldı, yeni kayıt kaldı, çalışma denetim kaydına yazıldı (zincir sağlam). Başka alanı değiştirme, boşaltılanı doldurma, kısmi boşaltma ve silme reddedildi. Laravel ve Celery zamanlama satırları denenmedi.

**Denenmeyenler:**
- GA4'ün Google'a gerçekten veri göndermesi (gerçek bir GA kimliği yok);
- `Lockout`, `PasswordResetLinkSent` ve `PasswordReset` olayları (bir giriş denetleyicisi ve parola sıfırlama akışı gerektirir);
- `/api/cerez-onayi` uç noktası;
- fastapi-next'in tam yığın içinde Umami ve banner ile birlikte çalışması (frontend parçaları ortaktır ve laravel-next'te denendi).
