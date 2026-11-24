#!/usr/bin/env python3
"""Projenin sağlık kontrolü: make doctor.

- .env ve .env.example aynı anahtarları aynı sırada taşıyor mu (değerler okunmaz, yalnızca adlar);
- .env.example değersiz mi;
- Docker çalışıyor mu;
- iki compose dosyası doğrulamadan geçiyor mu (canlı dosyanın zorunlu alanları geçici değerle);
- yerel portlar boş mu, ya da bu projenin konteynerinde mi.

İskeletin kendi yardımcısıdır; bilgisayardaki python3 ile çalışır (docker.md). Hiçbir dosyayı değiştirmez.
"""

import os
import re
import socket
import subprocess
import sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANAHTAR = re.compile(r"^([A-Z_][A-Z0-9_]*)=(.*)$")
hatalar, uyarilar = [], []


def oku(ad):
    with open(os.path.join(KOK, ad), encoding="utf-8") as f:
        return f.read()


def anahtarlar(metin):
    return [(m.group(1), m.group(2)) for m in map(ANAHTAR.match, metin.splitlines()) if m]


def tamam(mesaj):
    print(f"  tamam  {mesaj}")


def env_kontrol():
    if not os.path.exists(os.path.join(KOK, ".env.example")):
        hatalar.append(".env.example yok")
        return
    ornek = anahtarlar(oku(".env.example"))
    degerli = [k for k, v in ornek if v]
    if degerli:
        hatalar.append(f".env.example değer taşıyor: {', '.join(degerli)} (veri.md)")
    else:
        tamam(".env.example değersiz")
    if not os.path.exists(os.path.join(KOK, ".env")):
        uyarilar.append(".env yok (yığın kurulunca kur.py açar)")
        return
    a, b = [k for k, _ in ornek], [k for k, _ in anahtarlar(oku(".env"))]
    if a == b:
        tamam(f".env ve .env.example aynı {len(a)} anahtarı aynı sırada taşıyor")
        return
    eksik, fazla = [k for k in a if k not in b], [k for k in b if k not in a]
    if eksik:
        hatalar.append(f".env içinde eksik anahtar: {', '.join(eksik)}")
    if fazla:
        hatalar.append(f".env içinde .env.example'da olmayan anahtar: {', '.join(fazla)}")
    if not eksik and not fazla:
        hatalar.append(".env ile .env.example anahtarları aynı ama sıra farklı")


def calis(komut, ortam=None):
    return subprocess.run(komut, cwd=KOK, capture_output=True, text=True, env=ortam)


def docker_kontrol():
    try:
        r = calis(["docker", "info", "--format", "{{.ServerVersion}}"])
    except FileNotFoundError:
        hatalar.append("docker komutu yok")
        return False
    if r.returncode != 0:
        hatalar.append("Docker çalışmıyor (docker info başarısız)")
        return False
    tamam(f"Docker çalışıyor ({r.stdout.strip()})")
    return True


def compose_kontrol():
    if re.search(r"^services: \{\}\s*$", oku("compose.local.yaml"), re.M):
        uyarilar.append("compose dosyalarında servis yok (yığın henüz seçilmemiş); compose ve port kontrolü atlandı")
        return False
    r = calis(["docker", "compose", "-f", "compose.local.yaml", "config", "--quiet"])
    if r.returncode:
        hatalar.append(f"compose.local.yaml doğrulanamadı: {r.stderr.strip()}")
    else:
        tamam("compose.local.yaml geçerli")
    ortam, gecici = dict(os.environ), []
    for _ in range(10):
        r = calis(["docker", "compose", "-f", "compose.live.yaml", "config", "--quiet"], ortam)
        m = re.search(r'required variable (\w+) is missing', r.stderr)
        if r.returncode == 0 or not m:
            break
        ortam[m.group(1)] = "dogrulama.test"
        gecici.append(m.group(1))
    if r.returncode:
        hatalar.append(f"compose.live.yaml doğrulanamadı: {r.stderr.strip()}")
    else:
        ek = f" (geçici değerle: {', '.join(gecici)}; canlıda .env içinde dolu olmalı)" if gecici else ""
        tamam("compose.live.yaml geçerli" + ek)
    return True


def port_kontrol():
    compose = oku("compose.local.yaml")
    ad = re.search(r"^name:\s*(\S+)-local\s*$", compose, re.M)
    proje = ad.group(1) if ad else ""
    r = calis(["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}"])
    kendi = {}
    for satir in r.stdout.splitlines():
        isim, _, portlar = satir.partition("\t")
        for p in re.findall(r":(\d+)->", portlar):
            kendi[int(p)] = isim
    for p in sorted({int(x) for x in re.findall(r'"(\d+):\d+"', compose)}):
        s = socket.socket()
        try:
            s.bind(("0.0.0.0", p))
            tamam(f"port {p} boş")
        except OSError:
            sahip = kendi.get(p)
            if sahip and sahip.startswith(proje + "-"):
                tamam(f"port {p} bu projenin konteynerinde ({sahip})")
            else:
                hatalar.append(f"port {p} başka bir süreçte" + (f" ({sahip})" if sahip else ""))
        finally:
            s.close()


def main():
    print("make doctor")
    env_kontrol()
    if docker_kontrol() and compose_kontrol():
        port_kontrol()
    for u in uyarilar:
        print(f"  uyarı  {u}")
    for h in hatalar:
        print(f"  HATA   {h}")
    print("sonuç: " + ("sorun yok" if not hatalar else f"{len(hatalar)} sorun"))
    return 1 if hatalar else 0


if __name__ == "__main__":
    sys.exit(main())
