# Kayıtlar

Defterler alta eklenir. Eski satır düzenlenmez. Düzeltme yeni kayıttır. Ajan imzası yok. Bu kural `.claude/hooks/` altındaki hook'larla da zorlanır; eski satırı değiştiren yazım reddedilir.

**İskelet ile proje ayrıdır.** `.claude/iskelet.json` içinde `tur` alanı `iskelet` ise bu depo iskeletin kendisidir: iskeletin değişiklikleri ve borçları `.claude/iskelet-gecmisi/` altındaki `degisiklikler.md` ve `teknik-borclar.md` defterlerine yazılır. Template'ten açılan projede `/basla` alanı `proje` yapar ve iskeletin geçmişini siler. `docs/kayitlar/` projenin defterleridir; yeni projede boş başlar ve ilk kaydı `/yigin` yazar. İki yerdeki defterler de yalnızca alta eklenir.

Tarih ve saat tahmin edilmez. `date '+%Y-%m-%d %H:%M'` komutuyla okunur.

Kayıt yazmak için skill'ler vardır. Değişiklik satırı `/changelog`, teknik borç kaydı `/td` ile yazılır. Biçimin ayrıntısı bu skill'lerdedir. Kullanıcı istemese de kayıt gerektiğinde ajan bu skill'leri kendisi kullanır.

## Değişiklikler

Dosya: `docs/kayitlar/degisiklikler.md`

Yapılan her değişiklik tek satırdır. Sıra: tarih, saat, alan, tür, not.

```text
2026-10-28 23:13 | backend | eklendi | oturum açma yanıtına kilit süresi eklendi
```

- Tarih `YYYY-MM-DD`, saat `HH:mm`, yerel saat.
- Alan: `backend`, `frontend` veya tek kelimelik katman.
- Tür: `eklendi`, `silindi`, `değişti`.
- Not: tek cümle.
- Ayrı davranış ayrı satırdır. Yazım hatası, boşluk ve yorum yazılmaz.

## Teknik borç

Dosya: `docs/kayitlar/teknik-borclar.md`. Biçim örneği de oradadır. Gerçek kayıtlar `## Kayıtlar` altına eklenir. Belgedeki `TD-örnek` kopyalanmaz.

Her borcun kimliği ve adı vardır. Kimlik `TD-001` biçimindedir. Ad kısa ve kalıcıdır; başlıkta ve `Ad` satırında yazılır. İlk metin donuktur.

Borç kapanmadan güncellenebilir. Kapsam, etki veya ilgili davranış değişince aynı kimlik ve aynı adla alta yeni kayıt eklenir. Durum `açık` kalabilir. `kapandı` yalnızca borç bittiğinde yazılır.

Durum: `açık`, `etkilendi`, `kapandı`.

Atlanan arayüz veya test, sayfa ve kontrol adıyla yazılır. "Bazı dosyalar değişmeli" yazılmaz.
