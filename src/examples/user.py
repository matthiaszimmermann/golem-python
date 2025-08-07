"""Example of using Pydantic for user data validation."""

from pydantic import BaseModel, EmailStr, Field

from logging_config import get_logger

logger = get_logger(__name__)


class User(BaseModel):
    """Represents a user with basic profile information."""

    id: int
    name: str = Field(..., min_length=2)  # Added min_length validation to match test
    email: EmailStr  # Using EmailStr for email validation

    def to_json(self) -> str:  # noqa: D102
        logger.info("Converting User instance to JSON")
        try:
            json_str = self.model_dump_json()
            logger.info(f"Conversion successful: {json_str}")
            return json_str
        except Exception as e:
            logger.error(f"Conversion exception: {e.__class__.__name__}: {e!r}")
            raise

    @classmethod
    def from_json(cls, json_str: str) -> "User":  # noqa: D102
        logger.info("Creating User instance from JSON")
        try:
            user = cls.model_validate_json(json_str)
            logger.info(f"Conversion successful with ID: {user.id}")
            return user
        except Exception as e:
            logger.error(f"Conversion exception: {e.__class__.__name__}: {e!s}")
            raise


# ruff: noqa
def main() -> None:
    """Show how to use the User class."""
    user = User(id=1, name="Alice Smith", email="alice.smith@example.com")

    print(f"User: {user.name}")
    print(f"Email: {user.email}")
    print(f"ID: {user.id}")
    print(f"to_json: {user.to_json()}")

    try:
        User.from_json('{"id":1,"name":"Alice')
    except:
        pass


# ruff: enable


if __name__ == "__main__":
    main()
