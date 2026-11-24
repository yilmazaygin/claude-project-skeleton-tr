#!/usr/bin/env python3
"""PreToolUse hook (Bash): proje kurallarını komutun tamamına bakarak zorlar.

Reddedilen komut için nedeni stderr'e yazar ve 2 ile çıkar. Claude nedeni görür.
Kurallar: .claude/rules/git.md, veri.md, docker.md, kayitlar.md
Hangi korumanın açık olduğu .claude/iskelet.json dosyasından okunur (korumalar.py).
"""
import json
import os
import re
import shlex
import sys

sys.dont_write_bytecode = True  # korumalar.py içe aktarılınca __pycache__ oluşmasın
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from korumalar import KORUNAN_AYARLAR, acik, iskelet_mi  # noqa: E402

GIT_ALLOWED = {"status", "log", "diff", "show"}
GIT_OPTS_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
SSH_TOOLS = {"ssh", "scp", "sftp", "ssh-copy-id", "ssh-keygen"}
SHELLS = {"bash", "sh", "zsh", "dash"}
PREFIXES = {"sudo", "env", "command", "exec", "nohup", "time", "nice", "xargs", "builtin", "stdbuf", "timeout"}
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "|&", ";;"}
HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

SCRIPT_MAX_BYTES = 256 * 1024

PROJECT_DIR = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
RECORDS_DIR = os.path.join(PROJECT_DIR, "docs", "kayitlar")
ISKELET_GECMISI = os.path.join(PROJECT_DIR, ".claude", "iskelet-gecmisi")  # iskeletin kendi defterleri


class Deny(Exception):
    pass


def resolve(path, cwd):
    return os.path.normpath(os.path.join(cwd, os.path.expanduser(path)))


def is_records(path, cwd):
    if not acik("defter"):
        return False
    full = os.path.realpath(resolve(path, cwd))
    # İskeletin geçmiş defterleri yalnızca iskeletin kendisinde korunur; projede /basla siler.
    dizinler = (RECORDS_DIR, ISKELET_GECMISI) if iskelet_mi() else (RECORDS_DIR,)
    return any(full == d or full.startswith(d + os.sep) for d in dizinler)


def read_script(path, cwd):
    """Çalıştırılan script dosyasının metnini döndürür; okunamazsa None."""
    full = resolve(path, cwd)
    try:
        if not os.path.isfile(full) or os.path.getsize(full) > SCRIPT_MAX_BYTES:
            return None
        with open(full, "rb") as f:
            raw = f.read()
    except OSError:
        return None
    if b"\0" in raw:
        return None  # ikili dosya
    return raw.decode("utf-8", errors="replace")


def is_env_example(path):
    return acik("env-ornek") and os.path.basename(path) == ".env.example"


def is_ayar(path, cwd):
    """iskelet.json ve settings.json: korumaları taşır; bash ile hiç yazılamaz (her zaman açık)."""
    return os.path.realpath(resolve(path, cwd)) in KORUNAN_AYARLAR


def heredoc_isaretleri(satir, tirnak):
    """Satırdaki TIRNAK DIŞI heredoc işaretlerini ve satır sonundaki tırnak durumunu döndürür.

    Tırnak içindeki `<<` (örneğin bir awk betiğindeki "# <<< ek:") ve here-string `<<<`
    heredoc sayılmaz; yoksa algılayıcı olmayan bir bitiş satırını arayıp komutun geri kalanını yutar.
    Tırnak durumu satırlar arasında taşınır (çok satırlı tek tırnaklı betikler).
    """
    isaretler, i, n = [], 0, len(satir)
    while i < n:
        ch = satir[i]
        if tirnak:
            if ch == "\\" and tirnak == '"':
                i += 2
                continue
            if ch == tirnak:
                tirnak = None
            i += 1
            continue
        if ch == "\\":
            i += 2
            continue
        if ch in ("'", '"'):
            tirnak = ch
            i += 1
            continue
        if ch == "#" and (i == 0 or satir[i - 1] in " \t;&|()"):
            break  # satırın geri kalanı yorum
        if satir.startswith("<<", i) and not satir.startswith("<<<", i) and (i == 0 or satir[i - 1] != "<"):
            m = HEREDOC_RE.match(satir, i)
            if m:
                isaretler.append(m.group(2))
                i = m.end()
                continue
        i += 1
    return isaretler, tirnak


def strip_heredocs(command):
    """Heredoc gövdelerini çıkarır. Gövde bir kabuğa veriliyorsa ayrıca döndürür."""
    out, shell_bodies = [], []
    lines = command.split("\n")
    i = 0
    tirnak = None
    while i < len(lines):
        line = lines[i]
        out.append(line)
        delims, tirnak = heredoc_isaretleri(line, tirnak)
        feeds_shell = bool(re.search(r"(^|[\s;&|(])(ba|z|da)?sh\b[^;&|]*<<", line))
        i += 1
        for d in delims:
            body = []
            while i < len(lines) and lines[i].strip() != d:
                body.append(lines[i])
                i += 1
            i += 1  # bitiş satırı
            if feeds_shell:
                shell_bodies.append("\n".join(body))
    return "\n".join(out), shell_bodies


def strip_comments(command):
    """Kabuk yorumlarını satır satır çıkarır; tırnak içindeki # dokunulmadan kalır.

    Yorum yalnızca kelime başındaki # ile başlar ve kendi satırının sonunda biter.
    Bu adım olmadan satırlar birleştirildikten sonra shlex, ilk #'ten sonraki bütün
    satırları yorum sayardı (örneğin 'echo x # not' altına yazılan 'git push' görünmezdi).
    """
    out, quote, i, n = [], None, 0, len(command)
    while i < n:
        ch = command[i]
        if quote:
            out.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < n:
                out.append(command[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch == "\\" and i + 1 < n:
            out.append(ch)
            out.append(command[i + 1])
            i += 2
            continue
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or command[i - 1] in " \t\n;&|()"):
            while i < n and command[i] != "\n":
                i += 1
            continue
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def tokenize(command):
    command = strip_comments(command)
    command = command.replace("`", " ; ").replace("\n", " ; ")
    lex = shlex.shlex(command, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    lex.commenters = ""  # yorumlar strip_comments ile satır satır çıkarıldı
    return list(lex)


def split_commands(tokens):
    cmd = []
    for t in tokens:
        if t in SEPARATORS:
            if cmd:
                yield cmd
            cmd = []
        elif t == "$":
            continue
        else:
            cmd.append(t)
    if cmd:
        yield cmd


def parse_redirects(tokens):
    words, writes = [], []  # writes: (hedef, ekleme_mi)
    i = 0
    while i < len(tokens):
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if t in (">", ">|", "&>", "<>"):
            if nxt:
                writes.append((nxt, False))
            i += 2
        elif t in (">>", "&>>"):
            if nxt:
                writes.append((nxt, True))
            i += 2
        elif t in ("<", "<<", "<<<", ">&", "<&", "<<-"):
            i += 2
        else:
            words.append(t)
            i += 1
    return words, writes


def strip_prefixes(words):
    while words:
        w = words[0]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w):
            words = words[1:]
        elif os.path.basename(w) in PREFIXES:
            words = words[1:]
            while words and words[0].startswith("-"):
                words = words[1:]
        else:
            break
    return words


def check_git(words):
    i = 1
    while i < len(words) and words[i].startswith("-"):
        i += 2 if (words[i] in GIT_OPTS_WITH_ARG) else 1
    if i >= len(words):
        return
    sub = words[i]
    if sub not in GIT_ALLOWED:
        raise Deny(
            f"git {sub} engellendi. Git bu projede salt okunur; yalnızca "
            "git status, git log, git diff ve git show kullanılabilir. "
            "Commit ve push haberini kullanıcı verir (.claude/rules/git.md)."
        )


def check_docker(words):
    rest = words[1:]
    if rest[:1] == ["volume"] and len(rest) > 1 and rest[1] in ("rm", "remove", "prune"):
        raise Deny("docker volume silme engellendi. Proje verisi korunur (.claude/rules/veri.md).")
    if rest[:1] == ["system"] and "prune" in rest:
        raise Deny("docker system prune engellendi. Proje verisi korunur (.claude/rules/veri.md).")
    is_compose = os.path.basename(words[0]) == "docker-compose" or "compose" in rest[:1]
    if is_compose and "down" in words:
        if any(w in ("-v", "--volumes") or re.match(r"^-[a-z]*v[a-z]*$", w) for w in words):
            raise Deny("docker compose down -v engellendi. Hacimler, yani veri, silinmez (.claude/rules/veri.md).")


AYAR_RED = ("{} bash ile değiştirilemez. Korumaları ve izinleri taşır; yalnızca Edit/Write ile ve "
            "kullanıcı onayıyla değişir. Koruma yalnızca /basla sırasında veya kullanıcı açıkça isteyince kapanır.")


def check_protected_files(head, words, writes, cwd):
    for target, _ in writes:
        if is_ayar(target, cwd):
            raise Deny(AYAR_RED.format(target))
    for target, append in writes:
        if is_env_example(target):
            raise Deny(".env.example bash ile yazılamaz. Edit veya Write aracıyla değiştirilir, değer yazılmaz (.claude/rules/veri.md).")
        if not append and is_records(target, cwd):
            raise Deny(f"{target} üzerine yazılamaz. Kayıt defterlerine yalnızca alta eklenir; >> kullanılabilir (.claude/rules/kayitlar.md).")

    args = [w for w in words[1:] if not w.startswith("-")]
    records_args = [a for a in args if is_records(a, cwd)]
    env_args = [a for a in args if is_env_example(a)]
    in_place = any(w.startswith("-i") or w.startswith("--in-place") for w in words[1:])
    ayar_args = [a for a in args if is_ayar(a, cwd)]
    if ayar_args and (
        (head in ("sed", "perl") and in_place)
        or head in ("rm", "mv", "truncate", "shred", "dd", "tee", "chmod")
        or (head in ("cp", "install", "rsync", "ln") and is_ayar(args[-1], cwd))
    ):
        raise Deny(AYAR_RED.format(ayar_args[0]))

    if head in ("sed", "perl") and in_place and (records_args or env_args):
        raise Deny("Kayıt defterleri ve .env.example yerinde düzenlenemez (.claude/rules/kayitlar.md, veri.md).")
    if head in ("rm", "mv", "truncate", "shred", "dd") and (records_args or env_args):
        raise Deny("Kayıt defterleri ve .env.example silinemez, taşınamaz veya kesilemez (.claude/rules/kayitlar.md, veri.md).")
    if head in ("cp", "install", "rsync") and args and (is_records(args[-1], cwd) or is_env_example(args[-1])):
        raise Deny("Kayıt defterinin veya .env.example dosyasının üzerine kopyalanamaz (.claude/rules/kayitlar.md, veri.md).")
    if head == "tee":
        appending = any(w in ("-a", "--append") for w in words[1:])
        if env_args or (records_args and not appending):
            raise Deny("tee ile yalnızca kayıt defterlerinin altına eklenebilir (tee -a); .env.example yazılamaz.")


def check(command, cwd, depth=0):
    if depth > 5:
        raise Deny("Komut çok derin iç içe; güvenle denetlenemedi.")
    command, shell_bodies = strip_heredocs(command)
    for body in shell_bodies:
        check(body, cwd, depth + 1)
    try:
        tokens = tokenize(command)
    except ValueError:
        raise Deny("Komut ayrıştırılamadı (kapanmamış tırnak olabilir). Komutu düzeltip tekrar verin.")

    for raw in split_commands(tokens):
        words, writes = parse_redirects(raw)
        words = strip_prefixes(words)
        if not words:
            check_protected_files("", [""], writes, cwd)
            continue
        head = os.path.basename(words[0])

        if words[0].startswith("$"):
            raise Deny(
                f"'{words[0]}' ile başlayan komut engellendi. Komut adı değişkenden kurulursa "
                "denetlenemez; komutu açık adıyla yazın."
            )
        if head == "cd":
            target = next((w for w in words[1:] if not w.startswith("-")), "~")
            cwd = resolve(target, cwd)
            continue

        if head in SHELLS and "-c" in words:
            idx = words.index("-c")
            if idx + 1 < len(words):
                check(words[idx + 1], cwd, depth + 1)
        elif head in SHELLS or head in ("source", "."):
            script = next((w for w in words[1:] if not w.startswith("-")), None)
            body = read_script(script, cwd) if script else None
            if body is not None:
                check(body, cwd, depth + 1)
        elif "/" in words[0]:
            body = read_script(words[0], cwd)
            if body is not None:
                check(body, cwd, depth + 1)
        if head == "eval":
            check(" ".join(words[1:]), cwd, depth + 1)
        if head == "git" and acik("git"):
            check_git(words)
        if head in SSH_TOOLS and acik("ssh"):
            raise Deny(f"{head} engellendi. Bu projede SSH, scp ve sftp kullanılmaz (.claude/rules/docker.md).")
        if head in ("docker", "docker-compose") and acik("docker-hacim"):
            check_docker(words)
        check_protected_files(head, words, writes, cwd)


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    command = (data.get("tool_input") or {}).get("command") or ""
    cwd = data.get("cwd") or PROJECT_DIR
    try:
        check(command, cwd)
    except Deny as e:
        print(f"Proje kuralı: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
