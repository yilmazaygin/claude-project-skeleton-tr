---
name: kural
description: İsteğe bağlı kuralları listeler, açar veya kapatır. Kurallar .claude/opsiyonel-kurallar/ klasöründe bekler; açılan kural .claude/rules/ altına kopyalanır ve her oturumda geçerli olur. Yalnızca kullanıcı /kural yazınca çalışır.
disable-model-invocation: true
argument-hint: "[liste | ac <ad> | kapat <ad>]"
---

# İsteğe bağlı kurallar

Kullanıcının verdiği bilgi: $ARGUMENTS

İsteğe bağlı kurallar `.claude/opsiyonel-kurallar/` klasöründedir. Bir kuralın açık olması, aynı adlı dosyanın `.claude/rules/` altında da bulunması demektir.

Argüman yoksa veya anlaşılmıyorsa şıklı sor: "liste", "aç", "kapat".

## liste

1. `.claude/opsiyonel-kurallar/*.md` dosyalarını listele (`README.md` hariç).
2. Her biri için `.claude/rules/` altında aynı adlı dosya var mı bak.
3. Tablo göster: kural, açık mı, tek cümlelik özet (README'deki tablodan).

## ac `<ad>`

1. `.claude/opsiyonel-kurallar/<ad>.md` yoksa dur ve mevcut kuralları göster. Kural zaten açıksa söyle ve dur.
2. Kural dosyasını baştan sona oku.
3. **Devreye alma soruları:** kuralın "Devreye alma" bölümündeki soruları şıklı soru aracıyla sor; her sorunun cevabı kuralın o soruda yazdığı dosyaya yazılır (gizli değerler hiçbir zaman); her soruda ilk şık önerindir. `docs/proje/hakkinda.md` doluysa öneriler ürüne göre yapılır. Ürün bilinmiyorsa uydurulmaz, sorulur.
4. **Plan:** yazılacak dosyaları kısaca söyle. Kural bir belge açtıracaksa (örneğin `docs/mantik/denetim-kaydi.md`), belgenin adı mantik-belgeleri kuralına göre ayrıca sorulur. Onay gelmeden dosya yazılmaz.
5. **Kopyala:** `.claude/opsiyonel-kurallar/<ad>.md` dosyasını `.claude/rules/<ad>.md` olarak aynen kopyala. Kopyada değişiklik yapılmaz; projeye özel bilgiler aşağıdaki yerlere yazılır.
6. **Cevapları yaz:** kuralın "Devreye alma" bölümü hangi cevabın nereye yazılacağını söyler (örneğin saklama süresi `docs/proje/yigin.md` dosyasına).
7. **`CLAUDE.md`:** "Açık isteğe bağlı kurallar" bölümüne bir satır ekle: `- <ad>: <tek cümle>`. Bölümdeki "Şu an açık isteğe bağlı kural yok." cümlesi ilk satır eklenince kaldırılır. Bölüm yoksa "İsteğe bağlı kurallar" bölümünün sonuna açılır.
8. **Hazır parçalar:** kuralın yardımcı klasöründe `PARCALAR.md` varsa (örneğin `.claude/opsiyonel-kurallar/cerez-ve-izleme/PARCALAR.md`):
   - parçalar kuralın "Devreye alma" sorusuyla çoklu seçimle seçtirilir; bir parçanın gerektirdiği parça seçilmediyse söylenir ve eklenir;
   - kurulum kod yazmaktır, bu yüzden seçilen parçaların değiştireceği dosyalar plan moduyla sunulur; onaydan sonra `PARCALAR.md` adımları sırayla uygulanır;
   - yığın (`laravel-next` / `fastapi-next`) `docs/proje/yigin.md` dosyasından okunur; yığın seçilmemişse parça kurulmaz, önce `/yigin` önerilir;
   - **uygulama klasörleri yoksa** (`backend/` veya `frontend/` henüz oluşturulmadıysa): compose, `.env` ve belge adımları uygulanır; `backend/` ve `frontend/` içine kopyalanacak adımlar "bekliyor" sayılır. Bekleyen adımlar dosya ve kontrol adıyla bir TD'ye yazılır (ad: `<ad> bekleyen parçalar`). **`/basla` içinden çalışırken** TD açılmaz: bekleyen adımlar `docs/proje/ilk-istem.md` dosyasının "Kurulacak parçalar" bölümüne yazılır, çünkü ilk prompt kodu oluşturup bu parçaları kuracaktır. Uygulama oluşturulduktan sonra `/kural ac <ad>` tekrar çağrılırsa (ya da ilk prompt uygulanırken) yalnızca bekleyen adımlar uygulanır; TD açıldıysa kapanır;
   - compose dosyası değiştiyse `/yigin` 6. adımdaki iki doğrulama (`docker compose ... config --quiet`) yeniden çalıştırılır; yeni zorunlu değişkenler `yigin.md` dosyasındaki listeye eklenir.
9. **Kurulum sonrası TD:** kuralda "Kurulum sonrası TD" bölümü varsa ve en az bir parça **seçildiyse** (kurulmuş veya bekliyor olsun) `/td` ile hemen o borç açılır. Borç metni seçilen parçaları ve hangilerinin beklediğini adıyla yazar.
10. **Kurallar arası bağ:** açılan kuralın "Diğer kurallarla bağ" bölümü okunur. Bağlı kural zaten açıksa oradaki adım uygulanır (örneğin denetim kaydı kataloğuna yeni olaylar eklenir). Bağlı kural sonradan açılırsa aynı adım o zaman uygulanır.
11. **Kayıt:** `/changelog` ile kayıt yaz: `iskelet | eklendi | <ad> isteğe bağlı kuralı açıldı`. Kurulan her parça için ayrı bir satır yazılır.
12. **Göster:** kural uygulama kodu istiyorsa (tablo, göç, servis) ve hazır parçası yoksa, bunun ayrı bir iş olduğunu ve plan moduyla yapılacağını söyle. Kural açmak kod yazmak değildir.

## kapat `<ad>`

1. `.claude/rules/<ad>.md` yoksa kural zaten kapalıdır; söyle ve dur.
2. Şıklı sor: "Kuralı kapat (Önerilen)" / "Vazgeç". Kapatmanın neyi etkilediğini yaz: Claude bu kurala artık uymaz. Projede yazılmış kayıtlar, tablolar ve belgeler yerinde kalır.
3. Onaydan sonra `.claude/rules/<ad>.md` kopyasını kaldır. `.claude/opsiyonel-kurallar/<ad>.md` asıl dosyası kalır.
4. `CLAUDE.md` içindeki satırını kaldır. Açık kural kalmadıysa yerine "Şu an açık isteğe bağlı kural yok." yazılır.
5. `/changelog` ile kayıt yaz: `iskelet | silindi | <ad> isteğe bağlı kuralı kapatıldı`.
6. Kuralın projeye eklediği kodlara, tablolara ve kayıtlara dokunma. Örneğin denetim kaydı tablosu ve içindeki kayıtlar silinmez.
