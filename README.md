# 📘 Assistant Bot CLI / Консольний бот-асистент

## Contents · Зміст
- [UA · Українська](#ua--українська)
- [EN · English](#en--english)

---
## UA · Українська

### 1. Опис
Assistant Bot — це консольний застосунок для керування контактами та нотатками. Він допомагає:
- додавати, редагувати та шукати контакти з телефонами й днями народження;
- вести нотатки з тегами та кольоровими мітками;
- зберігати й відновлювати стан із файлів (ручні збереження та автозбереження);
- спілкуватися через дружній CLI з інтерактивними підказками;
- переглядати форматовані таблиці та календар з днями народження (Rich-rendering).

### 2. Системні вимоги
1. **Операційна система:** Windows, macOS або Linux.
2. **Python:** версія **3.12+** (обов'язково!).
3. **pip:** встановлений менеджер пакетів Python.

> ⚠️ **Важливо:** Проект використовує Python 3.12+. Версії 3.10 та 3.11 не підтримуються.

### 3. Встановлення

Встановлення як пакет 
**Клонування репозиторію**
```pwsh
git clone https://github.com/GUARD10/goit-group-3-final-project.git
cd goit-group-3-final-project
```

**Створення та активація середовища (рекомендовано)**
```pwsh
# Якщо 'py' є стандартним лаунчером python
py -m venv .venv 

# Якщо 'python' є стандартним лаунчером
python -m venv .venv 

 # Активація середовища в Windows
.\.venv\Scripts\activate 

# Активація середовища в macOS/Linux
source .venv/bin/activate  
```

**Встановлення у режимі редагування**
```pwsh
pip install -e .
```

### 4. Запуск
```pwsh
assistant-bot
```

Після старту бот автоматично намагається підвантажити останній збережений стан контактів і нотаток, якщо файли є у директорії `files/`.

## 5. Список команд

### 🟦 Базові
| Команда | Опис |
|--------|------|
| `hello` | 👋 Привітання |
| `help` | ❓ Показати всі команди |
| `exit` | 👋 Зберегти стан і вийти |
| `close` | 👋 Те саме, що `exit` |
| `calendar [month]? [year]?` | 📅 Календар з днями народження |

---

### 🟩 Контакти
| Команда | Опис |
|--------|------|
| `add-contact [contact-name] [phone]` | ➕ Додати контакт |
| `delete-contact [contact-name]` | 🗑️ Видалити контакт |
| `show-contact [contact-name]` | 👁️ Показати деталі |
| `all-contacts` | 📋 Усі контакти |
| `add-phone [contact-name] [phone]` | 📞 Додати телефон |
| `delete-phone [contact-name] [phone]` | 🗑️ Видалити телефон |
| `add-email [contact-name] [email]` | 📧 Додати email |
| `delete-email [contact-name] [email]` | 🗑️ Видалити email |
| `set-address [contact-name] [address...]` | 🏠 Встановити адресу |
| `clear-address [contact-name]` | 🗑️ Очистити адресу |
| `add-birthday [contact-name] [DD.MM.YYYY]` | 🎂 Додати/замінити день народження |
| `clear-birthday [contact-name]` | 🗑️ Видалити день народження |
| `upcoming-birthdays [days]?` | 🎁 Найближчі дні народження |
| `search-contacts [text]` | 🔍 Пошук контактів |

---

### 🟧 Нотатки
| Команда | Опис |
|--------|------|
| `add-note [note-name]` | 📝 Створити ноту |
| `delete-note [note-name]` | 🗑️ Видалити ноту |
| `show-note [note-name]` | 👁️ Показати ноту |
| `all-notes` | 📚 Усі ноти |
| `search-notes [text]` | 🔍 Пошук |
| `edit-note-title [note-name]` | ✏️ Редагувати заголовок |
| `edit-note-content [note-name]` | 📄 Редагувати контент |
| `add-note-tags [note-name] [tag:color]...` | 🏷️ Додати теги |
| `remove-note-tag [note-name] [tag]` | ❌ Видалити тег |
| `show-notes-by-tag [tag]?` | 🏷️ Фільтр за тегом |

---

### 🟪 Файли
| Команда | Опис |
|--------|------|
| `save-note [file-name]?` | 💾 Зберегти нотатки |
| `load-note [file-name]` | 📂 Завантажити нотатки |
| `delete-note-file [file-name]` | 🗑️ Видалити файл нотатки |
| `note-files` | 📁 Список файлів |
| `save-contact [file-name]?` | 💾 Зберегти контакти |
| `load-contact [file-name]` | 📂 Завантажити контакти |
| `delete-contact-file [file-name]` | 🗑️ Видалити файл |
| `contacts-files` | 📁 Список файлів |
---
### 6. Конфігурація (опціонально)
Ви можете налаштувати директорії для збереження файлів за допомогою змінних середовища:

```pwsh
# Windows PowerShell
$env:ASSISTANT_CONTACTS_DIR="C:\MyData\contacts"
$env:ASSISTANT_NOTES_DIR="C:\MyData\notes"
assistant-bot

# Linux/macOS
export ASSISTANT_CONTACTS_DIR="/home/user/data/contacts"
export ASSISTANT_NOTES_DIR="/home/user/data/notes"
assistant-bot
```

**За замовчуванням:**
- Контакти: `files/contacts`
- Нотатки: `files/notes`

### 7. Архітектура (огляд)
Шарова модель:
- CLI (`assistant_bot_cli.py`, `main.py`): цикл введення, автодоповнення через Prompt Toolkit.
- BLL (`bll/services`, `helpers`, `entity_builders`): маршрутизація команд, CRUD, форматування таблиць/календаря.
- DAL (`dal/entities`, `storages`, `file_managers`): доменні сутності, збереження pickle-снепшотів.
Докладніше: див. `structure.md`.

### 8. Персистентність даних
- Файли зберігаються окремо для контактів та нотаток у `files/contacts`, `files/notes`.
- Автозбереження при виконанні команд `save-*` без імені файлу.
- Можливість мати історію станів (timestamp у назві файлу) та завантажувати будь-який.
- Поточний backend: лише `pickle`.

### 8.1 Змінні середовища (повний список)
| Змінна | Значення за замовчуванням | Призначення |
|--------|---------------------------|-------------|
| `ASSISTANT_CONTACTS_DIR` | `files/contacts` | Каталог збереження контактів |
| `ASSISTANT_NOTES_DIR` | `files/notes` | Каталог збереження нотаток |
| `ASSISTANT_PHONE_REGION` | `UA` | Регіон для валідації телефонів (`UA`, `US`, `INTL`) |

Приклад:
```pwsh
$env:ASSISTANT_PHONE_REGION="US"
assistant-bot
```

### 8.2 Палітра кольорів тегів
Доступні кольори (назва → HEX):
```
Coral Red  #F44336
Cerise     #E91E63
Royal Purple #9C27B0
Indigo     #3F51B5
Sky Blue   #03A9F4
Teal       #009688
Emerald    #4CAF50
Amber      #FF9800
Mocha      #795548
Slate      #607D8B
```
Використання: `add-note-tags idea teal:009688 focus amber:FF9800` (можна задавати ім'я або hex через `tag:color`).

### 11. Тестування та якість коду
Запуск тестів:
```pwsh
pytest -q
```
Інструменти якості (dev-залежності у `pyproject.toml`):
```pwsh
pip install -e .[dev]
ruff check .
mypy .
```
PEP 8 забезпечується через Ruff; типи — через mypy. Тести покривають календар, дати, команди, роботу зі сховищами.
Додатково: запуск частини тестів:
```pwsh
pytest tests/test_calendar_renderer.py -q
pytest tests/note_tests -q
```

### 11.1 GitHub Actions (CI)
У каталозі `.github/workflows/` знаходяться ОКРЕМІ файли робочих процесів CI:

| Файл | Призначення |
|------|-------------|
| `.github/workflows/tests.yml` | Запуск `pytest` (юнiт-тести) на гілках `main`, `main-beta` для `push` та `pull_request`. |
| `.github/workflows/code_quality.yml` | Лінтинг (Ruff) і статична перевірка типів (mypy) на тих самих гілках. |

Як працює pipeline узагальнено:
1. Checkout репозиторію.
2. Встановлення Python 3.12.
3. Встановлення залежностей з `requirements.txt`.
4. Виконання лінтингу / типізації (code_quality) або тестів (tests).
5. У разі помилок робочий процес завершується зі статусом failure.

### 11.2 Гайд для розробника
Швидкий старт:
```pwsh
git clone https://github.com/GUARD10/goit-group-3-final-project.git
cd goit-group-3-final-project
py -m venv .venv
./.venv/Scripts/activate
pip install -e .[dev]
ruff check .
mypy .
pytest -q
assistant-bot
```
Перед пушем:
```pwsh
ruff check .
ruff format .  # якщо потрібно автоформатування
mypy .
pytest
```

### 13. Відповідність критеріям прийому
| Критерій | Виконання                                |
|----------|------------------------------------------|
| Публічний репозиторій | ✅ GitHub, відкритий доступ               |
| Документація/README | ✅ Опис, інструкції, команди, архітектура |
| CLI інтерфейс (цикл) | ✅ `main.py` цикл до `exit`               |
| Інтерактивність / автодоповнення | ✅ Prompt Toolkit (`PromptCompleter`)     |
| Меню лише при старті | ✅ Привітальне повідомлення один раз      |
| Читабельність та кольори | ✅ Colorama + таблиці/календар            |
| Збереження даних між сесіями | ✅ Pickle файли у `files/*`               |
| Обробка некоректних даних | ✅ Винятки без падіння програми           |
| ООП, спадкування, композиція | ✅ Сутності + builder + сервіси           |
| Валідація кожного поля | ✅ Телефон, email, дата народження        |
| Чистий код, PEP 8 | ✅ Ruff, структуровані модулі             |
| Код-ревʼю ментора | ✅ Перевірено                             |
| Теги до нотаток | ✅ `add-note-tags`, `show-notes-by-tag`   |
| Пошук/фільтр за тегами | ✅ `show-notes-by-tag`, `search-notes`    |
| Наявність CI (GitHub Actions) | ✅ `tests.yml`, `code_quality.yml`        |

### 14. Roadmap (можливі покращення)
- Перехід з pickle на SQLite/JSON.
- Розширена типізація (увімкнути `disallow_untyped_defs`).
- Логування замість `print` (модуль `logging`).
- Інтеграційні тести для повних сценаріїв.
- Підтримка `json` backend як перша альтернатива.
- Документація палітри тегів у окремому markdown (`tags.md`).

### 15. Ліцензія
MIT License (див. `pyproject.toml`).

---
## EN · English

### 1. Overview
Assistant Bot is a command-line application for managing contacts and notes. It lets you:
- add, edit, and search contacts with phones and birthdays;
- maintain tagged notes with color-coded labels;
- persist and restore state from files (manual saves plus autosaves);
- interact via a friendly CLI with interactive prompts;
- view rich-formatted tables and a calendar highlighting birthdays.

### 2. Prerequisites
1. **Operating System:** Windows, macOS, or Linux.
2. **Python:** version **3.12 or newer** (required!).
3. **pip:** Python package manager installed.

> ⚠️ **Important:** This project uses Python 3.12+. Python 3.10 and 3.11 are not supported.

### 3. Installation

### Install as package

**Clone the repository**
```pwsh
git clone https://github.com/GUARD10/goit-group-3-final-project.git
cd goit-group-3-final-project
```
**Create & activate a virtual environment (recommended)**
```pwsh
# if 'py' is the default python launcher
py -m venv .venv 

# if 'python' is the default python launcher
python -m venv .venv 

 # .venv actiovation in Windows
.\.venv\Scripts\activate 

# .venv actiovation in macOS/Linux
source .venv/bin/activate 
```

**Install in editable mode**
```pwsh
pip install -e .
```

### 4. Run

```pwsh
assistant-bot
```

On startup the bot tries to load the most recent contacts/notes snapshot from the `files/` directory when available.

## 5. Command List

### 🟦 Basic
| Command | Description |
|--------|-------------|
| `hello` | 👋 Say hello |
| `help` | ❓ Show all commands |
| `exit` | 👋 Save & exit |
| `close` | 👋 Alias for exit |
| `calendar [month]? [year]?` | 📅 Calendar with birthdays |

---

### 🟩 Contacts
| Command | Description |
|--------|-------------|
| `add-contact [contact-name] [phone]` | ➕ Create contact |
| `delete-contact [contact-name]` | 🗑️ Delete contact |
| `show-contact [contact-name]` | 👁️ Show details |
| `all-contacts` | 📋 List all contacts |
| `add-phone [contact-name] [phone]` | 📞 Add phone |
| `delete-phone [contact-name] [phone]` | 🗑️ Remove phone |
| `add-email [contact-name] [email]` | 📧 Add email |
| `delete-email [contact-name] [email]` | 🗑️ Remove email |
| `set-address [contact-name] [address...]` | 🏠 Set address |
| `clear-address [contact-name]` | 🗑️ Clear address |
| `add-birthday [contact-name] [DD.MM.YYYY]` | 🎂 Add birthday |
| `clear-birthday [contact-name]` | 🗑️ Clear birthday |
| `upcoming-birthdays [days]?` | 🎁 Birthdays in next N days |
| `search-contacts [text]` | 🔍 Search contacts |

---

### 🟧 Notes
| Command | Description |
|--------|-------------|
| `add-note [note-name]` | 📝 Create note |
| `delete-note [note-name]` | 🗑️ Delete note |
| `show-note [note-name]` | 👁️ Show note |
| `all-notes` | 📚 List notes |
| `search-notes [text]` | 🔍 Search notes |
| `edit-note-title [note-name]` | ✏️ Edit title |
| `edit-note-content [note-name]` | 📄 Edit content |
| `add-note-tags [note-name] [tag:color]...` | 🏷️ Add tags |
| `remove-note-tag [note-name] [tag]` | ❌ Remove tag |
| `show-notes-by-tag [tag]?` | 🏷️ Filter by tag |

---

### 🟪 Files
| Command | Description |
|--------|-------------|
| `save-note [file-name]?` | 💾 Save notes |
| `load-note [file-name]` | 📂 Load notes |
| `delete-note-file [file-name]` | 🗑️ Delete note file |
| `note-files` | 📁 List files |
| `save-contact [file-name]?` | 💾 Save contacts |
| `load-contact [file-name]` | 📂 Load contacts |
| `delete-contact-file [file-name]` | 🗑️ Delete file |
| `contacts-files` | 📁 List files |


### 6. Configuration (optional)
You can customize file storage directories using environment variables:

```pwsh
# Windows PowerShell
$env:ASSISTANT_CONTACTS_DIR="C:\MyData\contacts"
$env:ASSISTANT_NOTES_DIR="C:\MyData\notes"
assistant-bot

# Linux/macOS
export ASSISTANT_CONTACTS_DIR="/home/user/data/contacts"
export ASSISTANT_NOTES_DIR="/home/user/data/notes"
assistant-bot
```

**Defaults:**
- Contacts: `files/contacts`
- Notes: `files/notes`

### 7. Architecture (overview)
Layered model:
- CLI (`assistant_bot_cli.py`, `main.py`): input loop, autocompletion via Prompt Toolkit.
- BLL (`bll/services`, `helpers`, `entity_builders`): command routing, CRUD, table/calendar formatting.
- DAL (`dal/entities`, `storages`, `file_managers`): domain entities, pickle snapshot persistence.
See `structure.md` for details.

### 8. Persistence
- Files are stored separately for contacts and notes in `files/contacts`, `files/notes`.
- Autosave on `save-*` commands without filename.
- Supports state history (timestamp in filename) and loading any state.
- Current backend: only `pickle`.

### 8.1 Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `ASSISTANT_CONTACTS_DIR` | `files/contacts` | Contacts storage dir |
| `ASSISTANT_NOTES_DIR` | `files/notes` | Notes storage dir |
| `ASSISTANT_PHONE_REGION` | `UA` | Phone validation region |

Example:
```pwsh
$env:ASSISTANT_PHONE_REGION="US"
assistant-bot
```

### 8.2 Tag Color Palette
Available colors (name → HEX):
```
Coral Red  #F44336
Cerise     #E91E63
Royal Purple #9C27B0
Indigo     #3F51B5
Sky Blue   #03A9F4
Teal       #009688
Emerald    #4CAF50
Amber      #FF9800
Mocha      #795548
Slate      #607D8B
```
Usage: `add-note-tags idea teal:009688 focus amber:FF9800` (can use name or hex via `tag:color`).

### 11. Testing & Quality
Run tests with:
```pwsh
pytest -q
```
Quality tools (dev dependencies in `pyproject.toml`):
```pwsh
pip install -e .[dev]
ruff check .
mypy .
```
PEP 8 compliance is ensured via Ruff; types — via mypy. Tests cover calendar, dates, commands, storage interactions.
Partial test runs:
```pwsh
pytest tests/test_calendar_renderer.py -q
pytest tests/note_tests -q
```

### 11.1 GitHub Actions (CI)
In catalog `.github/workflows/` we have separate CI workflow files:

| File | Purpose                                                                                 |
|------|-----------------------------------------------------------------------------------------|
| `.github/workflows/tests.yml` | Run `pytest` (unit-tests) on branches `main`, `main-beta` for `push` an `pull_request`. |
| `.github/workflows/code_quality.yml` | Lint (Ruff) and static type checking (mypy) on the same branches.             |

How the pipeline works in general:
1. Checkout the repository.
2. Install Python 3.12.
3. Install dependencies from `requirements.txt`.
4. Perform linting/typing (code_quality) or tests (tests).
5. If there are errors, the workflow ends with a failure status.

### 11.2 Developer Guide
Quick start:
```pwsh
git clone https://github.com/GUARD10/goit-group-3-final-project.git
cd goit-group-3-final-project
py -m venv .venv
./.venv/Scripts/activate
pip install -e .[dev]
ruff check .
mypy .
pytest -q
assistant-bot
```
Pre-push:
```pwsh
ruff check .
ruff format .  # if auto-formatting needed
mypy .
pytest
```

### 13. Compliance Checklist
| Criterion | Met                                                 |
|----------|-----------------------------------------------------|
| Public repository | ✅ GitHub, open access                               |
| Documentation/README | ✅ Description, instructions, commands, architecture |
| CLI interface (loop) | ✅ `main.py` loop until `exit`                       |
| Interactivity / autocompletion | ✅ Prompt Toolkit (`PromptCompleter`)                |
| Menu only at startup | ✅ Welcome message once                              |
| Readability and colors | ✅ Colorama + tables/calendar                        |
| Data persistence between sessions | ✅ Pickle files in `files/*`                         |
| Invalid data handling | ✅ Exceptions without crashing                       |
| OOP, inheritance, composition | ✅ Entities + builder + services                     |
| Field validation | ✅ Phone, email, birth date                          |
| Clean code, PEP 8 | ✅ Ruff, structured modules                          |
| Mentor code review | ✅ Verified                                             |
| Tags for notes | ✅ `add-note-tags`, `show-notes-by-tag`              |
| Search/filter by tags | ✅ `show-notes-by-tag`, `search-notes`               |
| CI (GitHub Actions) | ✅ `tests.yml`, `code_quality.yml`                   |

### 14. Roadmap (possible improvements)
- Migrate from pickle to SQLite/JSON.
- Enhanced typing (enable `disallow_untyped_defs`).
- CI (GitHub Actions): pytest + ruff + mypy.
- Logging instead of `print` (use `logging` module).
- Integration tests for full scenarios.
- Enable json backend (env already supports value).
- Separate tag palette doc (`tags.md`).

### 15. License
MIT License (see `pyproject.toml`).
