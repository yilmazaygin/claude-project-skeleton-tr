"""Güvenlik kaydı: giriş denemeleri, çıkış, parola işlemleri (çerez-ve-izleme kuralı).

Giriş ve parola uç noktaları her olayda `kaydet(...)` çağırır:

    await guvenlik.kaydet(session, "giris.basarisiz", request, denenen_kimlik=form.email)
    await guvenlik.kaydet(session, "giris.basarili", request, kullanici_id=user.id)

Olaylar: giris.basarili, giris.basarisiz, giris.kilitlendi, cikis,
parola.sifirlama_istendi, parola.degisti.

Konum için DB-IP Lite kullanılır (CC BY 4.0, https://db-ip.com); dosya
`python -m app.geoip_indir` ile data/geoip/ altına indirilir. Dosya yoksa konum boş kalır.
"""

import ipaddress
import re
from pathlib import Path

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

GEOIP_DOSYASI = Path(__file__).resolve().parents[1] / "data" / "geoip" / "dbip-city-lite.mmdb"

_BOT = re.compile(r"bot|spider|crawl|slurp|curl|wget|python-requests|httpclient|go-http|postman", re.I)
_ISLETIM_SISTEMI = [
    (re.compile(r"Windows NT", re.I), "Windows"),
    (re.compile(r"iPhone|iPad|iPod", re.I), "iOS"),
    (re.compile(r"Android", re.I), "Android"),
    (re.compile(r"CrOS", re.I), "ChromeOS"),
    (re.compile(r"Mac OS X|Macintosh", re.I), "macOS"),
    (re.compile(r"Linux", re.I), "Linux"),
]
_TARAYICI = [
    (_BOT, "bot/araç"),
    (re.compile(r"Edg(e|A|iOS)?/"), "Edge"),
    (re.compile(r"OPR/|Opera"), "Opera"),
    (re.compile(r"SamsungBrowser"), "Samsung Internet"),
    (re.compile(r"Firefox/|FxiOS"), "Firefox"),
    (re.compile(r"Chrome/|CriOS"), "Chrome"),
    (re.compile(r"Safari/"), "Safari"),
]

_okuyucu = None
_okuyucu_denendi = False


def _ozel_mi(ip: str) -> bool:
    try:
        adres = ipaddress.ip_address(ip)
    except ValueError:
        return True
    return adres.is_private or adres.is_loopback or adres.is_reserved or adres.is_link_local


def istemci_ip(request: Request) -> str | None:
    """Ziyaretçinin gerçek IP'si.

    X-Forwarded-For sağdan sola okunur; özel ağdaki (Docker, NPM, Traefik) adresler atlanır,
    ilk genel adres ziyaretçidir. En soldaki değer alınmaz: onu ziyaretçi kendisi uydurabilir.
    Genel adres yoksa (yerel geliştirme) bağlantının kendi adresi döner.
    """
    zincir = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
    for ip in reversed(zincir):
        if not _ozel_mi(ip):
            return ip
    if zincir:
        return zincir[-1]
    return request.client.host if request.client else None


def user_agent_coz(ua: str | None) -> dict[str, str | None]:
    ua = ua or ""
    isletim_sistemi = next((ad for kalip, ad in _ISLETIM_SISTEMI if ua and kalip.search(ua)), None)
    tarayici = next((ad for kalip, ad in _TARAYICI if ua and kalip.search(ua)), None)
    if _BOT.search(ua):
        cihaz = "bot"
    elif re.search(r"iPad|Tablet", ua, re.I):
        cihaz = "tablet"
    elif re.search(r"Mobi|iPhone|Android", ua, re.I):
        cihaz = "mobil"
    else:
        cihaz = "masaustu"
    return {"isletim_sistemi": isletim_sistemi, "tarayici": tarayici, "cihaz": cihaz}


def maskele(kimlik: str | None) -> str | None:
    """ayse@ornek.com → a***@ornek.com"""
    if not kimlik:
        return None
    if "@" in kimlik:
        ad, alan = kimlik.split("@", 1)
        return f"{ad[:1]}***@{alan}"
    return f"{kimlik[:1]}***"


def konum(ip: str | None) -> tuple[str | None, str | None]:
    global _okuyucu, _okuyucu_denendi
    if not ip or _ozel_mi(ip):
        return None, None
    if not _okuyucu_denendi:
        _okuyucu_denendi = True
        if GEOIP_DOSYASI.is_file():
            import maxminddb

            _okuyucu = maxminddb.open_database(str(GEOIP_DOSYASI))
    if _okuyucu is None:
        return None, None
    kayit = _okuyucu.get(ip) or {}
    ulke = (kayit.get("country") or {}).get("iso_code")
    sehir = ((kayit.get("city") or {}).get("names") or {}).get("en")
    return ulke, sehir


async def kaydet(
    session: AsyncSession,
    olay: str,
    request: Request,
    kullanici_id: str | int | None = None,
    denenen_kimlik: str | None = None,
) -> None:
    """Bir güvenlik olayını yazar ve işlemi onaylar (commit)."""
    ip = istemci_ip(request)
    ulke, sehir = konum(ip)
    ua = request.headers.get("user-agent")
    cihaz = user_agent_coz(ua)
    await session.execute(
        text(
            "INSERT INTO guvenlik_kaydi (olay, kullanici_id, denenen_kimlik, ip, ulke, sehir,"
            " user_agent, isletim_sistemi, tarayici, cihaz)"
            " VALUES (:olay, :kullanici_id, :denenen_kimlik, CAST(:ip AS inet), :ulke, :sehir,"
            " :user_agent, :isletim_sistemi, :tarayici, :cihaz)"
        ),
        {
            "olay": olay,
            "kullanici_id": None if kullanici_id is None else str(kullanici_id),
            "denenen_kimlik": maskele(denenen_kimlik),
            "ip": ip,
            "ulke": ulke,
            "sehir": sehir,
            "user_agent": ua[:512] if ua else None,
            **cihaz,
        },
    )
    await session.commit()
