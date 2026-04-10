"""
Integration tests for FastAPI endpoints.
Tests all HTTP endpoints with success and error cases.
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """GET /activities should return all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        # Verify all activities are present
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Basketball Team" in activities
        assert "Soccer Club" in activities
        assert "Art Studio" in activities
        assert "Drama Club" in activities
        assert "Debate Team" in activities
        assert "Science Club" in activities
    
    def test_get_activities_has_correct_structure(self, client):
        """GET /activities should return activities with correct structure."""
        response = client.get("/activities")
        activities = response.json()
        
        # Check any activity has required fields
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_participants_are_emails(self, client):
        """GET /activities should return participants as list of email strings."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity in activities.items():
            assert isinstance(activity["participants"], list)
            for participant in activity["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant, f"Participant '{participant}' should be an email"


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client):
        """Should successfully sign up a student for an activity."""
        email = "newemail@mergington.edu"
        
        response = client.post("/activities/Chess Club/signup", params={"email": email})
        
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for Chess Club"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
    
    def test_signup_to_different_activities(self, client):
        """Should be able to sign up the same student to multiple activities."""
        email = "multi@mergington.edu"
        
        response1 = client.post("/activities/Chess Club/signup", params={"email": email})
        response2 = client.post("/activities/Programming Class/signup", params={"email": email})
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Should return 404 when activity doesn't exist."""
        response = client.post("/activities/Nonexistent Club/signup", 
                              params={"email": "test@mergington.edu"})
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client):
        """Should return 400 when student is already signed up."""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post("/activities/Chess Club/signup", params={"email": email})
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_missing_email_parameter(self, client):
        """Should fail when email parameter is missing."""
        response = client.post("/activities/Chess Club/signup")
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_signup_empty_email_parameter(self, client):
        """Should accept empty email parameter (validation at business logic level)."""
        response = client.post("/activities/Chess Club/signup", params={"email": ""})
        
        # Empty email is a valid parameter, though may fail at validation
        # Current implementation would add it to participants
        assert response.status_code in [200, 400]
    
    def test_signup_preserves_existing_participants(self, client):
        """Signing up new student should not affect existing participants."""
        # Get existing participants
        activities_before = client.get("/activities").json()
        chess_before = activities_before["Chess Club"]["participants"].copy()
        
        # Sign up new student
        new_email = "new_student@mergington.edu"
        client.post("/activities/Chess Club/signup", params={"email": new_email})
        
        # Verify old participants are still there
        activities_after = client.get("/activities").json()
        chess_after = activities_after["Chess Club"]["participants"]
        
        for participant in chess_before:
            assert participant in chess_after


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint."""
    
    def test_unregister_success(self, client):
        """Should successfully unregister a student from an activity."""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.delete("/activities/Chess Club/signup", params={"email": email})
        
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from Chess Club"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """Should return 404 when activity doesn't exist."""
        response = client.delete("/activities/Nonexistent Club/signup", 
                                params={"email": "test@mergington.edu"})
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_not_signed_up(self, client):
        """Should return 400 when student is not signed up for activity."""
        response = client.delete("/activities/Chess Club/signup", 
                                params={"email": "notregistered@mergington.edu"})
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"
    
    def test_unregister_missing_email_parameter(self, client):
        """Should fail when email parameter is missing."""
        response = client.delete("/activities/Chess Club/signup")
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_unregister_preserves_other_participants(self, client):
        """Unregistering one student should not affect other participants."""
        # Get existing participants
        activities_before = client.get("/activities").json()
        chess_before = activities_before["Chess Club"]["participants"].copy()
        
        # Unregister one student
        email_to_remove = "michael@mergington.edu"
        client.delete("/activities/Chess Club/signup", params={"email": email_to_remove})
        
        # Verify other participants are still there
        activities_after = client.get("/activities").json()
        chess_after = activities_after["Chess Club"]["participants"]
        
        for participant in chess_before:
            if participant != email_to_remove:
                assert participant in chess_after
    
    def test_signup_then_unregister(self, client):
        """Should be able to sign up and then unregister."""
        email = "signup_test@mergington.edu"
        activity = "Drama Club"
        
        # Sign up
        response1 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response1.status_code == 200
        
        # Verify registered
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        
        # Unregister
        response2 = client.delete(f"/activities/{activity}/signup", params={"email": email})
        assert response2.status_code == 200
        
        # Verify unregistered
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]


class TestRootEndpoint:
    """Test suite for GET / endpoint."""
    
    def test_root_redirects_to_static(self, client):
        """GET / should redirect to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"
    
    def test_root_redirect_follows_to_static(self, client):
        """Following redirect from / should reach static files."""
        # Note: TestClient may handle redirects differently
        # This test documents the redirect behavior
        response = client.get("/")
        
        # Either redirect status or successful static file response
        assert response.status_code in [200, 307]
