#!/usr/bin/env python3
"""Build the «Сценарії» page and the skills command table from prompts/*.md.

Reads every prompt in prompts/*.md (not prompts/tasks/) and writes:
  docs/scenarios/index.md            two-pane page: scenario list on the left;
                                     on the right a description (from
                                     docs/_snippets/scenarios/<slug>.md) and
                                     the full prompt, with a copy button;
  docs/_snippets/skills-commands.md  table «Сценарій | Команда зі скілом»
                                     for the Skills page;
  docs/_snippets/copy/<slug>.html    one copy button per prompt, for use on
                                     other pages;
  docs/_snippets/schedule-list.html  schedule list with copy buttons for the
                                     task versions (prompts/tasks/*.md).

Prompts are embedded as base64 so the page stays valid Markdown whatever the
prompt contains. The output is deterministic: re-running it on the same
prompts changes nothing.

Usage:
  python3 scripts/build-scenarios-page.py           rebuild both files
  python3 scripts/build-scenarios-page.py --check   exit 1 if either file is stale
                                                    or a description is missing
"""
import argparse
import base64
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / 'prompts'
PAGE = ROOT / 'docs/scenarios/index.md'
DESCRIPTIONS = ROOT / 'docs/_snippets/scenarios'
COMMANDS = ROOT / 'docs/_snippets/skills-commands.md'
COPY = ROOT / 'docs/_snippets/copy'
SCHEDULE = ROOT / 'docs/_snippets/schedule-list.html'
TASKS = PROMPTS / 'tasks'

# Card order follows the workshop. Prompt files not listed here are appended
# at the end with their own H1 as the title.
CARDS = [
    {
        'slug': 'exec-daily-brief', 'emoji': '☀️', 'title': 'Бриф дня',
        'meta': 'щодня · пошта, календар, CRM, документи', 'tags': 'щодня',
        'desc': 'План дня, що вже відбулось і що лишилось. Нові документи, ваші обіцянки, хто мовчить. Кожен висновок має посилання на джерело.',
        'cmd': 'Бриф дня',
    },
    {
        'slug': 'exec-document-analysis', 'emoji': '🔎', 'title': 'Аналіз документа',
        'meta': 'на запит · P&L, договір, звіт', 'tags': 'на-запит',
        'desc': 'Перераховує цифри до клітинки, шукає приховані рядки, вписані вручну числа і тихі правки. Показує гроші під ризиком і питання до відповідального.',
        'cmd': 'Проведи повний аналіз [назва документа]',
    },
    {
        'slug': 'exec-meeting-prep', 'emoji': '🤝', 'title': 'Підготовка до зустрічі',
        'meta': 'на запит · одна зустріч чи дзвінок', 'tags': 'на-запит',
        'desc': 'Учасники та історія з ними, що домовлено минулого разу, обіцянки обох сторін, документи, питання і ваша межа.',
        'cmd': 'Підготуй мене до зустрічі з [людина чи компанія]',
    },
    {
        'slug': 'exec-research', 'emoji': '🧭', 'title': 'Глибоке дослідження',
        'meta': 'на запит · ТЗ для Deep Research', 'tags': 'на-запит',
        'desc': 'Вирішує, чи потрібне дослідження, і складає ТЗ без назв вашої компанії. Ви вставляєте ТЗ у Deep Research, потім просите звірити звіти.',
        'cmd': 'Склади ТЗ на дослідження [тема]',
    },
    {
        'slug': 'exec-review', 'emoji': '📆', 'title': 'Огляд періоду',
        'meta': 'на запит або щоп’ятниці · будь-який період', 'tags': 'щотижня на-запит',
        'desc': 'Куди пішли час і увага, що це дало та чи відповідало пріоритетам. Що делегувати, скоротити і чому приділити більше часу.',
        'cmd': 'Огляд тижня',
    },
    {
        'slug': 'exec-radar', 'emoji': '📡', 'title': 'Тижневий радар',
        'meta': 'щопонеділка · регуляторика, конкуренти, згадки', 'tags': 'щотижня',
        'desc': 'Раз на тиждень збирає зовнішні зміни, що стосуються вашого бізнесу. Кожен сигнал має джерело, дату і наступний крок.',
        'cmd': 'Радар',
    },
    {
        'slug': 'notes-triage', 'emoji': '🗂️', 'title': 'Розбір нотаток',
        'meta': 'щодня · нові нотатки', 'tags': 'щодня нотатки',
        'desc': 'Розбирає нові нотатки: дія чи ідея. Дії стають чернетками і нагадуваннями, нотатки переходять у папки-статуси.',
        'cmd': 'Оброби нові нотатки',
    },
    {
        'slug': 'notes-assistant', 'emoji': '💬', 'title': 'Робота з нотатками',
        'meta': 'на запит · нотатки в розмові', 'tags': 'на-запит нотатки',
        'desc': 'Знаходить думки на тему, розбирає нотатки разом з вами, перетворює нотатку на задачу в CRM, лист чи ТЗ дослідження.',
        'cmd': 'Візьми нотатку про [тема] і створи задачу',
    },
    {
        'slug': 'exec-family-week', 'emoji': '🏡', 'title': 'Тиждень для родини',
        'meta': 'щонеділі · план для родини і помічника', 'tags': 'щотижня',
        'desc': 'Де ви будете по днях, коли не на зв’язку, де потрібен водій. Без ділових деталей. Результат у чаті, надсилаєте ви.',
        'cmd': 'Тиждень для родини',
    },
]

CHIPS = [('', 'Усі'), ('щодня', 'щодня'), ('щотижня', 'щотижня'), ('на-запит', 'на запит'), ('нотатки', 'нотатки')]

INTRO = """---
title: Сценарії
hide:
  - toc
---

<!-- Generated by scripts/build-scenarios-page.py from prompts/*.md and docs/_snippets/scenarios/*.md. Edit those, not this file. -->

<p class="ea-eyebrow">Сценарії</p>

# Сценарії

Сценарій це готова робота для асистента. Відкрийте картку: праворуч повний промпт, поруч вкладка з детальним описом.

!!! do "Що зробити зараз"
    1. Оберіть «Бриф дня» і натисніть **Скопіювати промпт**.
    2. Відкрийте новий чат, вставте текст і надішліть.
"""

OUTRO = """
Щоб сценарій запускався сам, поставте його на [розклад](../schedule.md). Щоб не копіювати промпт щоразу, встановіть [скіли](../skills.md).
"""


def b64(text):
    return base64.b64encode(text.encode('utf-8')).decode('ascii')


def esc(text):
    return html.escape(text, quote=True)


def read_prompts():
    found = {p.stem: p.read_text(encoding='utf-8') for p in sorted(PROMPTS.glob('*.md'))}
    cards = []
    for card in CARDS:
        if card['slug'] in found:
            cards.append(dict(card, text=found.pop(card['slug'])))
        else:
            print(f"warning: prompts/{card['slug']}.md not found, card skipped", file=sys.stderr)
    for slug, text in sorted(found.items()):
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        title = next((l.lstrip('# ').strip() for l in lines if l.startswith('# ')), slug)
        desc = next((l for l in lines if not l.startswith('#')), '')
        cards.append({'slug': slug, 'emoji': '📄', 'title': title, 'meta': 'на запит',
                      'tags': 'на-запит', 'desc': desc, 'cmd': '', 'text': text})
    return cards


def card_html(c):
    return (
        f'<li><div class="ea-card" id="{c["slug"]}" data-slug="{c["slug"]}" data-tags="{c["tags"]}">'
        f'<button class="ea-card__head" type="button" aria-expanded="false">'
        f'<span class="ea-card__emoji" aria-hidden="true">{c["emoji"]}</span>'
        f'<span class="ea-card__main"><span class="ea-card__title">{esc(c["title"])}</span>'
        f'<span class="ea-card__meta">{esc(c["meta"])}</span></span>'
        f'<span class="ea-card__chevron" aria-hidden="true"></span></button>'
        f'<div class="ea-card__body" hidden><p class="ea-card__desc">{esc(c["desc"])}</p></div>'
        f'</div></li>'
    )


def detail_block(c):
    # Hidden store; the viewer moves the section in when the card is selected.
    # Headings become styled paragraphs: no anchors, no TOC entries, so the
    # URL hash keeps naming the selected scenario.
    path = DESCRIPTIONS / f'{c["slug"]}.md'
    if path.exists():
        lines = []
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.startswith('#### '):
                lines.append(f'<p class="ea-dh">{esc(line[5:].strip())}</p>')
            else:
                lines.append(line)
        body = '\n'.join(lines).strip()
    else:
        body = esc(c['desc'])
    return (f'<section class="ea-detail" data-detail="{c["slug"]}" markdown>\n\n'
            f'{body}\n\n</section>')


def build_page(cards):
    chips = '\n'.join(
        f'<button class="ea-chip{" is-active" if not tag else ""}" type="button" data-tag="{tag}">{label}</button>'
        for tag, label in CHIPS)
    items = '\n'.join(card_html(c) for c in cards)
    prompts = '\n'.join(f'<script type="text/plain" data-prompt="{c["slug"]}">{b64(c["text"])}</script>' for c in cards)
    details = '\n\n'.join(detail_block(c) for c in cards)
    app = f"""<div class="ea-app ea-app--scenarios" data-ea-app data-mode="scenario">
<div class="ea-app__list">
<div class="ea-filter">
{chips}
</div>
<ul class="ea-cards">
{items}
</ul>
</div>
<aside class="ea-app__viewer" data-ea-viewer aria-live="polite">
<div class="ea-viewer__empty">Оберіть сценарій у списку.</div>
<div class="ea-viewer__content" hidden>
<div class="ea-viewer__bar"><span class="ea-viewer__title"></span><button class="ea-copy ea-copy--bar" type="button" data-copy-current>Скопіювати промпт</button></div>
<div class="ea-viewer__tabs" role="tablist">
<button class="ea-vtab is-active" type="button" role="tab" aria-selected="true" data-view="prompt">Промпт</button>
<button class="ea-vtab" type="button" role="tab" aria-selected="false" data-view="detail">Детальний опис</button>
</div>
<pre class="ea-viewer__pre" data-pane="prompt"><code class="ea-viewer__code"></code></pre>
<div class="ea-viewer__detail" data-pane="detail" hidden></div>
</div>
</aside>
<template class="ea-prompts">
{prompts}
</template>
</div>

<div class="ea-details" markdown>

{details}

</div>
"""
    return INTRO + '\n' + app + OUTRO


def build_commands(cards):
    rows = '\n'.join(
        f'| [{c["title"]}](scenarios/index.md#{c["slug"]}) | `{c["cmd"]}` |'
        for c in cards if c['cmd'])
    return ('<!-- Generated by scripts/build-scenarios-page.py. Do not edit by hand. -->\n\n'
            '| Сценарій | Команда зі скілом |\n|---|---|\n' + rows + '\n')


# Scheduled scenarios: slug, when, time, one-line result. The copied text is
# prompts/tasks/<slug>.md when it exists, otherwise the plain prompt.
SCHEDULED = [
    ('exec-daily-brief', 'Робочі дні', '07:30', 'План дня, документи, ваші обіцянки'),
    ('notes-triage', 'Щодня', '09:30', 'Нові думки стають задачами і нагадуваннями'),
    ('exec-radar', 'Понеділок', '08:00', 'Регуляторика, конкуренти, згадки компанії'),
    ('exec-review', "П'ятниця", '17:00', 'Куди пішли зусилля, що це дало і що змінити'),
    ('exec-family-week', 'Неділя', '17:00', 'Де ви будете наступного тижня'),
]


def build_copy(c):
    pid = f'copy-{c["slug"]}'
    return (f'<!-- Generated by scripts/build-scenarios-page.py from prompts/{c["slug"]}.md. Do not edit by hand. -->\n'
            f'<span class="ea-prompt ea-prompt--inline">'
            f'<button class="ea-copy ea-copy--orange" type="button" data-copy-b64="{pid}">Скопіювати промпт «{esc(c["title"])}»</button>'
            f'<span class="ea-copy-status" role="status" aria-live="polite"></span></span>'
            f'<template class="ea-prompts"><script type="text/plain" data-prompt="{pid}">{b64(c["text"])}</script></template>\n')


def build_schedule(cards):
    by = {c['slug']: c for c in cards}
    rows, store = [], []
    for slug, day, time, desc in SCHEDULED:
        c = by.get(slug)
        if not c:
            continue
        task = TASKS / f'{slug}.md'
        text = task.read_text(encoding='utf-8') if task.exists() else c['text']
        pid = f'task-{slug}'
        store.append(f'<script type="text/plain" data-prompt="{pid}">{b64(text)}</script>')
        rows.append(
            f'<div class="ea-sched__row"><span class="ea-sched__emoji" aria-hidden="true">{c["emoji"]}</span>'
            f'<span class="ea-sched__main"><b>{esc(c["title"])}</b><span>{esc(desc)}</span></span>'
            f'<span class="ea-sched__when"><span>{esc(day)}</span><b>{time}</b></span>'
            f'<button class="ea-copy ea-copy--orange ea-sched__copy" type="button" data-copy-b64="{pid}">Скопіювати промпт</button></div>')
    return ('<!-- Generated by scripts/build-scenarios-page.py from prompts/tasks/*.md. Do not edit by hand. -->\n'
            '<div class="ea-sched">\n' + '\n'.join(rows) + '\n</div>\n'
            '<template class="ea-prompts">\n' + '\n'.join(store) + '\n</template>\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='exit 1 if the generated files are stale')
    args = parser.parse_args()
    cards = read_prompts()
    outputs = {PAGE: build_page(cards), COMMANDS: build_commands(cards), SCHEDULE: build_schedule(cards)}
    for c in cards:
        outputs[COPY / f'{c["slug"]}.html'] = build_copy(c)
    stale = []
    missing = [c['slug'] for c in cards if not (DESCRIPTIONS / f'{c["slug"]}.md').exists()]
    if missing:
        print('warning: no description in docs/_snippets/scenarios/ for: ' + ', '.join(missing), file=sys.stderr)
        if args.check:
            stale.extend(f'docs/_snippets/scenarios/{m}.md (missing)' for m in missing)
    for path, text in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != text:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
    if stale:
        print('Stale, run python3 scripts/build-scenarios-page.py: ' + ', '.join(stale), file=sys.stderr)
        sys.exit(1)
    total = sum(len(c['text']) for c in cards)
    print(f'OK: {len(cards)} prompts, {total:,} characters embedded')


if __name__ == '__main__':
    main()
