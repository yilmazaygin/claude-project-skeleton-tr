#!/bin/sh
# Yedek servisini başlatır: zamanlamayı kurar ve crond'u ön planda çalıştırır.
# crond işleri boş bir ortamla çalıştırır; bu yüzden bağlantı ve ayar değişkenleri bir dosyaya yazılır
# ve betikler onu okur. Dosya yalnızca konteynerin içindedir (izin 600).
set -eu
: "${YEDEK_SAATI:=03:30}"
SAAT=$(echo "$YEDEK_SAATI" | cut -d: -f1 | sed 's/^0//'); SAAT=${SAAT:-0}
DAKIKA=$(echo "$YEDEK_SAATI" | cut -d: -f2 | sed 's/^0//'); DAKIKA=${DAKIKA:-0}

umask 077
export -p | grep -E 'export (PG|YEDEK_|RCLONE_|TZ=)' > /etc/yedek.env

mkdir -p /etc/crontabs
{
  echo "$DAKIKA $SAAT * * * /usr/local/bin/yedekle.sh >> /proc/1/fd/1 2>&1"
  # Geri yükleme sınaması: pazar günleri, yedekten bir saat sonra.
  echo "$DAKIKA $(( (SAAT + 1) % 24 )) * * 0 /usr/local/bin/geri-yukle-sina.sh >> /proc/1/fd/1 2>&1"
} > /etc/crontabs/root

echo "yedek servisi hazır: her gün $YEDEK_SAATI (${TZ:-UTC}), saklama: ${YEDEK_GUNLUK:-7} gün / ${YEDEK_HAFTALIK:-4} hafta / ${YEDEK_AYLIK:-6} ay"
exec crond -f -l 8
