"""
Unit tests for data models and validation logic.
Tests data structure conformance and business logic validation.
"""

import pytest


class TestActivityDataStructure:
    """Test suite for activity data structure validation."""
    
    def test_all_activities_have_required_fields(self, sample_activities):
        """All activities should have required fields."""
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity in sample_activities.items():
            for field in required_fields:
                assert field in activity, f"Activity '{activity_name}' missing field '{field}'"
    
    def test_description_is_string(self, sample_activities):
        """Activity description should be a string."""
        for activity_name, activity in sample_activities.items():
            assert isinstance(activity["description"], str)
            assert len(activity["description"]) > 0
    
    def test_schedule_is_string(self, sample_activities):
        """Activity schedule should be a string."""
        for activity_name, activity in sample_activities.items():
            assert isinstance(activity["schedule"], str)
            assert len(activity["schedule"]) > 0
    
    def test_max_participants_is_positive_integer(self, sample_activities):
        """Activity max_participants should be a positive integer."""
        for activity_name, activity in sample_activities.items():
            assert isinstance(activity["max_participants"], int)
            assert activity["max_participants"] > 0
    
    def test_participants_is_list_of_strings(self, sample_activities):
        """Activity participants should be a list of email strings."""
        for activity_name, activity in sample_activities.items():
            assert isinstance(activity["participants"], list)
            for participant in activity["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant, f"Participant '{participant}' should be an email"
    
    def test_participants_dont_exceed_max(self, sample_activities):
        """Participant count should not exceed max_participants."""
        for activity_name, activity in sample_activities.items():
            assert len(activity["participants"]) <= activity["max_participants"]


class TestActivityParticipants:
    """Test suite for participant list operations."""
    
    def test_participants_list_is_mutable(self, sample_activities):
        """Participants list should be mutable (can add/remove)."""
        activity = sample_activities["Chess Club"]
        original_count = len(activity["participants"])
        
        # Should be able to append
        activity["participants"].append("test@mergington.edu")
        assert len(activity["participants"]) == original_count + 1
        
        # Should be able to remove
        activity["participants"].remove("test@mergington.edu")
        assert len(activity["participants"]) == original_count
    
    def test_participants_are_unique(self, sample_activities):
        """Participants in an activity should be unique."""
        for activity_name, activity in sample_activities.items():
            participants = activity["participants"]
            assert len(participants) == len(set(participants))
    
    def test_email_format_validation(self, sample_activities):
        """Participants should have valid email format."""
        for activity_name, activity in sample_activities.items():
            for email in activity["participants"]:
                # Basic email validation
                assert "@" in email
                assert "." in email.split("@")[1]
                assert email.count("@") == 1


class TestActivityValidation:
    """Test suite for activity-level validation."""
    
    def test_activity_names_are_not_empty(self, sample_activities):
        """Activity names should not be empty."""
        for activity_name in sample_activities.keys():
            assert len(activity_name) > 0
    
    def test_no_duplicate_activities(self, sample_activities):
        """Activity names should be unique."""
        activity_names = list(sample_activities.keys())
        assert len(activity_names) == len(set(activity_names))
    
    def test_description_length(self, sample_activities):
        """Activity description should be reasonable length."""
        for activity_name, activity in sample_activities.items():
            description = activity["description"]
            assert len(description) >= 10, f"Description too short for {activity_name}"
            assert len(description) <= 500, f"Description too long for {activity_name}"
    
    def test_schedule_contains_days_or_times(self, sample_activities):
        """Activity schedule should look like a schedule."""
        time_keywords = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", 
                        "Saturday", "Sunday", "AM", "PM", "am", "pm"]
        
        for activity_name, activity in sample_activities.items():
            schedule = activity["schedule"]
            # At least one time-related keyword should be present
            has_time_keyword = any(keyword in schedule for keyword in time_keywords)
            assert has_time_keyword, f"Schedule for {activity_name} doesn't look like a schedule"
    
    def test_max_participants_reasonable(self, sample_activities):
        """Activity max_participants should be reasonable."""
        for activity_name, activity in sample_activities.items():
            max_p = activity["max_participants"]
            assert max_p >= 5, f"{activity_name} max_participants too low ({max_p})"
            assert max_p <= 200, f"{activity_name} max_participants too high ({max_p})"


class TestSampleActivityIntegrity:
    """Test suite for sample activities data integrity."""
    
    def test_chess_club_exists(self, sample_activities):
        """Sample data should include Chess Club."""
        assert "Chess Club" in sample_activities
    
    def test_programming_class_exists(self, sample_activities):
        """Sample data should include Programming Class."""
        assert "Programming Class" in sample_activities
    
    def test_gym_class_exists(self, sample_activities):
        """Sample data should include Gym Class."""
        assert "Gym Class" in sample_activities
    
    def test_sample_has_participants(self, sample_activities):
        """All sample activities should have initial participants."""
        for activity_name, activity in sample_activities.items():
            assert len(activity["participants"]) > 0, f"{activity_name} has no participants"
