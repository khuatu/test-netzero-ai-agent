# setup_project.py
"""
Einmaliges Setup-Skript zur Erstellung der Projektstruktur für den
NetZero AI Onboarding Agent.

Ausführung:
    python setup_project.py
"""

import os
import sys

# -------------------------------------------------------------------
# 1. Definition der gewünschten Ordnerstruktur
# -------------------------------------------------------------------
# Die Struktur wird als Dictionary abgebildet.
# Schlüssel = Dateiname, Wert = Inhalt (String) oder None für leere Dateien.
# Ordner werden durch Schlüssel mit einem Unter-Dictionary erkannt.

PROJECT_STRUCTURE = {
    ".github": {
        "workflows": {
            "ci.yml": """# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Code aus GitHub auschecken
        uses: actions/checkout@v4

      - name: Python 3.14 einrichten
        uses: actions/setup-python@v5
        with:
          python-version: "3.14"

      - name: Abhängigkeiten installieren
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Tests ausführen
        run: |
          pytest tests/
"""
        }
    },
    "agent": {
        "__init__.py": "",
        "state.py": '''# agent/state.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class OnboardingState(BaseModel):
    """Der Zustand, der zwischen den Agenten-Knoten geteilt wird."""
    student_data: Dict[str, Any] = Field(description="Rohdaten des Studenten")
    email_valid: bool = Field(default=False)
    course_suggestions: Optional[List[str]] = Field(default=None)
    hubspot_contact_id: Optional[str] = Field(default=None)
    email_sent: bool = Field(default=False)
    calendar_event_created: bool = Field(default=False)
    error_message: Optional[str] = Field(default=None)
''',
        "graph.py": '''# agent/graph.py
import os
import re
import litellm
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from agent.state import OnboardingState

load_dotenv()
litellm.api_key = os.getenv("OPENAI_API_KEY")

# -------------------------------------------------------------------
# 1. Node-Funktionen
# -------------------------------------------------------------------

def validate_email(state: OnboardingState) -> dict:
    email = state.student_data.get("email", "")
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    valid = re.match(pattern, email) is not None
    if valid:
        return {"email_valid": True, "error_message": None}
    else:
        return {"email_valid": False, "error_message": f"Ungültige E-Mail-Adresse: {email}"}

def analyze_profile(state: OnboardingState) -> dict:
    prompt = f"""
    Du bist ein erfahrener Bildungsberater der NetZero Academy.
    Analysiere das Profil: {state.student_data}
    Schlage maximal 3 passende Kurse vor.
    Antworte NUR mit einer Python-Liste von Strings.
    """
    try:
        response = litellm.completion(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        suggestions = eval(response.choices[0].message.content)
        if not isinstance(suggestions, list):
            suggestions = []
    except Exception:
        suggestions = []
    return {"course_suggestions": suggestions}

def create_hubspot_contact(state: OnboardingState) -> dict:
    print(f"[HubSpot] Erstelle Kontakt für {state.student_data.get('name')}")
    contact_id = f"hubspot_contact_{hash(state.student_data.get('email'))}"
    return {"hubspot_contact_id": contact_id}

def send_welcome_email(state: OnboardingState) -> dict:
    print(f"[Gmail] Sende Willkommens-E-Mail an {state.student_data.get('email')}")
    return {"email_sent": True}

def create_calendar_event(state: OnboardingState) -> dict:
    print(f"[Calendar] Erstelle Termin für {state.student_data.get('name')}")
    return {"calendar_event_created": True}

def handle_error(state: OnboardingState) -> dict:
    print(f"[ERROR] {state.error_message}")
    return {}

# -------------------------------------------------------------------
# 2. Router
# -------------------------------------------------------------------

def route_after_validation(state: OnboardingState) -> str:
    return "analyze_profile" if state.email_valid else "handle_error"

# -------------------------------------------------------------------
# 3. Graph bauen
# -------------------------------------------------------------------

def build_graph():
    workflow = StateGraph(OnboardingState)
    workflow.add_node("validate_email", validate_email)
    workflow.add_node("analyze_profile", analyze_profile)
    workflow.add_node("create_hubspot_contact", create_hubspot_contact)
    workflow.add_node("send_welcome_email", send_welcome_email)
    workflow.add_node("create_calendar_event", create_calendar_event)
    workflow.add_node("handle_error", handle_error)
    workflow.set_entry_point("validate_email")
    workflow.add_conditional_edges(
        "validate_email", route_after_validation,
        {"analyze_profile": "analyze_profile", "handle_error": "handle_error"}
    )
    workflow.add_edge("analyze_profile", "create_hubspot_contact")
    workflow.add_edge("create_hubspot_contact", "send_welcome_email")
    workflow.add_edge("send_welcome_email", "create_calendar_event")
    workflow.add_edge("create_calendar_event", END)
    workflow.add_edge("handle_error", END)
    return workflow.compile()

agent_app = build_graph()
''',
        "nodes": {
            "__init__.py": "",
            # Weitere Knoten könnten hier in eigene Dateien ausgelagert werden
        }
    },
    "api": {
        "__init__.py": "",
        "main.py": '''# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.graph import agent_app
from agent.state import OnboardingState

app = FastAPI(title="NetZero AI Onboarding Agent", version="0.1.0")

class StudentData(BaseModel):
    name: str
    email: str
    company: str
    role: str

@app.post("/onboard")
async def onboard_student(data: StudentData):
    initial_state = OnboardingState(
        student_data=data.model_dump(),
        email_valid=False,
        course_suggestions=None,
        hubspot_contact_id=None,
        email_sent=False,
        calendar_event_created=False,
        error_message=None
    )
    try:
        final_state_dict = agent_app.invoke(initial_state.model_dump())
        final_state = OnboardingState(**final_state_dict)
        if final_state.error_message:
            raise HTTPException(status_code=400, detail=final_state.error_message)
        return {
            "status": "success",
            "hubspot_contact_id": final_state.hubspot_contact_id,
            "course_suggestions": final_state.course_suggestions,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "NetZero AI Onboarding Agent läuft."}
'''
    },
    "tests": {
        "__init__.py": "",
        "test_validation.py": '''# tests/test_validation.py
import pytest
from agent.graph import validate_email
from agent.state import OnboardingState

def test_valid_email():
    state = OnboardingState(student_data={"email": "max@example.com", "name": "", "company": "", "role": ""})
    result = validate_email(state)
    assert result["email_valid"] is True

def test_invalid_email():
    state = OnboardingState(student_data={"email": "max@example", "name": "", "company": "", "role": ""})
    result = validate_email(state)
    assert result["email_valid"] is False
'''
    },
    ".env.example": '''# Beispiel .env-Datei – kopiere zu .env und trage deine echten Keys ein
OPENAI_API_KEY=your-openai-api-key-here
USE_CRM=true
''',
    ".gitignore": '''# .gitignore
venv/
__pycache__/
*.pyc
.env
.idea/
*.log
''',
    "requirements.txt": '''# requirements.txt
fastapi==0.115.0
uvicorn==0.32.0
langgraph==0.2.0
langchain==0.3.0
langchain-community==0.3.0
langchain-openai==0.2.0
litellm==1.52.0
python-dotenv==1.0.0
pydantic==2.9.0
pytest==8.0.0
''',
    "README.md": '''# NetZero AI Onboarding Agent

Ein KI-gesteuerter Agent zur automatisierten Aufnahme neuer Studenten.

## Installation
1. `python -m venv venv`
2. `venv\\Scripts\\activate` (Windows)
3. `pip install -r requirements.txt`
4. `.env` Datei mit `OPENAI_API_KEY=...` anlegen (siehe `.env.example`)

## Starten
`python run.py`

Server läuft unter `http://127.0.0.1:8000`. Dokumentation unter `/docs`.

## Tests
`pytest tests/`
''',
    "run.py": '''# run.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
'''
}


# -------------------------------------------------------------------
# 2. Hilfsfunktion zum rekursiven Erstellen von Ordnern und Dateien
# -------------------------------------------------------------------
def create_structure(base_path: str, structure: dict):
    """
    Erstellt rekursiv Ordner und Dateien basierend auf dem `structure`-Dictionary.
    """
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # Es ist ein Ordner
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # Es ist eine Datei
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Erstellt: {path}")

# -------------------------------------------------------------------
# 3. Hauptprogramm
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Aktuelles Verzeichnis ist dort, wo das Skript liegt
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Erstelle Projektstruktur in: {base_dir}")
    create_structure(base_dir, PROJECT_STRUCTURE)
    print("\n✅ Projektstruktur erfolgreich erstellt!")
    print("\nNächste Schritte:")
    print("1. python -m venv venv")
    print("2. venv\\Scripts\\activate")
    print("3. pip install -r requirements.txt")
    print("4. Kopiere .env.example zu .env und trage deinen OpenAI-API-Key ein.")
    print("5. python run.py")