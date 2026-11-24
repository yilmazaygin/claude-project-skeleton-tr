"""Hook'ların ortak ayarı: hangi koruma açık?

Ayar .claude/iskelet.json içindeki "korumalar" alanındadır:
  git           Git salt okunur (git.md)
  ssh           SSH, scp, sftp yasak (docker.md)
  docker-hacim  hacim ve veri silen Docker komutları yasak (veri.md)
  defter        docs/kayitlar ve .claude/iskelet-gecmisi yalnızca alta eklenir (kayitlar.md)
  env-ornek     .env.example yalnızca değersiz anahtar taşır (veri.md)

Dosya yoksa veya koruma yazılmamışsa koruma AÇIK sayılır. Dosya okunamazsa (bozuk JSON) hata
yükselir; settings.json'daki sarmalayıcı bu durumda işlemi engeller. Koruma yalnızca /basla sırasında veya
kullanıcı açıkça isteyince kapanır. "tur" alanı iskelet mi proje mi olduğunu söyler (iskelet_mi).
"""
import json
import os

PROJECT_DIR = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
AYAR = os.path.join(PROJECT_DIR, ".claude", "iskelet.json")
# Bash ile yazılamayan ayar dosyaları; değişiklikleri Edit/Write ile ve kullanıcı onayıyla yapılır.
KORUNAN_AYARLAR = (AYAR, os.path.join(PROJECT_DIR, ".claude", "settings.json"))

_ayar = None


def _oku():
    global _ayar
    if _ayar is None:
        if os.path.exists(AYAR):
            with open(AYAR, encoding="utf-8") as f:
                _ayar = json.load(f)
        else:
            _ayar = {}
    return _ayar


def acik(ad):
    return (_oku().get("korumalar") or {}).get(ad, True) is not False


def iskelet_mi():
    """tur alanı: "iskelet" (bu deponun kendisi) veya "proje" (/basla ile başlatılmış proje).
    Yoksa iskelet sayılır; iskeletin geçmiş defterleri korunur."""
    return _oku().get("tur", "iskelet") != "proje"


_oku()  # hook başlarken okunur: bozuk ayar her komutta hata verir, işlem engellenir (fail-closed)
