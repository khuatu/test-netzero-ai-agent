# NetZero AI Onboarding Agent

Ein KI-gesteuerter Agent zur automatisierten Aufnahme neuer Studenten an der NetZero Academy. Entwickelt als Demonstrationsprojekt für den Einsatz von **LangGraph**, **FastAPI** und lokalen LLMs (**Ollama**).

## ✨ Features

- **Intelligente Datenvalidierung**: Prüft E-Mail-Adressen auf syntaktische Korrektheit.
- **Personalisierte Kursvorschläge**: Nutzt ein lokales LLM (Llama 3.2) zur Generierung passender Kursempfehlungen basierend auf Rolle und Unternehmen.
- **Modulare Architektur**: Trennung von API, Agentenlogik und Zustand. Leicht erweiterbar um CRM- (HubSpot), E-Mail- (Gmail) und Kalender-Integrationen (Google Calendar).
- **Automatisierte Tests**: Unit-Tests für kritische Komponenten.
- **CI/CD Ready**: GitHub Actions Pipeline für kontinuierliche Integration.

## Schnellstart

### Voraussetzungen

- Python 3.14
- [Ollama](https://ollama.com/) (mit `llama3.2` Modell)
- Git

### Installation

1. **Repository klonen**
   ```bash
   git clone https://github.com/khuatu/test-netzero-ai-agent.git
   cd test-netzero-ai-agent
   
2. Virtuelle Umgebunb erstellen & aktivieren 

       python -m venv venv
       venv\Scripts\activate   # Windows
       source venv/bin/activate # macOS/Linux

3. Abhängigkeiten installieren
    ```
    pip install -r requirements.txt

4. Ollama Modell laden (einmalig)
    ```
   ollama pull lama3.2

5. Konfiguration (optional)
    ```
   cp .env.example .env

6. Server starten
    ```
   python run.py

7. Testen
    ```
   http://127.0.0.1:8000/docs
   
   {
     "name": "Anna Solar",
     "email": "anna@example.com",
    "company": "Solarbau GmbH",
     "role": "Projektleiterin"
    }


   pytest tests/
   
8. ngrok
- ngrok Dateipfad
   ``` 
  ngrok http 8000
- URL kopieren, die nach dem Schema aufgebaut ist:
   ```
  Forwarding  https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:8000

9. make.com
- Szenario erstellen und laufen lassen
- Beispielaufruf auf PS
   ```
  Invoke-RestMethod -Uri "<WEBHOOK-URL>" -Method Post -ContentType "application/json" -Body '{"name":"Test User","email":"test@example.com","company":"Test GmbH","role":"Ingenieur"}'
