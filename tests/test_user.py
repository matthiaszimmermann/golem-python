"""Tests for the User class."""

import pytest
from pydantic import ValidationError

from examples.user import User

# Test data constants
TEST_ID = 1
TEST_NAME = "Alice Smith"
TEST_EMAIL = "alice.smith@example.com"
INVALID_EMAIL = "invalid-email"
INVALID_NAME = "A"  # Too short


def test_valid_user() -> None:
    """Test creating a valid user."""
    user = User(id=TEST_ID, name=TEST_NAME, email=TEST_EMAIL)

    assert user.id == TEST_ID
    assert user.name == TEST_NAME
    assert user.email == TEST_EMAIL


def test_to_json() -> None:
    """Test converting user to JSON."""
    user = User(id=TEST_ID, name=TEST_NAME, email=TEST_EMAIL)

    json_str: str = user.to_json()
    assert f'"id":{TEST_ID}' in json_str
    assert f'"name":"{TEST_NAME}"' in json_str
    assert f'"email":"{TEST_EMAIL}"' in json_str


def test_from_json() -> None:
    """Test creating user from JSON."""
    json_str = f'{{"id": {TEST_ID}, "name": "{TEST_NAME}", "email": "{TEST_EMAIL}"}}'
    user = User.from_json(json_str)

    assert user.id == TEST_ID
    assert user.name == TEST_NAME
    assert user.email == TEST_EMAIL


def test_invalid_json() -> None:
    """Test handling invalid JSON."""
    with pytest.raises(ValueError, match="Input should be a valid integer"):
        User.from_json(
            '{"id": "not_an_integer", "name": "Alice", "email": "alice@example.com"}'
        )


def test_malformed_json() -> None:
    """Test handling malformed JSON string."""
    with pytest.raises(ValidationError) as exc_info:
        User.from_json('{"id": 1, "name": "Alice" "email": "alice@example.com"}')

    print(f"exc_info.type.__name__: {exc_info.type.__name__}")
    print(f"str(exc_info.value).lower(): {str(exc_info.value).lower()}")
    # Verify we get a JSON parsing error
    assert "json_invalid" in str(exc_info.value).lower()


def test_invalid_email() -> None:
    """Test invalid email format."""
    with pytest.raises(ValueError, match="value is not a valid email address"):
        User(
            id=TEST_ID,
            name=TEST_NAME,
            email=INVALID_EMAIL,  # Invalid email format
        )


def test_invalid_name() -> None:
    """Test invalid name length."""
    with pytest.raises(ValueError, match="String should have at least 2 characters"):
        User(
            id=TEST_ID,
            name=INVALID_NAME,  # Too short (min_length=2)
            email=TEST_EMAIL,
        )
