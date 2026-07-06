---
name: skill-architect
description: Create, scaffold, test and improve Claude Code skills with spec-compliant SKILL.md and frontmatter. Use when building new skills, generating SKILL.md, testing or optimizing a skill, or checking conformance against the official Anthropic spec.
argument-hint: "[skill-name]"
allowed-tools: Read Write Bash(mkdir *) Bash(ls *) Bash(find *) Bash(cp *)
---

<!--
Description length: 242/250 characters. The buffer is intentional — all keywords
are needed for accurate auto-invocation. Do not shorten without verifying that
"spec-compliant", "frontmatter", "testing or optimizing" and "Anthropic spec"
remain present in the description.
-->

# Skill Architect

**CRITICAL — Read before any action:** Before creating or modifying any skill, read the official Anthropic Skills specification at `${CLAUDE_SKILL_DIR}/references/skills-spec-officielle.md`. This is the single source of truth for frontmatter fields, variable substitutions, lifecycle behavior, and placement rules. Never rely on pre-trained knowledge about skills — always verify against this file.

**Anti-folklore rule:** Never use the following terms in any skill you generate — they do not exist in the official Anthropic specification and must never appear in generated SKILL.md files:
- "Tier 1", "Tier 2", "Tier 3"
- "V1", "V2" (as skill specification versions)
- "Objectif Supreme"
- "~100 tokens scan"
- "Architecture Indentee chronologique"

If a user mentions these concepts, explain they are undocumented folklore and redirect to the embedded spec.

**Cas particulier « pushy »** : hors spec, mais le skill-creator natif d'Anthropic recommande des descriptions « un peu pushy » contre le sous-déclenchement. Choix assumé ici : description **sobre, keywords front-loadés** — une description gonflée pousse l'agent à suivre la description au lieu de lire le corps du skill. Si l'utilisateur cite le natif, expliquer ce choix (ce n'est pas du folklore, c'est un arbitrage différent) ; la Phase 5 traite le sous-déclenchement par le test, pas par l'inflation.

## Standing rules for all skill creation

These rules apply throughout the entire session, for every skill generated:

- Every generated SKILL.md must have valid YAML frontmatter between `---` delimiters.
- Only use frontmatter fields documented in the spec (section 4). The official fields are: `name`, `description`, `argument-hint`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell`. No other field is permitted. **Exception : ne JAMAIS émettre `paths` — bug de chargement Claude Code 2.x, voir la section ci-dessous.**
- The `description` field must be present, under 250 characters, with keywords front-loaded that users would naturally say.
- Directory names: lowercase, digits, and hyphens only, max 64 characters. No underscores, no spaces, no uppercase.
- Write all SKILL.md body instructions as **standing instructions** (persistent across the session), never as one-shot steps that become irrelevant after execution.
- Place critical instructions within the **first 5,000 tokens** of the body — only this portion survives context compaction.
- Reference supporting files via `${CLAUDE_SKILL_DIR}/`, never via hardcoded absolute paths.
- The `allowed-tools` field **pre-approves** tools — it does **not restrict** them. Scope it to the minimum necessary.
- Include only frontmatter fields relevant to the specific skill. Omit fields that would use default values.

### ⚠️ Bug de chargement Claude Code — champ `paths` (vérifié CC 2.1.160, juin 2026)

**Empirique, hors spec officielle.** Sur Claude Code 2.x, le loader rejette **en silence** tout skill dont le frontmatter contient un champ `paths`, **quelle que soit sa valeur** : noms de fichiers exacts (`composer.json`), glob simple (`*.twig`), glob `**`, en chaîne comma-separated comme en liste YAML. Le skill n'apparaît jamais dans la liste, aucun message d'erreur, `/reload-skills` affiche "no changes". (Sur CC 1.x en avril 2026, seuls les `**` cassaient ; le bug s'est élargi à toute valeur sur 2.x — vérifié sur 2.1.160 via 7 canaris, seul le skill SANS `paths` charge.)

**Règle obligatoire :** ne JAMAIS émettre de champ `paths` dans un skill généré, tant que le bug persiste côté Claude Code. Pour cibler des fichiers, encoder les mots-clés de déclenchement (types de fichiers, noms de techno, framework) dans `description` — l'auto-invocation par contexte marche de façon fiable.

**Note :** les clés frontmatter inconnues sont *ignorées* sans casser le chargement (vérifié avec un champ `globs` bidon : le skill charge, mais le champ ne fait rien). Seul `paths`, clé *reconnue* au traitement buggé, fait planter. Remplacer `paths` par un champ inventé (`globs`, etc.) ne sert donc à rien.

Lors d'un audit d'un skill absent de la liste : vérifier la présence de `paths` en premier, et le supprimer.

### Compatibilité plateformes — un SKILL.md, 3 schémas

Un SKILL.md peut être consommé par 3 plateformes aux frontmatter **différents**. Ne JAMAIS présenter les champs Claude Code comme universels. Toujours demander/déduire la cible avant de choisir les champs.

| Champ frontmatter | Claude Code | claude.ai (standard ouvert) | Agents VS Code |
|---|:---:|:---:|:---:|
| `name`, `description` | ✅ (`description` requise) | ✅ (les 2 requis) | ✅ |
| `argument-hint`, `disable-model-invocation`, `user-invocable`, `context` | ✅ | ✅ standard | ✅ |
| `allowed-tools`, `disallowed-tools`, `model`, `effort`, `agent`, `hooks`, `paths`, `shell`, `arguments`, `when_to_use` | ✅ extensions CC | ❌ hors standard (ignoré ou refusé) | ❌ refusé |
| `license`, `compatibility`, `metadata` | ❌ | ✅ standard | ✅ |

Règles selon la cible :
- **Skill Claude Code** : champs CC autorisés, SAUF `paths` (bug 2.x ci-dessus).
- **Skill claude.ai** (téléversé en zip via Réglages → Fonctionnalités) : frontmatter **minimal `name` + `description`**. Aucune extension CC (`allowed-tools`, `paths`, `model`…) — claude.ai ne les supporte pas. Réf. : standard ouvert agentskills.io.
- **Cible inconnue / portable** : se limiter à `name` + `description` + champs standard.

## Principes d'écriture (appliqués en Phase 2, vérifiés en Phase 3)

- **Expliquer le pourquoi.** Préférer une consigne motivée (« vérifier X, car Y casse sinon ») aux MUST/NEVER en majuscules. Un impératif nu invite le modèle à négocier ; une raison compréhensible le fait adhérer. Réserver les majuscules aux 2-3 règles réellement non négociables.
- **Généraliser, ne pas overfitter.** Un skill sera utilisé sur des cas jamais vus. Si une règle ne sert qu'à faire passer l'exemple qui l'a inspirée, la reformuler en principe général ou la supprimer.
- **Bundler le travail répété.** Si les tests (Phase 4) montrent que chaque run réécrit le même script ou refait la même séquence, extraire ce travail dans `scripts/` ou `references/` et faire pointer le SKILL.md dessus. Écrire une fois, réutiliser à chaque invocation.
- **Rester maigre.** Chaque ligne du corps coûte du contexte à chaque activation. Supprimer ce qui ne change pas le comportement du modèle.

## Phase 1 — Before creation

When invoked with `/skill-architect $0`, start by gathering requirements. Ask the user the following calibration questions before writing any file:

1. **Skill name:** Confirm `$0` is the intended name. Validate: lowercase, hyphens, digits only, max 64 characters. Propose a correction if it violates the convention.
2. **Purpose:** What should this skill enable Claude to do? Request a concrete description of the desired behavior or workflow.
3. **Scope and placement:** Where should this skill live?
   - Personal: `~/.claude/skills/$0/` (available across all projects)
   - Project: `.claude/skills/$0/` (this project only)
   - Plugin: `<plugin>/skills/$0/` (scoped to plugin activation)
4. **Target files:** Y a-t-il des fichiers où ce skill devrait s'auto-activer ? **⚠️ Ne PAS utiliser le champ `paths` — il casse le chargement sur Claude Code 2.x quelle que soit sa valeur.** À la place, encoder les mots-clés de ciblage (types de fichiers, noms de techno, framework) dans la `description` ; l'auto-invocation par contexte s'en charge.
5. **Invocation mode:** Should Claude auto-invoke this skill when the conversation context matches, or should it be manual-only? (maps to `disable-model-invocation: true` if manual-only)
6. **Tools needed:** Which tools should be pre-approved without permission prompts? (maps to `allowed-tools`). Examples: `Read`, `Write`, `Bash(npm *)`, `Bash(git *)`.
7. **Supporting files:** Does the skill need bundled references, templates, or scripts? If yes, describe their purpose.
8. **Audience du skill :** qui l'utilisera ? (développeur / non-développeur / mixte). Pour une audience non-dev, le SKILL.md généré explique brièvement les termes techniques au premier usage (« JSON », « assertion »…) et privilégie des instructions pas-à-pas.

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
- Add `argument-hint` only if the skill accepts arguments. **Si la valeur contient des crochets, la quoter** : `argument-hint: "[filename]"`. Sinon YAML la lit comme une liste et le skill est rejeté avec « argument-hint must be a string ».
- Add `allowed-tools` only if tools need pre-approval.
- Ne JAMAIS ajouter `paths` : ce champ casse le chargement sur Claude Code 2.x quelle que soit sa valeur. Encoder les mots-clés de ciblage dans `description` à la place.
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
- Use variable substitutions where applicable — see complete list in `${CLAUDE_SKILL_DIR}/references/skills-spec-officielle.md` section 5.
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
6. **Absence de `paths`** — le champ `paths` doit être ABSENT du frontmatter (il casse le chargement sur CC 2.x quelle que soit sa valeur). S'il est présent, FAIL : le supprimer et déplacer les mots-clés de ciblage dans `description`.
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

Then move to Phase 4 — a skill that has never run on a real case is not finished.

## Phase 4 — Test réel

La checklist (Phase 3) prouve la conformité, pas l'utilité. Tester le skill sur des cas réels avant de le déclarer terminé.

1. **Proposer 2-3 prompts de test réalistes** — ce qu'un vrai utilisateur taperait, avec des détails concrets (chemins, noms de fichiers, contexte métier), pas des requêtes abstraites. Les faire valider par l'utilisateur avant de lancer.
2. **Lancer les runs en subagents, dans le même tour** : pour chaque prompt, un run AVEC le skill (le subagent lit le SKILL.md généré puis exécute la tâche) et un run SANS (baseline — il révèle ce que le skill apporte réellement). Sans subagents disponibles (claude.ai), dérouler soi-même le skill sur chaque prompt, séquentiellement, et sauter la baseline.
3. **Comparer et présenter** : pour chaque prompt, montrer les résultats des deux runs, pointer les différences concrètes (qualité, respect des conventions, temps), demander le feedback de l'utilisateur.
4. **Améliorer puis re-tester** : appliquer le feedback au SKILL.md (en respectant les Principes d'écriture — généraliser, pas de rustine overfittée sur le cas de test), relancer les mêmes prompts. Répéter jusqu'à satisfaction ou absence de progrès.
5. **Signal de bundling** : si les runs réécrivent tous le même code ou refont la même séquence, extraire ce travail dans `scripts/`/`references/` (cf. Principes d'écriture).

## Phase 5 — Optimisation de la description (optionnelle, Claude Code uniquement)

La description est le mécanisme de déclenchement automatique. Pour un skill destiné à l'auto-invocation :

1. Écrire 6-8 requêtes de test : moitié qui DOIVENT déclencher (formulations variées, langage casual, sans jamais nommer le skill), moitié qui ne doivent PAS déclencher — privilégier les **near-misses** (mêmes mots-clés, besoin différent) plutôt que le hors-sujet évident, qui ne teste rien.
2. Pour chaque requête : `claude -p "<requête>"` et observer si le skill est consulté.
3. Ajuster la description (keyword manquant, contexte à préciser), re-tester. 2-3 itérations suffisent — sélectionner sur l'ensemble des requêtes, pas sur la dernière qui échouait (anti-overfit).

Note : une requête trop simple ne déclenche aucun skill (Claude la traite seul) — tester avec des demandes substantielles, multi-étapes.
