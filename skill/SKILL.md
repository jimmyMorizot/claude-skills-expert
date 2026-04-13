---
name: skill-architect
description: Create and scaffold Claude Code skills with spec-compliant SKILL.md, frontmatter, and directory structure. Use when building new skills, generating SKILL.md files, or checking conformance against the official Anthropic specification.
argument-hint: [skill-name]
allowed-tools: Read Write Bash(mkdir *) Bash(ls *) Bash(cat *) Bash(cp *)
---

# Skill Architect

**CRITICAL — Read before any action:** Before creating or modifying any skill, read the official Anthropic Skills specification at `${CLAUDE_SKILL_DIR}/references/skills-spec-officielle.md`. This is the single source of truth for frontmatter fields, variable substitutions, lifecycle behavior, and placement rules. Never rely on pre-trained knowledge about skills — always verify against this file.

**Anti-folklore rule:** Never use the following terms in any skill you generate — they do not exist in the official Anthropic specification and must never appear in generated SKILL.md files:
- "Tier 1", "Tier 2", "Tier 3"
- "Pushy" (as a description style qualifier)
- "V1", "V2" (as skill specification versions)
- "Objectif Supreme"
- "~100 tokens scan"
- "Architecture Indentee chronologique"

If a user mentions these concepts, explain they are undocumented folklore and redirect to the embedded spec.

## Standing rules for all skill creation

These rules apply throughout the entire session, for every skill generated:

- Every generated SKILL.md must have valid YAML frontmatter between `---` delimiters.
- Only use frontmatter fields documented in the spec (section 4). The official fields are: `name`, `description`, `argument-hint`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell`. No other field is permitted.
- The `description` field must be present, under 250 characters, with keywords front-loaded that users would naturally say.
- Directory names: lowercase, digits, and hyphens only, max 64 characters. No underscores, no spaces, no uppercase.
- Write all SKILL.md body instructions as **standing instructions** (persistent across the session), never as one-shot steps that become irrelevant after execution.
- Place critical instructions within the **first 5,000 tokens** of the body — only this portion survives context compaction.
- Reference supporting files via `${CLAUDE_SKILL_DIR}/`, never via hardcoded absolute paths.
- The `allowed-tools` field **pre-approves** tools — it does **not restrict** them. Scope it to the minimum necessary.
- Include only frontmatter fields relevant to the specific skill. Omit fields that would use default values.

## Phase 1 — Before creation

When invoked with `/skill-architect $0`, start by gathering requirements. Ask the user the following calibration questions before writing any file:

1. **Skill name:** Confirm `$0` is the intended name. Validate: lowercase, hyphens, digits only, max 64 characters. Propose a correction if it violates the convention.
2. **Purpose:** What should this skill enable Claude to do? Request a concrete description of the desired behavior or workflow.
3. **Scope and placement:** Where should this skill live?
   - Personal: `~/.claude/skills/$0/` (available across all projects)
   - Project: `.claude/skills/$0/` (this project only)
   - Plugin: `<plugin>/skills/$0/` (scoped to plugin activation)
4. **Target files:** Are there specific file patterns where this skill should auto-activate? (maps to the `paths` field, e.g., `src/**/*.ts`, `*.py`). Leave empty if the skill should activate on conversation context alone.
5. **Invocation mode:** Should Claude auto-invoke this skill when the conversation context matches, or should it be manual-only? (maps to `disable-model-invocation: true` if manual-only)
6. **Tools needed:** Which tools should be pre-approved without permission prompts? (maps to `allowed-tools`). Examples: `Read`, `Write`, `Bash(npm *)`, `Bash(git *)`.
7. **Supporting files:** Does the skill need bundled references, templates, or scripts? If yes, describe their purpose.

Do not proceed to Phase 2 until the user has confirmed the answers. If a question is not applicable, the user may skip it.

## Phase 2 — During creation

### 2.1 Scaffold the directory

Create the directory structure based on the user's answers:

```bash
mkdir -p <scope-path>/$0
```

Add subdirectories only if the user confirmed supporting files:
- `references/` — for documentation or specs the skill needs to consult
- `templates/` — for output templates the skill fills in
- `scripts/` — for executable scripts the skill runs

### 2.2 Write the target SKILL.md

Read the template at `${CLAUDE_SKILL_DIR}/templates/SKILL.md.template` for the structural skeleton.

**Frontmatter construction:**
- Always include `name` and `description`.
- Add `argument-hint` only if the skill accepts arguments.
- Add `allowed-tools` only if tools need pre-approval.
- Add `paths` only if file-pattern activation is desired.
- Add `disable-model-invocation: true` only if manual-only.
- Every field must be verified against the spec before inclusion. If in doubt, read the spec.

**Description construction:**
- Front-load keywords that a user would naturally say when they need this skill.
- Stay under 250 characters.
- Do not summarize the skill's internal workflow or process in the description — only describe triggering conditions and capabilities.

**Body construction:**
- Open with the most critical rules and constraints — these survive compaction.
- Write as standing instructions that remain valid throughout the session.
- Reference every supporting file explicitly with `${CLAUDE_SKILL_DIR}/path/to/file` and explain when Claude should read it.
- Use variable substitutions where applicable: `$0`, `$1`, `$ARGUMENTS`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_SKILL_DIR}`.
- Prefer imperative form ("Read the file", "Verify the output").
- If the body risks exceeding 5,000 tokens, move detailed reference content into supporting files under `references/`.

### 2.3 Write supporting files

For each supporting file confirmed in Phase 1:
- Create it in the appropriate subdirectory.
- Reference it from the SKILL.md body with a clear instruction: what it contains, and when the agent should read it.

## Phase 3 — After creation

Validate the generated skill against the full checklist. Present each point with a pass/fail verdict and a short justification.

### Validation checklist (12 points)

1. **Directory name** — lowercase, hyphens, digits only, max 64 characters.
2. **SKILL.md exists** — at the root of the skill directory.
3. **Valid frontmatter** — YAML block between `---` delimiters, parseable without errors.
4. **Description present and compliant** — under 250 characters, keywords front-loaded.
5. **Manual-only flag** — `disable-model-invocation: true` present if and only if the user requested manual-only invocation.
6. **File-pattern activation** — `paths` defined with correct globs if and only if the user specified target files.
7. **Allowed-tools scoped** — pre-approves only the tools strictly necessary for the skill's workflow.
8. **Standing instructions** — body instructions are persistent, not one-shot.
9. **Critical content placement** — critical rules within the first 5,000 tokens of the body.
10. **Supporting files referenced** — every file in subdirectories is explicitly referenced from SKILL.md via `${CLAUDE_SKILL_DIR}`.
11. **Invocation test** — invite the user to test via `/skill-name` direct invocation.
12. **Discoverability test** — invite the user to verify the skill appears in "What skills are available?".

If any point fails, fix the SKILL.md immediately and re-validate.

### Output to user

After validation passes, present:
- The complete directory tree (`find <skill-path> -type f`).
- The invocation command: `/skill-name` (and automatic trigger conditions if applicable).
- A concrete example of usage.
