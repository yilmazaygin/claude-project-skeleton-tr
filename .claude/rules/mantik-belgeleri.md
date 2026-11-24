# Mantık belgeleri

Bir davranışın belgesi varsa önce o okunur. Sonra belgenin işaret ettiği dosyalara bakılır. Aynı iş için tüm depo taranmaz.

Belge, bir butonun kuralı değildir. Bir davranışın nasıl işlediğini anlatır. Adı o davranışı söyler ve küçük harf kebab-case olur. Belgeler `docs/mantik/` altındadır.

```text
iyi: admin-yetkilendirmesi.md
iyi: free-paket-sinirlari.md
kötü: ayarlar-kaydet-butonu.md
kötü: sistem.md
```

Yeni belge açmadan önce kullanıcıya sorulur. İlk şık önerilen addır. Diğer makul sınırlar da yazılır. Seçim gelmeden dosya açılmaz.

Belgenin anlattığı kod değişince belge aynı işte güncellenir. Belge ile kod çelişirse ve bu iş o değişikliği içermiyorsa devam edilmez; hangisinin geçerli olduğu sorulur.

Belge yoksa kod okunabilir. Ürün uydurulmaz.

## Birlikte yazma

Belge Claude'un tahminiyle doldurulmaz. Sistemin sözleşmeleri kullanıcıyla birlikte kurulur.

- **Önce sorular.** Belge yazılmadan önce sözleşme soruları şıklı soru aracıyla sorulur. İlk şık anlatıma göre öneridir. Konular:
  - roller ve yetkiler: kim, neyi yapabilir;
  - durumlar ve geçişler: taslak, yayında, askıda gibi;
  - veri kuralları: zorunlu alanlar, birimler, sınırlar, benzersizlik;
  - kenar durumlar: boş liste, silinmiş kayıt, aynı anda düzenleme;
  - başka davranışlarla bağ.
- **Konu geçince.** Kullanıcı bir konudan söz ederken o konunun belgesi yoksa ya da konuşulan şey belgeyle çelişiyorsa bu söylenir. Belge açmak veya güncellemek önerilir ve aynı sorularla birlikte yazılır.
- **Açık sorular.** Cevapsız kalan her soru belgenin "Açık sorular" bölümüne yazılır. Kod yazılırken o konuda tahmin yapılmaz; sorulur, cevap belgeye işlenir.

Belgenin iskeleti:

```markdown
# <Davranış>

## Amaç
## Kavramlar
## Kurallar
## Durumlar
## Kenar durumlar
## İlgili dosyalar
## Açık sorular
```

Boş kalan bölüm silinmez, "Yok." yazılır. `Kurallar` bölümü sözleşmedir: her madde tek cümle, test edilebilir.

```text
kötü: Menü fiyatları düzgün gösterilir.
iyi: Fiyat kuruş olarak tamsayı tutulur; arayüzde iki ondalıkla ve TL simgesiyle gösterilir.
```
