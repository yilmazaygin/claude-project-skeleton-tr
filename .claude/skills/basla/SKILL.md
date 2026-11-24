---
name: basla
description: Template'ten açılmış yeni projenin onboarding'i. Kullanıcının serbest anlatımından projeyi anlar, yalnızca eksik soruları sorar; ürün belgesini, yığın ayarlarını, gereken isteğe bağlı kuralları, projeye özel kuralları ve mantık belgelerini kullanıcıyla birlikte yazar, gereksizleri siler ve ilk prompt'u birlikte hazırlar. Kod yazmaz. Kullanıcı "başla", "/basla" veya "projeyi başlatalım" dediğinde ve .claude/iskelet.json içinde tur "iskelet" iken kullanılır.
argument-hint: "[projenin serbest anlatımı]"
---

# Proje onboarding'i

Bu skill, iskeletten açılmış bir depoyu o projenin kendi iskeletine dönüştürür. Sonunda depoda şunlar vardır:
- kurallar;
- ürün ve yığın belgeleri;
- mantık belgelerinin taslakları;
- ayar dosyaları;
- birlikte yazılmış bir ilk prompt.

**Kod yazılmaz.** Kod, kullanıcı ilk prompt'u verdiğinde oluşur.

Kullanıcının anlatımı (boş olabilir): $ARGUMENTS

**İlkeler:**
- **Önce anlat, sonra az soru.** Anlatımda cevabı olan soru sorulmaz. Sorular şıklı soru aracıyla, en fazla dörderli gruplar halinde sorulur; ilk şık anlatıma göre öneridir ve "(Önerilen)" diye işaretlenir.
- **Uydurma yok.** Anlatımda olmayan özellik, rol veya kural eklenmez. Bilinmeyen "bilinmiyor" diye yazılır ya da sorulur.
- **Sesli anlatım.** Anlatım mikrofonla yazılmış, dağınık ve yazım hatalı olabilir. Anlam çıkarılır; emin olunmayan yer "Anladıklarım" adımında sorulur.
- **Tek plan onayı.** Bütün yazma işleri tek bir plan modu onayıyla yapılır (`plan.md`). Onaydan önce hiçbir dosya değişmez.
- **Kod yok.** `kur.py kod`, `composer`, `npm` çalıştırılmaz; `backend/` ve `frontend/` oluşturulmaz.

## 0. Ön kontrol

- `.claude/iskelet.json` okunur. `tur` zaten `proje` ise dur ve söyle: "Bu proje zaten başlatılmış. Yığın için `/yigin`, isteğe bağlı kurallar için `/kural` kullanılabilir."
- İskeletin kendi deposu da `tur: iskelet` taşır. Bu yüzden başlamadan önce şıklı sor: "Bu depo, iskeletten (template) açılmış yeni projeniz mi?" Şıklar: "Evet, yeni projem (Önerilen)" ve "Hayır, iskeletin kendisi". İkincisi seçilirse dur: onboarding iskeletin kendisinde yapılmaz.

## 1. Anlatım

Argüman boşsa şunu iste ve bekle:

> Projeyi istediğiniz uzunlukta anlatın. Ne yapıyor, kimler kullanıyor, hangi roller var, hangi sayfalar ve özellikler olacak, tasarım nasıl olacak, canlıya nasıl çıkacak? Aklınıza gelen her şey; eksikleri ben sorarım.

## 2. Anladıklarım

Anlatımdan çıkarılanları tek bir özet olarak göster. Başlıklar:

- **Ürün:** tek cümle ve kısa açıklama.
- **Kullanıcılar ve roller:** ör. süper admin, işletme sahibi, ziyaretçi.
- **Ana özellikler ve sayfalar.**
- **Veri:** ana kavramlar, ör. işletme, menü, kategori, ürün.
- **Entegrasyonlar:** ödeme, e-posta, harita gibi.
- **Tasarım:** tarz, referanslar, kullanılacak skill'ler.
- **Canlı ortam:** alan adı, sunucu.
- **Kapsam dışı:** anlatımda "şimdilik yok" denenler.
- **Bilinmeyenler:** sonraki adımda sorulacaklar.

Sor: "Doğru anlamış mıyım? Düzeltmek veya eklemek istediğiniz bir şey var mı?" Düzeltmeler özete işlenir. Kullanıcı onaylayana kadar bu adım tekrarlanır.

## 3. Eksik sorular

Yalnızca anlatımdan ve düzeltmelerden çıkmayanlar sorulur. Katalog ve her cevabın nereye gittiği:

| Konu | Soru | Sonuç |
|---|---|---|
| Yığın | Hazır yığın (`.claude/skills/yigin/hazir/*/HAZIR.md`: `ad`, `ozet`) veya özel yığın; ekler (mailpit, queue, scheduler, e2e) | `kur.py yapilandir` argümanları |
| Proje adı | Küçük harf ve tire; ilk şık depo klasörünün adı | aynı |
| Proje numarası | İki hane (01-99), başka projede kullanılmayan; portlar `80NN`, `54NN`, `63NN` | aynı; `kur.py` port doluysa durur |
| Kayıt | Önemli işlerin (ör. süper admin işlemleri) değiştirilemez bir kaydı tutulsun mu? | `denetim-kaydi` açılır |
| Çerez ve analitik | Ziyaretçi analitiği (GA4, Umami), çerez onayı, giriş ve IP kaydı | `cerez-ve-izleme` ve parçaları |
| Yedek | Canlıya çıkacak mı, yedek nereye, uzak kopya | `yedekleme` |
| Çekirdek kurallar | Hepsi kalsın mı? Özellikle: Git salt okunur (`git.md`), SSH yasağı. İlk şık "Hepsi kalsın". `veri.md` kaldırılmak istenirse veri korumasının kalkacağı söylenir ve ikinci kez onay istenir. | `sadelestirme.md` 2. adım |
| Skill'ler | `/iskelet-guncelle` kalsın mı (iskeletten güncelleme alınacak mı)? | `sadelestirme.md` 3. adım |
| Tasarım | Tasarımda kullanılacak skill'ler, referans siteler, renk ve yazı tercihleri | `hakkinda.md` ve ilk prompt |
| Lisans | Projenin lisansı: "Kapalı kaynak, lisans dosyası yok (Önerilen)", "MIT", başka. İskeletin MIT lisansı projeye geçmez. | `LICENSE` ve README |
| Diğer | Dil (tek, çok), e-posta gönderimi, ödeme, dosya yükleme gibi anlatımda geçen ama net olmayan konular | `hakkinda.md` ve ilgili mantık belgesi |

- **İsteğe bağlı kuralın soruları:** açılması seçilen her isteğe bağlı kuralın dosyası okunur; "Devreye alma" sorularından cevabı bilinmeyenler de bu adımda sorulur.
- **Katalog dışı sorular:** katalog dışında, anlatımın gerektirdiği her soru sorulabilir. Ama her soru bir karar içindir: cevabı hiçbir dosyaya yazılmayacak soru sorulmaz.

## 4. Öneriler

Anlatıma dayanarak öner, çoklu seçimle sor. Onaylananlar plana girer:

- **Projeye özel kurallar.** Anlatımdan çıkan kalıcı davranışlar. Her kural:
  - tek dosyadır (`.claude/rules/<davranis-adi>.md`), adı küçük harf kebab-case;
  - mevcut kuralların biçimindedir: başlık, kısa cümleler, `kötü`/`iyi` örneği.

  Örnek: "her işletme yalnızca kendi menüsünü görür" → `isletme-yalitimi.md`; "fiyatlar kuruş olarak tamsayı tutulur" → `para-birimi.md`. Mevcut bir kurala tek cümleyle eklenebilecek olan ayrı dosya olmaz.
- **Projeye özel skill'ler.** Projede tekrar edecek işler, ör. "yeni menü teması ekle". Bu adımda yalnızca adı ve amacı yazılır (`hakkinda.md`, "Yapılacak skill'ler"); skill'in içi ilk kullanımda kullanıcıyla birlikte yazılır.
- **Mantık belgeleri.** Anlatımdaki her ana davranış için bir belge adı, ör. `yetkilendirme.md`, `menu-yapisi.md`, `qr-kod-uretimi.md`. Ad, `mantik-belgeleri.md` kuralına uyar.

## 5. Mantık belgeleri, birlikte

Seçilen her belge için `mantik-belgeleri.md` kuralındaki "Birlikte yazma" uygulanır:

- Belgeye özel sözleşme soruları sorulur: roller ve yetkiler, durumlar ve geçişler, veri kuralları, kenar durumlar, başka davranışlarla bağ.
- Cevaplar belgenin iskeletine yerleştirilir. Cevapsız kalanlar "Açık sorular" bölümüne yazılır.
- Kullanıcı bir konuyu kısaca geçerse o konu zorla derinleştirilmez: belge "Açık sorular" ağırlıklı kalır ve ikinci turda tamamlanır.

## 6. Plan

Plan moduna geç. Planda şunlar bulunur:

- değişecek proje türü (`tur: proje`); silinecek iskelet dosyaları (`.claude/iskelet-gecmisi/`, `CHANGELOG.md`, iskeletin `LICENSE` dosyası) ve projenin lisansı;
- `hakkinda.md` taslağının başlıkları;
- yığın: hazır yığın, proje adı, numara, ekler, portlar, yazılacak dosyalar;
- açılacak isteğe bağlı kurallar ve bekleyen parçaları;
- yazılacak proje kuralları ve mantık belgeleri (adlarıyla);
- silinecekler (`sadelestirme.md`): kurallar, skill'ler, kapanacak korumalar;
- CLAUDE.md, README ve `docs/proje/ilk-istem.md`.

Onay gelmezse sor: "Plan moduna onay vermediniz, ne yapmamı istersiniz?"

## 7. Uygula

Sırayla:

1. **Proje türü:** `.claude/iskelet.json` içinde `tur` alanı `proje` yapılır (Edit; Claude Code onaylatır). `surum` alanına dokunulmaz: projenin hangi iskelet sürümünden açıldığını gösterir. Sonra iskeletin kendi dosyaları silinir: `rm -r .claude/iskelet-gecmisi CHANGELOG.md` (iskeletin geçmişi ve sürüm notları; projede gereksiz).
   **Lisans:** iskeletin `LICENSE` dosyası (MIT, iskeletin sahibine ait) silinir. Kullanıcı projeye bir lisans seçtiyse yeni `LICENSE` yazılır; telif satırındaki ad ve yıl kullanıcıya sorulur, uydurulmaz.
2. **`docs/proje/hakkinda.md`:** 2. adımdaki başlıklarla yazılır. Bunlara ek olarak:
   - "Tasarım" altında kullanılacak skill'ler;
   - "Yapılacak skill'ler";
   - "Açık sorular".
3. **`docs/proje/ilk-istem.md`:** `ilk-istem.md.tmpl` şablonundan açılır. Kural adımları "Kurulacak parçalar" bölümüne yazacağı için bu dosya önce açılır.
4. **Yığın:** `python3 .claude/skills/yigin/kur.py yapilandir <hazir> <proje> <no> <ekler>`. `docs/proje/yigin.md`, compose, Makefile ve `.env` yazılır; yerel `.env` değerleri üretilir. `/yigin` 5. adım (araç engeli) 3. adımda sorulmadıysa burada sorulur. Özel yığın seçildiyse `/yigin` skill'inin özel yığın adımları uygulanır.
5. **İsteğe bağlı kurallar:** her biri için `/kural ac` adımları uygulanır. Sorular 3. adımda soruldu, yeniden sorulmaz. Uygulama klasörleri olmadığı için `backend/` ve `frontend/` adımları bekler ve `ilk-istem.md` dosyasının "Kurulacak parçalar" bölümüne yazılır. Kuralın "Kurulum sonrası TD"si açılır.
6. **Proje kuralları:** `.claude/rules/` altına yazılır.
7. **Mantık belgeleri:** `docs/mantik/` altına yazılır.
8. **Sadeleştirme:** `sadelestirme.md` uygulanır.
9. **CLAUDE.md:**
   - İlk paragraf ("Bu depo, yeni bir projeye başlarken kullanılan iskelettir…") projeyi anlatan iki üç cümleyle değişir.
   - "Oturum başı" bölümü kaldırılır.
   - Kural listesine proje kuralları "Projeye özel" alt başlığıyla eklenir.
   - Skill ve isteğe bağlı kural listeleri güncellenir.
10. **README.md:** kök README, `README.proje.md.tmpl` şablonundan projenin README'si olarak yeniden yazılır. İskeletin tanıtımı projede gerekmez.
11. **Kayıt:** `/changelog` ile ilk kayıtlar yazılır (alan `proje`): proje başlatıldı, yığın, açılan kurallar, proje kuralları, mantık belgeleri, sadeleştirme.
12. **Kontrol:** `make doctor` çalıştırılır ve hook testleri çalıştırılır; sonuçlar aynen söylenir.

## 8. İlk prompt, birlikte

`docs/proje/ilk-istem.md` doldurulur ve kullanıcıya gösterilir. Şablonun bölümleri:
- hedef;
- adım 1 `kur.py kod`;
- kurulacak parçalar;
- yapılacaklar;
- tasarım;
- kapsam dışı;
- bitti ölçütü.

Kullanıcıyla birlikte düzeltilir:
- **İlk sürüm:** "İlk sürümde bunların hepsi olsun mu, yoksa önce şu kısmı mı?" diye sorulur. İlk prompt küçük ve bitirilebilir olmalı; geri kalanlar "Sonraki sürümler" bölümüne gider.
- **Tasarım skill'leri:** tasarım için kullanılacak skill'ler adıyla yazılır.
- **Atıflar:** her madde ilgili mantık belgesine atıf yapar.

Sonunda şunu söyle:

> Hazır olduğunuzda yeni bir mesajda şunu yazmanız yeterli: **"docs/proje/ilk-istem.md dosyasını uygula."** Kod o zaman oluşacak; önce plan sunulacak.

## 9. Kendini kaldırma

`/basla` bir kez çalışır. Sor: "Onboarding bitti. `/basla` skill'i kaldırılsın mı?" İlk şık "Kaldır (Önerilen)".

Kaldırılırsa:
- `.claude/skills/basla/` silinir;
- yol `iskelet.json` içindeki `kaldirilanlar` listesine eklenir;
- CLAUDE.md'den satırı çıkarılır.
