# Claude Code Skills : référence technique officielle

> **Source primaire** : https://code.claude.com/docs/en/skills.md (relevée le 22 octobre 2026, Claude Code 2.1.308)
> **Standard ouvert** : https://agentskills.io/specification (relevé le 22 octobre 2026)
> **Repo de référence** : https://github.com/anthropics/skills
> **Audience** : agent Claude Code expert en création de skills
> **Statut** : document normatif. Chaque affirmation vient de l'une des deux sources ci-dessus, sauf les passages marqués **Vérifié en local** (test daté, version notée), **Déduction**, **skill-creator** (plugin officiel `skill-creator`, hors des deux sources) ou **Recommandation maison**.

---

## 0. Avertissement anti-folklore

Des contenus non sourcés (LinkedIn, YouTube, synthèses générées) circulent sur les skills. Ce tableau remet chaque affirmation face aux sources.

| Affirmation qui circule | Ce que disent les sources |
|---|---|
| « Skills V1 août 2025, V2 octobre 2025 » | Aucun versionnage officiel de la spécification. Les skills suivent le standard ouvert agentskills.io ; Claude Code ajoute ses extensions, datées par version de Claude Code. |
| « Architecture en 3 Tiers (Scan / Trigger / Immersion) » | Le mot « Tier » n'existe pas dans les sources. Le mécanisme réel s'appelle *progressive disclosure* (agentskills.io) : métadonnées chargées au démarrage, corps chargé à l'activation, fichiers supports chargés à la demande. |
| « Le scan coûte ~100 tokens » | agentskills.io donne « ~100 tokens » comme **ordre de grandeur** pour `name` + `description`. Ce n'est pas une limite. La limite réelle côté Claude Code : 1 536 caractères par entrée (`description` + `when_to_use`), dans un budget de listing égal à 1 % de la fenêtre de contexte. |
| « Le SKILL.md doit faire moins de 5 000 tokens » | Recommandation, pas limite : agentskills.io recommande un corps sous 5 000 tokens, et les deux sources recommandent moins de 500 lignes. Contrainte réelle distincte : après compaction, Claude Code ne conserve que les 5 000 premiers tokens de chaque skill invoqué (budget combiné 25 000). |
| « Description pushy = 90 % d'activation » | Chiffres inventés. Conseil officiel : mettre le cas d'usage clé en premier, inclure les mots que l'utilisateur dirait naturellement. |
| « Les custom commands sont obsolètes » | Faux. Elles ont **fusionné** dans les skills : `.claude/commands/deploy.md` et `.claude/skills/deploy/SKILL.md` créent tous deux `/deploy`. |
| « Le champ `paths` casse le chargement » | Faux sur 2.1.308. `paths` est une **activation conditionnelle** : le skill reste invisible tant que Claude n'a pas lu ou modifié un fichier correspondant (section 12). |

---

## 1. Définition

Un skill est un répertoire contenant un `SKILL.md` : un frontmatter YAML entre `---` (quand l'utiliser) suivi d'instructions Markdown (quoi faire). Claude le charge quand il est pertinent, ou l'utilisateur l'invoque avec `/nom-du-skill`.

**Quand créer un skill** : quand on recolle régulièrement les mêmes instructions, checklist ou procédure, ou quand une section de `CLAUDE.md` est devenue une procédure plutôt qu'un fait. Le corps d'un skill ne coûte du contexte qu'une fois utilisé.

**Garder le corps concis** : une fois chargé, le contenu reste dans la conversation, donc chaque ligne est un coût récurrent. Dire quoi faire plutôt que raconter comment ou pourquoi.

**Skills intégrés (bundled)** : `/doctor`, `/code-review`, `/batch`, `/debug`, `/loop`, `/claude-api`, `/run`, `/verify`, `/run-skill-generator`… Un skill à vous du même nom remplace la commande intégrée, mais pas ses alias. Désactivation globale : `disableBundledSkills`.

**Skill nommé `verify` ou `simplify`** (v2.1.286+) : s'il est présent au démarrage (emplacement enterprise, personnel, projet ou répertoire additionnel) et invocable par Claude, les instructions de commit demandent à Claude de l'exécuter juste avant chaque commit (sauf changements de docs ou de tests). Les skills de plugin et ceux synchronisés depuis claude.ai ne comptent pas.

---

## 2. Emplacements, précédence, synchronisation

### 2.1 Emplacements

| Niveau | Chemin | Chargé dans |
|---|---|---|
| Enterprise | `.claude/skills/<nom>/SKILL.md` dans le répertoire des managed settings | Toutes les machines où l'organisation le déploie |
| Personnel | `~/.claude/skills/<nom>/SKILL.md` | Tous les projets de cette machine, pas Cowork ni le cloud |
| Projet | `.claude/skills/<nom>/SKILL.md` | Sessions dans ce dépôt (pas les threads cloud d'un projet) |
| Imbriqué | `<sous-dossier>/.claude/skills/<nom>/SKILL.md` | Sessions lancées dans ou sous ce dossier ; sinon chargé la première fois que Claude lit ou modifie un fichier de ce dossier |
| Répertoire additionnel | `.claude/skills/` d'un dossier passé avec `--add-dir` | Cette session |
| Plugin | `<plugin>/skills/<nom>/SKILL.md` | Là où le plugin est activé, sous `/plugin:nom` |
| Compte claude.ai | Skills activés sur le compte claude.ai | Cowork, cloud, et terminal connecté avec ce compte (section 2.4) |

Règles des dossiers :
- **Liens symboliques** acceptés (enterprise, personnel, projet) : Claude Code lit le `SKILL.md` de la cible et ne charge le skill qu'une fois même si plusieurs emplacements pointent dessus.
- **Noms réservés** : `synced` (n'importe quelle casse) et `anthropic-skills` (ou tout nom commençant par `anthropic-skills:`) ne se chargent pas hors plugin.
- **Caractères refusés** (section 4.4) : un dossier dont le nom en contient ne se charge pas.
- **Fichiers `.claude/commands/*.md`** : ancien format, toujours valide, mêmes champs sauf `name` et `paths`. Préférer un skill pour tout nouveau travail.
- **Dossier de skill devenu plugin** : un `.claude-plugin/plugin.json` dans un dossier de skill personnel ou projet le charge comme plugin `<nom>@skills-dir`.

### 2.2 Monorepos, worktrees, `--add-dir`

- Claude Code charge les skills projet du dossier de lancement **et de chaque parent jusqu'à la racine du dépôt**. `/cd` (v2.1.246+) ajoute ceux du nouveau dossier.
- En worktree, la remontée s'arrête à la racine du worktree ; sans `.claude/skills` à sa racine, Claude Code charge ceux du checkout principal (v2.1.277+).
- Les skills d'un sous-dossier ne se chargent pas au démarrage : seulement quand Claude lit ou modifie un fichier de ce sous-dossier, puis pour toute la session. Avant cela, ils sont absents du menu `/`. `/add-dir <chemin>` (v2.1.257+) les charge plus tôt.
- Deux skills imbriqués de même nom restent disponibles : `/deploy` lance celui de la racine, `/apps/web:deploy` celui du sous-dossier.
- `--add-dir` charge `.claude/skills/`, `.claude/commands/` et `.claude/agents/` du dossier ajouté. `permissions.additionalDirectories` ne donne qu'un accès fichiers et ne charge rien.

### 2.3 Précédence quand deux skills portent le même nom

| Même nom dans | Lequel s'exécute |
|---|---|
| Enterprise, personnel, projet | Enterprise > personnel > projet |
| Un de ces emplacements et un skill intégré | Le vôtre remplace la commande, pas ses alias |
| Un de ces emplacements et une commande intégrée | En terminal local, le vôtre remplace la commande, pas ses alias |
| Un skill et un fichier `.claude/commands/` | Le skill |
| Skill racine et skill imbriqué | Les deux |
| Skill de plugin et skill d'un autre emplacement | Les deux (namespace `/plugin:nom`) |
| N'importe lequel et le nom court d'un skill synchronisé claude.ai | L'autre ; le synchronisé ne répond plus qu'à `/anthropic-skills:nom` |

### 2.4 Skills synchronisés depuis claude.ai

- En terminal connecté avec un compte claude.ai (v2.1.273+), Claude Code télécharge les skills activés sur le compte dans `~/.claude/skills/synced/`, puis vérifie les changements (environ toutes les 10 minutes en activité, 40 minutes au repos) et les applique sans redémarrage.
- Pas de synchronisation avec une clé API, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`, Bedrock, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, le mode bare, `--safe-mode`. En `-p`, `CLAUDE_CODE_SYNC_SKILLS=1` force l'attente du téléchargement.
- **Téléchargement seul, jamais d'envoi** : modifier un fichier sous `synced/` ne change rien sur claude.ai et sera écrasé. Pour modifier un skill synchronisé, le modifier sur claude.ai.
- **Nom de commande** : `/nom` ou `/anthropic-skills:nom`. Si un skill local porte déjà le nom court, `/nom` lance le local et le synchronisé ne répond qu'au nom complet. La comparaison ignore casse, espaces, caractères invisibles et variantes de tirets.
- **Frontmatter d'un skill synchronisé** : s'applique partout ; `allowed-tools` passe par le flux de permissions normal. La description est assainie (caractères de contrôle retirés, chevrons échappés).
- **Corps d'un skill synchronisé**, dans une session locale (ni cloud, ni Cowork) : les commandes `!` ne s'exécutent pas, les références `@` ne sont pas jointes, `${CLAUDE_PROJECT_DIR}` et `${CLAUDE_SESSION_ID}` ne sont pas substitués (ils arrivent en texte brut). En cloud, le corps se comporte comme un skill local ; en Cowork, chaque ligne `!` est remplacée par le texte de `disableSkillShellExecution`.
- `/skills` les liste sous « claude.ai sync ». Arrêter la synchronisation : `syncClaudeAiSkills: false`.

### 2.5 Cowork, cloud, tâches planifiées

Cowork et les sessions cloud (dont les routines cloud) ne lisent pas `~/.claude/skills/` : seulement les skills du compte claude.ai. Un skill uniquement local est « not found » dans une routine cloud. Solutions : l'activer sur le compte claude.ai, ou le committer dans `.claude/skills/` du dépôt (sauf threads cloud d'un projet). Les tâches planifiées du Desktop tournent en local et chargent `~/.claude/skills/`.

### 2.6 Édition à chaud, suppression

- Claude Code surveille `~/.claude/skills/`, `.claude/skills/` du projet et ceux des dossiers `--add-dir` : ajout, modification ou suppression pris en compte sans redémarrage (sauf mode bare). Un dossier de skills de premier niveau créé en cours de session demande `/reload-skills`.
- La détection ne couvre que le texte de `SKILL.md` ; pour un dossier de skill qui est aussi un plugin, `hooks/`, `.mcp.json`, `agents/` demandent `/reload-plugins`.
- Supprimer : effacer le dossier (personnel, projet) ; désactiver le plugin ; désactiver le skill sur claude.ai (le supprimer à la main sous `synced/` ne sert à rien, il revient).

---

## 3. Structure d'un répertoire de skill

```text
mon-skill/
├── SKILL.md          # requis : vue d'ensemble et navigation
├── references/       # documentation chargée à la demande
├── templates/        # modèles à remplir (agentskills.io dit assets/)
├── examples/         # exemples de sortie attendue
└── scripts/          # code exécuté, pas chargé
```

- Seul `SKILL.md` est requis. **Référencer chaque fichier support depuis `SKILL.md`** en disant ce qu'il contient et quand le lire.
- Garder `SKILL.md` sous 500 lignes ; déplacer le détail dans des fichiers séparés, à un seul niveau de profondeur (agentskills.io).
- Nom du dossier (agentskills.io) : minuscules, chiffres, tirets, 64 caractères au plus, pas de tiret au début ni à la fin, pas de `--`, et `name` identique au nom du dossier. La doc Claude Code, elle, ne liste que des caractères refusés (section 4.4).

---

## 4. Frontmatter

### 4.1 Règles de lecture

- Le frontmatter n'est lu que si la **première ligne** du fichier est `---`. Sinon tout le fichier, marqueurs compris, devient le contenu.
- YAML invalide : le skill se charge **sans aucun champ** (`/nom` marche, l'auto-invocation non). `claude --debug` montre l'erreur ; `claude plugin validate ~/.claude/skills` (v2.1.233+) trouve les `SKILL.md` invalides.
- Un champ au nom inexact est **ignoré sans erreur**. Les noms sont en minuscules avec tirets, sauf `when_to_use`.
- Booléens : `true`/`false`, et depuis v2.1.218 `yes`, `no`, `on`, `off`, `1`, `0` (toute casse).
- Tous les champs sont optionnels ; seul `description` est recommandé.

### 4.2 Les 20 champs reconnus par Claude Code

| Champ | Rôle |
|---|---|
| `name` | Nom de commande affiché dans `/`. Défaut : nom du dossier. |
| `description` | Ce que fait le skill et quand l'utiliser. Si absent : première ligne non vide du corps. `description` + `when_to_use` sont tronqués à **1 536 caractères** dans le listing : cas d'usage clé en premier. |
| `when_to_use` | Contexte de déclenchement supplémentaire (phrases, exemples de demandes). Ajouté à `description`, compte dans les 1 536. |
| `argument-hint` | Indice d'autocomplétion, ex. `"[issue-number]"`. Quoter si crochets, sinon YAML lit une liste (effet : voir la note sous ce tableau). |
| `arguments` | Arguments positionnels nommés pour la substitution `$nom`. Chaîne séparée par espaces ou liste YAML ; les noms suivent l'ordre des positions. |
| `disable-model-invocation` | `true` : Claude ne peut pas l'invoquer seul. Empêche aussi le préchargement dans les subagents et l'exécution par une tâche planifiée de session. Défaut `false`. |
| `user-invocable` | `false` : caché du menu `/` et `/nom` ne l'exécute pas ; seul Claude l'invoque. Défaut `true`. |
| `allowed-tools` | Outils utilisables sans demande **pendant le tour qui invoque le skill** ; l'autorisation tombe au message suivant. Chaîne (espaces ou virgules) ou liste YAML. Pré-approuve, ne restreint pas. |
| `disallowed-tools` | Outils retirés tant que le skill est actif ; la restriction tombe au message suivant. Ne peut pas retirer `EndConversation` tant qu'un autre outil reste. |
| `model` | Modèle pour le reste du tour courant (non sauvegardé). Mêmes valeurs que `/model`, ou `inherit`. Ignoré si exclu par `availableModels` ou non supporté en auto mode. Avec `context: fork`, fixe le modèle du subagent. |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max` ; niveaux disponibles selon le modèle. Remplace l'effort de session. |
| `context` | `fork` : exécution dans un subagent isolé (section 11). |
| `agent` | Type de subagent avec `context: fork`. Défaut `general-purpose`. |
| `background` | Avec `context: fork` seulement. `false` : attendre le résultat dans le tour. Défaut `true` (v2.1.218+). |
| `hooks` | Hooks enregistrés à l'invocation, actifs jusqu'à la fin de la session. |
| `paths` | Globs (chaîne séparée par virgules ou liste YAML) qui limitent l'activation aux fichiers correspondants, relatifs au dossier courant de Claude. Format des path-specific rules. Voir section 12. |
| `shell` | `bash` (défaut) ou `powershell` pour les blocs `` !`cmd` `` et ` ```! `. |
| `metadata` | Map libre pour vos outils ; Claude Code n'en fait rien et ignore une valeur qui n'est pas une map. Ne pas réutiliser des noms de champs (`paths`…) comme clés. |
| `license` | Licence du skill (standard agentskills.io). Accepté, sans effet. |
| `compatibility` | Prérequis d'environnement, 500 caractères au plus (standard agentskills.io). Accepté, sans effet. |

**Vérifié en local le 22/10/2026 (2.1.308)** : un `argument-hint: [fichier]` non quoté (lu par YAML comme une liste) n'empêche ni le chargement ni l'invocation du skill. Le rejet « argument-hint must be a string » noté dans une version antérieure de ce document ne se reproduit pas. Quoter reste la forme correcte.

### 4.3 Hors de Claude Code : claude.ai, API, `package_skill.py`

| Canal | Champs autorisés |
|---|---|
| Claude Code (tout emplacement, plugins compris) | Les 20 champs |
| Téléversement claude.ai, Skills API, `package_skill.py` (anthropics/skills) | `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` |

Tout autre champ fait **échouer** le téléversement ou le packaging (pas d'ignorance silencieuse) :

```
Unexpected key(s) in SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name
```

**Constat** : la copie de skill-architect téléversée sur claude.ai le 20/09/2026 contenait `argument-hint` et a été acceptée. La doc du 22/10 annonce un refus : appliquer la règle stricte.

Contraintes du standard agentskills.io sur ces six champs :
- `name` **requis**, 1 à 64 caractères, `a-z`, `0-9`, `-`, pas de tiret au début ni à la fin, pas de `--`, identique au nom du dossier parent.
- `description` **requise**, 1 à **1 024** caractères (plus strict que les 1 536 de Claude Code).
- `compatibility` 1 à 500 caractères ; `metadata` map de chaînes vers chaînes (quoter `"1.0"`) ; `allowed-tools` chaîne séparée par espaces, expérimental.

La doc cite l'injection de commandes comme fonction du corps propre à Claude Code, inopérante dans le chat claude.ai et via l'API ; les substitutions de variables sont à traiter de même (**Déduction** : elles ne sont documentées que pour Claude Code). Un skill limité aux six champs se charge tel quel dans Claude Code. Le standard demande des **chemins relatifs à la racine du skill** pour les fichiers supports.

### 4.4 Nom de commande et caractères refusés

| Emplacement | Source du nom | Exemple |
|---|---|---|
| `~/.claude/skills/` ou `.claude/skills/` | `name` ou nom du dossier (les deux invoquent le skill) | `deploy-staging/` → `/deploy-staging`, ou `/deploy` avec `name: deploy` |
| Imbriqué en conflit de nom | chemin relatif + nom | `/apps/web:deploy` |
| `.claude/commands/x.md` | nom du fichier | `/x` ; sous-dossier `frontend/x.md` → `/frontend:x` |
| Plugin `skills/` | `name` ou dossier, préfixé du plugin | `/mon-plugin:review` |
| Synchronisé claude.ai | nom sur le compte, préfixé | `/anthropic-skills:deploy` ou `/deploy` si libre |

Refusés dans un nom de commande ou un `name` : espace sans chasse, caractère de contrôle, caractère privé ou non attribué (glyphes d'icônes), caractère de direction du texte, blanc autre qu'un espace simple entre deux mots, `<` ou `>`. Un dossier ainsi nommé ne se charge pas ; un `name` ainsi écrit n'est pas affiché ni invocable. Diagnostic : `claude --debug`, chercher `[names]`.

---

## 5. Substitutions de variables

| Variable | Valeur |
|---|---|
| `$ARGUMENTS` | Tous les arguments tels que tapés. Si aucun placeholder ne reçoit d'argument, Claude Code ajoute `ARGUMENTS: <valeur>` à la fin. |
| `$ARGUMENTS[N]` | Argument par index, base 0. |
| `$N` | Raccourci de `$ARGUMENTS[N]` (`$0`, `$1`…). |
| `$nom` | Argument nommé déclaré dans `arguments` (`arguments: [issue, branch]` → `$issue`, `$branch`). |
| `${CLAUDE_SESSION_ID}` | ID de la session. |
| `${CLAUDE_EFFORT}` | Niveau d'effort courant (`low` … `max`), pour adapter les instructions. |
| `${CLAUDE_SKILL_DIR}` | Dossier du `SKILL.md` (pour un plugin : le sous-dossier du skill). À utiliser pour les scripts et fichiers bundlés. |
| `${CLAUDE_PROJECT_DIR}` | Racine du projet (même valeur que pour les hooks et serveurs MCP). |
| `${CLAUDE_PLUGIN_ROOT}` | Dossier d'installation du plugin. Plugins seulement. |
| `${CLAUDE_PLUGIN_DATA}` | Dossier de données persistantes du plugin (survit aux mises à jour). Plugins seulement. |

Règles :
- `${CLAUDE_SKILL_DIR}` et `${CLAUDE_PROJECT_DIR}` (et pour les plugins `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`) sont substitués dans le corps **et** dans les règles Bash de `allowed-tools`. Même variable aux deux endroits = script bundlé lancé sans demande :
  ```yaml
  allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)
  ```
- Arguments indexés en quoting shell : `/skill "hello world" second` → `$0` = `hello world`, `$1` = `second`.
- Placeholder indexé sans argument : laissé tel quel. Placeholder nommé sans argument : chaîne vide.
- Une valeur d'argument contenant `$1` ou `$ARGUMENTS` est insérée littéralement ; les `${CLAUDE_*}` sont substitués après.
- Écrire un `$` littéral devant un chiffre, `ARGUMENTS` ou un nom déclaré : `\$1.00`. L'échappement ne protège pas les `${CLAUDE_*}`.

---

## 6. Qui invoque le skill

| Frontmatter | L'utilisateur peut | Claude peut | Chargement en contexte |
|---|---|---|---|
| (défaut) | Oui | Oui | Description toujours en contexte, corps à l'invocation |
| `disable-model-invocation: true` | Oui | Pas de lui-même | Description **hors** contexte, corps à l'invocation |
| `user-invocable: false` | Non | Oui | Description toujours en contexte, corps à l'invocation |

- `disable-model-invocation: true` pour les actions à effets de bord (`/deploy`, `/commit`, envoi de message). Si Claude tente quand même, Claude Code bloque l'appel et lui interdit de reproduire les étapes autrement.
- `/nom` **en début de message** exécute le skill. Après du texte (« vas-y et /deploy en staging »), le nom vaut seulement autorisation : Claude juge s'il doit le lancer. Sans slash, aucune autorisation.
- Empilement en terminal : `/write-tests /fix-issue 123` charge les deux (jusqu'à 1 + 5 skills). En `-p` ou SDK, seul le premier se charge.
- Subagents avec `skills` préchargés : le contenu complet est injecté au démarrage du subagent.

---

## 7. Cycle de vie et compaction

- À l'invocation, le `SKILL.md` rendu entre dans la conversation **en un seul message** et y reste. Claude Code **ne relit pas** le fichier ensuite : écrire des **consignes permanentes**, pas des étapes ponctuelles.
- La persistance concerne les instructions, pas les permissions : `allowed-tools` tombe au message suivant ; une nouvelle invocation le réapplique pour son tour.
- Réinvocation à contenu identique : simple note « déjà chargé ». Contenu différent (arguments, sortie d'injection) : contenu complet ajouté à nouveau.
- **Compaction** : Claude Code rattache après le résumé la dernière invocation de chaque skill, **5 000 premiers tokens** par skill, **budget combiné 25 000 tokens**, rempli à partir du plus récent. Les plus anciens peuvent disparaître. Mettre les instructions critiques en haut.

---

## 8. Budget du listing des descriptions

- Le listing contient toujours tous les noms. S'il déborde, Claude Code **retire des descriptions**, en commençant par les skills les moins invoqués.
- Budget : **1 % de la fenêtre de contexte** du modèle. Réglages : `skillListingBudgetFraction` (ex. `0.02`) ou `SLASH_COMMAND_TOOL_CHAR_BUDGET` (nombre fixe de caractères).
- Plafond par entrée : **1 536 caractères** (`description` + `when_to_use`), réglable par `skillListingMaxDescChars`.
- `skillOverrides` en `"name-only"` libère du budget. `/doctor` estime le coût du listing ; la ligne Skills de `/context` montre la taille réelle après budget (depuis v2.1.196) ; `--debug` signale le débordement.

---

## 9. Outils : `allowed-tools`, `disallowed-tools`, permissions

- `allowed-tools` pré-approuve pour le tour d'invocation ; tous les outils restent appelables et les réglages de permission gouvernent le reste. Pour une approbation de session, utiliser des règles allow dans les settings.
- **La confiance de l'espace de travail ne filtre pas ce champ** : un skill projet applique son `allowed-tools` même en `-p` dans un dossier jamais approuvé. Relire les `allowed-tools` des skills d'un dépôt avant d'y lancer Claude Code.
- `allowManagedPermissionRulesOnly` (managed settings, v2.1.282+) : `allowed-tools` des skills personnels et projet ignoré ; `/status` liste les skills concernés.
- `disallowed-tools` retire des outils tant que le skill est actif (ex. `AskUserQuestion` pour une boucle autonome). Pour bloquer partout : règles deny.
- Restreindre l'accès aux skills : `Skill` en deny (tous), `Skill(commit)` (nom exact), `Skill(deploy *)` (préfixe). Un deny sur un nom court bloque aussi les variantes imbriquées. Pour autoriser un skill synchronisé sans demande : `Skill(anthropic-skills:pdf)`, ou `Skill(anthropic-skills *)` pour tous.

---

## 10. Injection de contexte dynamique

- `` !`commande` `` exécute la commande **avant** l'envoi du contenu à Claude ; la sortie remplace la ligne. Bloc multi-lignes : bloc de code ouvert par ` ```! `.
- Reconnu seulement en début de ligne ou après un blanc (`KEY=!`cmd`` reste du texte). Une seule passe : la sortie n'est pas réanalysée.
- Exécution par l'outil Bash (ou PowerShell selon `shell`) dans le **dossier courant de la session**, qui bouge avec `cd` : utiliser `${CLAUDE_SKILL_DIR}` ou `${CLAUDE_PROJECT_DIR}`. stderr fusionné dans stdout (bash). Timeout de l'outil (2 min par défaut).
- **Un échec annule toute l'invocation** (`Shell command failed for pattern "..."`) : Claude ne voit rien du skill. Tout code de sortie non nul échoue, sauf code 1 des commandes de recherche ou comparaison. Ajouter `|| true` aux scripts de vérification qui sortent en 1.
- Permissions : jamais de demande pendant le rendu. Une règle deny annule l'invocation ; hors auto mode, tout ce qui n'est pas « allow » l'annule aussi. Pré-approuver la commande dans `allowed-tools`.
- `"disableSkillShellExecution": true` remplace chaque commande par `[shell command execution disabled by policy]` (sauf skills intégrés et managed).
- Jamais exécuté pour un skill synchronisé depuis claude.ai, sur la machine locale (v2.1.228+).
- Mettre `ultrathink` dans le contenu demande un raisonnement plus profond quand le skill tourne.
- **Vérifié en local le 22/10/2026 (2.1.308)** : la syntaxe est reconnue y compris dans un span de code Markdown et dans un commentaire HTML, dès qu'elle ouvre une ligne ou suit un blanc. En mode de permission par défaut, une commande non pré-approuvée annule l'invocation (`Shell command permission check failed for pattern ...`) ; en mode auto, Claude reçoit l'ordre de la lancer et la lance. Les variables `${CLAUDE_*}` sont de même substituées partout dans le corps, sans échappement possible (doc, section 5). **Ne jamais écrire une injection ni une variable à titre d'exemple dans un SKILL.md** ; ce fichier de référence n'est pas rendu, il peut les montrer.

---

## 11. Exécution dans un subagent (`context: fork`)

- Claude Code lance un subagent du type `agent` (défaut `general-purpose`) avec le contenu du skill comme prompt. Il **ne voit pas l'historique** : le skill doit se suffire. Ce n'est pas un fork de la conversation.
- Par défaut en **arrière-plan** (v2.1.218+) : le résultat arrive à la fin. `background: false` pour attendre dans le tour. Attente forcée aussi en `-p`/SDK, avec `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, si une invocation du même skill tourne déjà, ou depuis une tâche planifiée de session. Un agent de workflow qui invoque un skill forké attend toujours son résultat (v2.1.295+).
- En arrière-plan, le subagent a le **jeu d'outils réduit** des subagents d'arrière-plan, et ses modifications échappent aux checkpoints (`/rewind` ne les annule pas).
- `Explore` et `Plan` démarrent sans CLAUDE.md ni git status : tout mettre dans le SKILL.md.
- Réservé aux skills avec une tâche explicite ; des consignes sans tâche produisent un résultat vide.

---

## 12. Le champ `paths` : activation conditionnelle

**Documenté** : avec `paths`, Claude charge le skill automatiquement seulement quand il travaille sur des fichiers correspondants. Motifs relatifs au dossier courant ; un fichier hors de ce dossier (worktree voisin, même ajouté par `/add-dir`) ne correspond pas. Les fichiers `.claude/commands/` ne supportent pas `paths`.

**Vérifié en local le 22 octobre 2026, Claude Code 2.1.308** (`claude -p`, sortie `stream-json`, 3 skills canaris dans un dépôt jetable) :
- au démarrage, seul le canari **sans** `paths` figure dans la liste des skills (`claude -p`, message `init`) ; les deux canaris avec `paths` (`"*.twig"` en chaîne, et liste YAML `"**/*.twig"` + `composer.json`) en sont absents ;
- `/canari-avec-paths` passé en prompt de `claude -p` au démarrage : « commande non installée » (le menu `/` interactif n'a pas été testé) ;
- après lecture de `sous/page.twig`, un événement `commands_changed` ajoute les deux canaris ; Claude les invoque et ils répondent correctement. `"*.twig"` a donc correspondu à un fichier situé dans un sous-dossier ;
- témoin négatif (second run, même jour) : un canari `paths: "*.php"` reste absent après la lecture de `sous/page.twig`, quand le canari `"*.twig"` apparaît. L'activation dépend donc bien de la correspondance du motif.

Conséquences :
- Un skill avec `paths` est **invisible, y compris pour `/nom`** (constaté en `-p`), tant qu'aucun fichier correspondant n'a été lu ou modifié dans la session. Après activation, l'invocation par Claude marche ; un `/nom` tapé après activation n'a pas été testé.
- Le « bug de chargement » relevé en juin 2026 sur la 2.1.160 (skill absent de la liste) s'explique probablement par ce comportement : un skill absent tant qu'aucun fichier correspondant n'est ouvert. Le protocole de juin n'est pas conservé ; non retesté sur la 2.1.160.
- `paths` est refusé au téléversement claude.ai (section 4.3).

---

## 13. Contrôler la visibilité, repérer les skills inutiles

`skillOverrides` dans les settings (le menu `/skills` l'écrit : `Espace` pour changer, `Échap` pour enregistrer dans `.claude/settings.local.json`) :

| Valeur | Listé à Claude | Menu `/` |
|---|---|---|
| `"on"` (défaut) | Nom et description | Oui |
| `"name-only"` | Nom seul | Oui |
| `"user-invocable-only"` | Caché | Oui |
| `"off"` | Caché | Caché |

Ne s'applique pas aux skills de plugin (gérés par `/plugin`). `/skill-doctor` (v2.1.252+) montre le coût en contexte et l'usage de chaque skill, et signale ceux jamais invoqués.

---

## 14. Évaluer un skill

- Voir un skill se déclencher prouve qu'il est trouvé, pas qu'il fait ce qu'on veut. Mesurer séparément **le déclenchement** et **la qualité du résultat**.
- Méthode officielle : quelques prompts réalistes, chacun dans une **session neuve** avec le skill puis sans (skill personnel ou projet mis en `"off"` dans `skillOverrides`), et comparer. La session neuve évite que le contexte de rédaction masque les trous des instructions.
- Skill de plugin : `claude plugin eval` (avec et sans plugin, graders, code de sortie non nul sous un seuil ; grader `tool_used: Skill` pour mesurer le déclenchement).
- Plugin **skill-creator** (`/plugin install skill-creator@claude-plugins-official`) : cas de test dans `evals/evals.json`, un subagent par cas, notation dans `grading.json`, comparaison avec et sans skill dans `benchmark.json`, A/B à l'aveugle entre deux versions, réglage de la description par prompts qui doivent et ne doivent pas déclencher, rapport HTML. Formats non interchangeables avec `claude plugin eval`.
- **Vérifié en local** (22/10/2026, 2.1.308) : en `claude -p ... --output-format stream-json --verbose`, le message `system`/`init` liste les skills chargés (clé `skills`), les événements `commands_changed` montrent les ajouts en cours de session, et chaque invocation apparaît comme un `tool_use` de l'outil `Skill`. C'est une mesure directe du déclenchement, mais un run n'est qu'un tirage : répéter chaque requête (**skill-creator** : 3 runs par requête par défaut). Lancer ces tests dans un dossier jetable : en mode auto, la tâche s'exécute pour de vrai.

---

## 15. Dépannage

**Le skill ne se déclenche pas**
1. La `description` contient-elle les mots que l'utilisateur dirait ?
2. Le skill apparaît-il dans « What skills are available? » ?
3. Reformuler la demande ; invoquer `/nom` directement.
4. `/nom` inconnu : nom refusé (section 4.4) ? Skill avec `paths` sans fichier correspondant touché (section 12) ? Skill imbriqué pas encore chargé (section 2.2) ?
5. YAML invalide : `/nom` marche mais pas l'auto-invocation ; `--debug` ou `claude plugin validate`.
6. Demande trop simple : Claude la traite seul sans skill (**skill-creator**). Tester avec une demande substantielle.

**Le skill se déclenche trop souvent** : description plus précise, ou `disable-model-invocation: true`.

**Claude cesse de suivre le skill**
- Règle qui doit tenir à chaque fois : la passer en **hook** (éventuellement dans le frontmatter `hooks` du skill).
- Consigne de jugement : la formuler pour toute la tâche (« lancer les tests après chaque modification »).
- Après compaction : réinvoquer le skill ; instructions importantes en haut.

**Descriptions coupées** : section 8.

**Skills personnels disparus** : regarder `~/.claude/skills/.trash/` (rétention 30 jours par défaut). Avant v2.1.280, un `manifest.json` dans `~/.claude/skills/` pouvait y déplacer des dossiers.

---

## 16. Exemple de SKILL.md complet

```yaml
---
name: wp-fse-component
description: Generate a WordPress FSE block component following project conventions. Use when scaffolding new Gutenberg blocks, creating block.json, or when the user mentions FSE, full site editing, or block development.
argument-hint: "[block-name] [block-category]"
arguments: block category
allowed-tools: Read Write Bash(npx @wordpress/create-block@latest *)
---

Generate a WordPress FSE block named `$block` in category `$category`.

## Before scaffolding

- Verify the current theme supports FSE by reading `theme.json`.
- Check if a block with the same name already exists in `blocks/`.
- Read `${CLAUDE_SKILL_DIR}/references/block-conventions.md` for naming and structure conventions.

## Scaffolding

1. Run `npx @wordpress/create-block@latest $block --variant=dynamic`.
2. Update `block.json` with category `$category` and the project namespace.
3. Replace the default render.php with `${CLAUDE_SKILL_DIR}/templates/render.php.template`.

## After scaffolding

- Run `npm run build` from the block directory.
- Output a summary: block name, category, files created, next steps.

## Standing instructions for this task

- Never use inline styles. Always use theme.json tokens.
- Never use jQuery. Use vanilla JS or @wordpress/element.
- Wrap all user-facing strings in `__()` with the project text domain.
```

Pourquoi il tient :
- description avec les mots-clés en tête (FSE, Gutenberg, block), courte ;
- pas de `paths` : le skill doit répondre à `/wp-fse-component` dès le début de session, avant tout fichier ouvert ;
- `arguments` nommés : `$block` et `$category` plus lisibles que `$0` `$1` ;
- `allowed-tools` limité au nécessaire ; fichiers supports via `${CLAUDE_SKILL_DIR}` ;
- consignes permanentes en bas, car le fichier n'est pas relu.

Version claude.ai du même skill : supprimer `argument-hint` et `arguments`, remplacer `$block`/`$category` par une consigne qui demande le nom et la catégorie, remplacer `${CLAUDE_SKILL_DIR}/` par des chemins relatifs (`references/block-conventions.md`).

---

## 17. Anti-patterns sourcés

| Anti-pattern | Pourquoi | Source |
|---|---|---|
| Description vague (« Helps with stuff ») | Claude ne peut pas faire correspondre la demande | Troubleshooting |
| Info clé en fin de description longue | Tronquée à 1 536 caractères, ou retirée si le budget déborde | Frontmatter reference, section 8 |
| Instructions ponctuelles | Le fichier n'est pas relu | Skill content lifecycle |
| Règles critiques en bas d'un long skill | Perdues après compaction (5 000 premiers tokens) | Skill content lifecycle |
| `allowed-tools` pour « restreindre » | Pré-approuve seulement ; utiliser `disallowed-tools` ou deny | Pre-approve tools |
| Croire que `allowed-tools` dure toute la session | Tombe au message suivant | Pre-approve tools |
| `paths` sur un skill qu'on appelle par `/nom` | Invisible tant qu'aucun fichier correspondant n'est touché | Section 12 |
| Champ Claude Code dans un skill pour claude.ai | Téléversement refusé (« Unexpected key(s) ») | Using frontmatter outside Claude Code |
| `${CLAUDE_SKILL_DIR}` ou `!` dans un skill pour claude.ai | Non fonctionnels hors Claude Code ; le standard veut des chemins relatifs | Idem, agentskills.io |
| Modifier un skill sous `~/.claude/skills/synced/` | Jamais renvoyé à claude.ai, écrasé à la sync | Skills synced from claude.ai |
| Skill pour une règle globale (« réponds en français ») | Relève de `CLAUDE.md` | When to create a skill |
| Fichier support non référencé | Claude ignore qu'il existe | Add supporting files |
| Commande injectée qui peut sortir en 1 sans `\|\| true` | Annule toute l'invocation | When an injected command fails |
| Injection ou variable écrite à titre d'exemple dans le corps | Exécutée ou substituée, même entre backticks ou dans un commentaire HTML | Section 10 (vérifié en local) |

---

## 18. Checklist de validation

- [ ] Nom du dossier : minuscules, chiffres, tirets, 64 caractères max, pas de tiret en bord ni `--` ; `name` identique au dossier.
- [ ] `SKILL.md` à la racine, `---` en première ligne, YAML valide.
- [ ] `description` présente, cas d'usage en tête ; `description` + `when_to_use` sous 1 536 caractères (sous 1 024 pour claude.ai).
- [ ] Champs limités à ceux de la section 4.2 (Claude Code) ou aux six de la section 4.3 (claude.ai, API).
- [ ] `disable-model-invocation: true` si et seulement si invocation manuelle voulue.
- [ ] `paths` seulement pour un skill lié à des fichiers, jamais pour un skill appelé par `/nom` en début de session, jamais pour claude.ai.
- [ ] `allowed-tools` au strict nécessaire.
- [ ] Consignes permanentes ; règles critiques dans les 5 000 premiers tokens ; corps sous 500 lignes.
- [ ] Fichiers supports référencés (`${CLAUDE_SKILL_DIR}` pour Claude Code, chemins relatifs pour claude.ai).
- [ ] Commandes injectées robustes (`|| true` si sortie 1 attendue) ; aucune injection ni variable écrite à titre d'exemple dans le corps (section 10).
- [ ] Testé : déclenchement automatique, `/nom`, comparaison avec et sans skill en session neuve.

---

## 19. Ressources officielles

- Skills (Claude Code) : https://code.claude.com/docs/en/skills.md
- Standard Agent Skills : https://agentskills.io/specification
- Évaluer un skill : https://agentskills.io/skill-creation/evaluating-skills
- Bonnes pratiques d'écriture : https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Skills API : https://docs.claude.com/en/api/skills-guide
- Repo officiel : https://github.com/anthropics/skills
- Subagents : https://code.claude.com/docs/en/sub-agents
- Plugins : https://code.claude.com/docs/en/plugins/overview
- Hooks : https://code.claude.com/docs/en/hooks
- Permissions : https://code.claude.com/docs/en/permissions

---

**Fin du document. Toute information absente d'ici se vérifie contre la doc officielle avant usage.**
