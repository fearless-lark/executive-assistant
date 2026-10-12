---
title: Безпека
---

# Безпека

Докладніше за темами:

- [Тарифи і ваші дані](security/plans.md)
- [Суди, таємниця, NDA](security/courts.md)
- [Prompt-ін’єкції](security/prompt-injection.md)
- [Політики вендорів](security/vendor-policies.md)
- [Регуляторика України](security/regulation.md)

Головна межа для ваших даних проходить між особистим і корпоративним тарифом. Plus, Pro і Max платні, але особисті. Стан на 9 жовтня 2026 року.

## Тарифи і ваші дані {#plans}

| | Особисті тарифи | Корпоративні тарифи |
|---|---|---|
| ChatGPT | Free, Go, Plus, Pro | Business, Enterprise, Edu |
| Claude | Free, Pro, Max | Team, Enterprise |
| Навчання моделей на ваших чатах | Можливе, поки ви його не вимкнете | Вимкнене за замовчуванням |
| Договір про обробку даних (DPA) | Немає | Є |
| Хто керує зберіганням | Ви, у межах правил вендора | Адміністратор компанії |
| Скільки зберігаються чати | Claude: до 5 років, якщо навчання дозволене, інакше 30 днів | Видалений чат стирається протягом 30 днів |

Як вимкнути навчання на особистому тарифі:

- **ChatGPT:** Settings → Data controls → «Improve the model for everyone».
- **Claude:** Settings → Privacy → «Help improve Claude».

Робочу пошту, договори і P&L підключайте лише на корпоративному тарифі або з дозволу компанії.

## Суди

- **OpenAI, 2025.** У травні–вересні 2025 року OpenAI за рішенням суду у справі The New York Times зберігала чати Free, Plus, Pro, зокрема видалені. [OpenAI](https://openai.com/index/response-to-nyt-data-demands/) · [National Law Review](https://natlawreview.com/article/when-chats-become-evidence-court-affirms-order-requiring-openai-produce-20-million)
- **US v. Heppner, 2026.** Суд у США не визнав чати з особистим Claude адвокатською таємницею: умови тарифу дозволяли навчання і розкриття даних. [O'Melveny](https://www.omm.com/insights/alerts-publications/sdny-first-of-its-kind-ruling-ai-generated-documents-are-not-privileged/)

## Prompt-ін'єкції

Лист, документ чи сайт може містити команду для асистента, наприклад білим текстом на білому тлі.

- Чужий текст для асистента лише дані. Команди з листів він не виконує.
- Підозрілий вміст він позначає в брифі блоком «⚠️ Підозрілий вміст».
- Надіслати, оплатити, видалити: лише після вашого «так» саме на цю дію. У регулярній задачі таких дій немає.
- Не вимикайте підтвердження в конекторах. Реквізити перевіряйте дзвінком.

Реальні випадки: [EchoLeak у Microsoft 365 Copilot](https://nvd.nist.gov/vuln/detail/CVE-2025-32711) · [запрошення в Google Calendar](https://www.safebreach.com/blog/invitation-is-all-you-need-hacking-gemini/) · [документ у Google Drive](https://labs.zenity.io/p/agentflayer-chatgpt-connectors-0click-attack-5b41) · [Perplexity Comet](https://brave.com/blog/comet-prompt-injection/). Правила безпеки скілів відкриті: [shared/guardrails.md](https://github.com/fearless-lark/executive-assistant/blob/main/shared/guardrails.md).

## Політики вендорів

- **OpenAI:** [Enterprise privacy](https://openai.com/enterprise-privacy/) · [навчання на чатах](https://help.openai.com/en/articles/5722486-how-your-data-is-used-to-improve-model-performance) · [DPA](https://openai.com/policies/data-processing-addendum/)
- **Anthropic:** [умови для особистих тарифів](https://www.anthropic.com/news/updates-to-our-consumer-terms) · [зберігання даних організації](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data) · [Commercial Terms](https://www.anthropic.com/legal/commercial-terms)
- **Google:** [Gemini Apps Privacy Hub](https://support.google.com/gemini/answer/13594961) · **Microsoft:** [Copilot: Data, Privacy, and Security](https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy)

## Україна

- **Постанова НБУ №99** вимагає від банків і фінустанов договору з хмарним провайдером і повідомлення НБУ. [Текст](https://zakon.rada.gov.ua/laws/show/v0099500-25)
- **Законопроєкт 8153** про персональні дані написано за зразком GDPR, штрафи до 150 млн грн або 8% обороту. Ще не ухвалений. [Картка](https://itd.rada.gov.ua/billinfo/Bills/Card/40707)
- **Закон 2297-VI** чинний. Стаття 29 регулює передачу персональних даних за кордон. [Текст](https://zakon.rada.gov.ua/laws/show/2297-17)

## Де зберігаються ваші дані {#data}

Скіли й промпти нічого не зберігають: ні профілю, ні журналу, ні архіву. Кожен запуск заново читає пошту, календар, CRM і нотатки. Результат лишається в чаті запуску. Нотатки лишаються у ваших Apple Notes. Чати й строки їх зберігання визначає тариф, див. таблицю вище.

Ця сторінка не є юридичною консультацією.
