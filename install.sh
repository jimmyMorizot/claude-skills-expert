#!/bin/bash
# ============================================================================
# install.sh — Link skill-architect into ~/.claude/skills/
#
# The skill is installed as a symlink, not a copy, so the repo stays the single
# source of truth: edits made through ~/.claude/skills/skill-architect land in
# this working tree and show up in `git status` instead of drifting silently.
# ============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/skill"
TARGET_DIR="$HOME/.claude/skills/skill-architect"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Claude Skills Expert — Installation${NC}"
echo -e "${BLUE}============================================${NC}"

if ! command -v claude &> /dev/null; then
    echo "Warning: 'claude' command not found. Install Claude Code first:"
    echo "  npm install -g @anthropic-ai/claude-code"
fi

mkdir -p "$HOME/.claude/skills"

# Order matters: a symlink pointing at a directory satisfies both -L and -d.
if [ -L "$TARGET_DIR" ]; then
    echo -e "${GREEN}[RELINK]${NC}  Refreshing existing symlink"
    rm "$TARGET_DIR"
elif [ -d "$TARGET_DIR" ]; then
    # A real directory predates the symlink install and may hold edits made in
    # place that never reached this repo. Never delete it without looking.
    if diff -rq "$SOURCE_DIR" "$TARGET_DIR" > /dev/null 2>&1; then
        echo -e "${GREEN}[MIGRATE]${NC} Installed copy matches this repo, replacing it with a symlink"
        rm -rf "$TARGET_DIR"
    else
        # Kept outside ~/.claude/skills so Claude Code does not discover the
        # backup as a second skill sharing the same name.
        BACKUP_DIR="$HOME/.claude/skill-architect.backup-$(date +%Y%m%d-%H%M%S)"
        echo -e "${YELLOW}[BACKUP]${NC}  Installed copy differs from this repo, so it holds work that"
        echo "           was never committed here. Moving it aside instead of deleting:"
        echo "             $BACKUP_DIR"
        echo "           Review it, then bring anything worth keeping into the repo:"
        echo "             diff -r \"$SOURCE_DIR\" \"$BACKUP_DIR\""
        mv "$TARGET_DIR" "$BACKUP_DIR"
    fi
else
    echo -e "${GREEN}[NEW]${NC}     Installing skill-architect"
fi

ln -s "$SOURCE_DIR" "$TARGET_DIR"

echo ""
echo -e "${GREEN}Installation complete.${NC}"
echo "  $TARGET_DIR"
echo "    -> $SOURCE_DIR"
echo ""
echo "The skill is linked, not copied: editing it from either path edits this"
echo "repo. Run 'git status' here after tweaking it."
echo ""
echo "If a Claude Code session is already open, run /reload-skills to load it now"
echo "(otherwise it loads automatically at the next session start)."
echo ""
echo "Usage in any Claude Code session:"
echo "  /skill-architect my-new-skill"
echo ""
