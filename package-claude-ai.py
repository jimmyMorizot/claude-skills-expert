#!/usr/bin/env python3
"""Build the claude.ai variant of skill-architect: dist/skill-architect.zip.

claude.ai, the Skills API and package_skill.py accept only six frontmatter fields, and
Claude Code variables such as CLAUDE_SKILL_DIR are not expected to work there (inferred
from the docs). This script derives the upload from skill/
with exact, targeted replacements, then checks the result. Any mismatch stops the
build: fix this script when skill/SKILL.md changes, never the generated zip.

Usage: python3 package-claude-ai.py
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "skill"
NAME = "skill-architect"
DIST = ROOT / "dist"
OUT_DIR = DIST / NAME
ZIP_PATH = DIST / f"{NAME}.zip"

ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MAX_DESCRIPTION = 1024

NOTICE = (
    "> **Variante claude.ai.** Les emplacements `~/.claude/skills`, `.claude/skills` et "
    "`/reload-skills` sont propres à Claude Code : sur claude.ai, produire les fichiers du "
    "skill dans le sandbox d'exécution de code et livrer un zip téléchargeable (dossier "
    "racine = nom du skill). `$0` désigne le nom de skill donné dans la conversation. Les "
    "mentions de la variable CLAUDE_SKILL_DIR ci-dessous concernent les skills Claude Code que tu "
    "génères, pas ce skill-ci, dont les fichiers se lisent en chemins relatifs.\n"
)

# Operational references to this skill's own files, rewritten as relative paths.
# Nothing else in the body may use a CLAUDE_* variable: check_sources() enforces it.
REPLACEMENTS = [
    ("`${CLAUDE_SKILL_DIR}/references/skills-spec-officielle.md`", "`references/skills-spec-officielle.md`"),
    ("`${CLAUDE_SKILL_DIR}/templates/SKILL.md.template`", "`templates/SKILL.md.template`"),
]


def fail(message):
    sys.exit(f"ERREUR : {message}")


def split_frontmatter(text, label):
    if not text.startswith("---\n"):
        fail(f"{label} ne commence pas par ---")
    end = text.find("\n---\n", 3)
    if end < 0:
        fail(f"{label} : frontmatter sans --- de fermeture")
    return text[4:end].splitlines(), text[end + 5:]


def field(lines, key):
    found = [line.split(":", 1)[1].strip() for line in lines if line.split(":", 1)[0] == key]
    if len(found) != 1 or not found[0] or found[0][0] in ">|":
        fail(f"{key} doit apparaître une fois, sur une seule ligne, non vide (pas de bloc YAML > ou |)")
    return found[0]


# Claude Code runs an injection and substitutes a CLAUDE_* variable anywhere in a SKILL.md
# body, even inside backticks or an HTML comment (checked on 2.1.308, 22/10/2026). Writing one
# as an example breaks the skill, so the build refuses it in the sources.
INJECTION = re.compile(r"(?:^|\s)!`|^```!", re.M)


def check_sources(body):
    rest = body
    for old, _ in REPLACEMENTS:
        rest = rest.replace(old, "")
    if INJECTION.search(body):
        fail("skill/SKILL.md : injection dans le corps (point d'exclamation suivi d'un backtick)")
    if "${CLAUDE_" in rest or "$ARGUMENTS" in rest or re.search(r"\$[1-9]", rest):
        fail("skill/SKILL.md : variable ou placeholder écrit dans le corps hors des références opérationnelles (seul $0 est voulu)")
    _, template_body = split_frontmatter((SOURCE / "templates" / "SKILL.md.template").read_text(encoding="utf-8"), "templates/SKILL.md.template")
    if INJECTION.search(template_body) or "$ARGUMENTS" in template_body or "${CLAUDE_" in template_body or re.search(r"\$[0-9]", template_body):
        fail("templates/SKILL.md.template : injection, variable ou placeholder dans le corps")


def main():
    text = (SOURCE / "SKILL.md").read_text(encoding="utf-8")
    lines, body = split_frontmatter(text, "skill/SKILL.md")
    check_sources(body)

    if field(lines, "name") != NAME:
        fail(f"name doit valoir {NAME}, comme le dossier racine du zip")
    description = field(lines, "description")
    kept = [f"name: {NAME}", f"description: {description}"]
    if len(description) > MAX_DESCRIPTION:
        fail(f"description de {len(description)} caractères, claude.ai en accepte {MAX_DESCRIPTION}")

    for old, new in REPLACEMENTS:
        if old not in body:
            fail(f"référence introuvable dans skill/SKILL.md : {old}")
        body = body.replace(old, new)

    heading = "# Skill Architect\n"
    if body.count(heading) != 1:
        fail("titre « # Skill Architect » introuvable ou en double")
    body = body.replace(heading, heading + "\n" + NOTICE, 1)

    if re.search(r"^!`|^```!", body, re.M):
        fail("injection ! en début de ligne : elle ne s'exécute pas hors Claude Code")

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SOURCE, OUT_DIR, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc", "*.swp", "*~"))
    (OUT_DIR / "SKILL.md").write_text("---\n" + "\n".join(kept) + "\n---\n" + body, encoding="utf-8")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUT_DIR.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(DIST).as_posix())

    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = archive.namelist()
        if {n.split("/", 1)[0] for n in names} != {NAME} or f"{NAME}/SKILL.md" not in names:
            fail("le zip doit contenir un seul dossier racine avec SKILL.md dedans")
        built_lines, _ = split_frontmatter(archive.read(f"{NAME}/SKILL.md").decode("utf-8"), "SKILL.md du zip")
    keys = {line.split(":", 1)[0] for line in built_lines if re.match(r"^[a-z_-]+:", line)}
    if not keys <= ALLOWED:
        fail(f"champs refusés par claude.ai : {sorted(keys - ALLOWED)}")

    print(f"OK : {ZIP_PATH.relative_to(ROOT)} ({len(names)} fichiers, description {len(description)}/{MAX_DESCRIPTION})")
    for name in names:
        print(f"  {name}")


if __name__ == "__main__":
    main()
