# Etki

Renk, boşluk ve yazı gibi yalnızca görünüş değişince test gerekmez.

Davranış veya API mantığı değişince o davranışın testleri ve onunla etkileşen testler çalıştırılır. Tüm suit her işte çalıştırılmaz. Aynı kurala bağlı arayüzler gözden geçirilir.

Backend'den kalkan özellik frontend'de kalamaz. Aynı işte arayüzden de kalkar. Frontend'de gizlenen özellik backend'den kalkmak zorunda değildir.

İlgili arayüz aynı işte güncellenir. Güncellenmeden iş bitecekse teknik borç yazılır. Borç sayfayı, kontrolü ve eksik işi adlandırır.

Test komutu Docker kuralına uyar ve `docs/proje/yigin.md` dosyasında yazar. Koşucu yoksa komut uydurulmaz. Testler yalnızca test veritabanında çalışır; testin geliştirme veritabanına bağlandığı görülürse iş durdurulur ve kullanıcıya söylenir. Eksik test, sayfa ve davranış adıyla teknik borca yazılır.

```text
kötü: Bazı dosyalar değişmeli.
iyi: Ayarlar sayfasındaki dışa aktar tuşu artık kullanılmıyor.
iyi: Ödeme sayfasındaki iade çağrısının testi yok.
```
