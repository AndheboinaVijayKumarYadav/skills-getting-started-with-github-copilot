"""
Tests for the unregister endpoint using the AAA (Arrange-Act-Assert) pattern.
Each test follows the structure:
  - Arrange: Set up test data and preconditions
  - Act: Call the endpoint being tested
  - Assert: Verify the response and state
"""

import pytest


class TestUnregisterHappyPath:
    """Tests for successful unregister scenarios"""
    
    def test_unregister_existing_participant_successfully(self, client, test_activity_name):
        """
        Arrange: Student is signed up for activity
        Act: Call unregister endpoint with valid email and activity
        Assert: Student removed from activity and success response returned
        """
        # Arrange
        existing_participant = client.get("/activities").json()[test_activity_name]["participants"][0]
        initial_count = len(
            client.get("/activities").json()[test_activity_name]["participants"]
        )
        
        # Act
        response = client.delete(
            f"/activities/{test_activity_name}/unregister",
            params={"email": existing_participant}
        )
        
        # Assert
        assert response.status_code == 200
        assert existing_participant not in client.get("/activities").json()[test_activity_name]["participants"]
        assert len(
            client.get("/activities").json()[test_activity_name]["participants"]
        ) == initial_count - 1
        assert "message" in response.json()
    
    def test_unregister_decreases_participant_count(self, client, test_activity_name):
        """
        Arrange: Student is signed up for activity with known count
        Act: Call unregister endpoint
        Assert: Participant count decreases by exactly 1
        """
        # Arrange
        participant = client.get("/activities").json()[test_activity_name]["participants"][0]
        before_count = len(
            client.get("/activities").json()[test_activity_name]["participants"]
        )
        
        # Act
        response = client.delete(
            f"/activities/{test_activity_name}/unregister",
            params={"email": participant}
        )
        
        # Assert
        after_count = len(
            client.get("/activities").json()[test_activity_name]["participants"]
        )
        assert response.status_code == 200
        assert after_count == before_count - 1


class TestUnregisterErrorCases:
    """Tests for unregister error scenarios"""
    
    def test_unregister_nonexistent_activity_returns_404(self, client, sample_email):
        """
        Arrange: Activity does not exist
        Act: Call unregister endpoint with nonexistent activity name
        Assert: 404 status and error message returned
        """
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_signed_up_returns_400(self, client, test_activity_name, sample_email):
        """
        Arrange: Student is not signed up for activity
        Act: Call unregister endpoint with email not in participants
        Assert: 400 status and error message returned
        """
        # Arrange
        # sample_email is not in any activity by default
        
        # Act
        response = client.delete(
            f"/activities/{test_activity_name}/unregister",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestUnregisterEdgeCases:
    """Tests for edge cases in unregister"""
    
    def test_unregister_then_signup_again(self, client, test_activity_name, sample_email):
        """
        Arrange: Student signs up, then unregisters, then signs up again
        Act: Perform signup, unregister, signup sequence
        Assert: All operations succeed and final state shows student signed up
        """
        # Arrange & Act & Assert - Sign up
        response1 = client.post(
            f"/activities/{test_activity_name}/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        assert sample_email in client.get("/activities").json()[test_activity_name]["participants"]
        
        # Arrange & Act & Assert - Unregister
        response2 = client.delete(
            f"/activities/{test_activity_name}/unregister",
            params={"email": sample_email}
        )
        assert response2.status_code == 200
        assert sample_email not in client.get("/activities").json()[test_activity_name]["participants"]
        
        # Arrange & Act & Assert - Sign up again
        response3 = client.post(
            f"/activities/{test_activity_name}/signup",
            params={"email": sample_email}
        )
        assert response3.status_code == 200
        assert sample_email in client.get("/activities").json()[test_activity_name]["participants"]
    
    def test_unregister_multiple_participants_from_activity(self, client, test_activity_name):
        """
        Arrange: Multiple students signed up for activity
        Act: Call unregister endpoint multiple times with different emails
        Assert: Only specified participants removed, others remain
        """
        # Arrange
        participants = client.get("/activities").json()[test_activity_name]["participants"].copy()
        if len(participants) < 2:
            # Skip if not enough participants
            pytest.skip("Activity does not have enough participants for this test")
        
        to_remove = participants[:2]
        to_keep = participants[2:]
        
        # Act
        for email in to_remove:
            response = client.delete(
                f"/activities/{test_activity_name}/unregister",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert
        current_participants = client.get("/activities").json()[test_activity_name]["participants"]
        for email in to_remove:
            assert email not in current_participants
        for email in to_keep:
            assert email in current_participants
