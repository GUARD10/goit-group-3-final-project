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

#### Варіант А: Встановлення як пакет (рекомендовано)
```pwsh
# Клонування репозиторію
git clone <url>
cd goit-group-3-final-project

# Створення та активація середовища (рекомендовано)
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Встановлення у режимі редагування
pip install -e .
```

#### Варіант Б: Запуск без встановлення
```pwsh
# Клонування та активація середовища (як вище)
# Встановлення лише залежностей
pip install -r requirements.txt
```

### 4. Запуск

#### Якщо встановлено як пакет (Варіант А):
```pwsh
assistant-bot
```

#### Якщо запускаєте без встановлення (Варіант Б):
```pwsh
python main.py
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

### 🟨 Файли контактів
| Команда | Опис |
|--------|------|
| `save-contact [file-name]?` | 💾 Зберегти контакти |
| `load-contact [file-name]` | 📂 Завантажити контакти |
| `delete-contact-file [file-name]` | 🗑️ Видалити файл |
| `contacts-files` | 📁 Список файлів |

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

### 🟪 Файли нотаток
| Команда | Опис |
|--------|------|
| `save-note [file-name]?` | 💾 Зберегти |
| `load-note [file-name]` | 📂 Завантажити |
| `delete-note-file [file-name]` | 🗑️ Видалити файл |
| `note-files` | 📁 Список файлів |

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

#### Option A: Install as package (recommended)
```pwsh
# Clone the repository
git clone <url>
cd goit-group-3-final-project

# Create & activate a virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install in editable mode
pip install -e .
```

#### Option B: Run without installation
```pwsh
# Clone and activate environment (as above)
# Install dependencies only
pip install -r requirements.txt
```

### 4. Run

#### If installed as package (Option A):
```pwsh
assistant-bot
```

#### If running without installation (Option B):
```pwsh
python main.py
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
| `add-contact [name] [phone]` | ➕ Create contact |
| `delete-contact [name]` | 🗑️ Delete contact |
| `show-contact [name]` | 👁️ Show details |
| `all-contacts` | 📋 List all contacts |
| `add-phone [name] [phone]` | 📞 Add phone |
| `delete-phone [name] [phone]` | 🗑️ Remove phone |
| `add-email [name] [email]` | 📧 Add email |
| `delete-email [name] [email]` | 🗑️ Remove email |
| `set-address [name] [address...]` | 🏠 Set address |
| `clear-address [name]` | 🗑️ Clear address |
| `add-birthday [name] [DD.MM.YYYY]` | 🎂 Add birthday |
| `clear-birthday [name]` | 🗑️ Clear birthday |
| `upcoming-birthdays [days]?` | 🎁 Birthdays in next N days |
| `search-contacts [text]` | 🔍 Search contacts |

---

### 🟨 Contact Files
| Command | Description |
|--------|-------------|
| `save-contact [file]?` | 💾 Save contacts |
| `load-contact [file]` | 📂 Load contacts |
| `delete-contact-file [file]` | 🗑️ Delete file |
| `contacts-files` | 📁 List files |

---

### 🟧 Notes
| Command | Description |
|--------|-------------|
| `add-note [name]` | 📝 Create note |
| `delete-note [name]` | 🗑️ Delete note |
| `show-note [name]` | 👁️ Show note |
| `all-notes` | 📚 List notes |
| `search-notes [text]` | 🔍 Search notes |
| `edit-note-title [name]` | ✏️ Edit title |
| `edit-note-content [name]` | 📄 Edit content |
| `add-note-tags [name] [tag:color]...` | 🏷️ Add tags |
| `remove-note-tag [name] [tag]` | ❌ Remove tag |
| `show-notes-by-tag [tag]?` | 🏷️ Filter by tag |

---

### 🟪 Note Files
| Command | Description |
|--------|-------------|
| `save-note [file]?` | 💾 Save notes |
| `load-note [file]` | 📂 Load notes |
| `delete-note-file [file]` | 🗑️ Delete note file |
| `note-files` | 📁 List files |

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