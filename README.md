# NetZero AI Onboarding Agent

Ein KI-gesteuerter Agent zur automatisierten Aufnahme neuer Studenten.

## Installation
1. `python -m venv venv`
2. `venv\Scripts\activate` (Windows)
3. `pip install -r requirements.txt`
4. `.env` Datei mit `OPENAI_API_KEY=...` anlegen (siehe `.env.example`)

## Starten
`python run.py`

Server läuft unter `http://127.0.0.1:8000`. Dokumentation unter `/docs`.

## Tests
`pytest tests/`
