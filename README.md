# Claude Skills Expert

> A meta-skill that scaffolds spec-compliant Claude Code skills, grounded on the official Anthropic specification.

## What it does

`skill-architect` is a Claude Code skill that creates other skills. It asks you 7 calibration questions, scaffolds the directory structure, writes a compliant `SKILL.md`, and validates the result against a 12-point checklist derived from the [official Anthropic Skills documentation](https://code.claude.com/docs/en/skills.md).

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

The script copies `skill/` into `~/.claude/skills/skill-architect/`. The skill is then available in all your projects.

## Usage

In any Claude Code session:
/skill-architect my-new-skill

Claude will ask you calibration questions, then scaffold the skill at the location you specify (personal, project, or plugin scope).

## Philosophy

This project exists because the French-speaking LinkedIn/YouTube ecosystem propagates inaccurate myths about Claude Skills (fake versioning, fabricated benchmarks, invented terminology). `skill-architect` is grounded strictly on the Anthropic documentation and the real `anthropics/skills` repository patterns — no folklore, no approximation.

See [`skill/references/skills-spec-officielle.md`](skill/references/skills-spec-officielle.md) for the full machine-grade specification document that grounds the agent.

## Development

To iterate on the skill:

```bash
# Edit skill/SKILL.md or skill/references/*
# Re-run the installer to propagate changes
./install.sh
```

For inspiration, optionally clone the official Anthropic skills repo:

```bash
git clone https://github.com/anthropics/skills.git references/anthropic-skills-examples
```

This directory is gitignored — it's only a local reference.

## License

MIT — use freely, attribute if you share.

## Author

Jimmy Morizot — web developer at [CreatisWeb](https://creatisweb.com).
