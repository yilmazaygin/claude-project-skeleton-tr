"""DB-IP Lite şehir veritabanını indirir (CC BY 4.0, https://db-ip.com).

Kullanım (backend konteynerinde): python -m app.geoip_indir
Dosya her ay yenilenir. Scheduler eki varsa app/worker.py içindeki beat_schedule'a eklenir:
    "geoip-indir": {"task": "app.geoip_indir.gorev", "schedule": crontab(day_of_month="3", hour="4", minute="0")}
Dosya bellekte açılmaz; diske indirilip akış halinde açılır (yaklaşık 130 MB).
"""

import gzip
import shutil
import sys
import urllib.request
from datetime import date
from pathlib import Path

from app.guvenlik import GEOIP_DOSYASI


def _aylar() -> list[str]:
    bugun = date.today()
    gecen = date(bugun.year - 1, 12, 1) if bugun.month == 1 else date(bugun.year, bugun.month - 1, 1)
    return [bugun.strftime("%Y-%m"), gecen.strftime("%Y-%m")]


def indir() -> Path:
    GEOIP_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    gz = GEOIP_DOSYASI.with_suffix(".mmdb.gz.tmp")
    gecici = GEOIP_DOSYASI.with_suffix(".mmdb.tmp")
    # Ayın dosyası ilk günlerde henüz yayımlanmamış olabilir; önce bu ay, sonra geçen ay denenir.
    for ay in _aylar():
        url = f"https://download.db-ip.com/free/dbip-city-lite-{ay}.mmdb.gz"
        try:
            with urllib.request.urlopen(url, timeout=300) as yanit, open(gz, "wb") as dosya:
                shutil.copyfileobj(yanit, dosya)
        except OSError:
            continue
        with gzip.open(gz, "rb") as kaynak, open(gecici, "wb") as hedef:
            shutil.copyfileobj(kaynak, hedef)
        gecici.replace(GEOIP_DOSYASI)
        gz.unlink(missing_ok=True)
        print(f"İndirildi: {url} → {GEOIP_DOSYASI} ({GEOIP_DOSYASI.stat().st_size // 1048576} MB)")
        return GEOIP_DOSYASI
    gz.unlink(missing_ok=True)
    raise SystemExit("DB-IP Lite indirilemedi.")


try:  # queue eki varsa Celery görevi olarak da çağrılabilir
    from app.worker import celery_app

    @celery_app.task(name="app.geoip_indir.gorev")
    def gorev() -> str:
        return str(indir())
except ImportError:
    pass


if __name__ == "__main__":
    indir()
    sys.exit(0)
