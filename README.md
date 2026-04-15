# Smart Expense Prediction & Financial Recommendation System

![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

A final-year project starter built with Flask, machine learning, and a financial recommendation engine.

## Features

- Predicts food, transport, entertainment, and miscellaneous expenses
- Accepts monthly income, EMI, rent, bills, lifestyle, and spending habit
- Allocates remaining money into savings, investment, and emergency fund
- Generates budget risk alerts based on financial rules
- Stores budget history in a database
- Displays a dashboard with expense and history charts
- Exports budget history as CSV
- Supports SQLite by default and MySQL through `DATABASE_URL`

## Technology Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Flask
- Machine Learning: scikit-learn Random Forest Regressor
- Machine Learning improvement: retrains from saved budget history when enough past plans exist, with synthetic fallback for new installs
- Production-ready explainability: feature importance-driven model insight endpoint
- Database: SQLite by default, MySQL-ready with SQLAlchemy
- Testing: pytest

## Project Structure

```text
smart expense/
├── app.py
├── requirements.txt
├── README.md
├── tests/
└── smart_expense/
    ├── __init__.py
    ├── models.py
    ├── routes.py
    ├── services/
    │   ├── advisor.py
    │   ├── predictor.py
    │   └── seed.py
    ├── static/
    │   ├── css/styles.css
    │   └── js/app.js
    └── templates/
        ├── base.html
        └── index.html
```

## Setup

1. Create and activate a virtual environment if needed:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies into the local virtual environment:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Run the Flask app using the `.venv` interpreter:

```powershell
.venv\Scripts\python.exe app.py
```

4. Open the browser:

```text
http://127.0.0.1:5000
```

> Tip: VS Code is configured to use the local `.venv` interpreter via `.vscode/settings.json`.

## Optional MySQL Configuration

If you want to use MySQL instead of SQLite, set:

```powershell
$env:DATABASE_URL="mysql+pymysql://root:password@localhost/smart_expense"
```

Then start the app again. SQLAlchemy will create the required tables automatically.

## API Endpoints

`POST /api/predict`

Example JSON body:

```json
{
  "monthly_income": 50000,
  "emi": 10000,
  "rent": 12000,
  "bills": 3500,
  "lifestyle": "working",
  "spending_habit": "balanced"
}
```

`GET /api/model-info`

Returns the model name, training source, sorted feature importances, and the top input drivers for budget prediction.

## Viva Explanation

- The model uses a synthetic training dataset so the project is demo-ready even without collected real user data.
- The recommendation engine is rule-based, which makes it easy to explain decisions in a project presentation.
- Historical records are stored in the database to support future extensions like login, monthly analytics, and personalized forecasting.
