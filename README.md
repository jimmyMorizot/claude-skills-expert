# Claude Skills Expert

> A meta-skill that scaffolds spec-compliant Claude Code skills, grounded on the official Anthropic specification.

## What it does

`skill-architect` is a Claude Code skill that creates other skills. It asks you 8 calibration questions, scaffolds the directory structure, writes a compliant `SKILL.md`, validates the result against a checklist derived from the [official Anthropic Skills documentation](https://code.claude.com/docs/en/skills.md), then runs the skill on real test cases before calling it done.

Every generated skill is guaranteed to:

- Use only documented frontmatter fields (13 official fields as of April 2026).
- Respect the 250-character description cap with front-loaded keywords.
- Survive context compaction (critical rules within the first 5,000 tokens).
- Reference supporting files via `${CLAUDE_SKILL_DIR}` instead of hardcoded paths.
- Ignore undocumented folklore (no "V1/V2", "Tier 1/2/3", "Pushy descriptions", etc.).

## Installation

```bash
# Clone the repo
git clone git@github.com:<your-username>/claude-skills-expert.git
cd claude-skills-expert

# Install the skill to your personal Claude Code directory
./install.sh
```

The script symlinks `skill/` to `~/.claude/skills/skill-architect/`. The skill is then available in all your projects.

Because it is a link and not a copy, this repo stays the single source of truth: editing the skill from either path changes the same files, and `git status` here shows what you changed. If an older copy-based install is already in place, the script migrates it, and moves it aside to `~/.claude/skill-architect.backup-<timestamp>` first when its contents differ from the repo.

## Usage

In any Claude Code session:
/skill-architect my-new-skill

Claude will ask you calibration questions, then scaffold the skill at the location you specify (personal, project, or plugin scope).

## Philosophy

This project exists because the French-speaking LinkedIn/YouTube ecosystem propagates inaccurate myths about Claude Skills (fake versioning, fabricated benchmarks, invented terminology). `skill-architect` is grounded strictly on the Anthropic documentation and the real `anthropics/skills` repository patterns — no folklore, no approximation.

See [`skill/references/skills-spec-officielle.md`](skill/references/skills-spec-officielle.md) for the full machine-grade specification document that grounds the agent.

## Development

To iterate on the skill:

Edit `skill/SKILL.md` or `skill/references/*` directly. The symlink means changes
are live immediately, with no reinstall step. Run `/reload-skills` in an open
Claude Code session to pick them up without restarting.

For inspiration, optionally clone the official Anthropic skills repo:

```bash
git clone https://github.com/anthropics/skills.git references/anthropic-skills-examples
```

This directory is gitignored — it's only a local reference.

## License

MIT — use freely, attribute if you share.

## Author

Jimmy Morizot — web developer at [CreatisWeb](https://creatisweb.com).
