---
title: Підключення
---

<p class="ea-eyebrow">Підключення</p>

# Підключення

Асистент бачить лише те, що ви підключили.

## Що підключити

| Джерело | Для чого | Microsoft 365 | Google |
|---|---|---|---|
| Пошта | Листи, вкладення, ваші обіцянки | Outlook | Gmail |
| Календар | Зустрічі дня і тижня | Outlook Calendar | Google Calendar |
| Документи | P&L, договори, звіти | SharePoint, OneDrive | Google Drive |
| CRM | Клієнти, угоди, задачі | Dynamics 365 через ІТ | HubSpot, Salesforce |

Коли базове працює, додайте одне-два джерела зі своєї роботи:

| Джерело | Приклад |
|---|---|
| **Записи зустрічей Teams** | «Що вирішили вчора на правлінні, хто відповідальний і до коли?» |
| **Папки в SharePoint** | «Підготуй мене до засідання: п'ять ризиків, відхилення від плану, по три питання кожному доповідачу» |
| **Спільна скринька Outlook** | «Які запити від інвесторів, банків і ключових клієнтів лишились без відповіді цього тижня? Кому доручити?» |
| **Jira, Asana чи monday.com** | «Які проєкти зсунули строки за місяць і чому?» |

!!! warning "Приватність даних"
    Робочу пошту й документи підключайте лише на корпоративному тарифі або з дозволу компанії. Деталі в розділі [Безпека](security.md).

!!! do "Що зробити зараз"

    === "ChatGPT"

        1. Settings → **Plugins** (у частині версій **Apps**).
        2. Знайдіть **Outlook Email**, **Outlook Calendar**, **SharePoint** або Gmail, Google Calendar, Google Drive → **Connect**.
        3. Увійдіть у робочий акаунт і підтвердьте доступ.

    === "Claude"

        1. Customize → **Connectors** → **+**.
        2. Знайдіть **Microsoft 365** (одразу пошта, календар, SharePoint, OneDrive і Teams) або Gmail, Google Calendar, Google Drive → **Connect**.
        3. Увійдіть у робочий акаунт і підтвердьте доступ.

    Потім відкрийте новий чат і вставте промпт перевірки доступу:

    ```text
    Перевір фактичний доступ до моєї пошти, календаря, сховища і CRM. Для пошти покажи теми трьох останніх листів, для календаря три найближчі події, для сховища назви трьох документів. Недоступні джерела назви прямо. Нічого не змінюй, не надсилай і не встановлюй.
    ```

## Що ви побачите

Три листи, три події і три документи з ваших джерел. Якщо якесь джерело недоступне, асистент так і напише.

## Microsoft 365: що зробить ІТ {#microsoft-365}

Microsoft 365 підключається лише з робочого акаунта. Глобальний адміністратор один раз дає згоду для компанії в Microsoft Entra. Без цього кнопка **Connect** покаже помилку доступу.

- **ChatGPT Business:** застосунки ввімкнені за замовчуванням. **Enterprise:** адміністратор вмикає кожен у Admin → Plugins.
- **Claude Team і Enterprise:** власник організації додає конектор в Organization settings → **Connectors**. Особисті акаунти @outlook.com Claude не підтримує.
- Спершу лише читання. Надсилання листів і зміни в календарі адміністратор вмикає окремо.

Готовий лист для ІТ: [Для компанії](company.md#it-letter).

## Усі можливості і де про них читати

=== "ChatGPT"

    | Що | Для чого | Довідка |
    |---|---|---|
    | Outlook Email і Calendar | Листи, спільні скриньки, зустрічі | [Outlook в ChatGPT](https://help.openai.com/en/articles/12512241-outlook-email-and-calendar-apps-in-chatgpt) |
    | SharePoint, OneDrive | Документи компанії | [SharePoint в ChatGPT](https://help.openai.com/en/articles/12143177-sharepoint-app-in-chatgpt) |
    | Microsoft Teams | Чати, канали, зустрічі | [Teams в ChatGPT](https://help.openai.com/en/articles/12552368-microsoft-teams-app-for-chatgpt) |
    | Gmail, Google Calendar | Пошта і зустрічі Google | [Google в ChatGPT](https://help.openai.com/en/articles/10408842-google-app-for-chatgpt-data-controls-faq) |
    | Google Drive | Документи, таблиці Google | [Google Drive в ChatGPT](https://help.openai.com/en/articles/10929079-google-drive-app-and-setup-in-chatgpt) |
    | HubSpot | Клієнти, угоди, задачі | [HubSpot і ChatGPT](https://knowledge.hubspot.com/integrations/connect-your-hubspot-account-to-chatgpt) |
    | Slack | Командні чати | [Slack в ChatGPT](https://help.openai.com/en/articles/12525822-using-slack-in-chatgpt) |
    | Notion | Бази знань | [Notion в ChatGPT](https://help.openai.com/en/articles/12532955-notion-app-and-setup-in-chatgpt) |
    | Аналіз файлів | Excel, CSV, графіки | [Аналіз даних](https://help.openai.com/en/articles/8437071-data-analysis-with-chatgpt) |
    | ChatGPT для Excel | Асистент у таблиці | [ChatGPT for Excel](https://help.openai.com/en/articles/20001063-chatgpt-for-excel-and-google-sheets) |
    | Документи й презентації | Word, Excel, PowerPoint | [Файли в ChatGPT Work](https://help.openai.com/en/articles/20001278-creating-and-editing-documents-spreadsheets-and-presentations-with-chatgpt-work) |
    | Браузер | Дії на сайтах і в ERP | [Вбудований браузер](https://help.openai.com/en/articles/20001277-using-the-built-in-browser-in-the-chatgpt-desktop-app) |
    | Deep research | Глибоке дослідження | [Deep research](https://help.openai.com/en/articles/10500283-deep-research-in-chatgpt) |
    | Регулярні задачі | Бриф щоранку | [Scheduled tasks](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt) |
    | Керування доступами | Для адміністратора | [Підключення застосунків](https://help.openai.com/en/articles/20001494-connecting-and-managing-app-accounts-in-chatgpt) |

=== "Claude"

    | Що | Для чого | Довідка |
    |---|---|---|
    | Microsoft 365 | Outlook, календар, SharePoint, OneDrive, Teams і записи зустрічей | [Конектор Microsoft 365](https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector) |
    | Gmail, Calendar, Drive | Пошта, зустрічі, документи Google | [Конектори Google](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors) |
    | HubSpot | Клієнти, угоди, задачі | [HubSpot](https://claude.com/connectors/hubspot) |
    | Salesforce | CRM, бета для схвалених компаній | [Salesforce](https://support.claude.com/en/articles/16952184-set-up-salesforce-in-claude-for-your-organization) |
    | Slack | Командні чати | [Slack](https://claude.com/connectors/slack) |
    | Jira, Confluence | Проєкти і документація | [Atlassian](https://claude.com/connectors/atlassian) |
    | Notion | Бази знань | [Notion](https://claude.com/connectors/notion) |
    | Zoom | Записи і підсумки зустрічей | [Zoom](https://claude.com/connectors/zoom-for-claude) |
    | Аналіз файлів | Excel, CSV, графіки, документи | [Файли в Claude](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude) |
    | Claude для Excel | Асистент у таблиці | [Claude for Excel](https://support.claude.com/en/articles/12650343-use-claude-for-excel) |
    | Claude in Chrome | Дії на сайтах і в ERP | [Claude in Chrome](https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome) |
    | Research | Глибоке дослідження | [Research](https://support.claude.com/en/articles/11088861-use-research-on-claude) |
    | Регулярні задачі | Бриф щоранку | [Scheduled tasks](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork) |
    | Керування доступами | Для адміністратора | [Конектори](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities) |

Далі: [Сценарії](scenarios/index.md).
