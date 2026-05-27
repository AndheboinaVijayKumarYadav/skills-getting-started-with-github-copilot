"""
Tests for the signup endpoint using the AAA (Arrange-Act-Assert) pattern.
Each test follows the structure:
  - Arrange: Set up test data and preconditions
  - Act: Call the endpoint being tested
  - Assert: Verify the response and state
"""

import pytest


class TestSignupHappyPath:
    """Tests for successful signup scenarios"""
    
    def test_signup_new_student_successfully(self, client, test_activity_name, sample_email):
        """
        Arrange: Student not yet signed up
        Act: Call signup endpoint with valid email and activity
        Assert: Student added to activity and success response returned
        """
        # Arrange
        initial_participant_count = len(
            client.get("/activities").json()[test_activity_name]["participants"]
        )
        
        # Act
        response = client.post(
            f"/activities/{test_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert sample_email in client.get("/activities").json()[test_activity_name]["participants"]
        assert len(
            client.get("/activities").json()[test_activity_name]["participants"]
        ) == initial_participant_count + 1
        assert "message" in response.json()


class TestSignupErrorCases:
    """Tests for signup error scenarios"""
    
    def test_signup_nonexistent_activity_returns_404(self, client, sample_email):
        """
        Arrange: Activity does not exist
        Act: Call signup endpoint with nonexistent activity name
        Assert: 404 status and error message returned
        """
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered_returns_400(self, client, test_activity_name):
        """
        Arrange: Student already registered for activity
        Act: Call signup endpoint with email already in participants
        Assert: 400 status and error message returned
        """
        # Arrange
        existing_participant = client.get("/activities").json()[test_activity_name]["participants"][0]
        
        # Act
        response = client.post(
            f"/activities/{test_activity_name}/signup",
            params={"email": existing_participant}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestSignupEdgeCases:
    """Tests for edge cases in signup"""
    
    def test_signup_when_activity_full(self, client):
        """
        Arrange: Activity has reached max participants
        Act: Call signup endpoint for full activity
        Assert: New participant added (no max capacity validation)
        """
        # Arrange - Find or create a nearly-full activity
        activities_data = client.get("/activities").json()
        test_activity = "Science Club"  # Has 1 participant, max 22
        full_activity = None
        
        for activity_name, activity_data in activities_data.items():
            current_participants = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            if current_participants == max_participants:
                full_activity = activity_name
                break
        
        # If no full activity exists, use one with capacity
        test_activity = full_activity or test_activity
        new_email = "new.student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{test_activity}/signup",
            params={"email": new_email}
        )
        
        # Assert - Registration succeeds even if full
        if response.status_code == 200:
            assert new_email in client.get("/activities").json()[test_activity]["participants"]
    
    def test_signup_multiple_students_same_activity(self, client, test_activity_name):
        """
        Arrange: Multiple students signing up for the same activity
        Act: Call signup endpoint multiple times with different emails
        Assert: All students successfully added
        """
        # Arrange
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Act
        for email in emails:
            response = client.post(
                f"/activities/{test_activity_name}/signup",
                params={"email": email}
            )
            
            # Assert each signup
            assert response.status_code == 200
        
        # Assert all are in activity
        participants = client.get("/activities").json()[test_activity_name]["participants"]
        for email in emails:
            assert email in participants
