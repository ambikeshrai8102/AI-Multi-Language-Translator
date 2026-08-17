# 🌐 LinguaBridge — Multi-Language Translator Web App

A full-featured Django web application for AI-powered translation across 100+ world languages.

---

## ✨ Features

| Feature | Description |
|---|---|
| ⚡ **Smart Translator** | Translate text with auto language detection |
| 🔀 **Batch Translate** | Translate one text into up to 8 languages at once |
| 📖 **Phrasebook** | 60+ common phrases across 6 categories |
| 📜 **History** | Full translation history with search & filter |
| ⭐ **Favorites** | Star and save important translations |
| 📊 **Analytics** | Visual stats on language usage |
| 📥 **CSV Export** | Download your history as a spreadsheet |
| 🔊 **Text-to-Speech** | Listen to source and translated text |
| 📋 **Copy/Paste** | Full clipboard integration |
| 📝 **Text Tools** | Live word count, read time, speak time |
| ⌨️ **Keyboard Shortcuts** | Ctrl+Enter to translate |
| 🔧 **Django Admin** | Manage all data from /admin/ |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install django
```

### 2. Set your Anthropic API key
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Run migrations
```bash
python manage.py migrate
```

### 4. Create admin user
```bash
python manage.py createsuperuser
```

### 5. Start the server
```bash
python manage.py runserver
```
cd translator_project
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

Open **http://127.0.0.1:8000** in your browser.

---

## 🗄️ Database Schema (SQLite)

### `translator_translation`
| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| source_text | TEXT | Original input text |
| translated_text | TEXT | Translated output |
| source_language | VARCHAR(10) | Language code (e.g. "en") |
| target_language | VARCHAR(10) | Language code (e.g. "es") |
| source_language_name | VARCHAR(100) | Human name (e.g. "English") |
| target_language_name | VARCHAR(100) | Human name (e.g. "Spanish") |
| character_count | INTEGER | Length of source text |
| ip_address | VARCHAR | Client IP address |
| created_at | DATETIME | Timestamp |

### `translator_favoritetranslation`
| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| translation_id | FK | Reference to Translation |
| label | VARCHAR(200) | Optional label |
| created_at | DATETIME | Timestamp |

### `translator_language`
| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| code | VARCHAR(10) | ISO language code |
| name | VARCHAR(100) | English name |
| native_name | VARCHAR(100) | Name in native script |
| flag_emoji | VARCHAR(10) | Flag emoji |

---

## 📁 Project Structure

```
translator_project/
├── manage.py
├── db.sqlite3                    ← SQLite database
├── requirements.txt
├── README.md
├── translator_site/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── translator/
│   ├── models.py                 ← DB models
│   ├── views.py                  ← All views & API endpoints
│   ├── urls.py                   ← URL routing
│   ├── admin.py                  ← Admin panel config
│   └── translation_engine.py    ← Claude API integration
├── templates/translator/
│   ├── base.html                 ← Shared layout
│   ├── index.html                ← Main translator
│   ├── batch.html                ← Batch translate
│   ├── phrasebook.html           ← Phrasebook
│   ├── history.html              ← Translation history
│   ├── favorites.html            ← Saved translations
│   └── analytics.html           ← Usage analytics
└── static/
    ├── css/style.css             ← Complete design system
    └── js/main.js                ← Frontend logic
```

---

## 🔗 URL Routes

| URL | View | Description |
|---|---|---|
| `/` | index | Main translator page |
| `/batch-page/` | batch_page | Batch translate UI |
| `/phrasebook/` | phrasebook | Common phrases |
| `/history/` | history | Translation history |
| `/favorites/` | favorites | Saved favorites |
| `/analytics/` | analytics | Usage statistics |
| `/export/csv/` | export_csv | Download CSV |
| `/translate/` | translate_text | POST: translate API |
| `/batch/` | batch_translate | POST: batch API |
| `/add-favorite/` | add_favorite | POST: save favorite |
| `/delete/<id>/` | delete_translation | POST: delete record |
| `/stats/` | stats_view | GET: live stats JSON |
| `/admin/` | Django Admin | Admin panel |

---

## 🔑 API Key

This app uses the **Anthropic Claude API** for translation.

Get your API key at: https://console.anthropic.com/

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Django 4+
- **Database**: SQLite (via Django ORM)
- **AI Engine**: Anthropic Claude API
- **Frontend**: Vanilla HTML, CSS, JavaScript
- **Fonts**: Syne (display) + DM Sans (body)
- **Admin**: Django Admin Panel