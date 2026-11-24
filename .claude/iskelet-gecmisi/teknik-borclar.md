# İskelet teknik borçları

Bu defter iskeletin kendi teknik borçlarıdır; projenin defteri değildir. Projenin defteri `docs/records/technical-debts.md` dosyasıdır ve boş başlar. Bu dosya da yalnızca alta eklenir.

Gerçek kayıtlar aşağıdaki `Kayıtlar` başlığının altına eklenir. Bu başlığa kadar olan bölüm biçimi anlatır ve borç değildir.

## Biçim

Her borcun bir kimliği ve bir adı vardır. Kimlik `TD-001` biçimindedir. Ad kısa ve kalıcıdır. İkisi de başlıkta, ad ayrıca `Ad` satırında yazılır.

İlk kayıt yerinde kalır. Borç kapanmadan güncellenebilir. Kapsam, etki veya ilgili davranış değişince aynı kimlik ve aynı adla en alta yeni kayıt eklenir. Eski kayıt düzenlenmez. Bu güncellemelerde durum `açık` kalabilir. `kapandı` yalnızca borç bittiğinde yazılır.

Durumlar `açık`, `etkilendi` ve `kapandı` değerleridir.

Atlanan bir arayüz veya test, sayfa ve kontrol adıyla yazılır. Borç metni yapılan eksiği söyler. Örneğin: "Ayarlar sayfasındaki dışa aktar tuşu artık kullanılmıyor." Test borcu da aynı açıklıktadır: "Ödeme sayfasındaki iade çağrısının testi yok."

### TD-örnek — ödeme kuyruğu — 2026-10-28 23:13

- Ad: ödeme kuyruğu
- Durum: açık
- Borç: başarısız ödeme yeniden denenmiyor
- Etki: kullanıcı çift çekim sanabilir
- İlgili davranış: ödeme onayı tek denemede bitiyor

### TD-örnek — ödeme kuyruğu — 2026-10-29 10:05

- Ad: ödeme kuyruğu
- Durum: açık
- Kapsam: yeniden deneme yalnızca zaman aşımında
- Değişiklik: kapsam daraldı; borç kapanmadı
- İlgili davranış: zaman aşımı ayrı sayılır

## Kayıtlar

### TD-001 — çatıların ajan belgeleri — 2026-11-23 17:20

- Ad: çatıların ajan belgeleri
- Durum: açık
- Borç: Laravel 13'ün `composer create-project` komutunun ürettiği `backend/CLAUDE.md` ve `backend/AGENTS.md` ile create-next-app'in ürettiği `frontend/AGENTS.md` okunmadı; içerikleri `.claude/rules/` altındaki kurallarla karşılaştırılmadı
- Etki: Claude `backend/` içinde çalışırken `backend/CLAUDE.md` dosyasını da yükler; iskeletin kurallarıyla çelişen bir talimat varsa (örneğin Git, test komutu, host'ta araç çalıştırma) Claude yanlış talimata uyabilir
- İlgili davranış: `laravel-next/HAZIR.md` ve `fastapi-next/HAZIR.md` "Bilinen sınırlar" bölümünde yalnızca "çelişirse iskeletin kuralı geçerli" notu var; hangi satırların çeliştiği bilinmiyor
- Yapılacak: ilk gerçek projede üç dosya okunur; çelişen satırlar HAZIR.md'ye yazılır ve kurulum adımlarına bu dosyaları düzenleme veya silme adımı eklenir

### TD-001 — çatıların ajan belgeleri — 2026-11-23 19:19

- Ad: çatıların ajan belgeleri
- Durum: kapandı
- Değişiklik: üç dosya geçici klasörde yeniden üretilip okundu ve kurallarla karşılaştırıldı
- `backend/CLAUDE.md` = `backend/AGENTS.md`: Laravel Boost açılış talimatı; host'ta php/composer çalıştırma, `curl | bash` ile PHP kurma ve sormadan paket kurma istiyor; docker.md ve questions.md ile çelişiyor. laravel-next "Sonraki adımlar"a create-project'ten hemen sonra `rm backend/CLAUDE.md backend/AGENTS.md` eklendi; Boost yalnızca kullanıcı kararıyla ve konteynerde kurulur
- `frontend/AGENTS.md`: çelişki yok; `next dev` her çalışmada yeniden yazar, silinmez. Next.js belgelerinin konteynerdeki yolu iki HAZIR.md'ye ve tech-stack.md kurulum adımına eklendi
