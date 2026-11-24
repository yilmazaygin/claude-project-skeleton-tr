---
ad: fastapi-next
ozet: FastAPI (Python 3.13, SQLAlchemy 2 async, Alembic) API ve hazır başlangıç kodu, Next.js (React, TypeScript, Tailwind) arayüz, Postgres, Redis, proje başına Traefik. API sürümlü (/api/v1). Canlıda Nginx Proxy Manager → Traefik → servisler.
ekler: mailpit, queue, scheduler, e2e
---

# Hazır yığın: fastapi-next

laravel-next (oben-stack) ile aynı mimari; backend Laravel yerine FastAPI'dir.

- **Hazır başlangıç kodu:** Laravel'in aksine FastAPI'nin resmi bir proje iskeleti yoktur. Bu yığın ayar dosyalarına ek olarak çalışan küçük bir `backend/` iskeleti de verir.
- **Next.js tarafı:** laravel-next ile aynıdır ve `../_ortak/` klasöründen gelir.

## İlkeler

- **Yerel canlıya benzer.** Aynı servisler, aynı Traefik, aynı yönlendirme mantığı.
- **Her şey proje başınadır.** Traefik, Mailpit, Flower ve soket vekili her projede ayrıdır.
- **Portlar proje numarasından türer:** Traefik `80NN`, Postgres `54NN`, Redis `63NN`.
- **API sürümlüdür.** Bütün uç noktalar `/api/v1/...` altındadır.

## Mimari

```
Yerel (proje no NN):
  tarayıcı → traefik:80NN → app.localhost    → frontend ─(/api/*)→ backend:8000 (FastAPI)
                          → api.localhost    → backend:8000   (/api/docs, Postman)
                          → mail.localhost   → mailpit
                          → flower.localhost → flower
  veritabanı istemcisi → localhost:54NN (Postgres), localhost:63NN (Redis)

Canlı:
  tarayıcı → NPM (80/443, SSL) → traefik:80 → APP_DOMAIN → frontend ─(/api/*)→ backend:8000
                                            → API_DOMAIN → backend:8000   (isteğe bağlı)

Her iki ortamda:
  traefik ─(iç "socket" ağı)→ socket-proxy ─(yalnızca listeleme)→ Docker
```

Laravel yığınından farkı: nginx yoktur. Traefik ve Next.js doğrudan uvicorn'a (`backend:8000`) gider. Next.js proxy'si yalnızca `/api/*` için kullanılır; `/sanctum` route'u bu yığında gereksizdir ve kopyalanmaz.

## API sürümleme

- Kök router `app/api/__init__.py` içinde, `/api` önekiyle tanımlıdır. Her sürüm kendi paketindedir: `app/api/v1/`, `app/api/v2/`...
- **Yeni sürüm:**
  - `app/api/v2/__init__.py` içinde `APIRouter(prefix="/v2")` açılır;
  - kök router'a bir `include_router` satırı eklenir;
  - v1 kaldırılmaz, iki sürüm birlikte yayında kalır.
- **Değişiklik kuralı:** geriye uyumsuz değişiklik yeni sürüme yazılır. Yeni alan veya yeni uç nokta gibi uyumlu eklemeler mevcut sürüme yapılabilir.
- **Belgeler** `/api/docs` ve `/api/openapi.json` adreslerindedir. `/api` altında oldukları için Next.js proxy'si üzerinden de açılırlar.

## Servisler

| Servis | Görev | Yerel | Canlı |
|---|---|---|---|
| socket-proxy | Traefik'in Docker'ı yalnızca okuyabilmesi | iç ağ, port yok | aynı |
| traefik | Ters vekil | `80NN:80`; panel `traefik.localhost:80NN` | port yok; NPM'den gelir; panel kapalı |
| backend | FastAPI (uvicorn) | `./backend` bağlanır, `--reload`; `api.localhost:80NN` | kod imajda, 4 işçi; `API_DOMAIN` doluysa o alan adı |
| frontend | Node 24, Next.js | `./frontend` bağlanır, `app.localhost:80NN` | standalone build, `APP_DOMAIN` |
| db | postgres:17-alpine | `54NN:5432` | port yok |
| redis | redis:8-alpine; Celery aracısı ve sonuç deposu; healthcheck var | `63NN:6379` | port yok |

## Ekler

Her ekin şablonlardaki blokları `# >>> ek:<ad>` ve `# <<< ek:<ad>` satırları arasındadır.

| Ek | Ne yapar | Nerede | Seçilmezse |
|---|---|---|---|
| mailpit | Giden e-postaları yakalar; arayüzü `mail.localhost:80NN`. Uygulama `SMTP_HOST`/`SMTP_PORT` ile gönderir. | yalnızca yerel | `SMTP_HOST` boş kalır |
| queue | Celery: `worker` (kısa işler), `worker-long` (uzun işler), `flower` (panel, yalnızca yerel) | yerel ve canlı | Celery servisleri yoktur |
| scheduler | `celery beat`; zamanlanmış görevler `app/worker.py` içindeki `beat_schedule`'dadır | yerel ve canlı | zamanlanmış görev yoktur |
| e2e | Playwright ile gerçek tarayıcıda uçtan uca test. `e2e` servisi Traefik'in ağını paylaşır; `make up` ile açılmaz | yalnızca yerel | uçtan uca test yoktur |

**scheduler tek başına işe yaramaz:** beat görevleri yalnızca kuyruğa koyar, çalıştıran worker'lardır. Kullanıcı scheduler'ı queue olmadan seçerse bu söylenir ve queue'nun da eklenmesi önerilir.

## Kuyruklar (queue eki)

| Worker | Kuyruklar | Zaman sınırı | Eşzamanlılık (yerel / canlı) | Durdurma bekleme süresi |
|---|---|---|---|---|
| worker | `high`, `default`, `low` | 120 sn (yumuşak: 110) | 2 / 4 | 130 sn |
| worker-long | `long` | 900 sn (yumuşak: 880) | 1 / 2 | 16 dk |

- Kısa iş `gorev.delay()` ile, uzun iş `gorev.apply_async(queue="long")` ile gönderilir.
- Redis aracısında Celery kuyrukları katı öncelikle değil sırayla okur. `high` kuyruğunun her zaman önce işlenmesi gerekiyorsa ona ayrı bir worker açılır.
- Yerelde kod değişince worker'lar yeniden başlatılır: `docker compose -f compose.local.yaml restart worker worker-long`.
- Görevler `app/tasks.py` içindedir. Yeni görev modülleri `app/worker.py` içindeki `include` listesine eklenir.

## Başlangıç kodu (`backend-baslangic/`)

```
backend/
├── requirements.txt          sabit sürümler (pip)
├── alembic.ini
├── alembic/
│   ├── env.py                async göç; adres app.config'ten, modeller app.models'ten
│   ├── script.py.mako
│   └── versions/
└── app/
    ├── main.py               FastAPI uygulaması; belgeler /api/docs
    ├── config.py             pydantic-settings; ortam değişkenleri
    ├── db.py                 async SQLAlchemy 2 engine + get_session bağımlılığı
    ├── models/__init__.py    Base (yeni modeller burada içe aktarılır)
    ├── api/__init__.py       /api kök router'ı ve sürümleme kuralı
    ├── api/v1/__init__.py    /api/v1 router'ı
    ├── api/v1/health.py      GET /api/v1/health: veritabanı ve Redis kontrolü
    ├── worker.py             Celery uygulaması (queue eki)
    └── tasks.py              örnek görev: ping (queue eki)
```

- **Paket ekleme:** yeni paket `requirements.txt` dosyasına sabit sürümle yazılır, ardından `docker compose -f compose.local.yaml build backend` ile imaj yeniden build edilir.
- **Model ve göç:**
  - model `app/models/` altına yazılır ve `app/models/__init__.py` içinde içe aktarılır;
  - göç dosyası `alembic revision --autogenerate -m "aciklama"` ile üretilir;
  - `alembic upgrade head` ile uygulanır.

  İki komut da backend konteynerinde çalıştırılır.

## Araç engeli

`/yigin` 5. adımda kabul edilirse engellenecek araçlar: `pip`, `pip3`, `uvicorn`, `alembic`, `pytest`, `celery`, `node`, `npm`, `npx`, `yarn`, `pnpm`. `python3` engellenmez: iskeletin kendi betikleri (hook'lar, `kur.py`, `doktor.py`) onunla çalışır. Konteyner içindeki kullanım etkilenmez.

## Testler

Testler geliştirme verisinden yalıtılmıştır (veri.md kuralı).

- **Test veritabanı:** `testing`. Yerel compose dosyasındaki tek seferlik `db-test-hazirla` servisi açar. Canlıda yoktur.
- **`backend/tests/conftest.py`:** `DB_DATABASE`, uygulama içe aktarılmadan önce `testing` yapılır, çünkü ayarlar ve bağlantı içe aktarma anında kurulur. Ardından bir koruma bunu doğrular; değilse test başlamadan durur. Göçler test veritabanına `alembic upgrade head` ile uygulanır.
- **Örnek testler:** `backend/tests/test_health.py`; sağlık kontrolü, olmayan API sürümünün 404 dönmesi ve test veritabanı kontrolü.
- **Test paketleri:** `backend/requirements-dev.txt` (pytest 9.2.0, pytest-asyncio 1.5.0, httpx 0.28.1, ruff 0.17.6). Yalnızca `dev` imajına kurulur, canlı imaja girmez.
- **Çalıştırma:** `make test` (backend `pytest`, frontend `npx vitest run`); e2e eki seçildiyse `make test-e2e`. Lint: `make lint` (ruff, ESLint). Ruff ayarı `backend/ruff.toml` içindedir; Alembic'in ürettiği göç dosyaları denetlenmez.

## Sorular

`/yigin` akışında hazır yığın seçildikten sonra şu sorular sorulur:

1. **Proje adı.** Küçük harf, boşluk yerine tire. `__PROJE__` yerine yazılır. Compose proje adı `<proje>-local` ve `<proje>-live`, ağ adları `<proje>-local-network` ve `<proje>-network` olur.
2. **Proje numarası.** İki hane, 01-99. `__NO__` yerine yazılır. Numaranın başka bir projede kullanılmadığını kullanıcı söyler; Claude başka proje klasörlerine bakmaz.
3. **Ekler.** Çoklu seçim. İlk şık: "mailpit + queue + scheduler (Önerilen)". Diğer şıklar: mailpit, queue, scheduler, e2e (Playwright).

## Kurulum

Plan onaylandıktan sonra iki komut çalışır. Ayrıntı ve sıra `kur.py` içindedir.

**`kur.py yapilandir fastapi-next <proje> <no> <ekler>`** (ağ gerekmez): laravel-next ile aynıdır; ek olarak `backend-baslangic/` proje köküne `backend/` adıyla kopyalanır. queue eki seçilmediyse `app/worker.py` ve `app/tasks.py` silinir, `requirements.txt` içinden `celery` ve `flower` satırları çıkarılır. Yerel `.env` değerleri: rastgele DB parolası ve `SECRET_KEY`, `DB_DATABASE`, kullanıcı kimliği. `laravel-next` klasörü silinir.

**`kur.py kod`** (Docker ve ağ gerekir):
1. `create-next-app` (konteynerde), proxy dosyaları (yalnızca `lib/api-proxy.ts` ve `app/api/[...path]/route.ts`; `sanctum` route'u bu yığında gerekmez), Vitest dosyaları, e2e eki varsa Playwright dosyaları, `next.config.ts` içine `output: "standalone"`, test paketleri;
2. `make up` (build ile);
3. ilk Alembic göçü (`alembic revision --autogenerate -m baslangic`);
4. `make migrate`, `make test`, `make lint`; sonunda adresler.

Her adım sonucunu kontrol eder; betik yeniden çalıştırılınca biten adımlar atlanır.

## Ortam değişkenleri

Tek kaynak kök `.env` dosyasıdır. Gizli olmayan bağlantı bilgileri compose içindeki `x-python-env` bloğunda durur: `DB_HOST`, `DB_PORT`, `REDIS_HOST`, `REDIS_PORT`, `SMTP_HOST`, `SMTP_PORT`. Frontend'in `INTERNAL_API_URL` değeri de compose içindedir.

| Anahtar | Not |
|---|---|
| `APP_NAME`, `APP_ENV` | Uygulama adı (API belgelerinin başlığı) ve ortam |
| `SECRET_KEY` | Uygulamanın imzalama anahtarı (oturum, token). Uzun ve rastgele olur; örneğin `python -c "import secrets; print(secrets.token_urlsafe(48))"` (backend konteynerinde) |
| `APP_DOMAIN` | Yalnızca canlıda, zorunlu. Frontend'in alan adı. Boşsa canlı compose dosyası hata verir. |
| `API_DOMAIN` | Yalnızca canlıda, isteğe bağlı. Doğrudan FastAPI'ye giden alan adı. |
| `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD` | Postgres bunlarla açılır; uygulama da aynı değerlerle bağlanır. Parola boşsa Postgres başlamaz. |

## Canlıda Nginx Proxy Manager

1. İlk `make live-up` ile proje kendi ağını açar: `<proje>-network`.
2. Sunucuda bir kez NPM bu ağa bağlanır: `docker network connect <proje>-network <npm-konteyneri>`.
3. NPM'de proxy host tanımlanır: `APP_DOMAIN` → `<proje>-traefik`, port `80`.
4. `API_DOMAIN` kullanılıyorsa ikinci bir proxy host tanımlanır: `API_DOMAIN` → `<proje>-traefik`, port `80`.
5. SSL sertifikaları NPM'de alınır.
6. Göçler canlıda elle uygulanır: `docker compose -f compose.live.yaml exec backend alembic upgrade head`.

## Sürüm notu

2026-11-23 tarihinde bu yığın baştan sona denendi. İmajlar:

- `python:3.13-slim`: 3.14 da var; kütüphane uyumu için 3.13 seçildi;
- `node:24-alpine`, `postgres:17-alpine`, `redis:8-alpine`, `traefik:v3.6`, `axllent/mailpit:v1.27`, `tecnativa/docker-socket-proxy:3.4`.

Paketler (`requirements.txt`): FastAPI 0.165.0, uvicorn 0.54.0, pydantic-settings 2.16.3, SQLAlchemy 2.1.9, asyncpg 0.32.0, Alembic 1.20.1, redis 8.2.0, Celery 5.7.0, Flower 2.2.0.

Frontend: Next.js 16.4.6. Kurulumda sabitlenen frontend test paketleri laravel-next ile aynıdır (HAZIR.md → Sürüm notu).

`kur.py` 2026-11-23 tarihinde bu yığınla bütün ekler seçili olarak denendi: `make test`, `make test-e2e`, `make lint`, `make doctor`, `make ci` geçti. GitHub Actions dosyası GitHub'da çalıştırılmadı; çağırdığı `make ci` yerelde denendi.

## Bilinen sınırlar

- **Kullanıcı kimliği:** Python ve Node dev imajlarının kullanıcısı ile e2e servisi, `.env` içindeki `HOST_UID` ve `HOST_GID` değerlerini alır (`kur.py` yazar). Değer boşsa 1000 kullanılır.

- **`init: true`:** Python servisleri ve frontend `init: true` ile çalışır; böylece kapanma sinyalini alırlar. Testte bütün servisler 0-3 saniyede kapandı.
- **Docker soketi:** `socket-proxy` sokete `:ro` ile bağlanır, ama `:ro` Docker API'sini kısıtlamaz. Asıl koruma vekilin izin ayarlarındadır: yalnızca `CONTAINERS` açık.
- **Bağımlılıklar imajda:** paket eklenince imaj yeniden build edilir. Yerelde bağlanan `./backend` klasöründe sanal ortam (`.venv`) yoktur ve gerekmez.
- **Flower canlıda yok:** canlıda kuyruk durumu `celery -A app.worker inspect active` gibi komutlarla görülür. Flower canlıda gerekirse parolalı (`--basic-auth`) ve ayrı bir alan adıyla açılır.
- **Next.js 16 `cacheComponents`:** create-next-app bunu açık getirir; proxy dosyaları buna göre yazılmıştır.
- **`frontend/AGENTS.md` (Next.js):** create-next-app açar, `next dev` her çalıştığında kendi bloğunu yeniden yazar; silmenin anlamı yoktur. İçeriği iskeletle çelişmez: "kod yazmadan önce bu sürümün belgelerini oku" der. Belgeler `node_modules/next/dist/docs/` içindedir ve `node_modules` bir Docker hacminde durduğu için bilgisayarda değil konteynerdedir: `docker compose -f compose.local.yaml exec frontend ls /app/node_modules/next/dist/docs`. Bildiğim kadarıyla Claude Code `AGENTS.md` dosyasını kendiliğinden yüklemez; Next.js koduna dokunmadan önce bu belgeler konteynerden okunur.

## Sonraki adımlar (kullanıcıya gösterilir)

`kur.py kod` uygulamayı açar, ilk göçü oluşturup uygular ve testleri çalıştırır. Elle kalanlar:

- **Canlı:** `.env` içinde `APP_DOMAIN` (ve isteğe bağlı `API_DOMAIN`) doldurulur, canlı için yeni `SECRET_KEY` ve parola üretilir; NPM ayarı "Canlıda Nginx Proxy Manager" bölümündedir.
- **`kur.py kod` çalıştırılmadıysa:** aynı komut sonra çalıştırılabilir.

Adresler (NN = proje numarası): arayüz `http://app.localhost:80NN`, API sağlık `http://api.localhost:80NN/api/v1/health`, API belgeleri `http://api.localhost:80NN/api/docs`, Flower `http://flower.localhost:80NN`, Mailpit `http://mail.localhost:80NN`, Traefik paneli `http://traefik.localhost:80NN`.
