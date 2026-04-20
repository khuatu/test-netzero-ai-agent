from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class OnboardingState(BaseModel):
    """Der zentrale Zustand, der durch alle Knoten des Agenten gereicht wird."""
    student_data: Dict[str, Any] = Field(description="Rohdaten des Studenten aus dem Webhook")
    email_valid: bool = Field(default=False, description="Ergebnis der E-Mail-Validierung")
    course_suggestions: Optional[List[str]] = Field(default=None, description="Vom LLM generierte Kursvorschläge")
    hubspot_contact_id: Optional[str] = Field(default=None, description="ID des erstellten HubSpot-Kontakts")
    email_sent: bool = Field(default=False, description="Wurde die Willkommens-E-Mail erfolgreich versendet?")
    calendar_event_created: bool = Field(default=False, description="Wurde der Kalendereintrag erfolgreich erstellt?")
    error_message: Optional[str] = Field(default=None, description="Fehlermeldung, falls ein Fehler auftritt")