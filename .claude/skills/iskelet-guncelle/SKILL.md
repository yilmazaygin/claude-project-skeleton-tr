---
name: iskelet-guncelle
description: Projenin kurallarını, hook'larını ve skill'lerini iskeletin yeni sürümüyle karşılaştırır, farkları gösterir ve kullanıcının seçtiği dosyaları kopyalar. Yalnızca kullanıcı /iskelet-guncelle <iskeletin yolu> yazınca çalışır.
disable-model-invocation: true
argument-hint: "<iskelet klasörünün yolu>"
---

# İskelet güncelleme

İskelet zamanla düzeltilir. Bu skill o düzeltmeleri, iskeletten daha önce açılmış bir projeye taşır. Hiçbir dosya kullanıcı seçmeden değişmez; hiçbir dosya silinmez.

İskeletin yolu: $ARGUMENTS

## 1. Yolu doğrula

- Yol boşsa sor; tahmin etme. Yol, kullanıcının açıkça verdiği tek dış yoldur (kapsam.md); başka klasöre bakılmaz.
- Yolda `.claude/iskelet-gecmisi/` yoksa dur ve söyle: "Bu klasör iskeletin kendisi görünmüyor."
- Proje iskeletin kendisiyse (projede `.claude/iskelet-gecmisi/` varsa) dur: güncellenecek bir şey yok.

## 2. Ne değişti?

- Projenin sürümü `.claude/iskelet.json` dosyasındaki `surum` alanındadır (tarih). Dosya veya alan yoksa "bilinmiyor" sayılır.
- İskeletin `.claude/iskelet-gecmisi/degisiklikler.md` dosyasından bu tarihten **sonraki** satırlar okunur ve kullanıcıya kısaca özetlenir. Sürüm bilinmiyorsa son 20 satır gösterilir.

## 3. Karşılaştır

Karşılaştırma yalnızca okuyarak yapılır: `diff -rq` ile liste, `diff -u` ile dosya farkı.

| Projede | İskelette | Not |
|---|---|---|
| `.claude/rules/` | `.claude/rules/` | Açılmış isteğe bağlı kuralın kopyası iskelette yoktur; o dosya `.claude/opsiyonel-kurallar/` altındaki asılla karşılaştırılır. |
| `.claude/hooks/` | `.claude/hooks/` | |
| `.claude/skills/` | `.claude/skills/` | `yigin/hazir/` yalnızca projede kalan yığın için karşılaştırılır; silinen yığın geri getirilmez. |
| `.claude/opsiyonel-kurallar/` | aynı | |
| `.claude/doktor.py` | aynı | |
| `.claude/iskelet.json` | aynı | Yalnızca `surum` alanı güncellenir (5. adım). |
| `.claude/settings.json` | aynı | Projeye özel satırlar taşır (araç engeli). |
| `CLAUDE.md`, `docs/README.md` | aynı | CLAUDE.md projeye özel bölüm taşır ("Açık isteğe bağlı kurallar"). |

Listeyi kullanıcıya üç grupta göster: **değişen**, **yalnızca iskelette olan (yeni)**, **yalnızca projede olan**. Yalnızca projede olan dosyalar silinmez, yalnızca listelenir.

**Sadeleştirilmiş proje:** projenin `iskelet.json` dosyasındaki `kaldirilanlar` listesindeki yollar (`/basla` sırasında sadeleştirmeyle kaldırılmış) "yeni" diye önerilmez; listenin sonunda "kaldırılmış, önerilmedi" diye ayrıca sayılır. Kullanıcı birini geri isterse kopyalanır ve listeden çıkarılır. `settings.json` birleştirilirken, `korumalar` içinde kapalı olan korumanın deny satırları geri eklenmez.

## 4. Dosya dosya sor

Her değişen veya yeni dosya için şıklı soru aracıyla sor. Bir soruda en fazla dört dosya birlikte sorulabilir.

- Her soruda farkın özeti yazılır: iskeletten gelen satır sayısı ve projede olup iskelette olmayan satır sayısı (`diff -u` çıktısındaki `+` ve `-` satırları).
- Projedeki dosyada iskelette olmayan satır yoksa (dosya yalnızca eskiyse): ilk şık "Kopyala (Önerilen)". Diğerleri: "Farkı göster", "Atla".
- Projedeki dosyada iskelette olmayan satır varsa, yani projede değiştirilmişse (kural metnine eklenmiş bir cümle gibi): kopyalamak o satırları siler. İlk şık "Elle birleştir (Önerilen)"dir.
- Projeye özel satır taşıyan dosyalar (`settings.json`, `CLAUDE.md`, açılmış isteğe bağlı kuralın `.claude/rules/` kopyası): ilk şık "Elle birleştir (Önerilen)". Bu seçilirse iskeletteki yeni satırlar Edit aracıyla eklenir, projeye özel satırlar korunur. Diğerleri: "Farkı göster", "Atla".
- "Farkı göster" seçilirse `diff -u` çıktısı gösterilir ve aynı soru yeniden sorulur.

Kopyalama `cp` ile yapılır. `docs/kayitlar/` ve `.env*` dosyalarına dokunulmaz.

## 5. Sonrası

1. Bir hook değiştiyse testler çalıştırılır: `python3 .claude/hooks/hook_testleri.py`. Test başarısızsa bu söylenir ve hangi dosyanın değiştiği hatırlatılır.
2. Projenin `.claude/iskelet.json` dosyasındaki `surum` alanı, iskeletin `iskelet.json` dosyasındaki tarihle güncellenir (Edit; kullanıcı onaylar). `korumalar` ve `kaldirilanlar` alanlarına dokunulmaz.
3. Kopyalanan veya birleştirilen her dosya için `/changelog` ile tek satır yazılır (alan: `iskelet`).
4. Atlanan dosyalar kullanıcıya listelenir.
