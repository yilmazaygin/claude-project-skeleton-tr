#!/usr/bin/env python3
"""Hazır yığın kurulum betiği. /yigin skill'i plan onaylandıktan sonra çalıştırır.

Kullanım (herhangi bir klasörden; proje kökü betiğin yerinden bulunur):
  python3 .claude/skills/yigin/kur.py yapilandir <hazir> <proje> <no> <ekler>
  python3 .claude/skills/yigin/kur.py kod
  python3 .claude/skills/yigin/kur.py env
  python3 .claude/skills/yigin/kur.py isle <şablon.tmpl> <proje> <no> <ekler>

  hazir: laravel-next veya fastapi-next
  ekler: virgülle ayrılmış seçili ekler, ör. "mailpit,queue,scheduler,e2e"; hiçbiri yoksa "".

yapilandir  Yalnızca dosya yazar, ağ gerektirmez: compose dosyaları, docker/, .dockerignore, Makefile,
            GitHub Actions dosyası, docs/proje/yigin.md, .env.example ve .env anahtarları, yerel .env
            değerleri. Seçilmeyen hazır yığının klasörünü siler.
kod         Docker ve ağ gerektirir: Laravel/Next.js projelerini konteynerde oluşturur, hazır dosyaları
            yerleştirir, paketleri kurar, konteynerleri açar, göçleri ve testleri çalıştırır.
            Onboarding'de (/basla) çalışmaz; ilk prompt'un ilk adımıdır (docs/proje/ilk-istem.md).
            Yarıda kalırsa yeniden çalıştırılır; biten adımlar atlanır.
env         .env yoksa .env.example'dan açar ve boş yerel değerleri üretir (CI bunu kullanır).
isle        Tek bir şablonu işleyip stdout'a yazar.

Şablon işaretleri:
- "# >>> ek:<ad>" ... "# <<< ek:<ad>": ek seçildiyse içerik kalır, seçilmediyse silinir.
- "# >>> ek-yok:<ad>" ... "# <<< ek-yok:<ad>": ek seçilmediyse içerik kalır, seçildiyse silinir.
- İşaret satırları her durumda silinir. __PROJE__ ve __NO__ doldurulur.

Gizli değerler: yerel .env için üretilen parola ve anahtarlar ekrana basılmaz; yalnızca doldurulan
anahtarların adı yazılır. Dolu bir değere dokunulmaz. Canlıya ait değerler boş kalır (veri.md).

Bu betik iskeletin kendi yardımcısıdır (hook'lar gibi bilgisayardaki python3 ile çalışır); projenin
araçları (composer, npm, artisan, alembic) her zaman Docker içinde çalışır.
"""

import base64
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys

SKILL = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(os.path.dirname(SKILL)))
HAZIR = os.path.join(SKILL, "hazir")
ORTAK = os.path.join(HAZIR, "_ortak")
YIGINLAR = ("laravel-next", "fastapi-next")
LOCAL = ["docker", "compose", "-f", "compose.local.yaml"]
ENV_BASLIK = "# Gerçek değerler bu dosyadadır. Git'e girmez. Anahtarlar .env.example ile aynı sırada durur.\n"

# Denenen sürümler (2026-11-23). Biri değişince HAZIR.md'deki sürüm notu da değişir.
LARAVEL_PAKETI = "laravel/laravel:^13.0"
CREATE_NEXT_APP = "create-next-app@16.4.6"
NPM_TEST = ["@types/node@24", "vitest@5.1.1", "@vitejs/plugin-react@6.3.0", "jsdom@31.0.1",
            "@testing-library/react@16.3.3", "@testing-library/dom@10.4.2"]
NPM_E2E = ["@playwright/test@1.65.1"]  # compose'daki playwright imajıyla birebir aynı


class Hata(Exception):
    pass


def yol(*p):
    return os.path.join(KOK, *p)


def oku(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def yaz(p, metin, kip=None):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(metin)
    if kip is not None:
        os.chmod(p, kip)


# --- şablon -----------------------------------------------------------------

def isle(metin, proje, no, secili):
    cikti, yigin = [], []
    for satir in metin.splitlines(keepends=True):
        m = re.match(r"\s*# (>>>|<<<) (ek|ek-yok):(\w+)\s*$", satir)
        if m:
            if m.group(1) == ">>>":
                yigin.append((m.group(2) == "ek") == (m.group(3) in secili))
            else:
                if not yigin:
                    raise Hata(f"açılmamış blok kapatılıyor: {satir.strip()}")
                yigin.pop()
            continue
        if all(yigin):
            cikti.append(satir.replace("__PROJE__", proje).replace("__NO__", no))
    if yigin:
        raise Hata("kapanmamış ek bloğu var")
    sonuc = "".join(cikti)
    if "__PROJE__" in sonuc or "__NO__" in sonuc:
        raise Hata("çıktıda doldurulmamış yer tutucu kaldı")
    return sonuc


def sablon_yaz(kaynak, hedef, proje, no, secili):
    yaz(hedef, isle(oku(kaynak), proje, no, secili))


def ek_listesi(hazir):
    m = re.search(r"^ekler:\s*(.*)$", oku(os.path.join(HAZIR, hazir, "HAZIR.md")), re.M)
    return {e.strip() for e in (m.group(1) if m else "").split(",") if e.strip()}


def dogrula_girdi(hazir, proje, no, ekler):
    if hazir not in YIGINLAR:
        raise Hata(f"hazır yığın {', '.join(YIGINLAR)} olmalı")
    if not os.path.isdir(os.path.join(HAZIR, hazir)):
        raise Hata(f"{hazir} klasörü yok (seçilmeyen yığın daha önce silinmiş olabilir)")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", proje):
        raise Hata("proje adı küçük harf, rakam ve tire olmalı")
    if not re.fullmatch(r"\d{2}", no) or no == "00":
        raise Hata("proje numarası iki hane olmalı (01-99)")
    bilinmeyen = ekler - ek_listesi(hazir)
    if bilinmeyen:
        raise Hata(f"bilinmeyen ek: {', '.join(sorted(bilinmeyen))}")


# --- ortam dosyaları ----------------------------------------------------------

ANAHTAR = re.compile(r"^([A-Z_][A-Z0-9_]*)=(.*)$")


def anahtarlar(metin):
    return [m.group(1) for m in map(ANAHTAR.match, metin.splitlines()) if m]


def anahtar_ekle(hazir):
    """Yığının anahtarlarını .env.example ve .env dosyalarının sonuna aynı sırayla ekler."""
    kaynak = oku(os.path.join(HAZIR, hazir, "env.example"))
    for satir in kaynak.splitlines():
        m = ANAHTAR.match(satir.strip())
        if m and m.group(2):
            raise Hata(f"{hazir}/env.example içinde değerli satır var: {m.group(1)}")
    yeni = anahtarlar(kaynak) + ["HOST_UID", "HOST_GID"]

    ornek_yol = yol(".env.example")
    ornek = oku(ornek_yol) if os.path.exists(ornek_yol) else ""
    eksik = [k for k in yeni if k not in anahtarlar(ornek)]
    if eksik:
        ek = f"\n# {hazir}. HOST_UID ve HOST_GID: bilgisayardaki kullanıcının kimliği (dosya izinleri için).\n"
        ek += "".join(f"{k}=\n" for k in eksik)
        ornek = ornek.rstrip("\n") + "\n" + ek
        yaz(ornek_yol, ornek)

    env_yol = yol(".env")
    if not os.path.exists(env_yol):
        govde = [s for s in ornek.splitlines(keepends=True)]
        while govde and (govde[0].startswith("#") or not govde[0].strip()):
            govde.pop(0)  # örnek dosyanın başlık yorumları yerine tek satırlık başlık
        yaz(env_yol, ENV_BASLIK + "\n" + "".join(govde), 0o600)
    else:
        env = oku(env_yol)
        var = anahtarlar(env)
        eksik_env = [k for k in anahtarlar(ornek) if k not in var]
        if eksik_env:
            yaz(env_yol, env.rstrip("\n") + "\n" + "".join(f"{k}=\n" for k in eksik_env))


def yerel_degerler(hazir, proje, no):
    db = proje.replace("-", "_")
    d = {
        "APP_NAME": proje,
        "APP_ENV": "local",
        "DB_DATABASE": db,
        "DB_USERNAME": db,
        "DB_PASSWORD": secrets.token_hex(24),
        "HOST_UID": str(os.getuid()),
        "HOST_GID": str(os.getgid()),
    }
    if hazir == "laravel-next":
        d.update({
            "APP_KEY": "base64:" + base64.b64encode(secrets.token_bytes(32)).decode(),
            "APP_DEBUG": "true",
            "APP_URL": f"http://app.localhost:80{no}",
        })
    else:
        d["SECRET_KEY"] = secrets.token_hex(32)
    return d


def env_doldur(hazir, proje, no):
    """.env içindeki boş anahtarlardan yerel değeri bilinenleri doldurur. Dolu değere dokunmaz."""
    env_yol = yol(".env")
    degerler = yerel_degerler(hazir, proje, no)
    doldurulan, satirlar = [], []
    for satir in oku(env_yol).splitlines(keepends=True):
        m = ANAHTAR.match(satir.rstrip("\n"))
        if m and m.group(2) == "" and m.group(1) in degerler:
            satir = f"{m.group(1)}={degerler[m.group(1)]}\n"
            doldurulan.append(m.group(1))
        satirlar.append(satir)
    yaz(env_yol, "".join(satirlar), 0o600)
    print(f".env: yerel değer yazılan anahtarlar: {', '.join(doldurulan) or 'yok (hepsi zaten dolu)'}")
    print(".env: canlıya ait anahtarlar (APP_DOMAIN, API_DOMAIN) boş bırakıldı.")


def projeyi_oku():
    """Kurulu projenin yığınını, adını, numarasını ve eklerini dosyalardan okur."""
    if not os.path.exists(yol("compose.local.yaml")):
        raise Hata("compose.local.yaml yok")
    compose = oku(yol("compose.local.yaml"))
    ad = re.search(r"^name:\s*(\S+)-local\s*$", compose, re.M)
    no = re.search(r'"80(\d\d):80"', compose)
    if not ad or not no:
        raise Hata("compose.local.yaml içinde proje adı veya Traefik portu bulunamadı; yığın kurulmamış olabilir")
    if os.path.exists(yol("docker", "php", "Dockerfile")):
        hazir = "laravel-next"
    elif os.path.exists(yol("docker", "python", "Dockerfile")):
        hazir = "fastapi-next"
    else:
        raise Hata("docker/php veya docker/python bulunamadı; hazır yığın kurulmamış")
    servis = lambda s: re.search(rf"^  {s}:\s*$", compose, re.M) is not None
    ekler = set()
    if servis("mailpit"):
        ekler.add("mailpit")
    if servis("horizon") or servis("worker"):
        ekler.add("queue")
    if servis("scheduler") or servis("beat"):
        ekler.add("scheduler")
    if servis("e2e"):
        ekler.add("e2e")
    return hazir, ad.group(1), no.group(1), ekler


# --- yapilandir ---------------------------------------------------------------

def port_bos(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("0.0.0.0", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def iskelet_degil():
    """iskelet.json içinde tur "proje" değilse durur: iskeletin kendisinde kurulum yapılmaz."""
    ayar = yol(".claude", "iskelet.json")
    tur = json.loads(oku(ayar)).get("tur", "iskelet") if os.path.exists(ayar) else "iskelet"
    if tur != "proje":
        raise Hata("Bu depo henüz iskelet (.claude/iskelet.json: tur iskelet). Önce /basla ile projeyi "
                   "başlatın; /basla projeyi tanır ve yığını kurar.")


def yapilandir(hazir, proje, no, ekler_metni):
    secili = set(filter(None, ekler_metni.split(",")))
    dogrula_girdi(hazir, proje, no, secili)
    iskelet_degil()
    if not re.search(r"^services: \{\}\s*$", oku(yol("compose.local.yaml")), re.M):
        raise Hata("compose.local.yaml boş değil (services dolu). Yığın zaten kurulmuş olabilir; /yigin "
                   "\"yığını değiştir\" yolunu kullanın.")
    for d in ("backend", "frontend"):
        if os.path.exists(yol(d)):
            raise Hata(f"{d}/ klasörü zaten var")
    dolu = [p for p in (int(f"80{no}"), int(f"54{no}"), int(f"63{no}")) if not port_bos(p)]
    if dolu:
        raise Hata(f"bu portlar kullanımda: {', '.join(map(str, dolu))}. Başka bir proje numarası seçin "
                   "ya da o portu kullanan konteyneri kapatın.")

    h = os.path.join(HAZIR, hazir)
    for ad in ("compose.local.yaml", "compose.live.yaml"):
        sablon_yaz(os.path.join(h, ad + ".tmpl"), yol(ad), proje, no, secili)
    shutil.copytree(os.path.join(h, "docker"), yol("docker"), dirs_exist_ok=True)
    shutil.copytree(os.path.join(ORTAK, "docker"), yol("docker"), dirs_exist_ok=True)
    shutil.copyfile(os.path.join(ORTAK, "dockerignore"), yol(".dockerignore"))
    if hazir == "fastapi-next":
        shutil.copytree(os.path.join(h, "backend-baslangic"), yol("backend"))
        if "queue" not in secili:
            for f in ("app/worker.py", "app/tasks.py"):
                os.remove(yol("backend", f))
            req = yol("backend", "requirements.txt")
            yaz(req, "".join(s for s in oku(req).splitlines(keepends=True)
                             if not re.match(r"(celery|flower)\b", s)))
    sablon_yaz(os.path.join(h, "Makefile.tmpl"), yol("Makefile"), proje, no, secili)
    os.makedirs(yol(".github", "workflows"), exist_ok=True)
    shutil.copyfile(os.path.join(ORTAK, "github", "test.yml"), yol(".github", "workflows", "test.yml"))
    sablon_yaz(os.path.join(h, "yigin.md.tmpl"), yol("docs", "proje", "yigin.md"), proje, no, secili)
    if not secili:
        yaz(yol("docs", "proje", "yigin.md"), oku(yol("docs", "proje", "yigin.md")).replace("- Ekler:\n", "- Ekler: yok\n"))
    anahtar_ekle(hazir)
    env_doldur(hazir, proje, no)

    for diger in YIGINLAR:
        if diger != hazir and os.path.isdir(os.path.join(HAZIR, diger)):
            shutil.rmtree(os.path.join(HAZIR, diger))
            print(f"kullanılmayan hazır yığın silindi: .claude/skills/yigin/hazir/{diger}")
    print(f"yapılandırma tamam: {hazir}, proje {proje}, numara {no}, ekler: {', '.join(sorted(secili)) or 'yok'}")
    print("Kod bu adımda oluşmaz. İlk prompt'un ilk adımı (docs/proje/ilk-istem.md): "
          "python3 .claude/skills/yigin/kur.py kod")


# --- kod ----------------------------------------------------------------------

def calistir(komut, **kw):
    print("$ " + " ".join(komut), flush=True)
    r = subprocess.run(komut, cwd=KOK, **kw)
    if r.returncode != 0:
        raise Hata(f"komut başarısız (çıkış {r.returncode}): {' '.join(komut)}\n"
                   "Sorun giderilince `python3 .claude/skills/yigin/kur.py kod` yeniden çalıştırılır; "
                   "biten adımlar atlanır.")


def adim(ad, yapildi, yap):
    if yapildi():
        print(f"✓ {ad} (zaten yapılmış)")
        return
    print(f"→ {ad}", flush=True)
    yap()


def yama(dosya, aranan, yeni, ad, regex=False, adet=1):
    """aranan metni yeni ile değiştirir. Bulamazsa durur; tahminle yazmaz."""
    p = yol(dosya)
    metin = oku(p)
    bulunan = len(re.findall(aranan, metin, re.S)) if regex else metin.count(aranan)
    if bulunan != adet:
        raise Hata(f"{ad}: {dosya} içinde beklenen bağlam bulunamadı ({bulunan} eşleşme, {adet} bekleniyordu).\n"
                   f"Aranan: {aranan!r}\nDosya elle düzenlenir, sonra `kur.py kod` yeniden çalıştırılır.")
    metin = re.sub(aranan, lambda _: yeni, metin, count=adet, flags=re.S) if regex \
        else metin.replace(aranan, yeni, adet)
    yaz(p, metin)


def kopyala_agac(kaynak, hedef, haric=()):
    for kok, _, dosyalar in os.walk(kaynak):
        for ad in dosyalar:
            k = os.path.join(kok, ad)
            goreli = os.path.relpath(k, kaynak)
            if any(goreli.startswith(h) for h in haric):
                continue
            os.makedirs(os.path.dirname(os.path.join(hedef, goreli)), exist_ok=True)
            shutil.copyfile(k, os.path.join(hedef, goreli))


def docker_run(imaj, *komut, ortam=()):
    k = ["docker", "run", "--rm", "-u", f"{os.getuid()}:{os.getgid()}", "-v", f"{KOK}:/app", "-w", "/app"]
    for e in ortam:
        k += ["-e", e]
    calistir(k + [imaj, *komut])


def dizi_degistir(metin, anahtar, yeni_blok, dosya):
    """PHP dizisinde 'anahtar' => [ ... ], girdisini köşeli parantezleri sayarak yeni_blok ile değiştirir."""
    m = re.search(rf"^([ \t]*)'{anahtar}' => \[", metin, re.M)
    if not m:
        raise Hata(f"{dosya} içinde '{anahtar}' => [ bulunamadı")
    i, derinlik = m.end() - 1, 0
    while i < len(metin):
        if metin[i] == "[":
            derinlik += 1
        elif metin[i] == "]":
            derinlik -= 1
            if derinlik == 0:
                break
        i += 1
    son = i + 1
    if metin[son:son + 1] == ",":
        son += 1
    girinti = m.group(1)
    blok = "\n".join((girinti + s) if s else s for s in yeni_blok.strip("\n").splitlines())
    return metin[:m.start()] + blok + metin[son:]


def horizon_bloklari():
    kaynak = oku(os.path.join(HAZIR, "laravel-next", "backend-horizon", "horizon-defaults.php"))
    bloklar = {}
    for anahtar in ("defaults", "environments"):
        m = re.search(rf"^'{anahtar}' => \[.*?^\],", kaynak, re.M | re.S)
        bloklar[anahtar] = m.group(0)
    return bloklar


def frontend_adimlari(hazir, ekler):
    adim("Next.js projesi oluşturulur", lambda: os.path.exists(yol("frontend", "package.json")),
         lambda: docker_run("node:24-alpine", "npx", "--yes", CREATE_NEXT_APP, "frontend", "--ts", "--tailwind",
                            "--eslint", "--app", "--src-dir", "--import-alias", "@/*", "--use-npm", "--yes",
                            "--skip-install", "--disable-git", ortam=["HOME=/tmp"]))
    # Docker, hacim bağlama noktalarını yoksa root sahibi olarak açar; önceden kullanıcı adına açılır.
    for d in ("node_modules", ".next"):
        os.makedirs(yol("frontend", d), exist_ok=True)

    def dosyalar():
        haric = ("app/sanctum",) if hazir == "fastapi-next" else ()
        kopyala_agac(os.path.join(ORTAK, "frontend-proxy", "src"), yol("frontend", "src"), haric)
        kopyala_agac(os.path.join(ORTAK, "frontend-test"), yol("frontend"))
        if "e2e" in ekler:
            kopyala_agac(os.path.join(ORTAK, "frontend-e2e"), yol("frontend"))
    adim("Proxy ve test dosyaları frontend/ altına kopyalanır", lambda: False, dosyalar)

    adim("next.config.ts: output standalone",
         lambda: 'output: "standalone"' in oku(yol("frontend", "next.config.ts")),
         lambda: yama("frontend/next.config.ts", "const nextConfig: NextConfig = {",
                      'const nextConfig: NextConfig = {\n  output: "standalone",', "next.config"))

    paketler = NPM_TEST + (NPM_E2E if "e2e" in ekler else [])
    adim("Frontend test paketleri kurulur",
         lambda: all(p.rsplit("@", 1)[0] in oku(yol("frontend", "package.json")) for p in paketler),
         lambda: calistir(LOCAL + ["run", "--rm", "--no-deps", "frontend", "npm", "install", "--no-audit",
                                   "--no-fund", "--save-dev", *paketler]))


def kod_laravel(ekler):
    adim("Laravel projesi oluşturulur", lambda: os.path.exists(yol("backend", "artisan")),
         lambda: docker_run("composer:2", "create-project", "--no-interaction", LARAVEL_PAKETI, "backend",
                            ortam=["COMPOSER_HOME=/tmp/composer"]))

    def ajan_belgeleri():
        for f in ("CLAUDE.md", "AGENTS.md"):
            if os.path.exists(yol("backend", f)):
                os.remove(yol("backend", f))
    adim("Laravel'in ajan belgeleri silinir (iskeletle çelişir; HAZIR.md → Bilinen sınırlar)",
         lambda: not any(os.path.exists(yol("backend", f)) for f in ("CLAUDE.md", "AGENTS.md")), ajan_belgeleri)

    hb = os.path.join(HAZIR, "laravel-next", "backend-test")
    adim("phpunit.xml: test yalıtımı", lambda: 'value="testing" force="true"' in oku(yol("backend", "phpunit.xml")),
         lambda: yama("backend/phpunit.xml", r"[ \t]*<php>.*?</php>",
                      oku(os.path.join(hb, "phpunit-php-blogu.xml")).rstrip("\n"), "phpunit.xml", regex=True))
    adim("Test koruması ve izolasyon testi kopyalanır", lambda: False,
         lambda: kopyala_agac(os.path.join(hb, "tests"), yol("backend", "tests")))

    adim("bootstrap/app.php: trustProxies ve statefulApi",
         lambda: "trustProxies" in oku(yol("backend", "bootstrap", "app.php")),
         lambda: yama("backend/bootstrap/app.php",
                      r"->withMiddleware\(function \(Middleware \$middleware\): void \{\s*//\s*\}\)",
                      "->withMiddleware(function (Middleware $middleware): void {\n"
                      "        // Yalnızca Docker iç ağlarındaki vekillere güvenilir; '*' kullanılmaz (HAZIR.md).\n"
                      "        $middleware->trustProxies(at: ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '127.0.0.1']);\n"
                      "        $middleware->statefulApi();\n"
                      "    })", "bootstrap/app.php", regex=True))

    frontend_adimlari("laravel-next", ekler)

    adim("Konteynerler açılır", lambda: False, lambda: calistir(LOCAL + ["up", "-d", "--build"]))

    adim("Sanctum kurulur (install:api)", lambda: os.path.exists(yol("backend", "routes", "api.php")),
         lambda: calistir(LOCAL + ["exec", "-T", "backend", "php", "artisan", "install:api", "--no-interaction"]))

    def has_api_tokens():
        yama("backend/app/Models/User.php", "use HasFactory, Notifiable;", "use HasApiTokens, HasFactory, Notifiable;",
             "User modeli")
        yama("backend/app/Models/User.php", "namespace App\\Models;\n\n",
             "namespace App\\Models;\n\nuse Laravel\\Sanctum\\HasApiTokens;\n", "User modeli")
    adim("User modeline HasApiTokens eklenir",
         lambda: "HasApiTokens" in oku(yol("backend", "app", "Models", "User.php")), has_api_tokens)

    if "queue" in ekler:
        adim("Horizon paketi kurulur", lambda: "laravel/horizon" in oku(yol("backend", "composer.json")),
             lambda: calistir(LOCAL + ["exec", "-T", "backend", "composer", "require", "--no-interaction",
                                       "laravel/horizon"]))
        adim("horizon:install", lambda: os.path.exists(yol("backend", "config", "horizon.php")),
             lambda: calistir(LOCAL + ["exec", "-T", "backend", "php", "artisan", "horizon:install"]))

        def horizon_ayari():
            p = yol("backend", "config", "horizon.php")
            metin = oku(p)
            for anahtar, blok in horizon_bloklari().items():
                metin = dizi_degistir(metin, anahtar, blok, "backend/config/horizon.php")
            yaz(p, metin)
        adim("config/horizon.php: iki supervisor (kısa ve uzun işler)",
             lambda: "supervisor-long" in oku(yol("backend", "config", "horizon.php")), horizon_ayari)

        if "scheduler" in ekler:
            def snapshot():
                p = "backend/routes/console.php"
                if "Facades\\Schedule;" not in oku(yol(p)):
                    yama(p, "use Illuminate\\Support\\Facades\\Artisan;\n",
                         "use Illuminate\\Support\\Facades\\Artisan;\nuse Illuminate\\Support\\Facades\\Schedule;\n",
                         "routes/console.php")
                yaz(yol(p), oku(yol(p)).rstrip("\n") +
                    "\n\n// Horizon panelinin grafikleri için.\nSchedule::command('horizon:snapshot')->everyFiveMinutes();\n")
            adim("horizon:snapshot zamanlanır", lambda: "horizon:snapshot" in oku(yol("backend", "routes", "console.php")),
                 snapshot)
        adim("Horizon yeniden başlatılır", lambda: False,
             lambda: (calistir(LOCAL + ["up", "-d"]), calistir(LOCAL + ["restart", "horizon"])))

    adim("Kod biçimi (pint)", lambda: False,
         lambda: calistir(LOCAL + ["exec", "-T", "backend", "./vendor/bin/pint", "--quiet"]))


def kod_fastapi(ekler):
    frontend_adimlari("fastapi-next", ekler)
    adim("Konteynerler açılır", lambda: False, lambda: calistir(LOCAL + ["up", "-d", "--build"]))
    surumler = yol("backend", "alembic", "versions")
    adim("İlk Alembic göçü oluşturulur", lambda: any(f.endswith(".py") for f in os.listdir(surumler)),
         lambda: calistir(LOCAL + ["exec", "-T", "backend", "alembic", "revision", "--autogenerate", "-m",
                                   "baslangic"]))


def adresler(hazir, no, ekler):
    print("\nAdresler:")
    print(f"  arayüz:          http://app.localhost:80{no}")
    if hazir == "laravel-next":
        print(f"  API:             http://api.localhost:80{no}")
        if "queue" in ekler:
            print(f"  Horizon:         http://api.localhost:80{no}/horizon")
    else:
        print(f"  API sağlık:      http://api.localhost:80{no}/api/v1/health")
        print(f"  API belgeleri:   http://api.localhost:80{no}/api/docs")
        if "queue" in ekler:
            print(f"  Flower:          http://flower.localhost:80{no}")
    if "mailpit" in ekler:
        print(f"  Mailpit:         http://mail.localhost:80{no}")
    print(f"  Traefik paneli:  http://traefik.localhost:80{no}")
    print(f"  Postgres:        localhost:54{no}   Redis: localhost:63{no}")


def kod():
    iskelet_degil()
    hazir, proje, no, ekler = projeyi_oku()
    print(f"kod: {hazir}, proje {proje}, ekler: {', '.join(sorted(ekler)) or 'yok'}")
    if hazir == "laravel-next":
        kod_laravel(ekler)
    else:
        kod_fastapi(ekler)
    adim("Göçler çalışır (make migrate)", lambda: False, lambda: calistir(["make", "migrate"]))
    adim("Testler çalışır (make test)", lambda: False, lambda: calistir(["make", "test"]))
    adim("Lint (make lint)", lambda: False, lambda: calistir(["make", "lint"]))
    print("\nKurulum tamam.")
    adresler(hazir, no, ekler)


def env():
    hazir, proje, no, _ = projeyi_oku()
    if not os.path.exists(yol(".env")):
        ornek = oku(yol(".env.example"))
        govde = ornek.splitlines(keepends=True)
        while govde and (govde[0].startswith("#") or not govde[0].strip()):
            govde.pop(0)
        yaz(yol(".env"), ENV_BASLIK + "\n" + "".join(govde), 0o600)
    env_doldur(hazir, proje, no)


def main(argv):
    if len(argv) >= 1 and argv[0] == "yapilandir" and len(argv) == 5:
        yapilandir(*argv[1:])
    elif argv == ["kod"]:
        kod()
    elif argv == ["env"]:
        env()
    elif len(argv) == 5 and argv[0] == "isle":
        sys.stdout.write(isle(oku(argv[1]), argv[2], argv[3], set(filter(None, argv[4].split(",")))))
    else:
        print(__doc__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Hata as e:
        print(f"HATA: {e}", file=sys.stderr)
        sys.exit(1)
