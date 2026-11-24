"""Hook testleri. Çalıştırma: python3 .claude/hooks/hook_testleri.py

Testler proje dosyalarına yazmaz ve projenin koruma ayarından bağımsızdır; hook'lara örnek girdi verip çıkış kodunu kontrol eder.
Script testleri için geçici bir klasör açılır ve test sonunda silinir.
"""

import atexit, json, os, shutil, subprocess, sys, tempfile

# Testler iskeletin varsayılanını (bütün korumalar açık) sınar. Bu yüzden projenin kendi
# .claude/iskelet.json ayarı kullanılmaz: defterler ve .env.example geçici bir proje klasörüne
# kopyalanır, hook'lar o klasörü proje sayar. Sadeleştirilmiş projede de testler aynı sonucu verir.
GERCEK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOOKS = os.path.join(GERCEK, ".claude", "hooks")
P = tempfile.mkdtemp(prefix="hook-testi-")
atexit.register(shutil.rmtree, P, True)
os.makedirs(os.path.join(P, ".claude"))
shutil.copytree(os.path.join(GERCEK, "docs", "kayitlar"), os.path.join(P, "docs", "kayitlar"))
shutil.copyfile(os.path.join(GERCEK, ".env.example"), os.path.join(P, ".env.example"))
ENV = dict(os.environ, CLAUDE_PROJECT_DIR=P)
fails = 0


def run(hook, payload):
    r = subprocess.run([sys.executable, os.path.join(HOOKS, hook)], input=json.dumps(payload),
                       capture_output=True, text=True, env=ENV)
    return r.returncode, r.stderr.strip()


def expect(name, hook, payload, code):
    global fails
    got, err = run(hook, payload)
    ok = got == code
    fails += not ok
    print(f"{'OK  ' if ok else 'FAIL'} [{'red' if code == 2 else 'geç'}] {name}" + ("" if ok else f"  -> exit {got} {err}"))


def bash(cmd, code):
    expect(cmd.replace("\n", "⏎"), "bash_bekci.py", {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": P}, code)


print("== bash_bekci: reddedilmeli")
for c in ["git commit -m x", "git -C . push", "cd x && git push", 'bash -c "git push"',
          "echo $(git reset --hard)", "echo `git add .`", "/usr/bin/git commit", "sudo git push",
          "GIT_DIR=x git commit", "git --no-pager -c a=b stash", "ssh host", "scp a host:b",
          "docker compose -f compose.local.yaml down -v", "docker compose down --volumes",
          "docker volume rm x", "docker system prune -a",
          "sed -i 's/a/b/' docs/kayitlar/degisiklikler.md", "echo x > docs/kayitlar/degisiklikler.md",
          "rm docs/kayitlar/teknik-borclar.md", "tee docs/kayitlar/degisiklikler.md",
          "echo A=1 >> .env.example", "sed -i s/A=/A=1/ .env.example",
          "bash <<'EOF'\ngit push\nEOF", "eval git commit",
          "G=git; $G push", "$CMD commit", "cd docs/kayitlar && echo x > degisiklikler.md",
          "cd docs && rm kayitlar/degisiklikler.md",
          "echo x > .claude/iskelet-gecmisi/degisiklikler.md", "rm .claude/iskelet-gecmisi/teknik-borclar.md",
          "echo x # not\ngit push", "echo $(( 10#5 ))\ngit commit -m x", "# yorum\ngit push",
          "echo a # Claude'un notu\ngit remote -v", "git rev-parse HEAD",
          "awk '\n/# <<< ek:/{ next }\n{ print }' f\ngit push",
          "bash <<'EOF'\ngit push\nEOF"]:
    bash(c, 2)

print("== bash_bekci: geçmeli")
for c in ["git status", "git -C . log --oneline", "git diff HEAD~1", "git --version", "make up",
          'grep -n "git commit" .claude/rules/git.md', "echo x >> docs/kayitlar/degisiklikler.md",
          "tee -a docs/kayitlar/degisiklikler.md", "cat docs/kayitlar/degisiklikler.md", "date '+%Y-%m-%d %H:%M'",
          "docker compose -f compose.local.yaml down", "docker compose -f compose.local.yaml exec api php -v",
          "cat > notes.md <<'EOF'\nClaude'un git push yazısı\nEOF", "cat .env.example", "echo $HOME",
          "echo x > /tmp/baska-proje/degisiklikler.md", "rm /tmp/baska-proje/teknik-borclar.md",
          "cd docs/kayitlar && cat degisiklikler.md", "echo x >> .claude/iskelet-gecmisi/degisiklikler.md",
          "ls # Claude'un notu", "echo 'a # tırnak içinde git push'", "echo ${#HOME}\ngit status",
          "# yalnızca yorum: git push",
          # Prova bulgusu: tek tırnaklı çok satırlı awk içindeki "# <<< ek:" heredoc sanılıyordu.
          "awk -v sel=\"a,b\" '\n/^[ \\t]*# >>> ek-yok:/{skip=1; next}\n/^[ \\t]*# <<< ek-yok:/{skip=0; next}\n{ if(!skip) print }' a.tmpl | sed -e 's/__NO__/42/g' > a.yaml\ngrep -n '>>>' a.yaml",
          "cat <<< \"git push metni\"", "echo 'x << EOF y'"]:
    bash(c, 0)

print("== bash_bekci: script dosyaları (geçici klasörde, test sonunda silinir)")
with tempfile.TemporaryDirectory() as tmp:
    kotu, iyi = os.path.join(tmp, "kotu.sh"), os.path.join(tmp, "iyi.sh")
    with open(kotu, "w") as f:
        f.write("echo hazırlık\ngit push origin main\n")
    with open(iyi, "w") as f:
        f.write("echo merhaba\ngit status\n")
    for c in [f"bash {kotu}", f"sh {kotu}", f"source {kotu}", f". {kotu}", f"{kotu}"]:
        bash(c, 2)
    for c in [f"bash {iyi}", f"{iyi}", "bash /yok/boyle/bir/dosya.sh"]:
        bash(c, 0)

print("== dosya_bekci")
cl = f"{P}/docs/kayitlar/degisiklikler.md"
cur = open(cl).read()
last = cur.rstrip("\n").split("\n")[-1]
first = cur.split("\n")[0]
expect("changelog: sona Edit ile ekleme", "dosya_bekci.py",
       {"tool_name": "Edit", "tool_input": {"file_path": cl, "old_string": last, "new_string": last + "\nyeni satır"}}, 0)
expect("changelog: Write ile sona ekleme", "dosya_bekci.py",
       {"tool_name": "Write", "tool_input": {"file_path": cl, "content": cur + "yeni\n"}}, 0)
expect("changelog: ilk satırı değiştirme", "dosya_bekci.py",
       {"tool_name": "Edit", "tool_input": {"file_path": cl, "old_string": first, "new_string": "# X"}}, 2)
expect("changelog: son satırı değiştirme", "dosya_bekci.py",
       {"tool_name": "Edit", "tool_input": {"file_path": cl, "old_string": last, "new_string": "başka"}}, 2)
expect("changelog: Write ile üzerine yazma", "dosya_bekci.py",
       {"tool_name": "Write", "tool_input": {"file_path": cl, "content": "boş\n"}}, 2)
expect("kayitlar: yeni defter açma", "dosya_bekci.py",
       {"tool_name": "Write", "tool_input": {"file_path": f"{P}/docs/kayitlar/yeni.md", "content": "x"}}, 0)
env = f"{P}/.env.example"
ecur = open(env).read()
expect(".env.example: API_KEY= ekleme", "dosya_bekci.py",
       {"tool_name": "Write", "tool_input": {"file_path": env, "content": ecur + "\nAPI_KEY=\nDB_HOST=\n"}}, 0)
expect(".env.example: API_KEY=abc", "dosya_bekci.py",
       {"tool_name": "Write", "tool_input": {"file_path": env, "content": ecur + "\nAPI_KEY=abc\n"}}, 2)
expect(".env.example: # API_KEY=abc", "dosya_bekci.py",
       {"tool_name": "Write", "tool_input": {"file_path": env, "content": ecur + "\n# API_KEY=abc\n"}}, 2)
expect(".env.example: Edit ile değer", "dosya_bekci.py",
       {"tool_name": "Edit", "tool_input": {"file_path": env, "old_string": ecur.rstrip("\n").split("\n")[-1],
                                            "new_string": ecur.rstrip("\n").split("\n")[-1] + "\nX=1"}}, 2)
expect("başka dosya: serbest", "dosya_bekci.py",
       {"tool_name": "Write", "tool_input": {"file_path": f"{P}/README.md", "content": "x"}}, 0)

print("== ayar dosyaları: bash ile yazılamaz (koruma ayarından bağımsız)")
for c in ["echo x > .claude/iskelet.json", "echo x >> .claude/iskelet.json", "sed -i s/true/false/ .claude/iskelet.json",
          "rm .claude/settings.json", "cp /tmp/x .claude/settings.json", "tee .claude/iskelet.json",
          "cd .claude && mv iskelet.json eski.json"]:
    bash(c, 2)
for c in ["cat .claude/iskelet.json", "grep git .claude/settings.json", "cp .claude/iskelet.json /tmp/yedek.json"]:
    bash(c, 0)

print("== korumalar: iskelet.json ile kapatılan koruma geçer, diğerleri engeller (geçici proje klasöründe)")


def proje_ile(ayar_metni, fn):
    global ENV
    eski = ENV
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, ".claude"))
        os.makedirs(os.path.join(tmp, "docs", "kayitlar"))
        with open(os.path.join(tmp, "docs", "kayitlar", "degisiklikler.md"), "w") as f:
            f.write("# Değişiklikler\nilk\n")
        if ayar_metni is not None:
            with open(os.path.join(tmp, ".claude", "iskelet.json"), "w") as f:
                f.write(ayar_metni)
        ENV = dict(os.environ, CLAUDE_PROJECT_DIR=tmp)
        try:
            fn(tmp)
        finally:
            ENV = eski


def kapali_git_ve_defter(tmp):
    b = lambda c, k: expect(c, "bash_bekci.py", {"tool_name": "Bash", "tool_input": {"command": c}, "cwd": tmp}, k)
    b("git commit -m x", 0)
    b("git push", 0)
    b("echo x > docs/kayitlar/degisiklikler.md", 0)
    b("ssh host", 2)
    b("docker volume rm x", 2)
    b("echo A=1 >> .env.example", 2)
    b("echo x > .claude/iskelet.json", 2)
    expect("defter kapalı: Write ile üzerine yazma", "dosya_bekci.py",
           {"tool_name": "Write", "tool_input": {"file_path": f"{tmp}/docs/kayitlar/degisiklikler.md", "content": "yeni\n"}}, 0)


def hepsi_kapali(tmp):
    b = lambda c, k: expect(c, "bash_bekci.py", {"tool_name": "Bash", "tool_input": {"command": c}, "cwd": tmp}, k)
    b("ssh host", 0)
    b("docker compose down -v", 0)
    b("echo A=1 >> .env.example", 0)
    b("rm .claude/iskelet.json", 2)  # ayar dosyası her zaman korunur
    expect("env-ornek kapalı: değerli satır", "dosya_bekci.py",
           {"tool_name": "Write", "tool_input": {"file_path": f"{tmp}/.env.example", "content": "A=1\n"}}, 0)


def ayar_yok(tmp):
    b = lambda c, k: expect(c, "bash_bekci.py", {"tool_name": "Bash", "tool_input": {"command": c}, "cwd": tmp}, k)
    b("git push", 2)
    b("echo x > docs/kayitlar/degisiklikler.md", 2)


def bozuk(tmp):
    got, _ = run("bash_bekci.py", {"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": tmp})
    global fails
    ok = got not in (0,)  # hook hata verir; settings.json sarmalayıcısı 0 ve 2 dışını engeller
    fails += not ok
    print(f"{'OK  ' if ok else 'FAIL'} [red] bozuk iskelet.json: hook hata verir (çıkış {got})")


proje_ile('{"korumalar": {"git": false, "defter": false}}', kapali_git_ve_defter)
proje_ile('{"korumalar": {"git": false, "ssh": false, "docker-hacim": false, "defter": false, "env-ornek": false}}', hepsi_kapali)
proje_ile(None, ayar_yok)


def proje_turu(tmp):
    os.makedirs(os.path.join(tmp, ".claude", "iskelet-gecmisi"))
    b = lambda c, k: expect(c, "bash_bekci.py", {"tool_name": "Bash", "tool_input": {"command": c}, "cwd": tmp}, k)
    b("rm -r .claude/iskelet-gecmisi", 0)  # projede iskeletin geçmişi silinebilir
    b("echo x > docs/kayitlar/degisiklikler.md", 2)  # projenin defteri yine korunur
    expect("proje: iskelet geçmişine Write serbest", "dosya_bekci.py",
           {"tool_name": "Write", "tool_input": {"file_path": f"{tmp}/.claude/iskelet-gecmisi/degisiklikler.md", "content": "x"}}, 0)


def iskelet_turu(tmp):
    b = lambda c, k: expect(c, "bash_bekci.py", {"tool_name": "Bash", "tool_input": {"command": c}, "cwd": tmp}, k)
    b("rm -r .claude/iskelet-gecmisi", 2)


proje_ile('{"tur": "proje"}', proje_turu)
proje_ile('{"tur": "iskelet"}', iskelet_turu)
proje_ile('{"korumalar": ', bozuk)

print(f"\n{fails} başarısız")
sys.exit(1 if fails else 0)
