#!/usr/bin/env python3
"""Parity check: every key rule of a skill must appear in its copy-paste prompt.

For each skill the script extracts rule markers from SKILL.md and every
references/*.md file:
  * headings (##, ###, ####) outside code examples;
  * bolded rule names (**Name.**, **Name:**, **Name**) outside code examples.
Each marker must be found in prompts/<skill>.md either as a normalised phrase or
by keywords: all its significant word stems on one line or neighbouring lines.

It also checks that prompts/tasks/<skill>.md is the full prompt with a
three-line task header and nothing shortened.

Usage: python3 tests/prompts/parity_check.py [--verbose]
Exit code 1 if coverage is below 100% for any prompt or a task copy is stale.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / 'skills'
PROMPTS = ROOT / 'prompts'
TASK_SKILLS = ['exec-daily-brief', 'exec-review', 'exec-radar', 'exec-family-week']

# Markers that are intentionally absent from the prompts, with the reason.
# Keys: (skill or '*', normalised marker).
ALLOW = {
    ('*', 'додаткові матеріали'): 'index of reference files; in a prompt every part is inline',
    ('*', 'рівні дій у цьому скілі'): 'renamed to «Рівні дій у цьому сценарії»',
    ('exec-document-analysis', 'виклик із брифу'): 'renamed to «Аналіз усередині брифу дня»: a pasted prompt is not called by another prompt',
    ('*', 'коли застосовувати'): 'renamed to «Коли цей сценарій доречний» in every prompt',
    # exec-review reads note state but does not perform the triage/maintenance
    # procedures bundled in the shared note-header reference. Its notes-pass
    # and method define the narrower use of notes as evidence of attention.
    ('exec-review', 'нові і змінені нотатки'): 'triage discovery; review selects notes relevant to the chosen period and priorities',
    ('exec-review', 'реєстр на льоту'): 'triage inventory; review groups evidence by work direction',
    ('exec-review', "зобов'язання з нотаток"): 'covered as evidence of results, not a separate triage pass',
    ('exec-review', 'що читає огляд періоду'): 'legacy shared triage procedure is superseded by review-specific notes-pass',
    ('exec-review', 'щотижня'): 'legacy weekly status assignment is outside the focused review',
    ('exec-review', 'щомісяця'): 'legacy monthly note cleanup is outside the focused review',
    ('exec-review', 'реальне переміщення між папками'): 'review never moves notes; the standalone prompt explicitly preserves this boundary',
    ('exec-review', 'аналізуй документ, лише якщо в ньому є нова активність у вікні'): 'review uses its full chosen period, including unchanged plans as priority evidence',
}

# Skill identifiers are written as prompt names inside prompts.
SKILL_NAMES = {
    'exec-daily-brief': 'бриф дня', 'exec-document-analysis': 'аналіз документа',
    'exec-meeting-prep': 'підготовка до зустрічі', 'notes-triage': 'розбір нотаток',
    'notes-assistant': 'асистент нотаток', 'exec-review': 'огляд періоду',
    'exec-research': 'глибоке дослідження', 'exec-radar': 'тижневий радар',
    'exec-family-week': 'тиждень для родини',
}

STOP = {'цього', 'цьому', 'який', 'яка', 'яке', 'які', 'його', 'якщо', 'лише', 'для', 'або',
        'та', 'від', 'після', 'перед', 'щодо', 'через', 'між', 'чого', 'того', 'тому', 'усіх',
        'всіх', 'кожен', 'кожна', 'кожне', 'кожного', 'скіла', 'скілі', 'скіл', 'скілу'}


def norm(text):
    text = text.lower().replace('’', "'").replace('ʼ', "'").replace('`', '')
    text = re.sub(r'[«»"“”*_]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def strip(text):
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith('```'):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return '\n'.join(out)


def markers(skill):
    files = [SKILLS / skill / 'SKILL.md'] + sorted((SKILLS / skill / 'references').glob('*.md'))
    found = []
    for path in files:
        text = strip(path.read_text())
        for line in text.splitlines():
            h = re.match(r'#{2,4} (.+)', line)
            if h:
                found.append((path.name, 'heading', h.group(1)))
            for b in re.findall(r'\*\*([^*]{3,80}?)[.:]?\*\*', line):
                found.append((path.name, 'bold', b))
    seen, unique = set(), []
    for src, kind, raw in found:
        clean = re.sub(r'^(\d+[а-я]?(\.\d+)*\.?|рівень \d\.?)\s*', '', norm(raw)).strip(' .:')
        clean = re.sub(r'\[[^\]]*\]', '', clean).strip(' .:·')
        for ident, name in SKILL_NAMES.items():
            clean = clean.replace(ident, name)
        if len(clean) < 3 or clean in seen:
            continue
        seen.add(clean)
        unique.append((src, kind, raw, clean))
    return unique


def stems(phrase):
    words = re.findall(r"[a-zа-яіїєґ0-9'&]+", phrase)
    return [w[:5] for w in words if len(w) >= 4 and w not in STOP]


def covered(clean, prompt_norm, prompt_lines):
    if clean in prompt_norm:
        return True
    keys = stems(clean)
    if not keys:
        return False
    for i in range(len(prompt_lines)):
        window = ' '.join(prompt_lines[max(0, i - 2):i + 3])
        if all(k in window for k in keys):
            return True
    return False


def main():
    verbose = '--verbose' in sys.argv
    failed = False
    print(f'{"prompt":<26} {"chars":>8} {"markers":>8} {"covered":>8} {"coverage":>9}')
    for skill_dir in sorted(p for p in SKILLS.iterdir() if (p / 'SKILL.md').exists()):
        skill = skill_dir.name
        path = PROMPTS / f'{skill}.md'
        if not path.exists():
            print(f'{skill:<26} missing prompt')
            failed = True
            continue
        prompt = path.read_text()
        prompt_norm = norm(prompt)
        lines = [norm(l) for l in prompt.splitlines()]
        total, ok, misses = 0, 0, []
        for src, kind, raw, clean in markers(skill):
            if (skill, clean) in ALLOW or ('*', clean) in ALLOW:
                continue
            total += 1
            if covered(clean, prompt_norm, lines):
                ok += 1
            else:
                misses.append(f'{src}: {kind} «{raw}»')
        pct = 100.0 * ok / total if total else 100.0
        print(f'{skill:<26} {len(prompt):>8,} {total:>8} {ok:>8} {pct:>8.1f}%')
        if misses:
            failed = True
            for m in misses if verbose else misses[:15]:
                print('   missing ' + m)
            if not verbose and len(misses) > 15:
                print(f'   ... {len(misses) - 15} more (use --verbose)')
    for skill in TASK_SKILLS:
        task, prompt = PROMPTS / 'tasks' / f'{skill}.md', PROMPTS / f'{skill}.md'
        if not task.exists():
            print(f'tasks/{skill}.md missing')
            failed = True
            continue
        text = task.read_text()
        head = text.split('\n\n', 1)
        if len(head) != 2 or len(head[0].splitlines()) != 3 or head[1] != prompt.read_text():
            print(f'tasks/{skill}.md is stale: expected 3-line header + full prompt')
            failed = True
        else:
            print(f'tasks/{skill}.md: header + full prompt, {len(text):,} chars')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
