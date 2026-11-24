# Sadeleştirme (`/basla` 7. adım)

İskelet her projeye her şeyi getirir. Bu adım, projede kullanılmayacak olanları kaldırır. Kaldırılan her şey iskelette durur; gerekirse `/iskelet-guncelle <iskelet-yolu>` ile geri gelir.

Neyin kalıp neyin gideceği `/basla` sorularında zaten seçilmiştir (3. adım) ve plan onayından geçmiştir. Burada yeniden sorulmaz; yalnızca plandaki seçim uygulanır. Planda olmayan bir şey silinmez.

**İlkeler:**
- **Dokunulmayanlar:** `docs/kayitlar/`, `.env`, `.env.example`, compose dosyaları, Makefile.
- **Hazır yığınlar:** `.claude/skills/yigin/hazir/` içinde seçilen yığın ve `_ortak/` kalır, çünkü ilk prompt'taki `kur.py kod` adımı onları kullanır. Seçilmeyen yığını `kur.py yapilandir` zaten siler. `kur.py` her durumda kalır: CI `kur.py env` çağırır.
- **Hook kodu silinmez:** bir korumanın kuralı kalkınca koruma `.claude/iskelet.json` dosyasında kapatılır. `iskelet.json` ve `settings.json` değişiklikleri Edit aracıyla yapılır; Claude Code her birini kullanıcıya onaylatır. Bash ile bu iki dosyaya yazılamaz (hook reddeder).

## 1. Açılmamış isteğe bağlı kurallar

- **Seçilen her kural için:** açılmayan her kuralın `.claude/opsiyonel-kurallar/<ad>.md` dosyası ve aynı adlı `.claude/opsiyonel-kurallar/<ad>/` klasörü silinir.
- **Açılan kurallar kalır:**
  - `.claude/rules/<ad>.md` kopyası durur;
  - `opsiyonel-kurallar/` altındaki aslı ve parça klasörü de durur, çünkü bekleyen parçalar ilk prompt'ta oradan kurulur.
- **Hiç kural kalmazsa:** `.claude/opsiyonel-kurallar/` klasörü ve `/kural` skill'i silinir. Bir kural kalırsa `README.md` tablosundan silinenlerin satırları çıkarılır.
- **Atıflar:** silinen isteğe bağlı kurala koşullu atıflar ("yedekleme kuralı açıksa…", "Diğer kurallarla bağ" bölümleri, skill örnekleri) olduğu gibi kalır; kural açılmadıkça etkisizdir ve iskelet güncellemesini kolaylaştırır. Yalnızca CLAUDE.md listesi güncellenir.

## 2. Çekirdek kurallar

Kullanıcının "kaldırılsın" dediği her kural için bağlı olan her şey aynı işte kalkar:

| Kaldırılan | Koruma (`iskelet.json`) | `settings.json` içinden kalkanlar | Ayrıca |
|---|---|---|---|
| `git.md` | `git: false` | `deny` içindeki bütün `Bash(git ...)` satırları | `allow` içindeki `git status/log/diff/show` kalabilir |
| SSH yasağı | `ssh: false` | `Bash(ssh:*)`, `Bash(scp:*)`, `Bash(sftp:*)` | `docker.md` içindeki "Hiçbir zaman SSH, scp veya sftp kurulmaz." cümlesi |
| `kayitlar.md` | `defter: false` | yok | `/changelog` ve `/td` skill'leri silinir. Defter dosyaları silinmez; kullanıcı isterse silme komutu gösterilir, çalıştırılmaz. |
| `veri.md` | `docker-hacim: false`, `env-ornek: false` | `docker compose ... down -v/--volumes`, `docker volume rm/prune`, `docker system prune` satırları | Yalnızca kullanıcı 3. adımda veri korumasının kalkacağını bilerek ikinci kez onayladıysa. |
| `durustluk`, `soru`, `plan`, `kapsam`, `etki`, `mantik-belgeleri`, `alt-ajan`, `docker` | yok | yok | yalnızca dosya |

Her kaldırmadan sonra:

1. **Atıflar:** kaldırılan kuralın adı (ör. `git.md`) kalan kurallarda, skill'lerde, CLAUDE.md'de ve README'de aranır (`grep -rn`). Her atıf Edit ile düzeltilir: cümle kaldırılır ya da kuralsız haliyle yeniden yazılır. Belirsizse sorulur. Hook kodu ve hook testlerindeki atıflar (`.claude/hooks/`) değiştirilmez: hook kodu her projede aynı kalır, koruma `iskelet.json` ile kapanır.
2. **Hook testleri:** `python3 .claude/hooks/hook_testleri.py` çalıştırılır; 0 başarısız olmalı. Testler projenin ayarından bağımsızdır (varsayılan ayarlı geçici bir kopyada çalışır).
3. **Etkinin gösterilmesi:** kapatmanın etkisi bir örnekle gösterilir. Örneğin `git` kapatıldıysa:
   `echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m deneme"},"cwd":"."}' | python3 .claude/hooks/bash_bekci.py; echo $?` → `0`.
   Bu komut yalnızca hook'u sınar, commit yapmaz.

## 3. Kullanılmayan skill'ler

Kullanıcının seçtiği skill'lerin klasörleri `.claude/skills/<ad>/` silinir. Olası adaylar:
- `/iskelet-guncelle`: iskeletten güncelleme alınmayacaksa;
- `/kural`: isteğe bağlı kural kalmadıysa (1. adım);
- `/yigin`: önerilmez, çünkü sonradan servis eklemek ve yığını değiştirmek için gerekir.

`/basla`'nın kendisi en sonda ayrıca sorulur (`SKILL.md`, 9. adım).

## 4. Kaydet

- **`.claude/iskelet.json`:** korumalar güncellenir. Silinen her yol `kaldirilanlar` listesine eklenir (ör. `.claude/opsiyonel-kurallar/cerez-ve-izleme.md`, `.claude/rules/git.md`); `/iskelet-guncelle` bu yolları yeniden önermez.
- **CLAUDE.md:** listeler güncellenir. Hook bölümünde kapatılan korumanın maddesi "kapalı (`iskelet.json`)" diye işaretlenir.
- **Geri alma:** bir korumayı geri açmak için `iskelet.json` içinde değeri `true` yapmak ve kural dosyasını iskeletten geri almak yeter. Kullanıcı bunu açıkça isteyince Claude Edit ile yapar; Claude Code onaylatır.
