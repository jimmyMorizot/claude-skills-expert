# Claude Code Skills — Référence Technique Officielle

> **Source primaire unique** : https://code.claude.com/docs/en/skills.md (consultée le 11 avril 2026)
> **Standard ouvert** : https://agentskills.io
> **Repo de référence** : https://github.com/anthropics/skills
> **Audience** : agent Claude Code expert en création de Skills + développeurs CreatisWeb
> **Statut** : document normatif, fidèle à 100% à la documentation Anthropic officielle.

---

## ⚠️ Avertissement anti-folklore

Ce document existe parce que l'écosystème francophone (LinkedIn, YouTube, NotebookLM-generated content) propage des **mythes non sourcés** sur les Skills. Les affirmations suivantes sont **FAUSSES** et doivent être ignorées :

| Mythe folklorique | Réalité documentée |
|---|---|
| « Skills V1 août 2025 → V2 octobre 2025 » | Aucun versionnage officiel. Les Agent Skills suivent le standard ouvert `agentskills.io`. |
| « Tier 1 scan = ~100 tokens » | Le char budget réel est de **8 000 caractères** (1% de la fenêtre de contexte), avec **250 caractères max par description**. |
| « SKILL.md doit faire moins de 5000 tokens » | Aucune limite hard sur le corps. La limite documentée concerne le **lifecycle après compaction** : 5 000 tokens conservés par skill, budget combiné de 25 000 tokens. |
| « Description Pushy = 90% d'activation, vague = 20% » | Chiffres inventés. Conseil officiel : « include keywords users would naturally say » et « front-load the key use case ». |
| « Architecture en 3 Tiers (Scan/Trigger/Immersion) » | Terminologie inventée. Le mécanisme réel : descriptions toujours en contexte, corps chargé à l'invocation, fichiers supports chargés à la demande via instructions du SKILL.md. |
| « Custom commands sont obsolètes » | **Faux**. Custom commands ont **fusionné dans skills**. Les fichiers `.claude/commands/*.md` continuent de fonctionner avec le même frontmatter. |

---

## 1. Définition canonique

Un **Skill** est un répertoire contenant un fichier `SKILL.md` qui étend les capacités de Claude Code. Claude charge automatiquement les skills pertinents en fonction du contexte de la conversation, ou l'utilisateur peut les invoquer manuellement avec `/skill-name`.

**Quand créer un skill** : quand tu colles régulièrement le même playbook, checklist ou procédure multi-étapes dans le chat, ou quand une section de `CLAUDE.md` devient une procédure plutôt qu'un fait. Contrairement au contenu de `CLAUDE.md`, le corps d'un skill ne se charge **que lorsqu'il est utilisé** — la documentation longue ne coûte presque rien jusqu'à ce qu'on en ait besoin.

**Skill ≠ subagent ≠ CLAUDE.md ≠ slash command** : un skill peut s'exécuter inline ou dans un subagent forké (`context: fork`), mais c'est une entité distincte.

---

## 2. Emplacements officiels et précédence

| Niveau | Chemin | Portée |
|---|---|---|
| Enterprise | Voir `managed settings` | Tous les utilisateurs de l'organisation |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | Tous tes projets |
| Project | `.claude/skills/<skill-name>/SKILL.md` | Ce projet uniquement |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Là où le plugin est activé |

**Règle de précédence** : Enterprise > Personal > Project. Les skills de plugin utilisent un namespace `plugin-name:skill-name` et ne peuvent donc jamais entrer en conflit avec les autres niveaux.

**Discovery imbriquée (monorepo)** : Claude Code découvre automatiquement les skills dans les sous-répertoires `.claude/skills/`. Si tu édites un fichier dans `packages/frontend/`, Claude Code cherche aussi dans `packages/frontend/.claude/skills/`. Crucial pour les architectures monorepo CreatisWeb.

**`--add-dir` exception** : contrairement aux subagents/commands/output styles qui ne sont PAS chargés depuis les répertoires additionnels, les skills dans `.claude/skills/` d'un répertoire ajouté **sont chargés automatiquement** avec live change detection (édition à chaud sans restart).

---

## 3. Structure d'un répertoire de skill

```text
my-skill/
├── SKILL.md           # Instructions principales (REQUIS)
├── template.md        # Template optionnel à remplir par Claude
├── examples/
│   └── sample.md      # Exemples de sortie attendue
└── scripts/
    └── validate.sh    # Scripts exécutables par Claude
```

Seul `SKILL.md` est requis. Tous les autres fichiers sont optionnels. **Référence-les explicitement depuis ton `SKILL.md`** pour que Claude sache ce qu'ils contiennent et quand les charger.

**Convention de nommage du répertoire** : lowercase, chiffres et hyphens uniquement, max 64 caractères. Pas d'underscores, pas d'espaces, pas de majuscules.

---

## 4. Spécification complète du frontmatter YAML

Le `SKILL.md` commence par un bloc YAML entre `---`. **Tous les champs sont optionnels**. Seul `description` est recommandé pour que Claude sache quand utiliser le skill.

### Tableau exhaustif des 13 champs officiels

| Champ | Requis | Description |
|---|---|---|
| `name` | Non | Nom d'affichage. Si omis, utilise le nom du répertoire. Lowercase, chiffres et hyphens uniquement, max 64 caractères. |
| `description` | Recommandé | Ce que fait le skill et quand l'utiliser. **Front-load le cas d'usage clé** : au-delà de 250 caractères, la description est tronquée dans le listing pour réduire l'usage de contexte. |
| `argument-hint` | Non | Hint d'autocomplétion. Ex : `[issue-number]` ou `[filename] [format]`. |
| `disable-model-invocation` | Non | `true` empêche Claude de charger automatiquement le skill. Pour les workflows déclenchés manuellement avec `/name`. Défaut : `false`. |
| `user-invocable` | Non | `false` cache le skill du menu `/`. Pour du background knowledge non invocable directement. Défaut : `true`. |
| `allowed-tools` | Non | Outils utilisables sans demande de permission quand le skill est actif. String séparée par espaces ou liste YAML. **Ne restreint pas** les outils — pré-approuve seulement. |
| `model` | Non | Modèle à utiliser quand le skill est actif. |
| `effort` | Non | Niveau d'effort. Options : `low`, `medium`, `high`, `max` (Opus 4.6 uniquement). Override l'effort de session. |
| `context` | Non | `fork` pour exécuter dans un subagent forké. |
| `agent` | Non | Type de subagent à utiliser quand `context: fork` est défini. |
| `hooks` | Non | Hooks scopés au lifecycle du skill. |
| `paths` | Non | Glob patterns limitant l'activation aux fichiers matchant. String comma-separated ou liste YAML. |
| `shell` | Non | `bash` (défaut) ou `powershell` pour les blocs d'injection shell. |

### Matrice d'invocation (table officielle)

| Frontmatter | Tu peux invoquer | Claude peut invoquer | Quand chargé en contexte |
|---|---|---|---|
| (défaut) | Oui | Oui | Description toujours en contexte, corps chargé à l'invocation |
| `disable-model-invocation: true` | Oui | Non | Description **pas** en contexte, corps chargé à ton invocation |
| `user-invocable: false` | Non | Oui | Description toujours en contexte, corps chargé à l'invocation |

---

## 5. Substitutions de variables officielles

Les skills supportent 5 variables de substitution dans le contenu :

| Variable | Description |
|---|---|
| `$ARGUMENTS` | Tous les arguments passés à l'invocation. Si absent du contenu, les arguments sont appendés en `ARGUMENTS: <value>` à la fin. |
| `$ARGUMENTS[N]` | Argument spécifique par index 0-based. `$ARGUMENTS[0]` = premier. |
| `$N` | Raccourci pour `$ARGUMENTS[N]`. `$0` = premier, `$1` = deuxième. |
| `${CLAUDE_SESSION_ID}` | ID de la session courante. Pour logging, fichiers session-specific, corrélation. |
| `${CLAUDE_SKILL_DIR}` | Répertoire contenant le `SKILL.md` du skill. Pour plugin skills, c'est le sous-répertoire du skill, pas la racine du plugin. **À utiliser dans les commandes bash injection** pour référencer scripts/fichiers bundlés indépendamment du cwd. |

Les arguments indexés utilisent un quoting shell-style : `/my-skill "hello world" second` → `$0` = `hello world`, `$1` = `second`.

---

## 6. Lifecycle et compaction (le mécanisme RÉEL, pas le folklore)

Quand un skill est invoqué, le contenu rendu de `SKILL.md` entre dans la conversation **comme un message unique** et y reste jusqu'à la fin de la session. **Claude Code ne re-lit pas le fichier** lors des tours suivants. Conséquence : écris des instructions comme des **standing instructions** applicables tout au long d'une tâche, pas comme des étapes one-shot.

**Auto-compaction** : quand le contexte se remplit et que la conversation est résumée, Claude Code ré-attache la **plus récente invocation de chaque skill** après le résumé, en gardant les **5 000 premiers tokens de chaque skill**. Les skills ré-attachés partagent un **budget combiné de 25 000 tokens**. Le budget est rempli à partir du skill le plus récemment invoqué — les anciens skills peuvent être complètement droppés.

**Implication design** : si ton skill fait plus de 5 000 tokens, seuls les 5 000 premiers survivront à une compaction. **Mets les instructions critiques en haut.**

**Si un skill semble cesser d'influencer le comportement** après la première réponse : le contenu est probablement toujours présent, mais le modèle choisit d'autres outils. Solutions : renforcer la `description` et les instructions, ou utiliser des **hooks** pour appliquer le comportement de manière déterministe. Si tu en as invoqué plusieurs, ré-invoque-le après compaction.

---

## 7. Char budget pour les descriptions

Toutes les descriptions de skills sont chargées en contexte pour que Claude sache ce qui est disponible. **Tous les noms sont toujours inclus**, mais si tu as beaucoup de skills, les **descriptions sont raccourcies** pour tenir dans le char budget.

- **Budget par défaut** : 1% de la fenêtre de contexte, fallback **8 000 caractères**.
- **Cap par description** : **250 caractères**, peu importe le budget total.
- **Variable d'environnement** : `SLASH_COMMAND_TOOL_CHAR_BUDGET` pour ajuster.

**Règle pratique** : front-load les keywords du cas d'usage dans les 250 premiers caractères de chaque description.

---

## 8. Pré-approbation d'outils (`allowed-tools`)

`allowed-tools` **pré-approuve** des outils — il ne **restreint** rien. Tous les outils restent appelables, et tes permission settings continuent de gouverner ceux qui ne sont pas listés. Pour bloquer un skill d'utiliser certains outils, ajoute des **deny rules** dans tes permission settings.

Exemple — un skill commit qui peut lancer git sans demander :

```yaml
---
name: commit
description: Stage and commit the current changes
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---
```

---

## 9. Injection de contexte dynamique

La syntaxe `` !`<command>` `` exécute des commandes shell **avant** que le contenu du skill soit envoyé à Claude. La sortie remplace le placeholder.

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context

Diff: !`gh pr diff`
Status: !`gh pr status`

Summarize the changes above.
```

Claude reçoit la sortie réelle des commandes, pas les commandes elles-mêmes. Idéal pour fetcher des données live (PR, issues, build status, git log).

---

## 10. SKILL.md template complet et fonctionnel

Inspiré de l'exemple `explain-code` officiel + best practices CreatisWeb.

```yaml
---
name: wp-fse-component
description: Generate a WordPress FSE block component following CreatisWeb conventions. Use when scaffolding new Gutenberg blocks, creating block.json, or when the user mentions FSE, full site editing, or block development.
argument-hint: [block-name] [block-category]
allowed-tools: Read Write Bash(npx @wordpress/create-block *)
paths: wp-content/themes/**, blocks/**
---

Generate a WordPress FSE block named `$0` in category `$1`.

## Before scaffolding

- Verify the current theme supports FSE by reading `theme.json`.
- Check if a block with the same name already exists in `blocks/`.
- Read `${CLAUDE_SKILL_DIR}/references/cw-block-conventions.md` for CreatisWeb naming and structure conventions.

## Scaffolding

1. Run `npx @wordpress/create-block@latest $0 --variant=dynamic`.
2. Update `block.json` with category `$1` and the CreatisWeb namespace `creatisweb/$0`.
3. Replace the default render.php with the template at `${CLAUDE_SKILL_DIR}/assets/render.php.template`.

## After scaffolding

- Run `npm run build` from the block directory.
- Verify the block appears in the editor by listing `wp-content/plugins/`.
- Output a summary with: block name, category, file paths created, next steps for the developer.

## Standing instructions for this task

- Never use inline styles. Always use theme.json tokens.
- Never use jQuery. Use vanilla JS or @wordpress/element.
- All user-facing strings must be wrapped in `__()` with the `creatisweb` text domain.
```

**Pourquoi ce template est exemplaire** :
- `description` front-loadée avec keywords (FSE, Gutenberg, block) sous 250 caractères.
- `paths` pour activation contextuelle automatique uniquement dans les répertoires WordPress.
- `allowed-tools` scopé au strict nécessaire.
- Utilisation de `${CLAUDE_SKILL_DIR}` pour référencer les fichiers supports indépendamment du cwd.
- Structure « Avant / Pendant / Après » naturelle (utile, mais pas un dogme).
- **Standing instructions en bas** car le SKILL.md ne sera pas re-lu — elles doivent persister.
- Arguments positionnels `$0` `$1` au lieu de `$ARGUMENTS` pour clarté.

---

## 11. Troubleshooting officiel

### Skill ne se déclenche pas

1. Vérifier que la `description` inclut les keywords que les utilisateurs prononceraient naturellement.
2. Vérifier que le skill apparaît dans `What skills are available?`.
3. Reformuler la requête pour matcher la description.
4. Invoquer directement avec `/skill-name`.

### ⚠️ Bug empirique — `paths` avec globs `**` (non documenté par Anthropic)

**Symptôme** : une skill avec un frontmatter YAML parfaitement valide n'apparaît **pas** dans `What skills are available?`. Aucune erreur visible.

**Cause** : le loader Claude Code rejette silencieusement toute skill dont le champ `paths` contient des wildcards `**`, que ce soit en chaîne comma-separated ou en YAML-liste quoted. Observation confirmée sur Linux avec Claude Code 1.x (avril 2026).

**Workaround** :
- Supprimer le champ `paths` entièrement.
- Encoder les keywords d'activation (noms de fichiers, frameworks, technos) dans la `description`.
- L'auto-invocation contextuelle fonctionne alors normalement.

**Exemples qui cassent** :
```yaml
paths: "**/Dockerfile, **/Caddyfile"
paths:
  - "**/theme.json"
  - "docker/**"
```

**Exemples qui fonctionnent** :
```yaml
paths: Dockerfile, docker-compose.yml
paths:
  - theme.json
  - composer.json
```

### Skill se déclenche trop souvent

1. Rendre la `description` plus spécifique.
2. Ajouter `disable-model-invocation: true` pour invocation manuelle uniquement.

### Descriptions tronquées

1. Augmenter `SLASH_COMMAND_TOOL_CHAR_BUDGET`.
2. Ou trimmer à la source : front-load le cas d'usage clé (cap dur à 250 caractères).

---

## 12. Anti-patterns sourcés

| Anti-pattern | Pourquoi c'est mauvais | Source |
|---|---|---|
| Description vague (`"Helps with stuff"`) | Claude ne peut pas matcher le contexte utilisateur | Troubleshooting officiel |
| Description > 250 caractères avec info clé en fin | Tronquée dans le listing, keywords perdus | Frontmatter reference |
| Instructions one-shot dans SKILL.md | Le fichier n'est pas re-lu après invocation | Skill content lifecycle |
| `name` avec underscores ou majuscules | Convention enfreinte (lowercase + hyphens uniquement) | Frontmatter reference |
| Skill > 5 000 tokens avec instructions critiques en bas | Perdues après compaction | Skill content lifecycle |
| Confier `allowed-tools` pour « restreindre » | `allowed-tools` pré-approuve, ne restreint pas | Pre-approve tools section |
| Créer un skill pour une règle globale (ex: « répondre en français ») | Appartient à `CLAUDE.md`, pas à un skill | Implicite dans la doc « when to create a skill » |
| Ne pas référencer les supporting files depuis SKILL.md | Claude ne saura pas qu'ils existent ni quand les charger | Add supporting files section |

---

## 13. Checklist de validation d'un skill

Avant de considérer un skill comme prêt pour CreatisWeb :

- [ ] Nom du répertoire en lowercase-hyphens, max 64 chars.
- [ ] `SKILL.md` existe à la racine du répertoire.
- [ ] Frontmatter valide entre `---`.
- [ ] `description` présente, sous 250 caractères, avec keywords front-loadés.
- [ ] Si invocation manuelle uniquement : `disable-model-invocation: true`.
- [ ] Si activation contextuelle par fichiers : `paths` défini avec globs.
- [ ] `allowed-tools` scopé au strict minimum.
- [ ] Instructions écrites comme **standing instructions** (pas one-shot).
- [ ] Instructions critiques dans les **5 000 premiers tokens**.
- [ ] Supporting files (templates, scripts, references) **explicitement référencés** dans SKILL.md avec `${CLAUDE_SKILL_DIR}`.
- [ ] Testé via invocation automatique ET via `/skill-name` direct.
- [ ] Le skill apparaît dans `What skills are available?`.

---

## 14. Ressources officielles

- **Doc Skills** : https://code.claude.com/docs/en/skills.md
- **Standard ouvert Agent Skills** : https://agentskills.io
- **Repo officiel skills** : https://github.com/anthropics/skills
- **Subagents** : https://code.claude.com/docs/en/sub-agents
- **Plugins** : https://code.claude.com/docs/en/plugins
- **Hooks** : https://code.claude.com/docs/en/hooks
- **Memory (CLAUDE.md)** : https://code.claude.com/docs/en/memory
- **Commands** : https://code.claude.com/docs/en/commands
- **Permissions** : https://code.claude.com/docs/en/permissions

---

**Fin du document. Toute information non présente ici doit être vérifiée contre la doc officielle avant ingestion par un agent.**
