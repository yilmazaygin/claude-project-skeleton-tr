---
name: td
description: docs/kayitlar/teknik-borclar.md dosyasına teknik borç kaydı ekler veya var olan bir borcu aynı kimlikle günceller. Bir arayüz veya test güncellenmeden iş bitecekse, açık bırakılan ya da sonradan fark edilen bir eksik varsa kullanılır.
argument-hint: "[yeni | TD-xxx] [açıklama]"
allowed-tools: Read, Edit, Bash(date:*)
---

# Teknik borç kaydı

Dosya: `docs/kayitlar/teknik-borclar.md`. Gerçek kayıtlar `## Kayıtlar` başlığının altına, dosyanın en sonuna eklenir. Üstteki `## Biçim` bölümü ve `TD-örnek` kayıtları borç değildir. Onlara dokunulmaz ve kopyalanmaz.

Kullanıcının verdiği bilgi: $ARGUMENTS

## Adımlar

1. Saati oku: `date '+%Y-%m-%d %H:%M'`. Saat tahmin edilmez.
2. Dosyayı oku. `## Kayıtlar` altındaki başlıklara bak.
3. Kaydın türüne karar ver:
   - **Yeni borç**: `## Kayıtlar` altındaki en büyük `TD-` numarasını bul ve bir artır. Hiç kayıt yoksa `TD-001`. Numara üç hanelidir. Silinmiş veya kullanılmış numara yeniden kullanılmaz.
   - **Var olan borcun güncellemesi**: aynı kimliği ve aynı adı kullan. Ad değiştirilmez.
   - Hangisi olduğu belli değilse şıklı sor. İlk şık önerindir.
4. Kaydı kur ve en alta ekle. Eski kayıt düzenlenmez.

## Yeni borç

```markdown
### TD-001 — ödeme kuyruğu — 2026-10-28 23:13

- Ad: ödeme kuyruğu
- Durum: açık
- Borç: başarısız ödeme yeniden denenmiyor
- Etki: kullanıcı çift çekim sanabilir
- İlgili davranış: ödeme onayı tek denemede bitiyor
```

## Güncelleme

```markdown
### TD-001 — ödeme kuyruğu — 2026-10-29 10:05

- Ad: ödeme kuyruğu
- Durum: açık
- Kapsam: yeniden deneme yalnızca zaman aşımında
- Değişiklik: kapsam daraldı; borç kapanmadı
- İlgili davranış: zaman aşımı ayrı sayılır
```

## Kurallar

- **Durum**: yalnızca `açık`, `etkilendi` veya `kapandı`. `kapandı` yalnızca borç gerçekten bittiğinde yazılır. Kullanıcı kapandığını söylemediyse ve iş görülmediyse yazılmaz.
- **Ad**: kısa ve kalıcı. Başlıkta ve `Ad` satırında aynı yazılır.
- **Borç metni**: eksiği sayfa, kontrol ve davranış adıyla söyler.

```text
iyi: Ayarlar sayfasındaki dışa aktar tuşu artık kullanılmıyor.
iyi: Ödeme sayfasındaki iade çağrısının testi yok.
kötü: Bazı dosyalar değişmeli.
```

Eklenen kayıt kullanıcıya aynen gösterilir. Ajan imzası yazılmaz.
