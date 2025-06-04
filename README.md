# Kolornote

A Django-based Progressive Web App for managing notes and checklists with import functionality.

## Features

- User authentication and registration
- Import notes from ZIP files containing TXT files
- Automatic detection of checklists vs regular notes
- Color-coded organization with customizable color names
- Search and filter functionality
- Responsive design for mobile and web
- PWA capabilities for offline access

## Setup

1. Install Poetry: `pip install poetry`
2. Install dependencies: `poetry install`
3. Create PostgreSQL database: `notes_db`
4. Copy `.env.example` to `.env` and configure database settings
5. Run migrations: `poetry run python manage.py migrate`
6. Create superuser: `poetry run python manage.py createsuperuser`
7. Run server: `poetry run python manage.py runserver`

## Import Format

- Regular TXT files are imported as notes
- TXT files with `[ ]` and `[V]` patterns are imported as checklists
- ZIP file name becomes the color name with a random hex value

## File Structure

```
kolornote/
├── kolornote/          # Django project settings
├── notes/                  # Main application
├── templates/              # HTML templates
├── static/                 # CSS, JS, and static files
├── logs/                   # Application logs
└── manage.py              # Django management script
```