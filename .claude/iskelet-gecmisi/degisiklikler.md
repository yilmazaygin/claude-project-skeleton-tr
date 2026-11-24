# İskelet changelog'u

Bu defter iskeletin kendi geliştirme geçmişidir; projenin defteri değildir. Projenin defteri `docs/records/changelog.md` dosyasıdır ve boş başlar. Bu dosya da yalnızca alta eklenir.

Her değişiklik tek satırdır. Sütunlar: Tarih Saat | Alan | Tür | Not

2026-11-23 15:10 | iskelet | eklendi | cursor-project-skeleton iskeleti claude code için kuruldu
2026-11-23 15:10 | docker | değişti | make up ve make live-up konteynerleri arka planda açıyor
2026-11-23 15:10 | docker | değişti | konteyner adı her serviste container_name ile açıkça yazılıyor
2026-11-23 15:10 | iskelet | eklendi | git, ssh, hacim silme ve canlı ortam için izin kuralları eklendi
2026-11-23 15:10 | iskelet | eklendi | kayıt defterleri için /changelog ve /td skill'leri eklendi
2026-11-23 15:19 | iskelet | eklendi | bash komutlarını tamamen tarayan git, ssh, veri silme ve kayıt koruma hook'u eklendi
2026-11-23 15:19 | iskelet | eklendi | kayıt defterlerinde yalnızca alta eklemeye izin veren hook eklendi
2026-11-23 15:19 | iskelet | eklendi | .env.example dosyasına değer yazılmasını engelleyen hook eklendi
2026-11-23 15:19 | iskelet | eklendi | yığını kullanıcıyla seçip iskelete işleyen /yigin skill'i eklendi
2026-11-23 15:28 | iskelet | değişti | bash hook'u değişkenle kurulan komutu reddediyor ve çalıştırılan script'in içini tarıyor
2026-11-23 15:28 | iskelet | değişti | bash hook'u cd ile klasör değişimini izliyor; proje dışındaki aynı adlı dosyalar artık engellenmiyor
2026-11-23 15:28 | iskelet | değişti | python3 yoksa veya hook hata verirse işlem engelleniyor
2026-11-23 15:53 | iskelet | eklendi | /yigin için laravel-next hazır yığını eklendi; dört ekin tamamıyla adı oben-stack
2026-11-23 15:53 | iskelet | değişti | /yigin hazır yığın seçeneği soruyor ve yeni hazır yığın ekleme kalıbını anlatıyor
2026-11-23 15:53 | iskelet | değişti | /yigin compose proje adını <proje>-local ve <proje>-live yazıyor; projelerin hacimleri karışmıyor
2026-11-23 16:18 | iskelet | değişti | laravel-next canlıda NPM → Traefik → servisler yolunu kullanıyor; Traefik yerelde ve canlıda zorunlu
2026-11-23 16:18 | iskelet | değişti | laravel-next canlıda kendi ağını açıyor, NPM bu ağa bağlanıyor; NPM_NETWORK anahtarı kalktı
2026-11-23 16:18 | iskelet | eklendi | laravel-next için /api ve /sanctum isteklerini Laravel'e aktaran Next.js proxy şablonu eklendi
2026-11-23 16:18 | iskelet | eklendi | laravel-next'e redis healthcheck'i ve 20 MB PHP yükleme sınırı eklendi
2026-11-23 16:18 | iskelet | değişti | laravel-next kuyruğu kısa işler (queue) ve uzun işler (queue-long) olarak ikiye ayrıldı
2026-11-23 16:28 | iskelet | eklendi | laravel-next yerel portları proje numarasından türetiyor: traefik 80NN, postgres 54NN, redis 63NN
2026-11-23 16:28 | iskelet | değişti | laravel-next'te traefik docker'a yalnızca listeleme izni veren socket-proxy üzerinden erişiyor
2026-11-23 16:28 | iskelet | eklendi | laravel-next canlıda isteğe bağlı API_DOMAIN ile doğrudan laravel'e yönlendirme yapıyor
2026-11-23 16:28 | iskelet | değişti | laravel-next queue eki iki worker yerine laravel horizon kullanıyor
2026-11-23 16:28 | iskelet | değişti | laravel-next belgesindeki yanlış "soket salt okunur" ifadesi düzeltildi
2026-11-23 17:18 | iskelet | eklendi | fastapi-next hazır yığını eklendi: fastapi, /api/v1 sürümleme, sqlalchemy, alembic, celery, flower ve başlangıç kodu
2026-11-23 17:18 | iskelet | eklendi | git günlüğü kayıtları için /git-journal skill'i eklendi
2026-11-23 17:18 | iskelet | değişti | next.js dockerfile'ı, proxy dosyaları ve dockerignore iki yığının ortak kullandığı hazir/_ortak klasörüne taşındı
2026-11-23 17:18 | iskelet | değişti | laravel ve python servisleri ile frontend init: true ile çalışıyor; kapanma sinyali artık alınıyor
2026-11-23 17:18 | iskelet | değişti | laravel dev imajı www-data kullanıcısıyla çalışıyor; backend altında root sahibi dosya oluşmuyor
2026-11-23 17:18 | iskelet | değişti | nginx backend adresini docker dns'inden yeniden soruyor; backend yenilenince 502 vermiyor
2026-11-23 17:18 | iskelet | değişti | proxy route dosyalarından next.js 16 cacheComponents ile uyumsuz dynamic satırı kaldırıldı
2026-11-23 17:18 | iskelet | değişti | horizon şablonu defaults ile birlikte environments girdisini de veriyor
2026-11-23 17:18 | iskelet | değişti | laravel canlıda oturum çerezi secure işaretiyle gönderiliyor
2026-11-23 19:20 | iskelet | değişti | bash hook'u yorumları satır satır çıkarıyor; # işaretinden sonraki satırlardaki komutlar artık gizlenemiyor
2026-11-23 19:20 | iskelet | değişti | /git-journal dal adını git status -sb ile okuyor ve izinli olmayan git komutlarını kullanmıyor
2026-11-23 19:20 | iskelet | değişti | laravel-next kurulumunda laravel'in iskeletle çelişen backend/CLAUDE.md ve AGENTS.md dosyaları siliniyor
2026-11-23 19:20 | iskelet | eklendi | iki hazır yığına next.js belgelerinin konteynerdeki yolu eklendi
2026-11-23 19:29 | iskelet | eklendi | isteğe bağlı kurallar için .claude/opsiyonel-kurallar klasörü ve /kural skill'i eklendi
2026-11-23 19:29 | iskelet | eklendi | denetim kaydı isteğe bağlı kuralı ve hash zincirli, değiştirilemez postgres tablosu eklendi
2026-11-23 20:11 | iskelet | eklendi | çerez ve izleme isteğe bağlı kuralı eklendi: dört onay kategorisi, onay öncesi betik yok, çerez listesi, güvenlik kaydı
2026-11-23 20:11 | iskelet | eklendi | çerez ve izleme için seçmeli hazır parçalar eklendi: çerez onayı, ga4, umami, güvenlik kaydı
2026-11-23 20:11 | iskelet | değişti | /kural hazır parçaları seçtirip kuruyor ve kuralın istediği kurulum sonrası teknik borcu açıyor
2026-11-23 20:11 | iskelet | değişti | laravel-next trustProxies yalnızca docker iç ağlarına güveniyor; uydurulan X-Forwarded-For artık gerçek ip sayılmıyor
2026-11-23 20:11 | iskelet | değişti | laravel-next canlı php imajı composer önbelleği kullanıyor; github indirme hatalarına daha dayanıklı
2026-11-23 20:11 | iskelet | değişti | ortak frontend dockerfile'ı NEXT_PUBLIC_ değerlerini build argümanı olarak alıyor
2026-11-23 20:51 | iskelet | eklendi | iki hazır yığına yalıtılmış test altyapısı eklendi: testing veritabanı, db-test-hazirla servisi, koruma
2026-11-23 20:51 | iskelet | değişti | laravel-next testleri phpunit server force ile testing veritabanına bağlanıyor; varsayılan ayar geliştirme veritabanına yazıyordu
2026-11-23 20:51 | iskelet | eklendi | fastapi-next başlangıç koduna pytest testleri, conftest koruması ve requirements-dev eklendi
2026-11-23 20:51 | iskelet | eklendi | ortak frontend için vitest kurulumu ve api proxy testleri eklendi
2026-11-23 20:51 | iskelet | eklendi | iki hazır yığına isteğe bağlı e2e eki eklendi: playwright, traefik ağını paylaşan servis
2026-11-23 20:51 | iskelet | eklendi | çerez onayı parçasına vitest ve playwright testleri eklendi
2026-11-23 20:51 | iskelet | eklendi | yedekleme isteğe bağlı kuralı ve yedek servisi eklendi: günlük döküm, doğrulama, saklama, geri yükleme sınaması, uzak kopya
2026-11-23 20:51 | iskelet | değişti | impact kuralı test komutunun tech-stack.md'de yazmasını ve testlerin yalnızca test veritabanında çalışmasını istiyor
2026-11-23 21:08 | iskelet | değişti | bash hook'u heredoc işaretlerini yalnızca tırnak dışında arıyor; tırnak içindeki <<< metni meşru komutları reddettiriyordu
2026-11-23 21:08 | iskelet | eklendi | hazır yığın şablonlarını işleyen ve denetleyen sablon-isle.py betiği eklendi
2026-11-23 21:08 | iskelet | değişti | /yigin hazır yığın yolunda da ürünü soruyor, planın içeriğini tanımlıyor ve .env kopyasının başlığını düzeltiyor
2026-11-23 21:08 | iskelet | değişti | /kural uygulama klasörü yokken bekleyen parçaları teknik borca yazıyor, kurallar arası bağları uyguluyor ve compose değişince doğrulama yapıyor
2026-11-23 21:08 | iskelet | değişti | üç isteğe bağlı kurala diğer kurallarla bağ bölümü ve her devreye alma cevabının hedef dosyası eklendi
2026-11-23 21:08 | iskelet | değişti | yedek servisinin saat dilimi YEDEK_SAAT_DILIMI anahtarıyla değişiyor
2026-11-23 21:08 | iskelet | değişti | hazır yığınlar engellenecek araçların kesin listesini veriyor; laravel-next canlı e-posta ayarını açıklıyor
2026-11-23 21:08 | iskelet | silindi | laravel-next belgesindeki kişisel proje adı kaldırıldı
2026-11-23 21:11 | iskelet | eklendi | güvenlik kaydında saklama süresi dolan kişisel veriyi boşaltan guvenlik_kaydi_anonimlestir fonksiyonu eklendi
2026-11-23 21:11 | iskelet | değişti | güvenlik kaydı trigger'ı yalnızca ip, şehir ve user_agent alanlarının boşaltılmasına izin veriyor
2026-11-23 21:11 | iskelet | eklendi | iskeletin geliştirme geçmişi .claude/iskelet-gecmisi altına taşındı; projenin defterleri boş başlıyor
2026-11-23 21:11 | iskelet | değişti | hook'lar .claude/iskelet-gecmisi defterlerini de yalnızca alta eklenir olarak koruyor
2026-11-24 13:19 | iskelet | değişti | kendi verdiğimiz dosya ve klasör adları Türkçeleşti (docs/proje, docs/mantik, docs/kayitlar, kural ve hook dosyaları); komut adları aynı kaldı
2026-11-24 13:19 | iskelet | silindi | /git-journal skill'i ve git-journal defteri kaldırıldı; commit geçmişi git log ile okunuyor
2026-11-24 13:19 | iskelet | eklendi | kur.py hazır yığını kuruyor: yapilandir ayar dosyalarını ve yerel .env değerlerini yazıyor, kod uygulamayı konteynerde oluşturup testleri çalıştırıyor
2026-11-24 13:19 | iskelet | silindi | sablon-isle.py kaldırıldı; şablon işleme kur.py içinde
2026-11-24 13:19 | iskelet | eklendi | hazır yığınlar logs, sh, migrate, test, test-e2e, lint, doctor ve ci hedefli Makefile ile geliyor
2026-11-24 13:19 | iskelet | eklendi | make doctor .env sırasını, compose doğrulamasını, Docker'ı ve portları denetliyor
2026-11-24 13:19 | iskelet | eklendi | hazır yığınlara make ci çağıran GitHub Actions dosyası eklendi
2026-11-24 13:19 | iskelet | eklendi | fastapi-next backend'ine ruff lint eklendi
2026-11-24 13:19 | iskelet | değişti | konteyner kullanıcıları .env içindeki HOST_UID ve HOST_GID değerlerini alıyor; kimlik 1000 varsayımı kalktı
2026-11-24 13:19 | iskelet | eklendi | /iskelet-guncelle skill'i ve .claude/iskelet-surumu dosyası eklendi
2026-11-24 13:19 | iskelet | eklendi | README'ye yeni projeye başlama adımları eklendi
2026-11-24 13:19 | iskelet | değişti | veri.md kuralına kur.py'nin yerel .env değerlerini üretme istisnası eklendi
2026-11-24 13:19 | iskelet | değişti | docker.md kuralı hazır yığın Makefile hedeflerini ve yeni betik istisnalarını anlatıyor
2026-11-24 13:28 | iskelet | değişti | denetim-kaydi.sql kendi klasörüne (opsiyonel-kurallar/denetim-kaydi/) taşındı
2026-11-24 13:33 | iskelet | eklendi | /sadelestir skill'i kullanılmayan isteğe bağlı kuralları, kurulum artıklarını, skill'leri ve çekirdek kuralları sorarak kaldırıyor
2026-11-24 13:33 | iskelet | eklendi | hook korumaları (git, ssh, docker-hacim, defter, env-ornek) .claude/iskelet.json dosyasından açılıp kapanıyor; varsayılan hepsi açık
2026-11-24 13:33 | iskelet | eklendi | iskelet.json ve settings.json bash ile yazılamıyor; Edit ve Write değişiklikleri kullanıcıya onaylatılıyor
2026-11-24 13:33 | iskelet | değişti | hook testleri projenin koruma ayarından bağımsız, geçici bir kopyada çalışıyor
2026-11-24 13:33 | iskelet | değişti | .claude/iskelet-surumu yerine iskelet.json; /iskelet-guncelle kaldırılanları yeniden önermiyor
2026-11-24 13:56 | iskelet | eklendi | /basla onboarding skill'i: serbest anlatımdan projeyi anlıyor, eksikleri soruyor, kuralları ve mantık belgelerini birlikte yazıyor, ilk prompt'u hazırlıyor
2026-11-24 13:56 | iskelet | silindi | /sadelestir ayrı skill olmaktan çıktı; adımları /basla içinde (basla/sadelestirme.md)
2026-11-24 13:56 | iskelet | eklendi | iskelet.json tur alanı; iskeletin geçmiş defterleri yalnızca tur iskeletken korunuyor, projede /basla siliyor
2026-11-24 13:56 | iskelet | değişti | kur.py ve /yigin onboarding'de kod oluşturmuyor; kur.py kod ilk prompt'un ilk adımı
2026-11-24 13:56 | iskelet | değişti | /kural, /basla içinden çağrılınca bekleyen parçaları TD yerine ilk prompt'a yazıyor
2026-11-24 13:56 | iskelet | değişti | mantik-belgeleri kuralına birlikte yazma bölümü ve belge iskeleti eklendi
2026-11-24 13:56 | iskelet | değişti | CLAUDE.md oturum başında /basla hatırlatıyor
2026-11-24 13:56 | iskelet | değişti | kök README iskeleti GitHub sayfası olarak anlatıyor
