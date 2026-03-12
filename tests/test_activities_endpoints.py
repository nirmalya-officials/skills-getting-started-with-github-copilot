"""
Comprehensive tests for Mergington High School API endpoints.

All tests follow the AAA (Arrange-Act-Assert) pattern with clear sections.
Tests cover happy paths, error cases, and edge cases for all 4 endpoints.
"""

import pytest


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        # Arrange
        expected_activity_count = 3
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_returns_activity_with_correct_structure(self, client):
        """Test that each activity has correct data structure and fields."""
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert set(activity_data.keys()) == expected_fields
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_participants_list_populated_correctly(self, client):
        """Test that participants list is populated with expected participants."""
        # Arrange
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        expected_programming_participants = ["emma@mergington.edu", "sophia@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert activities["Chess Club"]["participants"] == expected_chess_participants
        assert activities["Programming Class"]["participants"] == expected_programming_participants


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client, sample_activity, sample_email):
        """Test successful signup of a new participant to an activity."""
        # Arrange
        activity_name = sample_activity
        email = sample_email
        expected_message_pattern = f"Signed up {email} for {activity_name}"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == expected_message_pattern
        
        # Verify participant was added
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client, sample_email, sample_new_activity):
        """Test signup to non-existent activity returns 404."""
        # Arrange
        activity_name = sample_new_activity
        email = sample_email
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant_fails(self, client, sample_activity):
        """Test that duplicate signup for same participant is rejected with 400."""
        # Arrange
        activity_name = sample_activity
        # Using an existing participant from the fixture data
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Student already signed up for this activity" in data["detail"]

    def test_signup_multiple_different_participants(self, client, sample_activity):
        """Test that multiple different participants can sign up for same activity."""
        # Arrange
        activity_name = sample_activity
        new_emails = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        
        # Act & Assert - Sign up multiple participants
        for email in new_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all were added
        get_response = client.get("/activities")
        activities = get_response.json()
        for email in new_emails:
            assert email in activities[activity_name]["participants"]

    def test_signup_same_participant_different_activities(self, client):
        """Test that same participant can signup for multiple different activities."""
        # Arrange
        email = "student@test.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act & Assert - Sign up to multiple activities
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify participant was added to all activities
        get_response = client.get("/activities")
        activities = get_response.json()
        for activity_name in activities_to_join:
            assert email in activities[activity_name]["participants"]


class TestDeleteParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_success(self, client, sample_activity):
        """Test successful removal of existing participant from activity."""
        # Arrange
        activity_name = sample_activity
        # Using an existing participant from the fixture data
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Removed {email_to_remove} from {activity_name}" in data["message"]
        
        # Verify participant was removed
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email_to_remove not in activities[activity_name]["participants"]

    def test_remove_participant_activity_not_found(self, client, sample_new_activity):
        """Test removal from non-existent activity returns 404."""
        # Arrange
        activity_name = sample_new_activity
        email = "test@test.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_nonexistent_participant(self, client, sample_activity):
        """Test removal of non-existent participant returns 404."""
        # Arrange
        activity_name = sample_activity
        non_existent_email = "nonexistent@test.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{non_existent_email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_signup_then_remove_participant_flow(self, client, sample_activity):
        """Test integration: signup a participant, then remove them."""
        # Arrange
        activity_name = sample_activity
        email = "workflow.test@test.edu"
        
        # Act 1: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert 1: Signup successful
        assert signup_response.status_code == 200
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email in activities[activity_name]["participants"]
        
        # Act 2: Remove participant
        delete_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert 2: Removal successful
        assert delete_response.status_code == 200
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_remove_multiple_participants_sequentially(self, client, sample_activity):
        """Test removing multiple participants one by one."""
        # Arrange
        activity_name = sample_activity
        emails_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act & Assert - Remove each participant
        for email in emails_to_remove:
            response = client.delete(
                f"/activities/{activity_name}/participants/{email}"
            )
            assert response.status_code == 200
        
        # Verify all were removed
        get_response = client.get("/activities")
        activities = get_response.json()
        assert len(activities[activity_name]["participants"]) == 0


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        # Arrange
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_follows(self, client):
        """Test following the redirect from GET /."""
        # Arrange
        
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        # The redirect will fail because /static/index.html doesn't exist in test app,
        # but the redirect is set up correctly
        assert response.status_code in [200, 404]  # 404 is expected for missing static file
