# Çerez ve izleme

Bu isteğe bağlı bir kuraldır. `/kural ac cerez-ve-izleme` ile açılınca `.claude/rules/` altına kopyalanır ve her oturumda geçerli olur.

Bu kural ziyaretçi izlemenin, çerezlerin ve güvenlik kaydının nasıl yapılacağını söyler. Hazır parçalar `.claude/opsiyonel-kurallar/cerez-ve-izleme/` klasöründedir, kurulumları `PARCALAR.md` dosyasında yazar.

Bu kural bir ilke metnidir, hukuki danışmanlık değildir. KVKK ve (AB'den ziyaretçi varsa) GDPR uyumu canlıya çıkmadan bir hukukçuya kontrol ettirilir.

## Kategoriler

| Kategori | Onay | Örnek |
|---|---|---|
| zorunlu | gerekmez | Oturum, CSRF (`XSRF-TOKEN`), `cerez_tercihi` |
| tercih | gerekir | Dil, tema |
| analitik | gerekir | GA4 (`_ga`), Umami, Microsoft Clarity |
| pazarlama | gerekir | Google Ads (`_gcl_au`), Meta Pixel (`_fbp`), TikTok |

- **Onay öncesi yükleme yok:** zorunlu olmayan hiçbir betik ve çerez onaydan önce yüklenmez veya yazılmaz.
- **Betik ekleme:** zorunlu olmayan her betik `<OnayliBetik kategori="..." />` ile eklenir; doğrudan `<Script>` veya `<script>` yazılmaz.
- **Çerezsiz araçlar da onaya bağlı:** Umami çerez yazmaz ve IP saklamaz, ama varsayılan olarak yine analitik onayına bağlıdır. Onaysız yüklenmesine ancak hukuki değerlendirmeden sonra karar verilir ve karar çerez listesine yazılır.

```text
kötü: <Script src="https://connect.facebook.net/en_US/fbevents.js" />
iyi:  <OnayliBetik kategori="pazarlama" id="meta-pixel" src="https://connect.facebook.net/en_US/fbevents.js" />
```

## Banner

- **Eşit düğmeler:** "Kabul et", "Reddet" ve "Ayarlar" aynı boyut ve ağırlıktadır. Reddetmek kabul etmek kadar kolaydır.
- **Kapanmaz:** banner seçim yapılmadan kaybolmaz. Önceden işaretlenmiş seçmeli kategori olmaz.
- **Sonradan değişiklik:** ziyaretçi seçimini her zaman "Çerez ayarları" linkiyle (alt bilgi) değiştirebilir.
- **Geri çekme:** onay geri çekilince sayfa yenilenir; yüklenmiş betikler kalkar.
- **Sürüm:** kategoriler veya metin değişince `ONAY_SURUMU` artırılır. Eski onaylar geçersiz sayılır, banner yeniden çıkar.
- **Kayıt:** denetim-kaydi kuralı açıksa onay ve geri çekme `cerez.onay_degisti` olayı olarak **zorunlu** kaydedilir (PARCALAR.md → cerez-onayi 4. adım). Kural kapalıysa kayıt isteğe bağlıdır ve "Devreye alma" sorusuyla seçilir.

## Çerez listesi

Proje, kullandığı her çerezi `docs/mantik/cerez-ve-izleme.md` dosyasında listeler: ad, kategori, süre, kimin çerezi (birinci veya üçüncü taraf), amaç.

- **Yeni çerez veya betik:** çerez listesi aynı işte güncellenir. Banner metni, listedeki gerçek çerezlerle çelişmez.
- **Çerez ayarları:** projenin kendi çerezleri `Secure` ve `SameSite=Lax` (veya `Strict`) taşır. JavaScript'in okuması gerekmeyenler `HttpOnly` olur. Oturum çerezinde mümkünse `__Host-` öneki kullanılır.

## Güvenlik kaydı

Giriş denemeleri, çıkış ve parola işlemleri `guvenlik_kaydi` tablosuna yazılır: olay, kullanıcı, maskelenmiş denenen kimlik, IP, ülke, şehir, user agent, işletim sistemi, tarayıcı, cihaz.

- **Değişmezlik:** tabloya yalnızca ekleme yapılır; değiştirme ve silme veritabanında reddedilir. Tek istisna anonimleştirmedir: saklama süresi dolan kayıtta yalnızca `ip`, `sehir` ve `user_agent` boşaltılabilir; bunu `guvenlik_kaydi_anonimlestir()` fonksiyonu her gün yapar ve denetim kaydı açıksa her çalışmayı oraya yazar. Başka bir alan değişemez, boşaltılan alan yeniden doldurulamaz.
- **Denetim kaydıyla ilişki:** başarılı giriş ve parola değişikliği, denetim-kaydi kuralı açıksa denetim kaydına da yazılır.
- **IP güvenilirliği:** IP yalnızca güvenilir vekillerin başlığından okunur. Laravel'de `trustProxies` yalnızca Docker iç ağ aralıklarını içerir, `'*'` olmaz. Python'da `X-Forwarded-For` sağdan sola okunur, iç ağ dışındaki ilk adres alınır. En soldaki değer alınmaz: onu ziyaretçi uydurabilir.
- **Kişisel veri:** IP ve konum kişisel veridir. Güvenlik kaydı dışında hiçbir yerde (uygulama günlüğü, analitik, hata izleme) ham IP saklanmaz.
- **GeoIP:** konum için DB-IP Lite kullanılır (CC BY 4.0). Sitede kaynak gösterilir: "IP Geolocation by DB-IP" (https://db-ip.com). Dosya her ay yenilenir.
- **Hata:** güvenlik kaydı yazılamazsa giriş akışı bozulmaz, hata uygulama günlüğüne düşer.

## Claude'un davranışı

- **Yeni betik veya çerez:** kategorisi belirlenir, betik onaya bağlanır, çerez listesi güncellenir.
  - Açık bir "çerez politikası" TD'si varsa aynı kimlikle `etkilendi` durumunda yeni bir kayıt eklenir. Kayıt, eklenen betiği veya çerezi adıyla yazar.
- **Giriş ve parola:** giriş, çıkış veya parola akışı yazılırken güvenlik kaydı çağrısı eklenir.
- **Ham IP yok:** IP'yi yeni bir yere yazan kod yazılmaz; gerekiyorsa önce kullanıcıya sorulur.
- **Doğrulama:** kurulumdan sonra onaysız sayfa HTML'inde zorunlu olmayan hiçbir betiğin bulunmadığı kontrol edilir.

## Diğer kurallarla bağ

- **denetim-kaydi:** açıksa `giris.basarili`, `parola.degisti` ve `cerez.onay_degisti` olayları denetim kaydının olay kataloğuna eklenir ve onay kaydı zorunlu olur.
- **yedekleme:** açıksa `guvenlik_kaydi` tablosu da yedeklenir (yedek servisi bütün veritabanını alır); güvenlik kaydının saklama süresi yedeklerin saklama süresiyle birlikte değerlendirilir.

## Devreye alma

`/kural ac cerez-ve-izleme` şu soruları sorar ve cevapları projeye yazar:

1. **Hangi parçalar kurulsun?** Çoklu seçim: `cerez-onayi`, `ga4`, `umami`, `guvenlik-kaydi`. `ga4` ve `umami` için `cerez-onayi` de gerekir. Seçilenler `PARCALAR.md` adımlarıyla kurulur.
2. **Güvenlik kaydı saklama süresi** (güvenlik kaydı seçildiyse; önerilen 730 gün): cevap `docs/proje/yigin.md` dosyasına yazılır. Süre dolan kayıtlarda kişisel veri (`ip`, `sehir`, `user_agent`) her gün `guvenlik_kaydi_anonimlestir(<gün>)` ile boşaltılır; olay, zaman, ülke, işletim sistemi kalır. Süre `.env` dosyasındaki `GUVENLIK_KAYDI_SAKLAMA_GUN` ile değişir (boşsa 730). Süre hukukçuyla teyit edilir ve bu TD'ye yazılır.
3. **Çerez listesi belgesi:** `docs/mantik/cerez-ve-izleme.md` açılır (mantik-belgeleri kuralına göre adı sorulur). Kurulan parçaların çerezleriyle doldurulur; bekleyen parçaların çerezleri "kurulunca doğrulanacak" diye işaretlenir.
4. **Onay kaydı** (denetim-kaydi kapalıysa sorulur): onay değişikliği backend'e kaydedilsin mi? Açıksa sorulmaz, kaydedilir.

## Kurulum sonrası TD

Herhangi bir parça seçildiyse (kurulmuş veya bekliyor olsun) `/td` ile hemen bir teknik borç açılır. Ad: `çerez politikası`. Durum: `açık`. Borç metni seçilen parçaları adıyla yazar ve şunları ister:

- Çerez politikası ve aydınlatma metni yazılmalı veya güncellenmeli; banner'daki `/cerez-politikasi` sayfası olmalı.
- Banner metinleri ve kategori açıklamaları, çerez listesindeki gerçek çerezlerle karşılaştırılmalı.
- `ga4` kurulduysa: yurt dışına veri aktarımı (Google) değerlendirilmeli.
- `umami` kurulduysa: varsayılan `admin` / `umami` parolası değiştirilmeli.
- `guvenlik-kaydi` kurulduysa: DB-IP kaynak gösterimi sitede olmalı; saklama süresi aydınlatma metniyle uyumlu olmalı.
- Hukukçu kontrolü.

Borç, kullanıcı kontrol edildiğini söyleyene kadar açık kalır.
