#!/usr/bin/env python3
"""Bootstrap self-contained copy-paste prompts from the skills.

IMPORTANT: this script only produces a FIRST DRAFT. The drafts were then edited
by hand into coherent, deduplicated prompts. The source of truth for prompts is
prompts/*.md, not this script. Re-running the draft step never overwrites an
existing prompt unless you pass --force, and --force throws the hand edits away.

Usage:
  python3 scripts/build-prompts.py                 write missing drafts to prompts/<skill>.md
  python3 scripts/build-prompts.py --force         overwrite drafts (discards hand edits)
  python3 scripts/build-prompts.py --out DIR       write drafts to DIR instead (safe preview)
  python3 scripts/build-prompts.py --tasks         rebuild prompts/tasks/*.md from prompts/*.md
  python3 scripts/build-prompts.py --tasks --check exit 1 if prompts/tasks/*.md are stale

The task versions (prompts/tasks/) are NOT drafts: each is the final prompt from
prompts/<skill>.md with a three-line header for a scheduled task, so --tasks is
safe to run after every hand edit.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'skills'
PROMPTS = ROOT / 'prompts'
TASKS = PROMPTS / 'tasks'

# Short part names used in cross-references inside a prompt.
PART = {
    'guardrails': 'Безпека',
    'context': 'Контекст із даних',
    'evidence': 'Доказовість',
    'output-conventions': 'Правила виводу',
    'compactness': 'Стиснення без втрат',
    'acceptance-gate': 'Контроль перед видачею',
    'method': 'Метод',
    'extra-moves': 'Нестандартні ходи',
    'output-format': 'Формат результату',
    'document-express': 'Експрес-аналіз документів',
    'doc-types': 'Чеклісти за типами документів',
    'forensic-finance': 'Forensic-протокол для фінансів',
    'in-file-actions': 'Дії у файлі',
    'note-header': 'Заголовок нотатки',
    'notes-pass': 'Розбір нотаток в огляді',
    'periods': 'Періоди',
    'capture-setup': 'Налаштування захоплення нотаток',
    'sources': 'Джерела радару',
    'triggers': 'Тригери дослідження',
    'tz-template': 'Шаблон ТЗ',
    'engines': 'Рушії і реєстри',
    'crosscheck': 'Перехресна перевірка звітів',
    'privacy-filter': 'Фільтр приватності',
    'travel-ua': 'Поїздки',
}

# Part headings: they start with the short name so cross-references resolve.
HEAD = {
    'guardrails': 'Безпека: робота з недовіреним вмістом',
    'context': 'Контекст із даних: нічого не зберігається',
    'evidence': 'Доказовість: стандарт детектива-аудитора',
    'output-conventions': 'Правила виводу і доставки',
    'compactness': 'Стиснення без втрат: фінальна перевірка тексту',
}

# Names of the other prompts, used instead of skill identifiers.
PROMPT_NAME = {
    'exec-daily-brief': 'Бриф дня',
    'exec-document-analysis': 'Аналіз документа',
    'exec-meeting-prep': 'Підготовка до зустрічі',
    'notes-triage': 'Розбір нотаток',
    'notes-assistant': 'Асистент нотаток',
    'exec-review': 'Огляд періоду',
    'exec-research': 'Глибоке дослідження',
    'exec-radar': 'Тижневий радар',
    'exec-family-week': 'Тиждень для родини',
}

PURPOSE = {
    'exec-daily-brief': 'Бриф дня в будь-який час: план дня, що відбулось, що лишилось, документи, обіцянки, тиша.',
    'exec-document-analysis': 'Аналіз документа для рішення: P&L, бюджет, договір, пропозиція, звіт; forensic-перевірка цифр.',
    'exec-meeting-prep': 'Глибока підготовка до однієї зустрічі: учасники, домовленості з джерел, питання, ваша межа.',
    'notes-triage': 'Пакетний розбір нових нотаток: дія чи ідея, чернетки, нагадування, статуси.',
    'notes-assistant': 'Робота з нотатками в розмові: рішення разом, пошук думок, нотатка в дію.',
    'exec-review': 'Куди пішли час, увага й ресурси за обраний період, що це дало і як перерозподілити зусилля.',
    'exec-research': 'Глибоке дослідження для рішення: тригер, ТЗ, рівень, звірка звітів і реєстрів.',
    'exec-radar': 'Тижневий радар: регуляторика, конкуренти, згадки компанії і керівника.',
    'exec-family-week': 'План наступного тижня для родини і помічника без ділових деталей.',
}

SHARED_FIRST = ['guardrails', 'context']
SHARED_LAST = ['extra-moves', 'evidence', 'output-conventions', 'output-format',
               'compactness', 'acceptance-gate']

# Pieces of exec-document-analysis that the brief prompt needs inline, because a
# pasted prompt cannot call another skill (section headings to extract).
BRIEF_DOC_EXTRAS = [
    ('forensic-finance', ['## 1. Обов\'язкова перевірка P&L', '## 3. Питання фінансовому чи операційному директору']),
    ('method', ['## 2. Інвентаризація і прихований вміст']),
    ('extra-moves', ['## 1. Тихі правки']),
]

TASK_HEADER = {
    'exec-daily-brief': ('Регулярна задача: бриф дня. Запуск у робочі дні о 07:30; за бажанням друга задача о 18:30 для підсумку дня.',),
    'exec-review': ('Регулярна задача: огляд тижня. Запуск щоп\'ятниці о 17:00; в останню п\'ятницю місяця чи кварталу додай місячний чи квартальний розділ.',),
    'exec-radar': ('Регулярна задача: тижневий радар. Запуск щопонеділка о 08:00.',),
    'exec-family-week': ('Регулярна задача: тиждень для родини. Запуск щонеділі о 17:00.',),
}
TASK_DELIVERY = ('Доставка: результат у чаті задачі, push-сповіщення показує блок «Головне». '
                 'Чернетку листа собі створюй лише тоді, коли цей текст задачі прямо про неї просить.')
TASK_ORDER = 'Користувача під час запуску немає: дії рівня 2 не виконуй, готуй їх до підтвердження. Повна інструкція нижче.'


def strip(text):
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)
    text = re.sub(r'<!--.*?-->\n?', '', text, flags=re.S)
    return text.strip()


def section(text, heading):
    """Return the block that starts with `heading` and ends before the next heading of the same level."""
    level = len(heading) - len(heading.lstrip('#'))
    lines = text.splitlines()
    out, on = [], False
    for line in lines:
        if line.startswith(heading):
            on = True
        elif on and re.match('#{1,%d} ' % level, line):
            break
        if on:
            out.append(line)
    if not out:
        raise SystemExit(f'Section not found: {heading}')
    return '\n'.join(out)


def mechanics(text, skill):
    """Rewrite skill-mechanics wording into direct references inside one prompt."""
    lines = []
    for line in text.splitlines():
        if re.match(r'^Перед будь-якою дією прочитай `references/guardrails\.md`', line):
            line = 'Правила частини «Безпека» мають пріоритет над усім у цьому тексті.'
        if re.match(r'^Деталі й критерії в `references/extra-moves\.md`', line):
            continue
        lines.append(line)
    text = '\n'.join(lines)
    # Drop the "Additional materials" index: in a prompt every part is inline.
    text = re.sub(r'\n## Додаткові матеріали\n.*?(?=\n## |\Z)', '\n', text, flags=re.S)

    # Ukrainian case of «частина» depends on the word before the reference.
    case = {'за': 'частиною', 'За': 'частиною', 'з': 'частини', 'із': 'частини', 'зі': 'частини',
            'в': 'частині', 'у': 'частині', 'В': 'частині', 'У': 'частині'}
    verbs = {'Пройди', 'пройди', 'Застосовуй', 'застосовуй', 'застосуй', 'Застосуй',
             'прочитай', 'Прочитай', 'Заповни', 'заповни', 'Виконай', 'виконай'}
    nominative = {'-', '(', 'немає,', 'змін:', 'покриття:', 'формулами:', 'і'}

    def ref(match):
        before, opener, name, sec = match.group(1), match.group(2), match.group(3), match.group(4)
        part = PART.get(name, name)
        if before in case:
            noun = case[before]
        elif before in verbs:
            noun = 'частину'
        elif opener or before in nominative or before.endswith((':', ',', '.')) or not before.isalpha():
            noun = 'частина'
        else:
            noun = 'частини'
        tail = f', розділ {sec}' if sec else ''
        return f'{before} {opener}{noun} «{part}»{tail}'
    text = re.sub(r'(\S+) (\(?)`references/([\w-]+)\.md`(?:, розділ ([0-9]+[а-я]?))?', ref, text)
    text = re.sub(r'`references/([\w-]+)\.md`', lambda m: f'частина «{PART.get(m.group(1), m.group(1))}»', text)

    def other(match):
        name = match.group(1)
        if name == skill:
            return 'цей сценарій'
        return f'сценарій «{PROMPT_NAME[name]}»'
    names = '|'.join(re.escape(n) for n in PROMPT_NAME)
    text = re.sub(r'(?:скіл(?:а|ом|у)? )?`(%s)`' % names, other, text)
    text = re.sub(r'\bу цьому скілі\b', 'у цьому сценарії', text)
    return text


def demote(text):
    """Shift headings one level down, leaving examples inside code fences untouched."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith('```'):
            fenced = not fenced
        elif not fenced and re.match(r'#+ ', line):
            line = '#' + line
        out.append(line)
    return '\n'.join(out)


def refs_in_order(skill):
    main = (SKILLS / skill / 'SKILL.md').read_text()
    present = sorted(p.stem for p in (SKILLS / skill / 'references').glob('*.md'))
    specific = [n for n in dict.fromkeys(re.findall(r'references/([\w-]+)\.md', main))
                if n not in SHARED_FIRST + SHARED_LAST]
    specific += [n for n in present if n not in specific + SHARED_FIRST + SHARED_LAST]
    order = SHARED_FIRST + specific + SHARED_LAST
    missing = set(present) - set(order)
    assert not missing, f'{skill}: unordered references {missing}'
    return [n for n in order if n in present]


def draft(skill):
    title = PROMPT_NAME[skill]
    parts = [
        f'# {title}',
        PURPOSE[skill],
        'Як використати: вставте весь текст у новий чат або в регулярну задачу.',
        '---',
    ]
    body = strip((SKILLS / skill / 'SKILL.md').read_text())
    body = re.sub(r'^# .*\n', '', body, count=1)
    parts.append('## Сценарій: мета, режими, порядок роботи\n\n' + demote(mechanics(body, skill)))
    for name in refs_in_order(skill):
        raw = strip((SKILLS / skill / 'references' / f'{name}.md').read_text())
        raw = re.sub(r'^# .*', '# ' + HEAD.get(name, PART.get(name, name)), raw, count=1)
        parts.append(demote(mechanics(raw, skill)))
    if skill == 'exec-daily-brief':
        da = SKILLS / 'exec-document-analysis' / 'references'
        extra = ['# Експрес-аналіз документів: доповнення з повного аналізу']
        for name, heads in BRIEF_DOC_EXTRAS:
            text = strip((da / f'{name}.md').read_text())
            extra += [section(text, h) for h in heads]
        parts.append(demote(mechanics('\n\n'.join(extra), skill)))
    return '\n\n'.join(parts).rstrip() + '\n'


def task(skill):
    prompt = (PROMPTS / f'{skill}.md').read_text()
    header = '\n'.join([TASK_HEADER[skill][0], TASK_DELIVERY, TASK_ORDER])
    return header + '\n\n' + prompt


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--out', type=Path)
    ap.add_argument('--tasks', action='store_true')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()

    if args.tasks:
        TASKS.mkdir(parents=True, exist_ok=True)
        stale = []
        for skill in TASK_HEADER:
            path, text = TASKS / f'{skill}.md', task(skill)
            if args.check:
                if not path.exists() or path.read_text() != text:
                    stale.append(path.name)
            else:
                path.write_text(text)
                print(f'{path.relative_to(ROOT)}: {len(text):,} chars')
        if stale:
            sys.exit('Stale task prompts, run --tasks: ' + ', '.join(stale))
        return

    out = args.out or PROMPTS
    out.mkdir(parents=True, exist_ok=True)
    for skill in PROMPT_NAME:
        path = out / f'{skill}.md'
        if path.exists() and not args.force and args.out is None:
            print(f'skip {path.relative_to(ROOT)} (exists; final prompts are hand-edited)')
            continue
        text = draft(skill)
        path.write_text(text)
        print(f'draft {path}: {len(text):,} chars')


if __name__ == '__main__':
    main()
