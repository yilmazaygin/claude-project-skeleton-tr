# Docker

Araçlar bilgisayarda doğrudan çalıştırılmaz. PHP gibi araçlar projenin konteynerinde çalışır. İstisna: iskeletin kendi yardımcıları (`.claude/` altındaki hook'lar, `kur.py`, `doktor.py`) bilgisayardaki `python3` ile çalışır; bunlar proje aracı değildir. `kur.py` projenin araçlarını (composer, npm, artisan) yine konteynerde çalıştırır.

Makefile'da karşılığı olan iş o hedefle verilir.

- `make up` ve `make down` yereldir. Dosya `compose.local.yaml`. `make up` konteynerleri arka planda açar ve komut biter.
- `make live-up` ve `make live-down` canlıdır. Dosya `compose.live.yaml`. Kullanıcı canlı demeden canlı hedef verilmez.

Hazır yığının Makefile'ı günlük işleri taşır: `make logs [s=servis]`, `make sh`, `make migrate`, `make test`, `make test-e2e`, `make lint`, `make doctor`, `make ci`. Yeni hedef yalnızca kullanıcı isteyince eklenir. Karşılığı olmayan tek seferlik iş Compose ile verilir.

```text
docker compose -f compose.local.yaml exec <servis> <komut>
docker compose -f compose.local.yaml run --rm <servis> <komut>
```

Servis adı compose dosyasından okunur. Servis yokken ad uydurulmaz.

Konteyner adı, proje adı ile hizmet adının tire ile birleşmesidir. Bu ad her serviste `container_name` satırıyla açıkça yazılır. Compose'un kendi verdiği ada bırakılmaz.

Konteyner içindeki port standart kalır. Bilgisayar portu yalnızca `compose.local.yaml` içinde değişir. Canlıda dışarı yalnızca 80 ve 443 açılır. Veritabanı portu canlıda yayımlanmaz.

Hiçbir zaman SSH, scp veya sftp kurulmaz.

```text
kötü: php -v
iyi: docker compose -f compose.local.yaml exec api php -v
```
