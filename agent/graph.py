import re
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from agent.state import OnboardingState

load_dotenv()


class CourseSuggestions(BaseModel):
    suggestions: list[str] = Field(description="Liste der vorgeschlagenen Kurse, maximal 3")


def validate_email(state: OnboardingState) -> dict:
    email = state.student_data.get("email", "")
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    valid = re.match(pattern, email) is not None
    if valid:
        return {"email_valid": True, "error_message": None}
    else:
        return {"email_valid": False, "error_message": f"Ungültige E-Mail-Adresse: {email}"}


def analyze_profile(state: OnboardingState) -> dict:
    prompt = f"""
    Du bist ein erfahrener Bildungsberater der NetZero Academy.
    Analysiere das Profil eines neuen Interessenten:
    Name: {state.student_data.get('name')}
    Firma: {state.student_data.get('company')}
    Rolle: {state.student_data.get('role')}

    Schlage maximal 3 passende Kurse aus den Bereichen Energieberatung,
    Dekarbonisierung oder erneuerbare Energien vor.
    """
    llm = ChatOllama(model="llama3.2", temperature=0.3)
    structured_llm = llm.with_structured_output(CourseSuggestions)
    try:
        result = structured_llm.invoke(prompt)
        suggestions = result.suggestions
    except Exception as e:
        print(f"[Analyze] Fehler: {e}")
        suggestions = []
    return {"course_suggestions": suggestions}


#Bisher nur Platzhalter
def create_hubspot_contact(state: OnboardingState) -> dict:
    print(f"[HubSpot] Erstelle Kontakt für {state.student_data.get('name')}")
    contact_id = f"hubspot_contact_{hash(state.student_data.get('email'))}"
    return {"hubspot_contact_id": contact_id}


def send_welcome_email(state: OnboardingState) -> dict:
    print(f"[Gmail] Sende E-Mail an {state.student_data.get('email')}")
    return {"email_sent": True}


def create_calendar_event(state: OnboardingState) -> dict:
    print(f"[Calendar] Erstelle Termin für {state.student_data.get('name')}")
    return {"calendar_event_created": True}


def handle_error(state: OnboardingState) -> dict:
    print(f"[ERROR] {state.error_message}")
    return {}


def route_after_validation(state: OnboardingState) -> str:
    return "analyze_profile" if state.email_valid else "handle_error"


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