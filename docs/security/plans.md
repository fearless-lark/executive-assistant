---
title: Тарифи і ваші дані
---

<p class="ea-eyebrow"><b>01</b> / Безпека / Тарифи</p>

# Тарифи і ваші дані

<p class="ea-lead">Головна межа проходить між особистими і корпоративними тарифами. Від неї залежить, чи навчається модель на ваших чатах, скільки вони зберігаються і хто ще їх бачить.</p>

## Особисті і корпоративні тарифи

| | Особисті тарифи | Корпоративні тарифи |
|---|---|---|
| ChatGPT | Free, Go, Plus, Pro | Business, Enterprise, Edu |
| Claude | Free, Pro, Max | Team, Enterprise |
| Навчання моделей на ваших даних | Можливе. Вимикається вами в налаштуваннях | За замовчуванням вимкнене |
| Договір обробки даних (DPA) | Немає | Є |
| Хто керує зберіганням | Ви, у межах правил вендора | Адміністратор компанії |
| Хто ще бачить чати | Вендор у визначених випадках | Адміністратори компанії, вендор у визначених випадках |

## Навчання на ваших даних

**ChatGPT, особисті тарифи.** Чати можуть використовуватися для навчання моделей. Вимкнути: **Settings → Data controls → «Improve the model for everyone»**. Важлива деталь: оцінка відповіді пальцем угору чи вниз передає всю розмову на можливе навчання навіть після вимкнення. [OpenAI: How your data is used](https://help.openai.com/en/articles/5722486-how-your-data-is-used-to-improve-model-performance)

**ChatGPT, корпоративні тарифи.** Дані Business, Enterprise, Edu і API за замовчуванням не використовуються для навчання. Увімкнути це може лише сама компанія. [OpenAI: Enterprise privacy](https://openai.com/enterprise-privacy/)

**Claude, особисті тарифи.** З 2025 року користувачі Free, Pro і Max самі обирають, чи дозволити навчання на своїх чатах. Якщо дозволили, дані зберігаються до 5 років. Якщо ні, діє 30-денний строк. Чати в режимі інкогніто для навчання не використовуються. [Anthropic: Updates to consumer terms](https://www.anthropic.com/news/updates-to-our-consumer-terms) · [Is my data used for model training?](https://privacy.claude.com/en/articles/10023580-is-my-data-used-for-model-training)

**Claude, корпоративні тарифи.** Комерційні умови прямо забороняють Anthropic навчати моделі на даних клієнта. [Anthropic: Commercial Terms](https://www.anthropic.com/legal/commercial-terms)

**Gemini, особисті акаунти.** Частину чатів переглядають люди, зокрема підрядники. Переглянуті чати зберігаються до 3 років навіть після видалення історії. Google сам радить не вводити конфіденційну інформацію. [Gemini Apps Privacy Hub](https://support.google.com/gemini/answer/13594961)

## Скільки зберігаються чати

| Ситуація | Строк | Джерело |
|---|---|---|
| ChatGPT, тимчасовий чат | Копія до 30 днів з міркувань безпеки | [Temporary Chat](https://help.openai.com/en/articles/8914046-temporary-chat-in-chatgpt) |
| ChatGPT Enterprise, видалений чат | Видаляється протягом 30 днів. Строк зберігання задає адміністратор | [Enterprise privacy](https://openai.com/enterprise-privacy/) |
| Claude Pro і Max, навчання дозволене | До 5 років | [Consumer terms](https://www.anthropic.com/news/updates-to-our-consumer-terms) |
| Claude Pro і Max, навчання заборонене | 30 днів | там само |
| Claude Team і Enterprise, видалений чат | Видаляється з серверів протягом 30 днів. Enterprise може домовитися про власний строк | [Data retention](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data) |
| Claude, чат, позначений системою безпеки | До 2 років | там само |
| Gemini, чат, переглянутий людиною | До 3 років | [Gemini Privacy Hub](https://support.google.com/gemini/answer/13594961) |

Окремий випадок: суд може зобов'язати вендора зберігати навіть видалені чати. Так було з OpenAI у 2025 році. Див. [Суди, таємниця, NDA](courts.md).

## Хто бачить ваші чати

**Адміністратори вашої компанії.** На корпоративних тарифах це нормально і правильно: компанія відповідає за свої дані.

- ChatGPT Enterprise: журнал розмов доступний через Compliance API. Business: адміністратори можуть переглядати, вивантажувати і видаляти чати учасників. [Enterprise privacy](https://openai.com/enterprise-privacy/)
- Claude Enterprise: Compliance API дає програмний доступ до чатів, файлів і проєктів. Власник організації може вивантажити вміст чатів. [Compliance API](https://platform.claude.com/docs/en/manage-claude/compliance-api) · [Audit logs](https://support.claude.com/en/articles/9970975-access-audit-logs)
- Microsoft Copilot: адміністратори шукають чати через Purview і задають строки зберігання. [Data, privacy and security](https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy)

**Працівники вендора.** На корпоративних тарифах OpenAI отримує доступ до чатів лише для розслідування інцидентів, з дозволу клієнта або на вимогу закону. На особистих тарифах Gemini частину чатів читають рецензенти.

**Суд.** Через вимогу суду до вендора. Див. наступний розділ.

## Практичний висновок

- Пошту, договори і P&L підключайте лише на корпоративному тарифі.
- Якщо корпоративного тарифу поки немає, працюйте на демо-компанії або вимкніть навчання і не підключайте конфіденційні документи.
- Скіли знають тип вашого тарифу з профілю. На особистому тарифі вони просять підтвердження перед аналізом документів із грифом конфіденційності, персональних даних працівників чи банківських даних.

Джерела та дати: [Політики вендорів](vendor-policies.md). Стан на 9 жовтня 2026 року.
