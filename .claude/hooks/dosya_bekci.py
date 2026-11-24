#!/usr/bin/env python3
"""PreToolUse hook (Edit, Write, MultiEdit): dosya yazım kurallarını zorlar.

- docs/kayitlar/ altındaki defterlere yalnızca alta eklenir. Eski satır değişmez.
- .env.example yalnızca değersiz anahtar ve yorum taşır.

Reddedilen yazım için nedeni stderr'e yazar ve 2 ile çıkar. Claude nedeni görür.
Kurallar: .claude/rules/kayitlar.md, veri.md
Hangi korumanın açık olduğu .claude/iskelet.json dosyasından okunur (korumalar.py).
"""
import json
import os
import re
import sys

sys.dont_write_bytecode = True  # korumalar.py içe aktarılınca __pycache__ oluşmasın
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from korumalar import acik, iskelet_mi  # noqa: E402

PROJECT_DIR = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
RECORDS_DIR = os.path.join(PROJECT_DIR, "docs", "kayitlar")
ISKELET_GECMISI = os.path.join(PROJECT_DIR, ".claude", "iskelet-gecmisi")  # iskeletin kendi defterleri
KEY_LINE = re.compile(r"^[A-Z_][A-Z0-9_]*=$")
VALUE_IN_COMMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\s*=\s*\S")


class Deny(Exception):
    pass


def edits_of(tool, inp):
    if tool == "MultiEdit":
        return inp.get("edits") or []
    if tool == "Edit":
        return [inp]
    return []


def check_records(tool, inp, path):
    if not os.path.exists(path):
        return  # yeni defter açılabilir
    with open(path, encoding="utf-8") as f:
        current = f.read()

    if tool == "Write":
        if not (inp.get("content") or "").startswith(current):
            raise Deny(
                f"{os.path.relpath(path, PROJECT_DIR)} üzerine yazılamaz. Kayıt defterine yalnızca "
                "alta eklenir; eski satır düzenlenmez. Düzeltme yeni bir kayıttır (.claude/rules/kayitlar.md)."
            )
        return

    text = current
    for e in edits_of(tool, inp):
        old, new = e.get("old_string") or "", e.get("new_string") or ""
        idx = text.rfind(old) if old else -1
        at_end = idx >= 0 and text[idx + len(old):].strip() == ""
        if e.get("replace_all") or not at_end or not new.startswith(old):
            raise Deny(
                f"{os.path.relpath(path, PROJECT_DIR)} içinde eski kayıt değiştirilemez. Yalnızca dosyanın "
                "son metninden sonra ekleme yapılır: old_string dosyanın sonundaki metin olmalı ve "
                "new_string onunla başlamalı (.claude/rules/kayitlar.md)."
            )
        text = text[:idx] + new + text[idx + len(old):]


def check_env_example(tool, inp, path):
    if tool == "Write":
        result = inp.get("content") or ""
    else:
        if not os.path.exists(path):
            return
        with open(path, encoding="utf-8") as f:
            result = f.read()
        for e in edits_of(tool, inp):
            old, new = e.get("old_string") or "", e.get("new_string") or ""
            result = result.replace(old, new) if e.get("replace_all") else result.replace(old, new, 1)

    for n, line in enumerate(result.splitlines(), 1):
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            if VALUE_IN_COMMENT.search(s):
                raise Deny(f".env.example satır {n}: yorum satırına değer yazılmaz (.claude/rules/veri.md).")
            continue
        if not KEY_LINE.match(s):
            raise Deny(
                f".env.example satır {n}: '{s}' kabul edilmedi. Bu dosyada yalnızca değersiz anahtar "
                "(ANAHTAR=) ve yorum durur (.claude/rules/veri.md)."
            )


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool = data.get("tool_name") or ""
    inp = data.get("tool_input") or {}
    raw = inp.get("file_path") or ""
    if not raw:
        return 0
    path = os.path.normpath(os.path.join(data.get("cwd") or PROJECT_DIR, raw))
    try:
        if acik("defter") and (path.startswith(RECORDS_DIR + os.sep) or (iskelet_mi() and path.startswith(ISKELET_GECMISI + os.sep))):
            check_records(tool, inp, path)
        if acik("env-ornek") and os.path.basename(path) == ".env.example":
            check_env_example(tool, inp, path)
    except Deny as e:
        print(f"Proje kuralı: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
