# AI-асистент керівника

Матеріали практичного воркшопу для керівників: скіли для Claude і ChatGPT та сайт із покроковими інструкціями.

**Сайт:** https://fearless-lark.github.io/executive-assistant/

Асистент щоранку готує бриф з аналізом нових документів, розбирає надиктовані нотатки, складає огляди тижня і місяця, готує глибокі дослідження і тижневий радар. Усі скіли мають спільні правила безпеки: чужий текст вважається даними, а зовнішні дії виконуються лише після вашого підтвердження.

## Встановлення скілів

Репозиторій є маркетплейсом плагінів.

- **Claude:** Customize → Plugins → Add → Add marketplace → `https://github.com/fearless-lark/executive-assistant` → Install. Увімкніть Sync automatically.
- **ChatGPT Business і Enterprise:** адміністратор відкриває Admin console → Plugins → Add → Import marketplace і вставляє те саме посилання.

Після встановлення напишіть асистенту «Налаштуй асистента». Скіл `exec-setup` створить ваш профіль і розклад регулярних задач. Детально: [Підключення](https://fearless-lark.github.io/executive-assistant/setup/).

## Скіли

| Скіл | Що робить |
|---|---|
| `exec-setup` | Інтерв'ю, персональний профіль `exec-profile`, розклад задач, чекліст безпеки |
| `exec-daily-brief` | Ранковий бриф з автоматичним аналізом документів |
| `exec-document-analysis` | Аналіз P&L, договору, пропозиції, звіту |
| `notes-triage` | Щоденний розбір надиктованих нотаток і реєстр |
| `notes-assistant` | Робота з нотатками в розмові |
| `exec-review` | Огляд тижня, місяця, кварталу, року і контроль запусків |
| `exec-research` | ТЗ для Deep Research, рівні «Стандарт» і «Максимум», звірка звітів |
| `exec-radar` | Тижневий радар регуляторики, конкурентів і згадок |
| `exec-family-week` | План тижня для родини і помічника без ділових деталей |

## Структура

```
.claude-plugin/   маніфести маркетплейсу і плагіна
skills/           скіли (кожен у своїй теці з SKILL.md і references/)
shared/           спільні блоки: безпека, профіль, формат виводу
templates/        шаблони профілю і розкладу
scripts/          службові скрипти
tests/            тести скілів
docs/             сайт (MkDocs Material)
overrides/        шаблони теми сайту
```

Локальна збірка сайту:

```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Сайт розгортається на GitHub Pages автоматично після push у `main`.

## Ліцензія

MIT, див. [LICENSE](LICENSE). Ліцензія поширюється на скіли, шаблони і тексти сайту.

## Контакти

Skywell, Київ, вул. Сурікова, 3, корп. 37 · [info@skywell.com.ua](mailto:info@skywell.com.ua) · +380 (44) 225-11-55 · [skywell.com.ua](https://skywell.com.ua/)
