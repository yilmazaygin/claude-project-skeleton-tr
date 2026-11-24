# Teknik borçlar

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
