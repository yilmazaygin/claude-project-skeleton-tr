# Belgeler

Bu dosya, `docs` altındaki klasörlere hangi belgenin konacağını anlatır. `proje`, `mantik` ve `kayitlar` klasörlerinin içinde ayrı bir README yoktur.

## proje

Ürünün kimliği burada durur. Şu belgeler açıktır:

- `hakkinda.md` ürünün ne olduğunu anlatır. Metin, ürün anlatılınca yazılır.
- `yigin.md` kullanılan yığını anlatır. Metin, yığın seçilince yazılır. Servis adları buradan okunur.
- `ilk-istem.md` projenin ilk kodunu oluşturacak istemdir. `/basla` kullanıcıyla birlikte yazar; kullanıcı "docs/proje/ilk-istem.md dosyasını uygula" deyince uygulanır.

Ürünün kimliğine ait yeni bir belge gerekiyorsa bu klasöre eklenebilir.

## mantik

Bir davranış bir belgede anlatılır. Belgenin adı küçük harftir, kelimelerin arasına tire konur ve anlattığı davranışı söyler. `admin-yetkilendirmesi.md` ve `free-paket-sinirlari.md` bu ada uyar. Bir butonun adı veya her şeyi kapsayan `sistem.md` gibi bir ad uymaz.

Yeni bir davranışın kendi belgesi bu klasöre eklenebilir. Belgeler kullanıcıyla birlikte, sözleşme soruları sorularak yazılır (`.claude/rules/mantik-belgeleri.md`). Kod, belgenin anlattığı davranışı değiştirirse belge aynı işte güncellenir.

## kayitlar

Burada olan işin kaydı tutulur. Kayıt en alta eklenir. Eski satır düzenlenmez. Düzeltme, yeni bir kayıttır. Yeni bir defter gerekiyorsa bu klasöre eklenebilir.

`degisiklikler.md` yapılan her değişikliği tek satırda tutar. Sıra tarih, saat, alan, tür ve nottur. Tür `eklendi`, `silindi` veya `değişti` olur.

`teknik-borclar.md` açık bırakılan veya sonradan fark edilen borcu tutar. Her borcun bir kimliği ve bir adı vardır. İlk metin yerinde kalır. Borç kapanmadan da güncellenebilir. Kapsam veya durum değişince aynı kimlik ve aynı adla en alta yeni kayıt eklenir. Durumlar `açık`, `etkilendi` ve `kapandı` değerleridir. Durum `açık` kalabilir. `kapandı` yalnızca borç bittiğinde yazılır. Atlanan arayüz veya test, sayfa ve kontrol adıyla yazılır.
