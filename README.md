# Claude Skills Expert

> A meta-skill that scaffolds spec-compliant Claude Code skills, grounded on the official Anthropic specification.

## What it does

`skill-architect` is a Claude Code skill that creates other skills. It asks you 10 calibration questions, scaffolds the directory structure, writes a compliant `SKILL.md`, validates the result against a checklist derived from the [official Anthropic Skills documentation](https://code.claude.com/docs/en/skills.md) and the [Agent Skills standard](https://agentskills.io/specification), then runs the skill on real test cases before calling it done. It also audits or improves an existing skill against the same checklist, packages a skill for claude.ai, and tests a description's triggering. By default it delivers two variants: the Claude Code skill and a zip ready to upload to claude.ai.

Every generated skill is checked to:

- Use only documented frontmatter fields: the 20 Claude Code fields, or the 6 fields claude.ai accepts for an upload (spec read on November 10, 2026, Claude Code 2.1.322).
- Front-load its description and stay within the listing caps (1,536 characters in Claude Code, 1,024 for claude.ai).
- Survive context compaction (critical rules within the first 5,000 tokens).
- Reference supporting files via `${CLAUDE_SKILL_DIR}` in Claude Code, and via relative paths in the claude.ai variant.
- Use `paths` only where its conditional activation fits: a skill with `paths` stays hidden, even from `/name`, until Claude touches a matching file.
- Ignore undocumented folklore (no "V1/V2", no "Tier 1/2/3").

## Installation

```bash
# Clone the repo
git clone https://github.com/jimmyMorizot/claude-skills-expert.git
cd claude-skills-expert

# Install the skill to your personal Claude Code directory
./install.sh
```

The script symlinks `skill/` to `~/.claude/skills/skill-architect/`. The skill is then available in all your projects.

Because it is a link and not a copy, this repo stays the single source of truth: editing the skill from either path changes the same files, and `git status` here shows what you changed. If an older copy-based install is already in place, the script migrates it, and moves it aside to `~/.claude/skill-architect.backup-<timestamp>` first when its contents differ from the repo.

## Usage

In any Claude Code session:

```text
/skill-architect my-new-skill
```

Claude will ask you calibration questions, then scaffold the skill at the location you specify (personal, project, or plugin scope). To audit or improve an existing skill, ask in plain words, for example `/skill-architect audit my-existing-skill`.

## Philosophy

This project exists because the French-speaking LinkedIn/YouTube ecosystem propagates inaccurate myths about Claude Skills (fake versioning, fabricated benchmarks, invented terminology). `skill-architect` is grounded strictly on the Anthropic documentation and the real `anthropics/skills` repository patterns: no folklore, no approximation.

See [`skill/references/skills-spec-officielle.md`](skill/references/skills-spec-officielle.md) for the full machine-grade specification document that grounds the agent.

## Development

Edit `skill/SKILL.md` or `skill/references/*` directly. The symlink means changes
are live immediately, with no reinstall step. Claude Code watches `~/.claude/skills/` and
picked up edits through the symlink in a running session (observed on 2.1.308 on
October 22, 2026, when the skill listing showed the new description, and on 2.1.322 on
November 10, 2026, when a re-invocation returned the edited body); if a change does not
show, run `/reload-skills`.

`references/skills-spec-officielle.md` at the repo root is a copy of
`skill/references/skills-spec-officielle.md`: keep both identical.

To refresh the spec, re-read https://code.claude.com/docs/en/skills.md,
https://agentskills.io/specification and
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices, then date
the new reading in the spec header.

For inspiration, optionally clone the official Anthropic skills repo:

```bash
git clone https://github.com/anthropics/skills.git references/anthropic-skills-examples
```

This directory is gitignored. It's only a local reference.

## claude.ai version

claude.ai accepts only six frontmatter fields, and Claude Code variables such as
`CLAUDE_SKILL_DIR` are not expected to work there (inferred from the docs), so the upload
is derived from `skill/`:

```bash
python3 package-claude-ai.py
```

The script writes `dist/skill-architect.zip` (gitignored) and stops with an error if the
derivation or the checks fail, or if the two copies of the spec differ. Upload the zip from
the skills settings on claude.ai.
Once uploaded, the skill also syncs into Claude Code sessions signed in to the same
account as `/anthropic-skills:skill-architect`; keep it at the same version as the local one.

## License

MIT, see [LICENSE](LICENSE). Use freely, attribute if you share.

## Author

Jimmy Morizot, web developer at [CreatisWeb](https://creatisweb.com).
