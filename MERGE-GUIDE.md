# Merging OK1 Custom Build with Upstream Nullclaw

## Setup (already done)

```
origin  = https://github.com/nullclaw/nullclaw.git   (upstream)
mine    = git@github.com:robindarlington/nullclaw.git (your fork)
branch  = ok1-custom
```

## When a new nullclaw version is released

```bash
cd ~/Documents/Projects/nullclaw

# 1. Fetch upstream changes
git fetch origin

# 2. Make sure you're on your branch
git checkout ok1-custom

# 3. Rebase your changes on top of the new version
git rebase origin/main
```

If there are conflicts:
```bash
# Git will pause and show which files conflict
# Open the conflicted file, look for <<<<<<< markers, resolve them
# Then:
git add <resolved-file>
git rebase --continue

# If it gets too messy and you want to start over:
git rebase --abort
```

## After resolving

```bash
# 4. Rebuild
zig build

# 5. Test
zig-out/bin/nullclaw doctor
zig-out/bin/nullclaw agent -m "health check"

# 6. Restart the service
systemctl --user restart nullclaw.service

# 7. Push your updated branch (force needed after rebase)
git push mine ok1-custom --force-with-lease
```

## Which files you've modified

These are the files that may conflict during rebase:

```
src/agent/cli.zig
src/agent/commands.zig
src/channel_loop.zig
src/channels/telegram.zig
src/config_parse.zig
src/config_types.zig
src/gateway.zig
src/main.zig
src/providers/anthropic.zig
src/providers/compatible.zig
src/providers/openrouter.zig
src/security/policy.zig
src/tools/http_request.zig
src/tools/root.zig
src/voice.zig
```

Files you added (won't conflict):
```
whisper-server.py
```

## If rebase is too painful

Use merge instead — it's less clean but easier:

```bash
git fetch origin
git checkout ok1-custom
git merge origin/main
# Resolve conflicts, then:
git add .
git commit
git push mine ok1-custom
```

## Generating a patch for reference

Before rebasing, save your current diff in case you need to reapply manually:

```bash
git diff origin/main..ok1-custom > ~/Documents/Vault/ai_workflows/ok1-custom-patches.diff
```

To reapply later on a fresh checkout:
```bash
git apply ~/Documents/Vault/ai_workflows/ok1-custom-patches.diff
```

## Quick reference

| Task | Command |
|------|---------|
| Check what's changed vs upstream | `git log origin/main..ok1-custom --oneline` |
| See your diff | `git diff origin/main..ok1-custom --stat` |
| Save patch backup | `git diff origin/main..ok1-custom > patch.diff` |
| Update from upstream | `git fetch origin && git rebase origin/main` |
| Push after rebase | `git push mine ok1-custom --force-with-lease` |
