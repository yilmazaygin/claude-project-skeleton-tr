#!/bin/sh
# Postgres yedeği (yedekleme kuralı).
# 1. Projenin bütün veritabanları pg_dump -Fc ile alınır (postgres, testing ve şablonlar hariç).
# 2. Her döküm pg_restore --list ile okunarak doğrulanır; okunamayan döküm yedek sayılmaz.
# 3. Pazar günleri haftalık, ayın 1'inde aylık klasörüne de kopyalanır.
# 4. Saklama: her klasörde her veritabanının en yeni N dosyası kalır. Silinen yalnızca eski YEDEK
#    DOSYALARIDIR; veritabanına dokunulmaz.
# 5. denetim_kaydi tablosu varsa zincirin son halkası (çapa) capa/ altına yazılır.
# 6. RCLONE_HEDEF doluysa yedek klasörü uzak depoya kopyalanır (copy: uzakta silme yapılmaz).
set -eu
# cron işleri boş bir ortamla çalıştırır; PATH olmadan psql ve pg_dump bulunamaz (denendi).
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
[ -f /etc/yedek.env ] && . /etc/yedek.env
umask 077
: "${YEDEK_GUNLUK:=7}" "${YEDEK_HAFTALIK:=4}" "${YEDEK_AYLIK:=6}"
HEDEF=/yedekler
ZAMAN=$(date +%Y%m%d-%H%M%S)
mkdir -p "$HEDEF/gunluk" "$HEDEF/haftalik" "$HEDEF/aylik" "$HEDEF/capa"

VERITABANLARI=$(psql -d postgres -tAc "SELECT datname FROM pg_database WHERE NOT datistemplate AND datname NOT IN ('postgres', 'testing') ORDER BY datname")
[ -n "$VERITABANLARI" ] || { echo "HATA: yedeklenecek veritabanı bulunamadı"; exit 1; }

for vt in $VERITABANLARI; do
  dosya="$HEDEF/gunluk/${vt}-${ZAMAN}.dump"
  pg_dump -Fc -d "$vt" -f "$dosya.tmp"
  if ! pg_restore --list "$dosya.tmp" > /dev/null; then
    rm -f "$dosya.tmp"
    echo "HATA: $vt dökümü okunamadı"
    exit 1
  fi
  mv "$dosya.tmp" "$dosya"
  [ "$(date +%u)" = 7 ] && cp "$dosya" "$HEDEF/haftalik/"
  [ "$(date +%d)" = 01 ] && cp "$dosya" "$HEDEF/aylik/"
  echo "yedek: $dosya ($(du -h "$dosya" | cut -f1))"
done

if psql -d "$PGDATABASE" -tAc "SELECT to_regclass('public.denetim_kaydi') IS NOT NULL" | grep -q t; then
  psql -d "$PGDATABASE" -tAc "SELECT sira || ' ' || encode(hash, 'hex') FROM denetim_kaydi ORDER BY sira DESC LIMIT 1" > "$HEDEF/capa/denetim-kaydi-${ZAMAN}.txt"
  echo "çapa: $HEDEF/capa/denetim-kaydi-${ZAMAN}.txt"
fi

sakla() {
  klasor=$1; adet=$2
  for vt in $VERITABANLARI; do
    # Dosya adındaki zaman damgası sıralanabilir (YYYYMMDD-HHMMSS); en yeni N dosya kalır.
    ls -1 "$klasor" 2>/dev/null | grep -E "^${vt}-[0-9]{8}-[0-9]{6}\.dump$" | sort -r | tail -n +$((adet + 1)) | while read -r eski; do
      rm -f "$klasor/$eski"
      echo "saklama süresi doldu, silindi: $klasor/$eski"
    done
  done
}
sakla "$HEDEF/gunluk" "$YEDEK_GUNLUK"
sakla "$HEDEF/haftalik" "$YEDEK_HAFTALIK"
sakla "$HEDEF/aylik" "$YEDEK_AYLIK"

if [ -n "${RCLONE_HEDEF:-}" ]; then
  rclone copy "$HEDEF" "$RCLONE_HEDEF" --exclude '*.tmp'
  echo "uzak kopya: $RCLONE_HEDEF"
fi
echo "yedekleme tamam: $ZAMAN"
