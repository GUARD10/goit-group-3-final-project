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
- спілкуватися через дружній CLI з інтерактивними підказками.

### 2. Системні вимоги
1. **Операційна система:** Windows, macOS або Linux.
2. **Python:** версія 3.11+.
3. **pip:** встановлений менеджер пакетів Python.

### 3. Встановлення
```pwsh
# Клонування репозиторію
git clone <url>
cd goit-group-3-final-project

# Створення та активація середовища (рекомендовано)
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Встановлення залежностей
pip install -r requirements.txt
```

### 4. Запуск
```pwsh
python main.py
```
Після старту бот автоматично намагається підвантажити останній збережений стан контактів і нотаток, якщо файли є у директорії `files/`.

### 5. Використання
- Наберіть `help`, щоб побачити список команд.
- Основні сценарії:
  - **Контакти:** `add-contact`, `add-phone`, `delete-contact`, `search-contacts`, `upcoming-birthdays` тощо.
  - **Нотатки:** `add-note`, `edit-note-title`, `add-note-tags`, `show-notes-by-tag`, `search-notes`.
  - **Файли:** `save-contact`, `load-contact`, `save-note`, `load-note`, `contacts-files`, `note-files`.
  - **Система:** `hello`, `help`, `exit`.
- Команди зчитують аргументи з CLI або, за потреби, запускають інтерактивні діалоги (наприклад, при додаванні нотаток).
- Для безпечного виходу використовуйте `exit` або `close` — перед завершенням бот збереже всі дані.

---

## EN · English

### 1. Overview
Assistant Bot is a command-line application for managing contacts and notes. It lets you:
- add, edit, and search contacts with phones and birthdays;
- maintain tagged notes with color-coded labels;
- persist and restore state from files (manual saves plus autosaves);
- interact via a friendly CLI with interactive prompts.

### 2. Prerequisites
1. **Operating System:** Windows, macOS, or Linux.
2. **Python:** version 3.11 or newer.
3. **pip:** Python package manager installed.

### 3. Installation
```pwsh
# Clone the repository
git clone <url>
cd goit-group-3-final-project

# Create & activate a virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 4. Run
```pwsh
python main.py
```
On startup the bot tries to load the most recent contacts/notes snapshot from the `files/` directory when available.

### 5. Usage
- Type `help` to see the full command list.
- Common flows:
  - **Contacts:** `add-contact`, `add-phone`, `delete-contact`, `search-contacts`, `upcoming-birthdays`, etc.
  - **Notes:** `add-note`, `edit-note-title`, `add-note-tags`, `show-notes-by-tag`, `search-notes`.
  - **Files:** `save-contact`, `load-contact`, `save-note`, `load-note`, `contacts-files`, `note-files`.
  - **System:** `hello`, `help`, `exit`.
- Commands accept CLI arguments or launch interactive dialogs when extra input is required (e.g., composing a note).
- Use `exit` or `close` to quit safely—both trigger state persistence before shutting down.

