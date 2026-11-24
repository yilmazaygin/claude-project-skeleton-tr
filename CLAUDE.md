# Proje

Bu depo, yeni bir projeye başlarken kullanılan iskelettir. Ürünün ne olduğu `docs/proje/hakkinda.md`, yığını `docs/proje/yigin.md` dosyasındadır. İkisi boşsa ürün ve yığın henüz seçilmemiştir; uydurulmaz.

## Oturum başı

`.claude/iskelet.json` içinde `tur` alanı `iskelet` ise proje henüz başlatılmamıştır. Kullanıcı iskeletin kendisini geliştirmiyorsa ilk yanıtta `/basla` hatırlatılır: "Projeyi anlatıp 'başla' derseniz onboarding'e başlarız." Kullanıcı "başla" derse `basla` skill'i kullanılır. Bu bölüm `/basla` bitince kaldırılır.

## Kurallar

Davranış kuralları `.claude/rules/` altındadır ve her oturumda kendiliğinden yüklenir. Her dosya tek bir davranışı anlatır:

- `durustluk.md` uydurma yok, yapılmayan iş yapılmış sayılmaz
- `soru.md` belirsizlikte şıklı soru, büyük kararda inisiyatif yok
- `plan.md` geniş işte plan modu, onaysız kod yok
- `kapsam.md` proje dizini dışına çıkılmaz
- `git.md` Git salt okunur
- `veri.md` veri ve gizli değerler korunur
- `docker.md` araçlar konteynerde çalışır, günlük işler Makefile'da
- `etki.md` davranış değişince test ve arayüz
- `mantik-belgeleri.md` önce mantık belgesi okunur; belgeler kullanıcıyla birlikte yazılır
- `kayitlar.md` değişiklik ve teknik borç defterleri
- `alt-ajan.md` alt ajan kullanımı

Yeni bir davranış, mevcut bir dosyaya bir cümle olarak yazılabiliyorsa ayrı dosya açılmaz. `.claude/rules/` altına README veya kural olmayan dosya konmaz; oradaki her `.md` yüklenir.

## İsteğe bağlı kurallar

`.claude/opsiyonel-kurallar/` altındaki kurallar repoyla gelir ama yüklenmez. Bir projede gerekirse `/kural ac <ad>` ile açılır (`/basla` gerekenleri kendisi açar); açılan kural `.claude/rules/` altına kopyalanır. Liste ve açıklama `.claude/opsiyonel-kurallar/README.md` dosyasındadır.

- `denetim-kaydi`: kullanıcıların ve sistemin önemli işleri değiştirilemez, hash zincirli bir kayda yazılır.
- `cerez-ve-izleme`: çerez onayı, onay öncesi betik yüklememe, çerez listesi ve güvenlik kaydı (giriş denemeleri, IP, konum). Seçmeli hazır parçalar: çerez onayı, GA4, Umami, güvenlik kaydı. Kurulunca "çerez politikası" TD'si açılır.
- `yedekleme`: Postgres her gün yedeklenir ve doğrulanır, saklama düzeni uygulanır, her hafta geri yükleme sınanır; isteğe bağlı uzak kopya. Kurulunca "yedek doğrulama" TD'si açılır.

### Açık isteğe bağlı kurallar

Şu an açık isteğe bağlı kural yok.

## Zorlama

Bazı kurallar `.claude/settings.json` içinde izin kuralıyla da zorlanır: Git yazma komutları, SSH, hacim silme ve canlı ortam. Kural metni değişince izin kuralı da aynı işte değişir.

## Skill'ler

- `/basla` onboarding: serbest anlatımdan projeyi anlar, eksikleri sorar; ürün belgesini, yığın ayarlarını, kuralları ve mantık belgelerini kullanıcıyla birlikte yazar, gereksizleri siler, ilk prompt'u (`docs/proje/ilk-istem.md`) birlikte hazırlar. Kod yazmaz. Bir kez çalışır.
- `/changelog` `docs/kayitlar/degisiklikler.md` dosyasına satır ekler.
- `/td` `docs/kayitlar/teknik-borclar.md` dosyasına borç kaydı ekler veya günceller.
- `/kural` isteğe bağlı kuralları listeler, açar veya kapatır. Yalnızca kullanıcı çağırır.
- `/yigin` yığını seçer veya değiştirir, servis ekler. Yalnızca kullanıcı çağırır.
  - Hazır yığınlar `.claude/skills/yigin/hazir/` altındadır: `laravel-next` (Laravel + Next.js + Postgres + Redis + Traefik; mailpit, queue ve scheduler eklerinin üçüyle adı oben-stack) ve `fastapi-next` (FastAPI + Next.js, `/api/v1` sürümleme, Celery).
  - Hazır yığını `kur.py` kurar: `yapilandir` ayar dosyalarını ve yerel `.env` dosyasını yazar. `kod` kodu konteynerde oluşturur, uygulamayı açar, göçleri, testleri ve lint'i çalıştırır; ilk prompt'un ilk adımıdır.
  - İki yığın da 2026-11-23 tarihinde `kur.py` ile baştan sona denendi.
  - Yeni hazır yığının nasıl ekleneceği skill dosyasında yazar.
- `/iskelet-guncelle <yol>` iskeletin yeni sürümüyle projeyi karşılaştırır, dosyaları sorarak kopyalar. Yalnızca kullanıcı çağırır.

## Hook'lar

`.claude/hooks/` altındaki iki hook her araç çağrısından önce çalışır. Reddedilen işlemde nedeni Claude'a söyler. Red geldiğinde başka bir komutla dolanılmaz; gerekirse kullanıcıya sorulur.

Hangi korumanın açık olduğu `.claude/iskelet.json` dosyasındaki `korumalar` alanındadır: `git`, `ssh`, `docker-hacim`, `defter`, `env-ornek`. Bu alanı okuyan modül `korumalar.py`.
- **Varsayılan:** hepsi açık.
- **Kapatma:** koruma yalnızca `/basla` sırasında kullanıcı seçince ya da kullanıcı açıkça isteyince kapanır.
- **Ayar dosyalarının korunması:** `iskelet.json` ve `settings.json` bash ile hiç yazılamaz. Edit ve Write ile yapılan değişiklikleri Claude Code kullanıcıya onaylatır.

- `bash_bekci.py` Bash komutunun tamamını tarar. `git -C`, `cd x && git`, `bash -c` ve `$( )` içindekiler dahil.
  - Git'te yazan komutları reddeder.
  - SSH, scp ve sftp kullanımını reddeder.
  - Hacim ve veri silen Docker komutlarını reddeder.
  - Kayıt defterlerinin üzerine yazmayı reddeder. `>>` ile alta ekleme serbesttir.
  - `.env.example` dosyasına bash ile yazmayı reddeder.
  - `iskelet.json` ve `settings.json` dosyalarına bash ile yazmayı her zaman reddeder.
- `dosya_bekci.py` Edit ve Write çağrılarını denetler.
  - `docs/kayitlar/` altında yalnızca alta eklemeye izin verir. İskeletin kendisinde (`tur: iskelet`) `.claude/iskelet-gecmisi/` için de aynısı geçerlidir.
  - `.env.example` dosyasında yalnızca değersiz `ANAHTAR=` satırlarına ve yorumlara izin verir.

Hook değişince testler çalıştırılır: `python3 .claude/hooks/hook_testleri.py`. Testler projenin ayarından bağımsızdır. Hook dosyasının adı değişirse `settings.json` aynı işte, ad değişmeden önce güncellenir; yoksa hook çalışamaz ve her araç çağrısı engellenir.

Komut adı değişkenden kurulamaz (`G=git; $G push` reddedilir). `bash x.sh`, `source x.sh` veya `./x.sh` ile çalıştırılan script'in içi de taranır. `cd` ile klasör değişimi takip edilir.

Hook'lar yüzde yüz koruma sağlamaz. Python, Node gibi başka bir dilin içinden yapılan çağrı ve 256 KB'tan büyük script yakalanmaz. Metin kuralları her durumda geçerlidir. `.env` ile `.env.example` arasındaki sıra eşitliğini hook değil `make doctor` denetler.

Hook'lar bilgisayardaki `python3` ile çalışır. `python3` yoksa veya hook hata verirse işlem güvenlik için engellenir; bu durumda önce `python3` kurulur. Docker kuralı projenin araçları içindir. Hook'lar Claude Code'un parçasıdır, proje aracı değildir.

## Ne nerede

- `.claude/iskelet.json`:
  - `tur`: `iskelet` (bu deponun kendisi) veya `proje` (`/basla` ile başlatılmış);
  - `surum`: iskeletin SemVer sürümü (projede: açıldığı sürüm);
  - `korumalar`;
  - `kaldirilanlar`: `/basla` sırasında silinenler; `/iskelet-guncelle` bunları yeniden önermez.
- `.claude/iskelet-gecmisi/` iskeletin kendi geliştirme geçmişi (değişiklikler ve teknik borçlar). `tur: iskelet` iken kayıtlar oraya yazılır; projede `/basla` bu klasörü siler.
- `CHANGELOG.md` iskeletin herkese açık sürüm notları (SemVer); `LICENSE` iskeletin MIT lisansı. İkisi de iskeletindir: projede `/basla` siler, lisansı projeye göre sorar.
- **Yeni sürüm** (yalnızca iskelette): `CHANGELOG.md` dosyasına yeni bölüm yazılır ve `iskelet.json` içindeki `surum` aynı işte yükseltilir. Tag ve GitHub release'i kullanıcı oluşturur.
- `docs/` belgeler ve kayıtlar. Hangi belgenin nereye konacağı `docs/README.md` dosyasındadır. Projenin defterleri `docs/kayitlar/` altındadır ve boş başlar. İlk prompt `docs/proje/ilk-istem.md` dosyasındadır (`/basla` yazar).
- `.dev/` geçici dosyalar. Yolu verilmedikçe bakılmaz.
- `Makefile`, `compose.local.yaml`, `compose.live.yaml` çalıştırma. `.claude/doktor.py` sağlık kontrolü (`make doctor`).
- `.env.example` ortam anahtarlarının değersiz listesi.
