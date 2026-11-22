# Crowdsourced City Issue Reporter – Backend

Backend API for the Crowdsourced City Issue Reporter capstone project.

## Tech Stack

- Python 3.14
- Django
- Django REST Framework
- PostgreSQL
- django-cors-headers

## Project Structure

```text
├── apps/
│   └── accounts/
├── config/
├── requirements/
│   └── base.txt
├── .env.example
├── .gitignore
├── manage.py
└── README.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Avinto-Foundation/CrowdsourcedCityIssueReporter-Backend.git
cd CrowdsourcedCityIssueReporter-Backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements/base.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and update the values with your local configuration.

### 5. Configure PostgreSQL

Create a PostgreSQL database and configure its credentials in `.env`.

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Run the development server

```bash
python manage.py runserver
```

The backend development server will be available at `http://127.0.0.1:8000/`.

## Security

- Never commit `.env` or expose secret keys and database credentials.
- Use `.env.example` as the environment configuration template.

## Project Status

Initial backend setup and account model foundation.