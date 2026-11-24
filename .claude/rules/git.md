# Git

Git üzerinde yazan işlem yok. Yalnızca izleme vardır.

İzinli komutlar: `git status`, `git log`, `git diff`, `git show`.

Commit, add, push, pull, fetch, merge, rebase, reset, switch, stash, tag ve `git config` yok. Kimlik, imza ve commit mesajı yazılmaz. Commit ve push işini kullanıcı yapar.

Commit ve push ayrıca bir deftere kaydedilmez; Git kendi geçmişini tutar. Neyin commit edildiği gerektiğinde `git log` ve `git show` ile okunur.

Bu yasak `.claude/settings.json` içindeki izin kuralıyla ve komutun tamamını tarayan `.claude/hooks/bash_bekci.py` ile de engellenir. Engel aşılmaya çalışılmaz; başka bir komutla dolanılmaz.
