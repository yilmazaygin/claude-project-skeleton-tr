# Sürüm notları

İskeletin herkese açık sürüm notları. Biçim [Keep a Changelog](https://keepachangelog.com/tr-TR/1.1.0/), sürümleme [SemVer](https://semver.org/lang/tr/).

Sürüm numarası `.claude/iskelet.json` içindeki `surum` alanındadır. `/iskelet-guncelle`, projenin sürümünden yeni olan bölümleri buradan okuyup özetler.

- **Ana sürüm (2.0.0):** projeyi elle düzeltmeyi gerektiren değişiklik. Örneğin bir kuralın adı veya `iskelet.json` biçimi değişti.
- **Ara sürüm (1.1.0):** yeni özellik. Örneğin yeni hazır yığın, yeni isteğe bağlı kural, yeni skill.
- **Yama (1.0.1):** düzeltme.

## [1.0.0] - 2026-11-24

İlk sürüm.

### Eklendi

- **`/basla` onboarding'i:**
  - projeyi serbestçe anlatırsınız, Claude yalnızca eksikleri şıklı sorar;
  - ürün belgesini, yığın ayarlarını, gereken isteğe bağlı kuralları, projeye özel kuralları ve mantık belgelerini birlikte yazar;
  - kullanılmayanları siler ve ilk prompt'u (`docs/proje/ilk-istem.md`) birlikte hazırlar.
- **Davranış kuralları:** dürüstlük, şıklı soru, plan modu, kapsam, Git salt okunur, veri ve gizli değer koruması, Docker, etki (test ve arayüz), mantık belgeleri (birlikte yazma), kayıtlar, alt ajan.
- **Hook'lar:** kuralların bir kısmını zorlar.
  - `bash_bekci.py`: Git yazma, SSH, hacim silme, defterin üzerine yazma.
  - `dosya_bekci.py`: defterler yalnızca alta eklenir, `.env.example` değersiz kalır.
  - Korumalar `.claude/iskelet.json` ile açılıp kapanır.
  - 112 test.
- **Hazır yığınlar:**
  - `laravel-next`: Laravel 13 + Next.js 16 + Postgres + Redis, Horizon. mailpit, queue ve scheduler ekleriyle adı oben-stack.
  - `fastapi-next`: FastAPI + Next.js, `/api/v1`, Celery.
  - İkisinde de proje başına Traefik, Mailpit ve Docker soket vekili; proje numarasından türeyen portlar; yalıtılmış `testing` veritabanı; Vitest ve isteğe bağlı Playwright.
- **`kur.py`:** ayar dosyalarını ve yerel `.env` değerlerini yazar. İlk prompt'ta kodu konteynerde oluşturur, testleri çalıştırır; yarıda kalırsa kaldığı yerden devam eder.
- **Makefile hedefleri:** `up`, `down`, `logs`, `sh`, `migrate`, `test`, `test-e2e`, `lint`, `doctor`, `ci`. GitHub Actions dosyası `make ci` çağırır.
- **İsteğe bağlı kurallar:**
  - `denetim-kaydi`: hash zincirli, değiştirilemez kayıt;
  - `cerez-ve-izleme`: çerez onayı, GA4 veya Umami, güvenlik kaydı ve anonimleştirme;
  - `yedekleme`: günlük döküm, saklama düzeni, geri yükleme sınaması, rclone.
- **Diğer skill'ler:** `/yigin`, `/kural`, `/changelog`, `/td`, `/iskelet-guncelle`.
