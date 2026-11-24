---
ad: laravel-next
ozet: Laravel (PHP-FPM + nginx) API, Next.js (React, TypeScript, Tailwind) arayüz, Postgres, Redis, proje başına Traefik. Canlıda Nginx Proxy Manager → Traefik → servisler.
ekler: mailpit, queue, scheduler, e2e
tam_ad: oben-stack
tam_ad_ekleri: mailpit, queue, scheduler
---

# Hazır yığın: laravel-next

mailpit, queue ve scheduler eklerinin üçü seçilirse bu yığının adı **oben-stack** olur. e2e eki (Playwright) bu ada dahil değildir; ayrıca seçilir.

Kurulumu `kur.py` yapar: `yapilandir` ayar dosyalarını yazar, `kod` Laravel ve Next.js projelerini `backend/` ve `frontend/` klasörlerinde konteynerde oluşturup uygulamayı açar.

## İlkeler

- **Yerel canlıya benzer.** Aynı servisler, aynı Traefik, aynı yönlendirme mantığı.
- **Her şey proje başınadır.** Traefik, Mailpit ve soket vekili her projede ayrıdır. Projeler arasında ortak bir servis yoktur.
- **Portlar proje numarasından türer.** İki projenin portları hiçbir zaman çakışmaz. Kullanıcı bir projeyle çalışırken diğerlerini kapatır.

## Mimari

```
Yerel (proje no 12 örneği):
  tarayıcı → traefik:8012 → app.localhost  → frontend ─(/api, /sanctum)→ nginx → backend
                          → api.localhost  → nginx → backend   (Postman, /horizon)
                          → mail.localhost → mailpit
  veritabanı istemcisi → localhost:5412 (Postgres), localhost:6312 (Redis)

Canlı:
  tarayıcı → NPM (80/443, SSL) → traefik:80 → APP_DOMAIN → frontend ─(/api, /sanctum)→ nginx → backend
                                            → API_DOMAIN → nginx → backend   (isteğe bağlı)

Her iki ortamda:
  traefik ─(iç "socket" ağı)→ socket-proxy ─(yalnızca listeleme)→ Docker
```

**Tarayıcı ve API.** Tarayıcı API'ye ayrı bir alan adıyla gitmez. `/api` ve `/sanctum` istekleri Next.js'e gelir; Next.js bunları Docker ağı içinden `http://nginx` adresine aktarır (`frontend-proxy/`). Bu yüzden CORS gerekmez ve Sanctum'un oturum çerezleri frontend alan adında kalır.

**Traefik.** Yönlendirmeler compose dosyalarındaki `labels` satırlarından okunur. Traefik bunun için Docker'a doğrudan değil, `socket-proxy` üzerinden erişir.
- `socket-proxy` yalnızca "konteynerleri listele" ve olay izleme izni verir. Konteyner açma, durdurma, silme gibi her istek reddedilir.
- `socket-proxy` yalnızca traefik ile paylaşılan iç bir ağdadır (`socket`, `internal: true`). NPM ya da diğer servisler ona ulaşamaz.

## Servisler

| Servis | Görev | Yerel | Canlı |
|---|---|---|---|
| socket-proxy | Traefik'in Docker'ı yalnızca okuyabilmesi | iç ağ, port yok | aynı |
| traefik | Ters vekil | `80NN:80`; panel `traefik.localhost:80NN` | port yok; NPM'den gelir; panel kapalı |
| nginx | Laravel'in önündeki iç web sunucusu | `api.localhost:80NN` | `API_DOMAIN` doluysa o alan adı |
| backend | PHP 8.4-FPM, Laravel | `./backend` bağlanır | kod imajda |
| frontend | Node 24, Next.js | `./frontend` bağlanır, `app.localhost:80NN` | standalone build, `APP_DOMAIN` |
| db | postgres:17-alpine | `54NN:5432` | port yok |
| redis | redis:8-alpine; önbellek, oturum, kuyruk; healthcheck var | `63NN:6379` | port yok |

## Ekler

Her ekin şablonlardaki blokları `# >>> ek:<ad>` ve `# <<< ek:<ad>` satırları arasındadır. Ek seçilmediğinde yerine geçecek bloklar `# >>> ek-yok:<ad>` ile `# <<< ek-yok:<ad>` arasındadır.

| Ek | Ne yapar | Nerede | Seçilmezse |
|---|---|---|---|
| mailpit | Giden e-postaları yakalar; arayüzü `mail.localhost:80NN` | yalnızca yerel | `MAIL_MAILER=log`; e-postalar Laravel günlüğüne yazılır |
| queue | Laravel Horizon: kuyruk worker'ları, panel, başarısız iş takibi | yerel ve canlı | `QUEUE_CONNECTION=sync`; işler istek içinde hemen çalışır |
| scheduler | `php artisan schedule:work` | yerel ve canlı | zamanlanmış görevler çalışmaz |
| e2e | Playwright ile gerçek tarayıcıda uçtan uca test. `e2e` servisi Traefik'in ağını paylaşır; `make up` ile açılmaz | yalnızca yerel | uçtan uca test yoktur |

## Kuyruklar (queue eki)

Horizon tek bir `horizon` konteynerinde çalışır. Kuyruklar ve zaman aşımları Laravel'de `config/horizon.php` içinde tanımlanır. Hazır blok: `backend-horizon/horizon-defaults.php`.

| Supervisor | Kuyruklar | Zaman aşımı | Süreç |
|---|---|---|---|
| supervisor-default | `high`, `default`, `low` (bu sırayla) | 120 sn | 1-4, otomatik dengeleme |
| supervisor-long | `long` | 900 sn | 1-2 |

- Uzun süren iş `->onQueue('long')` ile gönderilir.
- `REDIS_QUEUE_RETRY_AFTER` 960 saniyedir ve compose'daki `x-laravel-env` bloğunda durur. En uzun zaman aşımından (900) büyük olmak zorundadır; yoksa uzun bir iş bitmeden ikinci kez başlatılır.
- Horizon konteynerinin `stop_grace_period` değeri 16 dakikadır, böylece kapanırken uzun iş yarıda kesilmez.
- Bu üç değerden biri değişince diğerleri aynı işte güncellenir.
- **Panel:** yerelde `api.localhost:80NN/horizon`, canlıda `API_DOMAIN/horizon`. Canlıda erişim `app/Providers/HorizonServiceProvider.php` içindeki `viewHorizon` gate'i ile verilir.
- **Metrikler:** scheduler eki de seçildiyse panelin grafikleri için `horizon:snapshot` komutu 5 dakikada bir zamanlanır.
- **Yerelde kod değişince:** Horizon kodu belleğinde tutar. Değişiklikten sonra `docker compose -f compose.local.yaml restart horizon` çalıştırılır. `php artisan horizon:terminate` backend konteynerinden verilirse horizon konteynerini durdurmaz, yalnızca worker'ları yeniden başlatır.

## Araç engeli

`/yigin` 5. adımda kabul edilirse engellenecek araçlar: `php`, `composer`, `node`, `npm`, `npx`, `yarn`, `pnpm`. (`php artisan` `php` ile engellenir.) Konteyner içindeki kullanım etkilenmez.

## Testler

Testler geliştirme verisinden yalıtılmıştır (veri.md kuralı).

- **Test veritabanı:** `testing`. Yerel compose dosyasındaki tek seferlik `db-test-hazirla` servisi projenin Postgres'inde açar. Canlıda yoktur.
- **Ayar (`phpunit.xml`):** `backend-test/phpunit-php-blogu.xml` içindeki `<php>` bloğu kullanılır. Değerler `<server ... force="true"/>` ile verilir.
  - Laravel'in varsayılan `phpunit.xml` dosyası bizim konteynerlerde **geliştirme veritabanına bağlanır**: konteynerde `DB_DATABASE` ve `CACHE_STORE` zaten tanımlıdır, PHPUnit bunları `force` olmadan ezmez.
  - `<env force="true"/>` de yetmez: Laravel ortam değişkenini önce `$_SERVER` dizisinden okur.
  - Her ikisi 2026-11-23 tarihinde denendi: varsayılan ayarla test geliştirme veritabanına kullanıcı yazdı.
- **Koruma (`backend-test/tests/TestCase.php`):** veritabanı `testing` değilse test başlamadan durur. Koruma `setUpTraits()` içindedir; böylece `RefreshDatabase` yanlış veritabanını silmeden önce çalışır.
- **`backend-test/tests/Feature/IzolasyonTest.php`:** yalıtımı doğrular: veritabanı, önbellek, oturum, kuyruk.
- **Çalıştırma:** `make test` (backend `php artisan test`, frontend `npx vitest run`); e2e eki seçildiyse `make test-e2e`. Lint: `make lint` (pint, ESLint).

## Sorular

`/yigin` akışında hazır yığın seçildikten sonra şu sorular sorulur:

1. **Proje adı.** Küçük harf, boşluk yerine tire. Şablonlardaki `__PROJE__` yerine yazılır. Compose proje adı `<proje>-local` ve `<proje>-live`, ağ adları `<proje>-local-network` ve `<proje>-network` olur.
2. **Proje numarası.** İki hane, 01-99. Şablonlardaki `__NO__` yerine yazılır. Portlar ondan türer: Traefik `80NN`, Postgres `54NN`, Redis `63NN`.
   - Numaranın başka bir projede kullanılmadığını kullanıcı söyler. Claude başka proje klasörlerine bakmaz.
   - Seçilen numara `yigin.md` dosyasına yazılır.
3. **Ekler.** Çoklu seçim. İlk şık: "mailpit + queue + scheduler — oben-stack (Önerilen)". Diğer şıklar: mailpit, queue, scheduler, e2e (Playwright).

## Kurulum

Plan onaylandıktan sonra iki komut çalışır. Ayrıntı ve sıra `kur.py` içindedir; burada ne yaptıkları yazar.

**`kur.py yapilandir laravel-next <proje> <no> <ekler>`** (ağ gerekmez):
- portlar (`80NN`, `54NN`, `63NN`) doluysa durur;
- şablonlardan `compose.local.yaml` ve `compose.live.yaml` yazar; seçilmeyen eklerin blokları silinir;
- `docker/` (php, nginx, frontend) ve `.dockerignore` kopyalanır;
- `Makefile.tmpl` → `Makefile`, `../_ortak/github/test.yml` → `.github/workflows/test.yml`, `yigin.md.tmpl` → `docs/proje/yigin.md`;
- `env.example` anahtarları ile `HOST_UID` ve `HOST_GID`, `.env.example` ve `.env` dosyalarına aynı sırayla eklenir;
- yerel `.env` değerleri üretilir: rastgele DB parolası ve `APP_KEY`, `APP_URL`, `DB_DATABASE`, kullanıcı kimliği. Dolu değere dokunulmaz; `APP_DOMAIN` ve `API_DOMAIN` boş kalır;
- `fastapi-next` klasörü silinir.

**`kur.py kod`** (Docker ve ağ gerekir; birkaç dakika):
1. `composer create-project laravel/laravel` (konteynerde) ve Laravel'in `backend/CLAUDE.md`, `backend/AGENTS.md` dosyalarının silinmesi (Bilinen sınırlar);
2. `phpunit.xml` içindeki `<php>` bloğunun `backend-test/phpunit-php-blogu.xml` ile değişmesi; `backend-test/tests/` kopyası;
3. `bootstrap/app.php`: `trustProxies` (yalnızca özel ağlar; `'*'` kullanılmaz: ziyaretçi `X-Forwarded-For` uydurabilir, 2026-11-23 tarihinde denendi) ve `statefulApi`;
4. `create-next-app` (konteynerde), proxy dosyaları (`../_ortak/frontend-proxy/`), Vitest dosyaları, e2e eki varsa Playwright dosyaları, `next.config.ts` içine `output: "standalone"`, test paketleri;
5. `make up` (build ile), `install:api` (Sanctum) ve `User` modeline `HasApiTokens`;
6. queue eki: Horizon kurulur; `config/horizon.php` içindeki `defaults` ve `environments` girdileri `backend-horizon/horizon-defaults.php` ile değişir (yalnızca `defaults` değişirse Horizon eski `supervisor-1` adını çalıştırır); scheduler eki de varsa `horizon:snapshot` beş dakikada bir zamanlanır;
7. `pint` ile biçim, `make migrate`, `make test`, `make lint`; sonunda adresler.

Her adım sonucunu kontrol eder; betik yeniden çalıştırılınca biten adımlar atlanır. Bir dosya yaması beklediği satırı bulamazsa durur ve aradığı metni yazar; dosya elle düzenlenip betik yeniden çalıştırılır.

## Ortam değişkenleri

Tek kaynak kök `.env` dosyasıdır. Konteynerlere `env_file: .env` ile verilir.

Gizli olmayan altyapı bilgisi compose içindeki `x-laravel-env` bloğunda durur. Bu bilgi `.env` dosyasına yazılmaz. Örnekler: `DB_HOST`, `REDIS_HOST`, `MAIL_HOST`, `QUEUE_CONNECTION`, `REDIS_QUEUE_RETRY_AFTER`, `SANCTUM_STATEFUL_DOMAINS`. Frontend'in `INTERNAL_API_URL` değeri de compose içindedir.

Laravel, konteynerde tanımlı bir ortam değişkenini kendi `backend/.env` dosyasındaki değere tercih eder. `composer create-project` bir `backend/.env` açar. Bu dosya silinirse tek kaynak kök `.env` kalır. Silinmezse, kökte olmayan anahtarlar oradan okunur.

Anahtarlar (yerel değerleri `kur.py` doldurur; canlıda kullanıcı doldurur):

| Anahtar | Not |
|---|---|
| `APP_NAME`, `APP_ENV`, `APP_DEBUG`, `APP_URL` | Laravel uygulama ayarları. Yerelde `APP_URL=http://app.localhost:80NN`. |
| `APP_DOMAIN` | Yalnızca canlıda, zorunlu. Frontend'in alan adı, örneğin `app.ornek.com`. Boşsa canlı compose dosyası hata verir. |
| `API_DOMAIN` | Yalnızca canlıda, isteğe bağlı. Doğrudan Laravel'e giden alan adı, örneğin `api.ornek.com`; mobil uygulama, webhook ve Horizon paneli için. Boşsa bu yönlendirme etkisizdir. |
| `APP_KEY` | Yerelde `kur.py` üretir. Canlı için yeni bir anahtar: `docker compose -f compose.local.yaml exec backend php artisan key:generate --show` |
| `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD` | Postgres bunlarla açılır. Parola boşsa Postgres başlamaz. |

Canlıda e-posta gibi yeni bir ayar gerekirse anahtarı aynı işte `.env` ve `.env.example` dosyalarına eklenir. Canlı compose dosyası `MAIL_*` değeri vermez; Laravel'in varsayılanı `MAIL_MAILER=log`'dur, yani canlıda e-posta gönderilmez, günlüğe yazılır. Gerçek e-posta için `MAIL_MAILER`, `MAIL_HOST`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM_ADDRESS` anahtarları eklenir.

## Canlıda Nginx Proxy Manager

1. İlk `make live-up` ile proje kendi ağını açar: `<proje>-network`.
2. Sunucuda bir kez NPM bu ağa bağlanır: `docker network connect <proje>-network <npm-konteyneri>`. NPM konteynerinin adı `docker ps` ile görülür.
3. NPM'de proxy host tanımlanır: `APP_DOMAIN` → `<proje>-traefik`, port `80`, şema `http`.
4. `API_DOMAIN` kullanılıyorsa ikinci bir proxy host tanımlanır: `API_DOMAIN` → `<proje>-traefik`, port `80`.
5. SSL sertifikaları NPM'de alınır.

Bağlantıyı NPM kurduğu için projenin compose dosyası NPM'in ağ adını bilmek zorunda değildir. `socket-proxy` ayrı bir iç ağda olduğu için NPM ona ulaşamaz.

## Sürüm notu

Bu sürümlerin Docker Hub'da var olduğu 2026-11-23 tarihinde Docker Hub tag API'sinden kontrol edildi. `kur.py` aynı gün üç kurulumla denendi (bütün ekler + e2e, eksiz; fastapi-next bütün eklerle): `make test`, `make test-e2e`, `make lint`, `make doctor`, `make ci` geçti. GitHub Actions dosyası GitHub'da çalıştırılmadı; çağırdığı `make ci` yerelde denendi.

- **PHP 8.4:** 8.5 imajı da var. Laravel'in 8.5 desteği doğrulanmadığı için 8.4 seçildi. Laravel 13.17, PHP 8.4 imajıyla bu yığının testinde çalıştı.
- **Postgres 17:** 18 imajı da var. 18 ile veri klasörünün yolu değişti; hacim yolu doğrulanmadan geçilmez.
- **Diğerleri:** Node 24, Redis 8, nginx 1.28, Traefik 3.6, Mailpit 1.27, tecnativa/docker-socket-proxy 3.4.
- **Kurulumda sabitlenenler (`kur.py`):** `laravel/laravel:^13.0`, `create-next-app@16.4.6`, vitest 5.1.1, @vitejs/plugin-react 6.3.0, jsdom 31.0.1, @testing-library/react 16.3.3, @testing-library/dom 10.4.2, @types/node 24 (create-next-app 20 kurar, Vitest 5 en az 22 ister), @playwright/test 1.65.1 (compose'daki `mcr.microsoft.com/playwright:v1.65.1-noble` imajıyla birebir aynı olmalı; biri değişince öbürü de değişir).

## Bilinen sınırlar

- **Kullanıcı kimliği:** PHP ve Node dev imajlarının kullanıcısı ile e2e servisi, `.env` içindeki `HOST_UID` ve `HOST_GID` değerlerini alır (`kur.py` yazar). Böylece `backend/` ve `frontend/` altında root sahibi dosya oluşmaz. Değer boşsa 1000 kullanılır.

- **`init: true`:** PHP servisleri ve frontend `init: true` ile çalışır. Bu olmadan Horizon ve Node PID 1'de kapanma sinyalini almaz; Docker `stop_grace_period` (Horizon'da 16 dakika) kadar bekleyip süreci zorla öldürür. Testte `init` olmadan durdurma 40 saniyelik sınırı doldurup zorla öldürüldü, `init` ile 1 saniyede bitti.
- **nginx ve backend IP'si:** nginx, `backend` adını Docker DNS'inden 10 saniyede bir yeniden sorar. Bu olmadan backend yeniden oluşturulunca nginx 502 verir (testte görüldü).
- **Next.js 16 `cacheComponents`:** create-next-app bunu açık getirir; route handler'larda `export const dynamic` yazılamaz. Proxy dosyaları buna göre yazılmıştır.
- **`backend/CLAUDE.md` ve `backend/AGENTS.md` (Laravel 13):** create-project ikisini birebir aynı içerikle açar. İçerik Laravel Boost'un açılış talimatıdır ve iskeletle çelişir: `php -v` ve `composer -V` komutlarını bilgisayarda çalıştırtır, PHP yoksa `curl … | bash` ile bilgisayara PHP kurdurur, isteğe başlamadan önce `composer require laravel/boost` ile paket kurdurur. Claude `backend/` içinde çalışırken `backend/CLAUDE.md` dosyasını yükler. Bu yüzden ikisi de Laravel oluşturulur oluşturulmaz silinir (Sonraki adımlar). Laravel Boost istenirse kullanıcı kararıyla ve konteynerde kurulur: `docker compose -f compose.local.yaml exec backend composer require laravel/boost --dev`; ürettiği yeni belgeler de iskeletin kurallarıyla karşılaştırılır.
- **`frontend/AGENTS.md` (Next.js):** create-next-app açar, `next dev` her çalıştığında kendi bloğunu yeniden yazar; silmenin anlamı yoktur. İçeriği iskeletle çelişmez: "kod yazmadan önce bu sürümün belgelerini oku" der. Belgeler `node_modules/next/dist/docs/` içindedir ve `node_modules` bir Docker hacminde durduğu için bilgisayarda değil konteynerdedir: `docker compose -f compose.local.yaml exec frontend ls /app/node_modules/next/dist/docs`. Bildiğim kadarıyla Claude Code `AGENTS.md` dosyasını kendiliğinden yüklemez; Next.js koduna dokunmadan önce bu belgeler konteynerden okunur.

- **Docker soketi:** `socket-proxy` sokete `:ro` ile bağlanır. Ama `:ro` yalnızca soket dosyasının kendisini korur, Docker API'sini kısıtlamaz. Asıl koruma vekilin izin ayarlarındadır: yalnızca `CONTAINERS` açık, `POST` kapalı. Vekile yeni bir izin eklemeden önce ne açtığı kontrol edilir.
- **Proje numarası:** iki proje aynı numarayı alırsa portları çakışır. Numaralar kullanıcı tarafından takip edilir.
- **Proxy belleği:** proxy, yükleme gövdesini Node belleğinde tutar. 20 MB sınırıyla bu sorun değildir. Çok büyük dosyalar `API_DOMAIN` üzerinden doğrudan Laravel'e yüklenebilir.
- **Yükleme sınırı:** `docker/php/Dockerfile` içindeki `upload_max_filesize` ile `docker/nginx/default.conf` içindeki `client_max_body_size` aynı değerdir (20 MB). Biri değişince öbürü de değişir.
- **`public/storage`:** canlı nginx imajı `backend/public` klasörünü kopyalar. `php artisan storage:link` bağlantısı canlı nginx'te çalışmaz.
- **Yüklenen dosyalar:** canlıda `backend-storage` hacminde (`storage/app`) durur. Hacim silinmez.
- **npm varsayımı:** frontend canlı imajı `package-lock.json` ister. Next.js canlı imajı için `next.config` içinde `output: "standalone"` olmalıdır.

## Sonraki adımlar (kullanıcıya gösterilir)

`kur.py kod` uygulamayı açar, göçleri ve testleri çalıştırır. Elle kalanlar:

- **Horizon (queue eki):** canlıda panel erişimi için `app/Providers/HorizonServiceProvider.php` içindeki `viewHorizon` gate'ine izinli kullanıcılar yazılır.
- **Canlı:** `.env` içinde `APP_DOMAIN` (ve isteğe bağlı `API_DOMAIN`) doldurulur, canlı için yeni `APP_KEY` ve parola üretilir; NPM ayarı "Canlıda Nginx Proxy Manager" bölümündedir.
- **`kur.py kod` çalıştırılmadıysa:** aynı komut sonra çalıştırılabilir.

Adresler (NN = proje numarası): arayüz `http://app.localhost:80NN`, API `http://api.localhost:80NN`, Mailpit `http://mail.localhost:80NN`, Traefik paneli `http://traefik.localhost:80NN`, Horizon `http://api.localhost:80NN/horizon`.
