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