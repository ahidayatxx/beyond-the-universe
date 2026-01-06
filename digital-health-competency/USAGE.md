# Auto-Commit Setup Guide

This directory is configured for automatic Git commits and pushes to GitHub.

## Quick Start

### Manual Auto-Commit

After making changes to files in this directory, run:

```bash
./auto-commit.sh
```

This will:
1. ✅ Check for changes in `digital-health-competency/`
2. ✅ Stage all modified/new files
3. ✅ Create a commit with timestamp
4. ✅ Push to GitHub automatically

### Continuous Monitoring (Optional)

For automatic commits whenever files change:

```bash
./watch-and-commit.sh
```

This requires `fswatch` to be installed:

```bash
# macOS with Homebrew
brew install fswatch
```

Then run the watch script—it will monitor the directory and auto-commit on any changes.

## What Gets Committed

- ✅ HTML files (`*.html`)
- ✅ README.md
- ✅ auto-commit.sh (the manual commit script)
- ✅ Documentation files

## What Gets Excluded

The `.gitignore` in the parent directory excludes:
- ❌ `CLAUDE.md` (local development docs)
- ❌ `.claude/` directory (architecture docs)
- ❌ `watch-and-commit.sh` (requires fswatch, local tool)

## GitHub Repository

- **Repository**: https://github.com/ahidayatxx/beyond-the-universe
- **Folder**: `digital-health-competency/`
- **Live Site**: https://ahidayatxx.github.io/beyond-the-universe/digital-health-competency/

## Tips

1. **Edit files normally** - Make changes to HTML files, README, etc.
2. **Run auto-commit** - Execute `./auto-commit.sh` to sync changes
3. **Check GitHub** - Changes appear instantly at the repository URL

## Troubleshooting

### Script not found
Make sure you're in the `digital-health-competency` directory:
```bash
cd /Users/ahmadhidayat/claude-code/digital-health-competency
./auto-commit.sh
```

### Permission denied
Make the script executable:
```bash
chmod +x auto-commit.sh
```

### Push rejected
If there are conflicts on GitHub:
```bash
cd /Users/ahmadhidayat/claude-code
git pull beyond-the-universe main --rebase
git push beyond-the-universe main
```

## Automation with Claude Code

When you update files through Claude Code, simply run:
```
Bash: /Users/ahmadhidayat/claude-code/digital-health-competency/auto-commit.sh
```

This will automatically commit and push your changes!
