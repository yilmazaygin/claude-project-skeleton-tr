#!/bin/sh
# Geri yükleme sınaması (yedekleme kuralı): açılmayan yedek, yedek sayılmaz.
# Ana veritabanının en son günlük yedeği GEÇİCİ bir veritabanına yüklenir, tablolar sayılır,
# sonuç yedek klasöründeki günlüğe yazılır ve geçici veritabanı kaldırılır.
# Projenin kendi veritabanına dokunulmaz.
set -eu
# cron işleri boş bir ortamla çalıştırır; PATH olmadan psql ve pg_dump bulunamaz (denendi).
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
[ -f /etc/yedek.env ] && . /etc/yedek.env
GECICI=geri_yukleme_sinamasi
GUNLUK=/yedekler/geri-yukleme-sinamalari.log

son=$(ls -1 /yedekler/gunluk 2>/dev/null | grep -E "^${PGDATABASE}-[0-9]{8}-[0-9]{6}\.dump$" | sort | tail -1)
if [ -z "$son" ]; then
  echo "$(date -Iseconds) BAŞARISIZ: ${PGDATABASE} için yedek yok" | tee -a "$GUNLUK"
  exit 1
fi

psql -d postgres -qc "DROP DATABASE IF EXISTS $GECICI"
psql -d postgres -qc "CREATE DATABASE $GECICI"
if pg_restore --no-owner --exit-on-error -d "$GECICI" "/yedekler/gunluk/$son"; then
  tablo=$(psql -d "$GECICI" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
  psql -d postgres -qc "DROP DATABASE $GECICI"
  echo "$(date -Iseconds) BAŞARILI: $son geçici veritabanına yüklendi, $tablo tablo" | tee -a "$GUNLUK"
else
  psql -d postgres -qc "DROP DATABASE IF EXISTS $GECICI"
  echo "$(date -Iseconds) BAŞARISIZ: $son yüklenemedi" | tee -a "$GUNLUK"
  exit 1
fi
