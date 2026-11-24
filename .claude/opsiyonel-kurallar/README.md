# İsteğe bağlı kurallar

Bu klasördeki kurallar repoyla birlikte gelir ama kendiliğinden yüklenmez. Bir projede gerekirse açılır.

`.claude/rules/` altındaki her `.md` dosyası her oturumda yüklendiği için isteğe bağlı kurallar orada beklemez; burada bekler.

## Kurallar

| Kural | Ne ister | Yardımcı dosya |
|---|---|---|
| `denetim-kaydi` | Kullanıcıların ve sistemin önemli işleri değiştirilemez bir kayda yazılır: kim, ne zaman, neyi, neyden neye; HTTP istekleri ve sonuçları | `denetim-kaydi/denetim-kaydi.sql` |
| `cerez-ve-izleme` | Çerez onayı (4 kategori), onay öncesi betik yok, çerez listesi; güvenlik kaydı (giriş denemeleri, IP, konum, işletim sistemi). Seçmeli hazır parçalar: `cerez-onayi`, `ga4`, `umami`, `guvenlik-kaydi`. Kurulunca "çerez politikası" TD'si açılır. | `cerez-ve-izleme/` (`PARCALAR.md`) |
| `yedekleme` | Postgres her gün yedeklenir ve doğrulanır; 7 gün / 4 hafta / 6 ay saklanır; her hafta geri yükleme sınanır; isteğe bağlı S3 uyumlu uzak kopya; denetim kaydı çapası. Kurulunca "yedek doğrulama" TD'si açılır. | `yedekleme/` (`PARCALAR.md`) |

## Açma ve kapatma

- **`/kural liste`:** kuralları ve hangilerinin açık olduğunu gösterir.
- **`/kural ac <ad>`:** kuralın "Devreye alma" sorularını sorar, dosyayı `.claude/rules/` altına kopyalar, `CLAUDE.md` dosyasına ve changelog'a yazar.
- **`/kural kapat <ad>`:** kopyayı `.claude/rules/` altından kaldırır. Bu klasördeki asıl dosya ve projede yazılmış kayıtlar yerinde kalır.

Açık bir kural, kuralların geri kalanı gibi her oturumda geçerlidir.

## Yeni isteğe bağlı kural ekleme

- Kural tek bir `.md` dosyasıdır. Dili ve biçimi `.claude/rules/` altındaki kurallarla aynıdır: kısa, emir kipinde, kötü/iyi örnekli.
- Dosyanın sonunda bir **"Devreye alma"** bölümü olur. `/kural ac` bu bölümdeki soruları sorar.
- SQL veya kod gibi yardımcı dosyalar kuralla aynı adlı bir klasöre konur (örneğin `denetim-kaydi/denetim-kaydi.sql`). Bu dosyalar `.claude/rules/` altına kopyalanmaz; kural onlara yoluyla referans verir. Seçmeli hazır parçaları olan kural, aynı adlı bir klasörde parçaları ve bir `PARCALAR.md` tutar; `/kural ac` parçaları seçtirip bu dosyaya göre kurar.
- Kurulumdan sonra açılması gereken bir borç varsa kuralda "Kurulum sonrası TD" bölümü olur; `/kural ac` onu `/td` ile açar.
- Kuralın denenen ve denenmeyen kısımları kuralda açıkça yazılır.
- Kural bu README'deki tabloya eklenir.
