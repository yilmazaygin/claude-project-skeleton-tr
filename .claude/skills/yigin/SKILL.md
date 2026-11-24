---
name: yigin
description: Projenin teknoloji yığınını kullanıcıyla birlikte seçer ve iskelete işler. Hazır yığınlardan (hazir/ klasörü) biri seçilebilir veya özel yığın kurulabilir. yigin.md, iki compose dosyası, .env ve .env.example aynı işte güncellenir. Yalnızca kullanıcı /yigin yazınca çalışır.
disable-model-invocation: true
argument-hint: "[isteğe bağlı: hazır yığın adı veya aklınızdaki yığın]"
---

# Yığın kurulumu

Yığın büyük bir karardır. Bu akışta hiçbir seçim kullanıcı yerine yapılmaz. Kullanıcının ön bilgisi: $ARGUMENTS

## 1. Durumu oku

Şu dosyaları oku:

- `docs/proje/hakkinda.md`
- `docs/proje/yigin.md`
- `compose.local.yaml`
- `compose.live.yaml`
- `.env.example`

`.claude/iskelet.json` içinde `tur` iskeletse dur: proje henüz başlatılmamış; `/basla` önerilir (`/basla` yığını da kendisi kurar). Bir dosyada yığın zaten yazılıysa veya `services` boş değilse dur. Şıklı sor: "yığını değiştir", "eksik servisi ekle" veya "vazgeç". Seçim gelmeden devam etme.

## 2. Hazır yığın mı, özel yığın mı?

Bu skill'in klasöründeki `hazir/*/HAZIR.md` dosyalarını listele (şu an `laravel-next` ve `fastapi-next`). Her birinin başındaki `ad` ve `ozet` alanlarını oku. `hazir/_ortak/` bir hazır yığın değildir; birden çok yığının paylaştığı dosyaları tutar (Next.js Dockerfile'ı, proxy dosyaları, dockerignore).

Şıklı sor. Her hazır yığın bir şıktır. Son şık "Özel yığın"dır. Kullanıcının ön bilgisi bir hazır yığının adını veya `tam_ad` alanını (örneğin oben-stack) içeriyorsa o şık önerilir ve sorulmadan seçilmez.

- **Hazır yığın seçilirse:** o yığının `HAZIR.md` dosyasını baştan sona oku.
  1. 3. adımdaki ürün sorusu (`hakkinda.md` boşsa) sorulur; yığın soruları sorulmaz. HAZIR.md'deki sorular sorulur: proje adı, proje numarası, ekler.
  2. Plan moduyla plan sunulur. Planda 4. adımdaki maddeler (servisler ve `container_name`, yerel portlar, canlıda açılan portlar, eklenecek anahtarlar) ve betiğin yapacakları yer alır.
  3. Onaydan sonra `python3 .claude/skills/yigin/kur.py yapilandir <hazir> <proje> <no> <ekler>` çalıştırılır. Betik compose dosyalarını, `docker/`, `.dockerignore`, Makefile, `.github/workflows/test.yml`, `docs/proje/yigin.md` dosyalarını ve `.env` anahtarlarını yazar; yerel `.env` değerlerini üretir (veri.md istisnası); seçilmeyen hazır yığını siler. Portlar doluysa durur.
  4. Kod bu skill'de oluşturulmaz. `python3 .claude/skills/yigin/kur.py kod` ilk prompt'un ilk adımıdır (`docs/proje/ilk-istem.md`) ya da kullanıcı açıkça isteyince çalışır. Betik Laravel/Next.js projelerini konteynerde oluşturur, hazır dosyaları yerleştirir, paketleri kurar, `make up`, `make migrate`, `make test`, `make lint` çalıştırır ve adresleri yazar (birkaç dakika sürer, ağ gerekir). Yarıda kalırsa hata mesajı nedeni söyler; sorun giderilince aynı komut yeniden çalıştırılır, biten adımlar atlanır.
  5. Sonra 5. ve 6. adımlara geçilir.

  Betiğin çıktısı kullanıcıya özetlenir. `.env` değerleri okunmaz ve sohbete yazılmaz.
- **Özel yığın seçilirse:** 3. adımdan devam et.

## 3. Özel yığın: şıklı sor

`hakkinda.md` boşsa ürünü tek cümleyle sor ve cevabı `docs/proje/hakkinda.md` dosyasına yaz (hazır yığın yolunda da). Ürünü bilmeden önerilen şık uydurulmaz.

Şıklı soru aracıyla sor. Her soruda ilk şık önerindir, "(Önerilen)" diye işaretlenir ve kısa gerekçesi yazılır. Kullanıcının ön bilgisinde cevabı olan soruyu atla.

1. **Proje adı**: konteyner adlarının önüne gelir. Küçük harf, boşluk yerine tire.
2. **Backend**: dil ve çatı.
3. **Veritabanı**.
4. **Önbellek ve kuyruk**: "yok" da bir şıktır.
5. **Frontend**: ayrı servis mi, backend içinde mi, yok mu.
6. **Web sunucusu ve TLS**: canlıda 80 ve 443 hangi serviste açılacak, ya da önde bir ters vekil (örneğin Nginx Proxy Manager) mi var.

Bir servisin imaj sürümü yazılacaksa, var olduğundan emin olduğun bir sürüm önerilir. Emin değilsen bunu söyle ve kullanıcıya sor.

## 4. Özel yığın: planı sun ve yaz

Bu iş geniş bir iştir. Plan moduna geç. Planda şunlar bulunur:

- servis listesi ve her servisin `container_name` değeri;
- yerel compose dosyasındaki port eşlemeleri;
- canlı compose dosyasında dışarı açılan portlar;
- `.env.example` dosyasına eklenecek anahtarlar, sırasıyla.

Onay gelmeden dosya yazma. Onay gelmezse sor: "Plan moduna onay vermediniz, ne yapmamı istersiniz?"

Onaydan sonra hepsi aynı işte yazılır. Hazır yığın şablonları `kur.py` ile işlenir (kullanımı betiğin başında yazar); elle düzenlenmez.

**`docs/proje/yigin.md`**
- Seçilen yığın ve kısa gerekçesi.
- Servis adı tablosu: servis, `container_name`, imaj, konteyner portu. Servis adları bundan sonra buradan okunur.

**`compose.local.yaml`**
- Compose proje adı `name: <proje>-local` olur. Böylece iki projenin hacimleri karışmaz.
- Her servise `container_name: <proje>-<servis>`.
- Konteyner içindeki port standart kalır. Bilgisayar portu yalnızca bu dosyada değişir.
- Veritabanı verisi adlandırılmış bir hacimde durur.

**`compose.live.yaml`**
- Compose proje adı `name: <proje>-live` olur.
- Aynı servisler ve aynı `container_name` değerleri.
- Dışarı en fazla 80 ve 443 açılır, o da yalnızca web sunucusunda. Önde ters vekil varsa hiçbir port açılmaz.
- Veritabanı portu yayımlanmaz.
- Bu dosya yerel ortamın provası değildir; yerel geliştirme ayarı buraya taşınmaz.

**`.env.example` ve `.env`**
- Anahtarlar iki dosyaya aynı sırayla eklenir.
- İki dosyada da değer boş kalır. Değeri kullanıcı doldurur.
- `.env` yoksa `.env.example` dosyasının kopyası olarak açılır; kopyadaki başlık yorumları şu tek satırla değiştirilir: `# Gerçek değerler bu dosyadadır. Git'e girmez. Anahtarlar .env.example ile aynı sırada durur.`
- Gerçek görünen uydurma değer, yorumda da olsa yazılmaz.
- Gizli olmayan altyapı bilgisi (servis adları, iç portlar) `.env` yerine compose içindeki `environment` alanına yazılabilir.

## 5. Bilgisayarda araç çalıştırma engeli

Şıklı sor: seçilen yığının araçları, örneğin `php`, `composer`, `npm`, `node` veya `python`, bilgisayarda doğrudan çalıştırılınca engellensin mi?

- İlk şık "Evet, engelle (Önerilen)".
- Hazır yığının `HAZIR.md` dosyası engellenecek araçların kesin listesini verir ("Araç engeli" satırı); özel yığında liste kullanıcıya şıklı sorulur.
- Kabul edilirse her araç için `Bash(<araç>:*)` satırı `.claude/settings.json` içindeki `permissions.deny` listesine eklenir. Konteyner içindeki kullanım (`docker compose ... exec <servis> <araç>`) bundan etkilenmez.

## 6. Kaydet ve doğrula

- Her ayrı değişiklik için `/changelog` ile satır yaz.
- `docker compose -f compose.local.yaml config --quiet` ile yerel dosyayı doğrula.
- `docker compose -f compose.live.yaml config --quiet` ile canlı dosyayı doğrula. Bu komut yalnızca dosyayı okur; canlıya bir şey göndermez. Canlı dosya `.env` içinde henüz boş olan değerleri zorunlu tutuyorsa (örneğin `APP_DOMAIN`, yedekleme açıksa `YEDEK_KLASORU`) doğrulama yalnızca o komuta verilen geçici değerlerle yapılır: `APP_DOMAIN=dogrulama.test docker compose -f compose.live.yaml config --quiet`. `.env` değiştirilmez. Canlıda zorunlu değişkenlerin listesi `yigin.md` dosyasında tutulur ve compose dosyası her değiştiğinde (yığın veya `/kural ac`) iki doğrulama yeniden çalıştırılır.
- Komut çalıştırılamadıysa veya hata verdiyse aynen söyle. Çalıştırılmayan doğrulama geçmiş sayılmaz.
- Hazır yığının "Sonraki adımlar" bölümünü kullanıcıya göster (betiğin yapmadığı, elle kalan işler).
- Son olarak `make doctor` çalıştırılır ve sonucu söylenir.

## Yeni hazır yığın ekleme

Yeni bir hazır yığın, örneğin bir Python yığını, `hazir/<ad>/` klasörü olarak eklenir. Klasörde şunlar bulunur:

- **`HAZIR.md`**: başında şu alanlar olur:
  - `ad`: klasör adıyla aynı;
  - `ozet`: tek cümle;
  - `ekler`: isteğe bağlı eklerin adları, virgülle;
  - `tam_ad`: belirli ekler birlikte seçildiğinde yığının özel adı (yoksa alan yazılmaz);
  - `tam_ad_ekleri`: `tam_ad` için seçilmesi gereken ekler, virgülle. Kullanıcı `tam_ad` ile isterse (örneğin `/yigin oben-stack`) bu ekler önerilir; diğer ekler ayrıca sorulur.

  Gövdede şu bölümler olur: Servisler, Ekler, Sorular, Kurulum, Ortam değişkenleri, Sürüm notu, Bilinen sınırlar, Sonraki adımlar. Örnek: `hazir/laravel-next/HAZIR.md`.
- **`compose.local.yaml.tmpl` ve `compose.live.yaml.tmpl` şablonları.** Uzantı `.tmpl`'dir, çünkü işlenmemiş şablon yinelenen anahtar taşıyabilir. Proje adı yerine `__PROJE__` yazılır. Proje başına farklı bilgisayar portu gerekiyorsa proje numarası yerine `__NO__` yazılır (örneğin `"80__NO__:80"`); numaranın sorusu `HAZIR.md` içindeki Sorular bölümüne eklenir. İsteğe bağlı bloklar `# >>> ek:<ad>` ile `# <<< ek:<ad>` arasına alınır. Ek seçilmediğinde onun yerine geçecek bloklar `# >>> ek-yok:<ad>` ile `# <<< ek-yok:<ad>` arasına alınır.
- **`env.example`**: eklenecek anahtarlar, değersiz ve sırasıyla. Dosyanın adı noktasızdır, böylece projenin kendi `.env.example` dosyasıyla karışmaz.
- **Gerekirse `docker/` klasörü ve `dockerignore`**: kurulumda proje köküne kopyalanır. Başka bir yığınla aynı olan dosyalar kopyalanmaz, `hazir/_ortak/` altına konur ve HAZIR.md oradan kopyalatır.
- **Gerekirse başlangıç kodu** (örnek: `fastapi-next/backend-baslangic/`): çatının kendi proje oluşturma komutu yoksa çalışan küçük bir iskelet verilir.
- **`Makefile.tmpl`**: aynı hedefler (`up`, `down`, `live-up`, `live-down`, `logs`, `sh`, `migrate`, `test`, `test-e2e`, `lint`, `doctor`, `ci`), yığının komutlarıyla. `ci` hedefi temiz bir makinede kurup test eder; GitHub Actions dosyası (`_ortak/github/test.yml`) yalnızca onu çağırır.
- **`yigin.md.tmpl`**: projenin `docs/proje/yigin.md` dosyası; aynı işaretlerle işlenir.
- **`kur.py` içinde yığının adımları:** `YIGINLAR` listesine ad eklenir; `yerel_degerler` yığının `.env` anahtarlarını, `kod_<yığın>` fonksiyonu kod oluşturma adımlarını tanımlar. Her adım `adim(ad, yapildi, yap)` ile yazılır: `yapildi` adımın sonucunu kontrol eder, böylece betik yeniden çalıştırılınca biten adım atlanır. Dosya yamaları `yama()` ile yapılır; bağlamı bulamayan yama durur, tahminle yazmaz.
- **Her yeni hazır yığın bir kez baştan sona denenir:** geçici bir klasörde işlenir, `up --build` ile yerel ve canlı ayağa kaldırılır, yönlendirmeler ve servisler kontrol edilir, sonra her şey temizlenir. Denenmeyen hazır yığın HAZIR.md'de "denenmedi" diye yazılır.

Şablonlardaki kurallar iskeletin kurallarıyla aynıdır: `container_name`, standart konteyner portu, canlıda yayımlanmayan veritabanı portu, değersiz `.env.example`.
