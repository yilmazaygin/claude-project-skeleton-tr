# Veri

Proje verisi korunur. Veritabanı silinmez. Yıkıcı işlem yapılmaz. Canlıya çıkışta ve canlı ortamda bu yasak kesindir.

Kullanıcı ağzıyla verilerin önemli olmadığını söylemedikçe silmeye yönelik komut, öneri, ipucu veya uyarı verilmez.

İstisna: yedekleme kuralı açıksa yedek servisi saklama süresi dolan eski yedek dosyalarını siler ve geri yükleme sınaması için kendi açtığı geçici veritabanını kaldırır. Bu, kullanıcının seçtiği saklama düzenidir; projenin veritabanına dokunmaz.

Testler proje verisinden izole çalışır. Test, geliştirme verisini veya canlı veriyi silmez ve değiştirmez.

```text
kötü: docker compose down -v ile temizleyebilirsin.
iyi: Veriyi yerinde bırakıyorum. Test ayrı bir deneme verisiyle çalışır.
```

## Gizli değerler

`.env`, `.env.*`, kimlik dosyası ve `.env.example` dosyasına gerçek anahtar, parola, token veya bağlantı cümlesi yazılmaz. Yorum satırı ve "örneğin" ya da "example" ile başlayan satır da buna dahildir. Değer boş kalır. Gerçek görünen uydurma anahtar da yazılmaz. Anahtar adı, yığın belli olmadan eklenmez.

İstisna: `kur.py` yerel `.env` dosyasındaki boş yerel geliştirme değerlerini (rastgele DB parolası, `APP_KEY` veya `SECRET_KEY`, yerel adresler, kullanıcı kimliği) kendisi üretir. Değerleri Claude okumaz, yazmaz ve sohbete taşımaz; betik de ekrana basmaz. Dolu değere dokunulmaz. Canlıya ait değerleri yine kullanıcı yazar.

`.env` ve `.env.example` aynı anahtarları, aynı sırayla taşır. Yeni anahtar aynı işte ikisine birden eklenir. Örnek dosyada değer yoktur. Sunucuya geçmek, örnek dosyayı kopyalayıp değerleri doldurmaktır. Yalnızca sunucuda duran anahtar açılmaz.

Kullanıcı sohbette gerçek anahtar verirse bu depoya kopyalanmaz.

`.env.example` dosyasına değer yazılması ile hacim ve veri silen Docker komutları `.claude/hooks/` altındaki hook'larla da engellenir. Engel aşılmaya çalışılmaz. Bir koruma yalnızca `/basla` sırasında kullanıcı seçince ya da kullanıcı açıkça isteyince kapanır; Claude `.claude/iskelet.json` dosyasındaki korumaları kendi başına değiştirmez.

```text
kötü: # örneğin burada gerçek anahtar
iyi: API_KEY=
```
