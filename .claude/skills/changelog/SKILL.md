---
name: changelog
description: docs/kayitlar/degisiklikler.md dosyasının en altına tek satırlık değişiklik kaydı ekler. Bir davranış, API, yapılandırma veya belge eklenince, silinince ya da değişince kullanılır. Yazım hatası, boşluk ve yorum için kullanılmaz.
argument-hint: "[alan] [eklendi|silindi|değişti] [not]"
allowed-tools: Read, Edit, Bash(date:*)
---

# Changelog kaydı

Dosya: `docs/kayitlar/degisiklikler.md`. Kayıt yalnızca en alta eklenir. Eski satır düzenlenmez, silinmez, yeniden sıralanmaz. Düzeltme yeni bir satırdır.

Kullanıcının verdiği bilgi: $ARGUMENTS

## Adımlar

1. Saati oku: `date '+%Y-%m-%d %H:%M'`. Saat tahmin edilmez.
2. Dosyayı oku. Son satırın biçimini gör.
3. Her ayrı davranış için bir satır kur:

   ```text
   YYYY-MM-DD HH:mm | alan | tür | not
   ```

   - **Alan**: `backend`, `frontend`, `docs`, `docker` gibi tek kelimelik katman. Kullanıcı verdiyse onu kullan.
   - **Tür**: yalnızca `eklendi`, `silindi` veya `değişti`.
   - **Not**: tek cümle, küçük harfle başlar, nokta yoktur. Neyin değiştiğini söyler, dosya listesi değildir.
4. Alan veya tür belli değilse şıklı sor. İlk şık önerindir.
5. Satırları dosyanın en sonuna ekle. Dosya sonunda tek bir yeni satır karakteri kalır.
6. Eklenen satırları kullanıcıya aynen göster.

## Örnek

```text
iyi: 2026-10-28 23:13 | backend | eklendi | oturum açma yanıtına kilit süresi eklendi
kötü: 2026-10-28 23:13 | backend | eklendi | auth.php ve user.php değişti.
kötü: 2026-10-28 | eklendi | birkaç düzeltme
```

Ajan imzası yazılmaz.
