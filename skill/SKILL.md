---
name: skill-architect
description: Create, scaffold, test and improve Claude Code and claude.ai skills with a spec-compliant SKILL.md and frontmatter. Use when building a new skill, writing or auditing a SKILL.md, packaging a skill zip for claude.ai, testing or optimizing a skill's triggering, or checking conformance with the official Anthropic spec.
argument-hint: "[skill-name]"
allowed-tools: Read Write Bash(mkdir *) Bash(ls *) Bash(find *) Bash(cp *)
---

<!--
Description : 317 caractères. Limites : 1 536 dans Claude Code (description + when_to_use),
1 024 pour le zip claude.ai. Rester court reste utile : quand le listing déborde, les skills
les moins invoqués perdent leur description en premier. Mots-clés à garder : spec-compliant,
SKILL.md, frontmatter, claude.ai, zip, testing, triggering, Anthropic spec.
-->

# Skill Architect

**CRITICAL, read before any action:** before creating, modifying or auditing any skill, read the official specification at `${CLAUDE_SKILL_DIR}/references/skills-spec-officielle.md` (relevée le 22/10/2026 sur Claude Code 2.1.308). It is the single source of truth for frontmatter fields, substitutions, lifecycle, placement and claude.ai limits. Never rely on pre-trained knowledge about skills: the platform changes every few weeks. If the user's Claude Code is much newer than 2.1.308, say that the spec may be out of date and offer to re-read https://code.claude.com/docs/en/skills.md.

**Anti-folklore rule:** never use these terms in a generated skill, they do not exist in the sources:
- "Tier 1", "Tier 2", "Tier 3" (the real mechanism is called progressive disclosure)
- "V1", "V2" (as skill specification versions)
- "Objectif Supreme"
- "Architecture Indentee chronologique"

"~100 tokens" (metadata) and "under 5,000 tokens" (body) appear in the agentskills.io standard as orders of magnitude and recommendations, never as limits. If a user cites them as limits, or cites any of the terms above, correct with the spec (section 0).

**Cas particulier « pushy »** : hors spec, mais le skill-creator natif d'Anthropic recommande des descriptions « un peu pushy » contre le sous-déclenchement. Choix assumé ici : description **sobre, mots-clés en tête**. Une description gonflée pousse l'agent à suivre la description au lieu de lire le corps du skill. Si l'utilisateur cite le natif, expliquer ce choix (un arbitrage différent, pas du folklore) ; la Phase 5 traite le sous-déclenchement par le test, pas par l'inflation.

## Standing rules for all skill creation

Ces règles valent pour toute la session, pour chaque skill généré :

- `---` en **première ligne** du SKILL.md, YAML valide. Un YAML invalide charge le skill sans aucun champ : `/nom` marche, l'auto-invocation non.
- **Champs Claude Code** : uniquement les 20 de la spec (section 4.2) : `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility`. Un nom mal orthographié est ignoré **sans erreur** : vérifier chaque nom contre la spec.
- **Champs claude.ai, Skills API, `package_skill.py`** : seulement `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Tout autre champ fait échouer le téléversement (« Unexpected key(s) »).
- **Description** : cas d'usage clé et mots que l'utilisateur dirait, en premier. `description` + `when_to_use` tronqués à 1 536 caractères dans Claude Code ; `description` limitée à 1 024 pour claude.ai. Ne pas y résumer le déroulé interne du skill.
- **Nom** : minuscules, chiffres, tirets, 64 caractères max, pas de tiret au début ni à la fin, pas de `--`, `name` identique au nom du dossier. Noms interdits : `synced`, `anthropic-skills`.
- Corps écrit en **consignes permanentes** : le fichier entre une fois dans la conversation et n'est jamais relu.
- Règles critiques dans les **5 000 premiers tokens** (seule partie conservée après compaction) ; corps sous 500 lignes, le détail dans `references/`.
- Fichiers supports : préfixe `CLAUDE_SKILL_DIR` pour Claude Code (syntaxe exacte en spec section 5), chemins relatifs pour claude.ai. Jamais de chemin absolu en dur.
- **Ne jamais écrire dans le corps d'un SKILL.md une injection ou une variable à titre d'exemple.** Claude Code les traite partout, même entre backticks ou dans un commentaire HTML (vérifié le 22/10/2026 sur 2.1.308) : un point d'exclamation suivi d'une commande entre backticks lance la commande, et un refus de permission annule toute l'invocation ; une variable `CLAUDE_*` écrite avec sa syntaxe complète est remplacée par sa valeur, sans échappement possible ; un placeholder d'argument (dollar suivi d'un chiffre ou de ARGUMENTS) est remplacé aussi, sauf s'il est précédé d'une barre oblique inverse. Pour en parler, nommer la chose sans sa syntaxe et renvoyer à la spec (sections 5 et 10).
- `allowed-tools` **pré-approuve** pour le seul tour d'invocation (l'autorisation tombe au message suivant) ; il ne restreint rien. Pour retirer des outils : `disallowed-tools`. Le limiter au strict nécessaire.
- N'inclure que les champs utiles au skill ; omettre ceux qui prendraient leur valeur par défaut.

### `paths` : activation conditionnelle (vérifié le 22/10/2026, Claude Code 2.1.308)

Un skill qui déclare `paths` est **absent au démarrage, y compris pour `/nom`** : il n'apparaît qu'après que Claude a lu ou modifié, dans la session, un fichier qui correspond aux motifs (relatifs au dossier courant). Ensuite Claude peut l'invoquer normalement. Constaté en `claude -p` avec des canaris (spec, section 12) ; le menu `/` interactif et un `/nom` tapé après activation n'ont pas été testés.

Règles :
- **Par défaut, pas de `paths`** : mettre les mots-clés de ciblage (types de fichiers, technos, frameworks) dans `description`. L'auto-invocation par contexte suffit dans la plupart des cas.
- `paths` seulement pour un skill de **connaissance liée à des fichiers** (conventions Twig, `theme.json`…), quand il est acceptable qu'il reste invisible tant qu'aucun fichier correspondant n'est ouvert.
- **Jamais** de `paths` sur un skill que l'utilisateur lance par `/nom` en début de session, sur un skill de workflow, ni dans une variante claude.ai (champ refusé).
- Audit d'un skill absent de la liste : chercher `paths` en premier. Le skill n'est pas cassé, il attend un fichier correspondant.

L'ancienne règle « ne jamais émettre `paths` » (juin 2026, Claude Code 2.1.160) s'explique probablement par ce comportement documenté : un skill absent de la liste tant qu'aucun fichier correspondant n'est ouvert. Non retesté sur la 2.1.160.

### Compatibilité plateformes : un SKILL.md, deux schémas

Ne jamais présenter les champs Claude Code comme universels. Demander ou déduire la cible avant de choisir les champs.

| Champ | Claude Code | claude.ai, Skills API, `package_skill.py` |
|---|:---:|:---:|
| `name`, `description` | ✅ | ✅ **requis** (`description` ≤ 1 024, `name` = dossier) |
| `allowed-tools` | ✅ | ✅ (expérimental dans le standard, chaîne séparée par espaces) |
| `license`, `compatibility`, `metadata` | ✅ (acceptés, sans effet) | ✅ |
| `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell` | ✅ | ❌ téléversement refusé |

Côté corps, l'injection de commandes (spec section 10) ne fonctionne que dans Claude Code (doc officielle) ; les substitutions de variables (spec section 5) sont aussi propres à Claude Code et ne sont pas à attendre sur claude.ai (déduction : la doc ne cite que l'injection en exemple). Un skill téléversé sur claude.ai se synchronise aussi dans Claude Code (terminal connecté au compte), où ses commandes `!` ne s'exécutent jamais. Les autres outils (agents VS Code, etc.) ne sont pas couverts par ces sources : vérifier leur documentation avant d'affirmer quoi que ce soit.

### Doctrine déterminisme : prose ou exécutable

Avant d'écrire le corps d'un skill, classer chaque exigence :

| Famille | Mécanisme | Exemples |
|---|---|---|
| **Forme stable d'un artefact** (document, scaffold, config au rendu identique à chaque génération) | **Template figé + script de fusion.** Le LLM remplit des données (JSON, variables), le script produit l'artefact. Pas de génération libre guidée par de la prose : la prose décrit, le LLM interprète, la forme varie à chaque tirage. | document éditorial, devis, rapport à la charte, boilerplate |
| **Contrainte non négociable** (interdits métier, formats imposés) | **Garde-fou exécutable** dans le script : une validation qui fait ÉCHOUER le build avec un message actionnable. Une règle « ne jamais X » en prose finit contournée sous pression ; un `sys.exit` jamais. | champ requis, regex de format, valeur interdite |
| **Jugement contextuel** (ton, arbitrages, correspondance floue) | Prose du SKILL.md, avec exemples calibrants. | reformulation, choix de la section la plus proche |

Pour tout skill qui produit un artefact :
- `templates/` contient la forme figée, `scripts/` le fuseur, `examples/` **au moins un jeu d'entrée canonique complet** (fixture).
- Le SKILL.md ordonne de lire la fixture avant toute extraction (calibrage de densité et de ton).
- Le SKILL.md documente la **commande de vérification** : builder la fixture et comparer à la sortie de référence.
- Interdire explicitement au LLM de modifier templates ou scripts pour faire passer un contenu refusé par un garde-fou.

### Règle des 2 versions : Claude Code + claude.ai

**Toute livraison de skill produit DEUX variantes**, sauf si l'utilisateur restreint la cible. Un seul fichier ne sert pas les deux plateformes :

| | Claude Code | claude.ai (zip téléversé) |
|---|---|---|
| Frontmatter | champs utiles parmi les 20 | **les 6 champs du standard seulement** ; tout autre champ, `argument-hint` compris, fait échouer le téléversement |
| Fichiers bundlés | préfixe `CLAUDE_SKILL_DIR` puis `/scripts/x.py` | **chemins relatifs** : `scripts/x.py` |
| Corps | injection de commandes, placeholders d'arguments (tous, par index, par nom), variables `CLAUDE_*` | rien de tout cela (voir Compatibilité) ; demander dans la conversation les informations que les arguments apportaient (recommandation maison) |
| Livraison | dossier dans `~/.claude/skills/<nom>/` ou `.claude/skills/<nom>/` | `<nom>.zip` contenant **un dossier racine `<nom>/`** avec `SKILL.md` dedans (structure produite par `package_skill.py` officiel ; un zip à plat n'a pas été testé) |
| Scripts | Bash local | exécution de code de claude.ai, à activer dans les réglages (interface hors doc Claude Code, à vérifier sur place) |
| Installation | copie ou lien du dossier ; pris en compte à chaud | téléversement dans les réglages de claude.ai, rubrique des skills (chemin exact hors doc, à vérifier sur place). Remplacer une version existante selon la procédure claude.ai du moment (hors doc Claude Code, à vérifier sur place) |

La variante Claude Code est la source ; la variante claude.ai se dérive (Phase 2.4). Si les deux sont installées, le skill local garde `/nom`, la copie synchronisée répond à `/anthropic-skills:nom`, et les deux figurent dans le listing (doc). Garder les deux à la même version, sinon Claude peut choisir l'ancienne (déduction).

## Principes d'écriture (appliqués en Phase 2, vérifiés en Phase 3)

- **Dire quoi faire, sobrement** (doc officielle : « State what to do rather than narrating how or why »). Chaque ligne chargée coûte du contexte à chaque tour : supprimer ce qui ne change pas le comportement du modèle.
- **Une raison courte quand la règle n'est pas évidente** (skill-creator officiel : « explain the why »). Préférer « vérifier X, car Y casse sinon » aux MUST/NEVER en majuscules : un impératif nu invite le modèle à négocier, une raison comprise le fait adhérer. Une phrase de raison, pas un récit. Réserver les majuscules aux 2 ou 3 règles réellement non négociables.
- **Généraliser, ne pas overfitter.** Un skill servira sur des cas jamais vus. Une règle qui ne sert qu'à faire passer l'exemple qui l'a inspirée se reformule en principe général ou disparaît.
- **Bundler le travail répété.** Si les tests (Phase 4) montrent que chaque run réécrit le même script ou refait la même séquence, l'extraire dans `scripts/` ou `references/` et y faire pointer le SKILL.md.

## Phase 1 : Before creation

When invoked with `/skill-architect $0`, start by gathering requirements. Ask these calibration questions before writing any file:

1. **Nom** : confirmer `$0`. Valider les règles de nom (Standing rules) ; proposer une correction sinon.
2. **But** : que doit permettre le skill ? Demander une description concrète du comportement ou du workflow attendu.
3. **Emplacement** :
   - personnel : `~/.claude/skills/$0/` (tous les projets de la machine, pas Cowork ni le cloud) ;
   - projet : `.claude/skills/$0/` (ce dépôt, partagé par commit) ;
   - plugin : `<plugin>/skills/$0/` (là où le plugin est activé).
4. **Fichiers cibles** : le skill doit-il s'activer sur certains types de fichiers ? Par défaut, mettre ces mots-clés dans `description`. Proposer `paths` seulement pour un skill de connaissance liée à des fichiers, en prévenant qu'il restera invisible, même pour `/nom`, tant qu'aucun fichier correspondant n'est ouvert.
5. **Mode d'invocation** : automatique, ou manuel seulement (`disable-model-invocation: true`, à conseiller pour tout effet de bord : envoi, déploiement, commit) ? Ou seulement par Claude (`user-invocable: false`) ?
6. **Outils** : lesquels pré-approuver (`allowed-tools`, ex. `Read`, `Bash(npm *)`) ? Lesquels retirer (`disallowed-tools`) ?
7. **Fichiers supports** : références, templates, scripts, exemples ? Décrire leur rôle.
8. **Audience** : développeur, non-développeur ou mixte ? Pour une audience non-dev, le skill explique brièvement les termes techniques au premier usage et privilégie le pas-à-pas.
9. **Plateforme cible** : Claude Code, claude.ai, ou les deux ? **Défaut : les deux**, donc deux variantes (Règle des 2 versions). Si claude.ai est visé et que le skill a des scripts, rappeler d'activer l'exécution de code.
10. **Artefact à forme stable ?** Le skill produit-il un document ou un scaffold au rendu identique à chaque génération ? Si oui : doctrine déterminisme (template figé + script + fixture). Demander s'il existe déjà un rendu validé à figer.

Do not proceed to Phase 2 until the user has confirmed the answers. A question that does not apply can be skipped.

## Phase 2 : During creation

### 2.1 Scaffold the directory

```bash
mkdir -p <scope-path>/$0
```

Add subdirectories only if the user confirmed supporting files: `references/` (documentation à consulter), `templates/` (formes à remplir), `scripts/` (code exécuté), `examples/` (fixtures et sorties de référence).

### 2.2 Write the target SKILL.md

Read `${CLAUDE_SKILL_DIR}/templates/SKILL.md.template` for the structural skeleton.

**Frontmatter :**
- Toujours `name` (identique au dossier) et `description`.
- `when_to_use` pour des phrases de déclenchement ou exemples de demandes, s'ils alourdiraient la description (Claude Code seulement ; pour claude.ai, les fondre dans `description`).
- `argument-hint` si le skill prend des arguments ; **quoter** une valeur avec crochets (`"[filename]"`), sinon YAML lit une liste (le skill se charge et s'exécute quand même sur 2.1.308, spec section 4.2 ; quoter reste la forme correcte). Claude Code seulement. `arguments` pour nommer les positions (un nom au lieu d'un index, spec section 5).
- `allowed-tools` seulement si des outils doivent être pré-approuvés ; `disallowed-tools` pour une boucle autonome qui ne doit jamais appeler un outil (ex. `AskUserQuestion`).
- `disable-model-invocation: true` si invocation manuelle voulue.
- `model` et `effort` seulement si le skill l'exige vraiment ; `model` ne vaut que pour le tour courant, `inherit` garde le modèle actif, les niveaux d'effort dépendent du modèle.
- `context: fork` + `agent` pour une tâche isolée et autonome ; ajouter `background: false` si le résultat doit arriver dans le tour.
- `paths` selon la règle ci-dessus, jamais par réflexe.
- `license`, `compatibility`, `metadata` si utiles (portables sur claude.ai ; `metadata` = chaînes, quoter `"1.0"`).
- Vérifier chaque champ contre la spec avant de l'écrire.

**Description :**
- Mots-clés que dirait l'utilisateur, en premier ; capacités et conditions de déclenchement, pas le déroulé interne.
- Viser court (quelques centaines de caractères) ; ne jamais dépasser 1 024 si une variante claude.ai est prévue.

**Corps :**
- Règles critiques en tête (elles survivent à la compaction) ; consignes permanentes ; forme impérative.
- Référencer chaque fichier support avec le préfixe `CLAUDE_SKILL_DIR` (syntaxe en spec section 5) en disant quand le lire.
- Substitutions disponibles : spec section 5 (tous les arguments, arguments par index ou par nom, ID de session, niveau d'effort, dossier du skill, racine du projet, et pour les plugins leurs dossiers d'installation et de données).
- Injection de commandes (spec section 10) : un échec annule toute l'invocation ; ajouter `|| true` à une commande qui peut sortir en 1 ; pré-approuver la commande dans `allowed-tools`, sinon l'invocation est annulée hors auto mode.
- Au-delà de 500 lignes ou d'environ 5 000 tokens, déplacer le détail dans `references/`.

### 2.3 Write supporting files

- Créer chaque fichier confirmé en Phase 1 et le référencer depuis le SKILL.md (contenu, moment de lecture).
- Skill à artefact : `templates/` (forme figée), `scripts/` (fuseur avec garde-fous bloquants), `examples/` (fixture complète). Le script échoue avec un message actionnable, jamais en silence.

### 2.4 Dériver la variante claude.ai (si la cible inclut claude.ai)

La variante Claude Code est la source. Dans un répertoire de travail :

1. Copier le dossier du skill.
2. Frontmatter : ne garder que `name`, `description` (≤ 1 024 caractères) et, si utiles, `license`, `compatibility`, `metadata`, `allowed-tools`. Fondre `when_to_use` dans `description`.
3. Remplacer chaque référence **opérationnelle** préfixée par `CLAUDE_SKILL_DIR` par un chemin relatif (`scripts/x.py`, `references/x.md`), dans le SKILL.md et dans les fichiers supports. Remplacement ciblé, chemin par chemin, jamais un `sed` aveugle : il mutilerait les mentions pédagogiques et les exemples.
4. Retirer ou réécrire les lignes d'injection, les variables `CLAUDE_*` et les placeholders d'arguments, ou expliquer dans une note ce qu'ils désignent sur claude.ai ; retirer les consignes propres à Claude Code (`~/.claude/skills`, `/reload-skills`) ou les marquer « Claude Code uniquement ».
5. Zipper : `cd <parent> && zip -r <nom>.zip <nom>`.
6. Contrôler, avant de livrer :
```bash
unzip -l <nom>.zip    # un seul dossier racine <nom>/, et <nom>/SKILL.md
unzip -p <nom>.zip <nom>/SKILL.md | python3 -c "
import re, sys
t = sys.stdin.read().replace(chr(13), '')
if not t.startswith('---' + chr(10)): sys.exit('SKILL.md absent du zip, ou sans --- en ligne 1')
fin = t.find(chr(10) + '---', 3)
if fin < 0: sys.exit('frontmatter sans --- de fermeture')
cles = re.findall(r'^([^ #][^:]*):', t[4:fin], re.M)
refus = [c for c in cles if c not in ('name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools')]
print('CHAMPS REFUSES PAR CLAUDE.AI : ' + ', '.join(refus) if refus else 'OK')"
```
La seconde commande doit afficher `OK`. `grep -r 'CLAUDE_SKILL_DIR'` dans le dossier dérivé ne doit plus montrer que des mentions pédagogiques, aucune commande exécutable.

## Phase 3 : After creation

Validate the generated skill against the full checklist. Present each point with a pass/fail verdict and a short justification.

### Validation checklist (16 points)

1. **Nom** : règles de nom respectées, `name` identique au dossier.
2. **SKILL.md** : à la racine du dossier, `---` en première ligne.
3. **Frontmatter valide** : YAML analysable ; aucun champ hors des 20 de la spec, aucun nom mal orthographié.
4. **Description** : présente, cas d'usage en tête ; `description` + `when_to_use` ≤ 1 536 ; `description` ≤ 1 024 si variante claude.ai.
5. **Mode manuel** : `disable-model-invocation: true` si et seulement si l'utilisateur l'a demandé.
6. **`paths`** : absent, ou justifié (skill de connaissance liée à des fichiers, jamais appelé par `/nom` en début de session) et l'utilisateur prévenu de l'invisibilité initiale. FAIL sinon.
7. **Outils** : `allowed-tools` au strict nécessaire ; commandes injectées pré-approuvées.
8. **Consignes permanentes** : pas d'étapes ponctuelles devenues inutiles après exécution.
9. **Placement** : règles critiques dans les 5 000 premiers tokens ; corps sous 500 lignes.
10. **Fichiers supports référencés** : chacun cité depuis le SKILL.md via le préfixe `CLAUDE_SKILL_DIR`.
11. **Injection sûre** : chaque commande injectée qui peut sortir en 1 se termine par `|| true` ; aucune injection ni variable écrite à titre d'exemple dans le corps.
12. **Déterminisme** : si artefact à forme stable : template + script + fixture présents, garde-fous exécutables, commande de vérification dans le SKILL.md. FAIL si la forme repose sur de la prose.
13. **Variante claude.ai** : si visée : 6 champs au plus, aucune référence opérationnelle `CLAUDE_SKILL_DIR`, aucune injection, zip contrôlé (Phase 2.4, étape 6).
14. **Invocation** : inviter l'utilisateur à tester `/nom`.
15. **Découvrabilité** : inviter l'utilisateur à vérifier que le skill figure dans « What skills are available? » (ou dans `/skills`).
16. **Test exécuté, pas promis** : Phase 4 faite AVANT livraison, résultats montrés.

If any point fails, fix the SKILL.md immediately and re-validate.

## Phase 4 : Test réel (obligatoire)

La checklist prouve la conformité, pas l'utilité. Un skill non testé n'est pas livré. Choisir le protocole selon le type :

**Skill à artefact** (template + script) :
1. Builder la fixture (`python3 scripts/<fuseur> examples/<fixture> -o <dossier-temporaire>`, à adapter).
2. Comparer la sortie au rendu de référence (visuel ou diff structurel) et la montrer.
3. Tester au moins 2 cas négatifs : un contenu qui viole un garde-fou (doit ÉCHOUER avec un message clair), une entrée minimale (le squelette reste cohérent : numérotation, sections optionnelles).

**Skill de comportement** (règles, workflow) :
1. **Proposer 2 ou 3 prompts réalistes** : ce qu'un vrai utilisateur taperait, avec des détails concrets (chemins, fichiers, contexte métier). Les faire valider avant de lancer.
2. **Comparer avec et sans le skill**, chaque run dans un **contexte neuf** (le contexte de rédaction masque les trous des instructions) :
   - méthode officielle : une session neuve par prompt, puis la même avec le skill coupé (`"off"` dans `skillOverrides` pour un skill personnel ou projet ; `claude plugin eval` pour un skill de plugin) ;
   - ou des subagents lancés dans le même tour, un qui lit le SKILL.md puis exécute la tâche, un sans (baseline) ;
   - sans subagents ni sessions séparées (claude.ai) : dérouler soi-même le skill sur chaque prompt, sans baseline.
3. **Présenter** : pour chaque prompt, les deux résultats et les différences concrètes (qualité, conventions, temps). Demander le retour de l'utilisateur.
4. **Améliorer puis re-tester** avec les mêmes prompts, en respectant les Principes d'écriture (pas de rustine taillée pour le cas de test). Si une règle est contournée par rationalisation, ajouter le contre-argument explicite, ou mieux, en faire un garde-fou exécutable.
5. **Signal de bundling** : si tous les runs réécrivent le même code, l'extraire dans `scripts/` ou `references/`.

Pour une boucle outillée (cas dans `evals/evals.json`, notation, A/B à l'aveugle entre deux versions, rapport HTML), proposer le plugin officiel skill-creator (spec section 14). Pour les skills de discipline à fort enjeu, `superpowers:writing-skills` détaille une méthode RED-GREEN-REFACTOR, si elle est installée.

## Phase 5 : Optimisation de la description (optionnelle, Claude Code uniquement)

La description est le mécanisme de déclenchement automatique. Pour un skill destiné à l'auto-invocation :

1. Écrire 6 à 8 requêtes de test : la moitié DOIT déclencher (formulations variées, langage courant, sans nommer le skill), l'autre moitié NE DOIT PAS. Privilégier les **quasi-pièges** (mêmes mots-clés, besoin différent) au hors-sujet évident, qui ne teste rien.
2. Pour chaque requête, **dans un dossier jetable** (copie du projet ou worktree : en mode auto, `claude -p` exécute vraiment la tâche), mesurer :
   ```bash
   claude -p "<requête>" --output-format stream-json --verbose | grep -c '"name":"Skill"'
   ```
   Un résultat non nul indique un appel de l'outil Skill ; vérifier dans la sortie que c'est bien ce skill. Le message `init` (clé `skills`) confirme qu'il est chargé. Un run n'est qu'un tirage : répéter chaque requête (le skill-creator officiel fait 3 runs par requête par défaut).
3. Ajuster la description (mot-clé manquant, contexte à préciser) et re-tester. 2 ou 3 itérations suffisent ; choisir la version sur l'ensemble des requêtes, pas sur la dernière qui échouait (anti-overfit).

Une requête trop simple ne déclenche aucun skill, Claude la traite seul (constat du skill-creator officiel) : tester avec des demandes substantielles, en plusieurs étapes.

### Output to user

After validation and tests, present:
- l'arborescence complète (`find <skill-path> -type f`) ;
- la commande d'invocation `/nom` et les conditions de déclenchement automatique ;
- un exemple d'usage concret ;
- les preuves de la Phase 4 (sortie du build de fixture, verdicts des cas négatifs, ou comparaison avec et sans skill) ;
- les deux livrables si double cible : dossier Claude Code et `<nom>.zip` claude.ai contrôlé.
