"""Pytest configuration and fixtures for Mergington High School API tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import FastAPI


@pytest.fixture
def app():
    """
    Fixture that creates a fresh FastAPI app instance with reset activities data.
    
    Each test gets a clean slate to ensure test isolation and prevent state pollution.
    We create a new app with reset/sample activities for each test.
    """
    # Create a new app instance
    new_app = FastAPI(
        title="Mergington High School API",
        description="API for viewing and signing up for extracurricular activities"
    )
    
    # Define fresh activities data for testing
    activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Define endpoints
    @new_app.get("/activities")
    def get_activities():
        return activities
    
    @new_app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """Sign up a student for an activity"""
        from fastapi import HTTPException
        
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = activities[activity_name]
        
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student already signed up for this activity")
        
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}
    
    @new_app.delete("/activities/{activity_name}/participants/{email}")
    def remove_participant(activity_name: str, email: str):
        """Remove a participant from an activity"""
        from fastapi import HTTPException
        
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = activities[activity_name]
        
        if email in activity["participants"]:
            activity["participants"].remove(email)
            return {"message": f"Removed {email} from {activity_name}"}
        else:
            raise HTTPException(status_code=404, detail="Participant not found")
    
    @new_app.get("/")
    def root():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/static/index.html")
    
    return new_app


@pytest.fixture
def client(app):
    """
    Fixture that provides a TestClient for making HTTP requests to the app.
    
    Uses the app fixture to ensure each test gets a fresh app instance.
    """
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Fixture providing a sample email for testing."""
    return "test.student@mergington.edu"


@pytest.fixture
def sample_activity():
    """Fixture providing a sample activity name for testing."""
    return "Chess Club"


@pytest.fixture
def sample_new_activity():
    """Fixture providing a non-existent activity name for testing error cases."""
    return "Non-Existent Activity"
