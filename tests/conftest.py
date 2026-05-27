"""
Shared pytest fixtures and configuration for FastAPI tests
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Fixture providing a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Fixture that resets activities to a known state before each test.
    Prevents test pollution by ensuring each test starts fresh.
    """
    # Save original state
    original_activities = {
        activity_name: {
            "description": data["description"],
            "schedule": data["schedule"],
            "max_participants": data["max_participants"],
            "participants": data["participants"].copy()
        }
        for activity_name, data in activities.items()
    }
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_email():
    """Fixture providing a sample student email for tests"""
    return "test.student@mergington.edu"


@pytest.fixture
def test_activity_name():
    """Fixture providing an existing activity name for tests"""
    return "Chess Club"
