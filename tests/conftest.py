"""
Pytest configuration and shared fixtures for FastAPI tests.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import FastAPI, app as fastapi_app


@pytest.fixture
def app():
    """Create a fresh FastAPI app instance for testing."""
    # Create a new app instance to avoid state pollution between tests
    test_app = FastAPI(
        title="Mergington High School API",
        description="API for viewing and signing up for extracurricular activities"
    )
    
    # Mount static files
    from fastapi.staticfiles import StaticFiles
    import os
    test_app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent.parent,
              "src", "static")), name="static")
    
    # Add in-memory activities database
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
        },
        "Basketball Team": {
            "description": "Competitive basketball team for tryouts and matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Join us for recreational and competitive soccer",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Art Studio": {
            "description": "Learn painting, drawing, and creative art techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["grace@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and develop theatrical skills",
            "schedule": "Thursdays and Saturdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "jackson@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore science experiments and scientific research",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Add routes to test app
    from fastapi.responses import RedirectResponse
    
    @test_app.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")

    @test_app.get("/activities")
    def get_activities():
        return activities

    @test_app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """Sign up a student for an activity"""
        from fastapi import HTTPException
        
        # Validate activity exists
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Get the specific activity
        activity = activities[activity_name]

        # Validate student is not already signed up
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student already signed up for this activity")  

        # Add student
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}

    @test_app.delete("/activities/{activity_name}/signup")
    def unregister_from_activity(activity_name: str, email: str):
        """Unregister a student from an activity"""
        from fastapi import HTTPException
        
        # Validate activity exists
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Get the specific activity
        activity = activities[activity_name]

        # Validate student is signed up
        if email not in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student not signed up for this activity")

        # Remove student
        activity["participants"].remove(email)
        return {"message": f"Unregistered {email} from {activity_name}"}
    
    return test_app


@pytest.fixture
def client(app):
    """Create a TestClient for making requests to the app."""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Provide sample activity data for tests."""
    return {
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
        },
    }
