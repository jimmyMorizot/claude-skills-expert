#!/bin/bash
# ============================================================================
# install.sh — Install skill-architect into ~/.claude/skills/
# ============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME/.claude/skills/skill-architect"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Claude Skills Expert — Installation${NC}"
echo -e "${BLUE}============================================${NC}"

if ! command -v claude &> /dev/null; then
    echo "Warning: 'claude' command not found. Install Claude Code first:"
    echo "  npm install -g @anthropic-ai/claude-code"
fi

mkdir -p "$HOME/.claude/skills"

if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}[UPDATE]${NC} Overwriting existing skill-architect"
else
    echo -e "${GREEN}[NEW]${NC}    Installing skill-architect"
fi

rm -rf "$TARGET_DIR"
cp -r "$SCRIPT_DIR/skill" "$TARGET_DIR"

echo ""
echo -e "${GREEN}Installation complete.${NC}"
echo ""
echo "Usage in any Claude Code session:"
echo "  /skill-architect my-new-skill"
echo ""
