from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.graph import agent_app
from agent.state import OnboardingState

app = FastAPI(title="NetZero AI Onboarding Agent", version="1.0.0")

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