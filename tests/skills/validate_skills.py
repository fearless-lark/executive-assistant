#!/usr/bin/env python3
"""Validate the skills in this repository. Standard library only.

Usage:
    python3 tests/skills/validate_skills.py

Exit code 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT / "skills"
SHARED_DIR = ROOT / "shared"
TEMPLATES_DIR = ROOT / "templates"
OWNED_DIRS = [".claude-plugin", "skills", "shared", "scripts", "templates", "tests/skills"]
STYLE_DIRS = ["skills", "shared", "templates"]

# Limits from the Agent Skills format and platform docs.
NAME_MAX = 64
DESCRIPTION_MAX = 1024
PROFILE_DESCRIPTION_MAX = 200  # manual skill upload on some platforms
SKILL_MD_MAX_LINES = 500
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_NAME_WORDS = ("claude", "anthropic")
MIN_REDTEAM_CASES = 12

# Patterns are assembled from parts so this file does not match itself.
FORBIDDEN_LITERALS = [
    ("internal brand name", re.compile("remi" + "link", re.IGNORECASE)),
    ("unfinished marker", re.compile(r"\b(" + "TO" + "DO" + "|" + "TB" + "D" + "|" + "FIX" + "ME" + r")\b")),
    ("AI attribution", re.compile("Co-" + "Authored-By|Generated " + "with", re.IGNORECASE)),
    ("robot emoji", re.compile("\U0001F916")),
]

STYLE_RULES = [
    ("em dash used as a clause join (allowed only inside «...» names)", re.compile("—")),
    ("spaced en dash used as a dash", re.compile(" – ")),
    ("construction «не X, а Y»", re.compile(r"(?i)(?<![\w'])не\s+[^,.;:!?\n«»]{1,40},\s+а\s")),
    ("construction «Y, а не X»", re.compile(r"(?i),\s+а\s+не\s")),
    ("construction «не просто»", re.compile(r"(?i)(?<![\w'])не\s+просто\b")),
    ("AI cliche", re.compile(
        r"(?i)важливо зазначити|варто зазначити|варто відзначити|зануримос|давайте розглянемо|"
        r"у сучасному світі|відіграє ключову роль|комплексний підхід|у світі, що швидко"
    )),
]

errors: list[str] = []
notes: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    data: dict[str, str] = {}
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            return data, "\n".join(lines[i + 1:])
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[key.strip()] = value
    return None, text


def strip_guillemets(line: str) -> str:
    return re.sub(r"«[^«»]*»", "«»", line)


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)


def check_skill(skill_dir: Path, shared_names: set[str]) -> None:
    skill_md = skill_dir / "SKILL.md"
    folder = skill_dir.name
    if not skill_md.is_file():
        err(f"{rel(skill_dir)}: SKILL.md is missing")
        return
    text = skill_md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if fm is None:
        err(f"{rel(skill_md)}: frontmatter must start on line 1 and close with ---")
        return

    unknown = set(fm) - ALLOWED_FRONTMATTER_KEYS
    if unknown:
        err(f"{rel(skill_md)}: frontmatter keys not portable: {sorted(unknown)}")

    name = fm.get("name", "")
    if not name:
        err(f"{rel(skill_md)}: frontmatter 'name' is missing")
    else:
        if name != folder:
            err(f"{rel(skill_md)}: name '{name}' does not match folder '{folder}'")
        if len(name) > NAME_MAX or not NAME_RE.match(name):
            err(f"{rel(skill_md)}: name '{name}' must be lowercase letters, digits, hyphens, max {NAME_MAX}")
        if any(word in name for word in RESERVED_NAME_WORDS):
            err(f"{rel(skill_md)}: name '{name}' contains a reserved word")

    desc = fm.get("description", "")
    if not desc:
        err(f"{rel(skill_md)}: frontmatter 'description' is missing")
    else:
        if len(desc) > DESCRIPTION_MAX:
            err(f"{rel(skill_md)}: description is {len(desc)} chars, max {DESCRIPTION_MAX}")
        if "<" in desc or ">" in desc:
            err(f"{rel(skill_md)}: description must not contain angle brackets")
        if not re.search(r"[А-Яа-яІіЇїЄєҐґ]", desc) or not re.search(r"\b[A-Za-z]{3,}\b", desc):
            err(f"{rel(skill_md)}: description needs Ukrainian and English trigger phrases")
        notes.append(f"{folder}: description {len(desc)} chars")

    n_lines = text.count("\n") + 1
    if n_lines > SKILL_MD_MAX_LINES:
        err(f"{rel(skill_md)}: {n_lines} lines, keep under {SKILL_MD_MAX_LINES}")

    head = "\n".join(body.strip().split("\n")[:8])
    if "references/guardrails.md" not in head:
        err(f"{rel(skill_md)}: must point to references/guardrails.md at the top of the body")
    if "exec-profile" not in body:
        err(f"{rel(skill_md)}: must mention the exec-profile skill")

    ref_dir = skill_dir / "references"
    mentioned = set(re.findall(r"references/([A-Za-z0-9_.\-]+\.md)", text))
    for ref in sorted(mentioned):
        if not (ref_dir / ref).is_file():
            err(f"{rel(skill_md)}: references/{ref} is mentioned but missing")
    if ref_dir.is_dir():
        for f in sorted(ref_dir.glob("*.md")):
            if f.name not in mentioned:
                err(f"{rel(f)}: not mentioned in SKILL.md (orphan reference)")
    for shared in sorted(shared_names):
        if shared not in mentioned:
            err(f"{rel(skill_md)}: shared reference references/{shared} is not mentioned")


TEMPLATE_COPIES = {
    "templates/exec-profile.template.md": "skills/exec-setup/references/profile-template.md",
    "templates/schedules.md": "skills/exec-setup/references/schedules.md",
}


def check_template_copies() -> None:
    for src_rel, dst_rel in TEMPLATE_COPIES.items():
        src, dst = ROOT / src_rel, ROOT / dst_rel
        if not src.is_file():
            continue
        if not dst.is_file():
            err(f"{dst_rel}: template copy missing (run scripts/sync-shared.sh)")
        elif dst.read_bytes() != src.read_bytes():
            err(f"{dst_rel}: template copy drifted from {src_rel} (run scripts/sync-shared.sh)")


def check_shared_sync(shared_files: list[Path], skill_dirs: list[Path]) -> None:
    for skill_dir in skill_dirs:
        for src in shared_files:
            dst = skill_dir / "references" / src.name
            if not dst.is_file():
                err(f"{rel(dst)}: shared copy missing (run scripts/sync-shared.sh)")
            elif dst.read_bytes() != src.read_bytes():
                err(f"{rel(dst)}: shared copy drifted from {rel(src)} (run scripts/sync-shared.sh)")


def iter_files(dirs: list[str], suffixes: tuple[str, ...] | None = None):
    for d in dirs:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                if suffixes is None or p.suffix in suffixes:
                    yield p


def check_forbidden() -> None:
    for p in iter_files(OWNED_DIRS):
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, rx in FORBIDDEN_LITERALS:
            for m in rx.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                err(f"{rel(p)}:{line_no}: {label}: '{m.group(0)}'")


def check_style() -> None:
    for p in iter_files(STYLE_DIRS, (".md",)):
        text = strip_html_comments(p.read_text(encoding="utf-8"))
        for line_no, line in enumerate(text.split("\n"), start=1):
            checked = strip_guillemets(line)
            for label, rx in STYLE_RULES:
                m = rx.search(checked)
                if m:
                    err(f"{rel(p)}:{line_no}: style: {label}: '{line.strip()[:90]}'")


def check_manifests() -> None:
    mp_path = ROOT / ".claude-plugin" / "marketplace.json"
    pj_path = ROOT / ".claude-plugin" / "plugin.json"
    try:
        mp = json.loads(mp_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        err(f".claude-plugin/marketplace.json: {e}")
        return
    try:
        pj = json.loads(pj_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        err(f".claude-plugin/plugin.json: {e}")
        return

    for key in ("name", "owner", "plugins"):
        if key not in mp:
            err(f"marketplace.json: required field '{key}' is missing")
    if not isinstance(mp.get("owner"), dict) or not mp["owner"].get("name"):
        err("marketplace.json: owner.name is required")
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*$", mp.get("name", "")) or ".." in mp.get("name", ""):
        err("marketplace.json: invalid marketplace name")
    plugins = mp.get("plugins") or []
    if not plugins:
        err("marketplace.json: plugins array is empty")
    for i, entry in enumerate(plugins):
        src = entry.get("source")
        if not entry.get("name") or src is None:
            err(f"marketplace.json: plugins[{i}] needs name and source")
            continue
        if isinstance(src, str):
            if not (src == "." or src.startswith("./")) or ".." in src:
                err(f"marketplace.json: plugins[{i}].source must start with ./ and not contain ..")
            plugin_root = (ROOT / src).resolve()
            if not plugin_root.is_dir():
                err(f"marketplace.json: plugins[{i}].source does not exist: {src}")
            elif plugin_root == ROOT and entry["name"] != pj.get("name"):
                err(f"marketplace.json: plugins[{i}].name '{entry['name']}' differs from plugin.json name")

    name = pj.get("name", "")
    if not NAME_RE.match(name):
        err("plugin.json: name must be kebab-case")
    for key in ("version", "description", "author"):
        if key not in pj:
            err(f"plugin.json: '{key}' is recommended and missing")
    if isinstance(pj.get("author"), dict) and not pj["author"].get("name"):
        err("plugin.json: author.name is required")
    if "homepage" in pj and not re.match(r"^https://", pj["homepage"]):
        err("plugin.json: homepage must be an https URL")
    if (ROOT / ".mcp.json").exists():
        err(".mcp.json must not exist: it makes the plugin desktop-only in ChatGPT workspaces")
    if (ROOT / "bin").exists():
        err("bin/ must not exist at the plugin root: claude.ai does not install such plugins")


def check_templates() -> None:
    tpl = TEMPLATES_DIR / "exec-profile.template.md"
    if not tpl.is_file():
        err("templates/exec-profile.template.md is missing")
    else:
        fm, _ = parse_frontmatter(tpl.read_text(encoding="utf-8"))
        if fm is None or fm.get("name") != "exec-profile":
            err("templates/exec-profile.template.md: frontmatter name must be exec-profile")
        elif len(fm.get("description", "")) > PROFILE_DESCRIPTION_MAX:
            err(f"templates/exec-profile.template.md: description over {PROFILE_DESCRIPTION_MAX} chars")
    if not (TEMPLATES_DIR / "schedules.md").is_file():
        err("templates/schedules.md is missing")


def check_redteam() -> None:
    path = ROOT / "tests" / "skills" / "redteam-cases.md"
    if not path.is_file():
        err("tests/skills/redteam-cases.md is missing")
        return
    cases = re.findall(r"^## Кейс \d+", path.read_text(encoding="utf-8"), flags=re.M)
    if len(cases) < MIN_REDTEAM_CASES:
        err(f"redteam-cases.md: {len(cases)} cases, expected at least {MIN_REDTEAM_CASES}")


def main() -> int:
    shared_files = sorted(SHARED_DIR.glob("*.md"))
    if not shared_files:
        err("shared/: no shared files")
    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir()) if SKILLS_DIR.is_dir() else []
    if not skill_dirs:
        err("skills/: no skills found")
    shared_names = {f.name for f in shared_files}

    for d in skill_dirs:
        check_skill(d, shared_names)
    check_shared_sync(shared_files, skill_dirs)
    check_template_copies()
    check_forbidden()
    check_style()
    check_manifests()
    check_templates()
    check_redteam()

    for n in notes:
        print(f"info  {n}")
    if errors:
        for e in errors:
            print(f"FAIL  {e}")
        print(f"\n{len(errors)} problem(s) in {len(skill_dirs)} skill(s).")
        return 1
    print(f"\nOK: {len(skill_dirs)} skills, {len(shared_files)} shared files, all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
