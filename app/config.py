"""
This module defines application configuration using Pydantic Settings.

The Settings class loads environment variables from a `.env` file or the system
environment, providing typed and validated configuration values for the app.
It also includes a cached helper function (`get_settings`) to ensure the
settings are instantiated only once across the entire application.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        database_url (str): Connection string for the application's database.
        twilio_account_sid (str): Twilio Account SID used for authentication.
        twilio_auth_token (str): Twilio authentication token.
        twilio_phone_number (str): Phone number provided by Twilio for sending messages.
        scheduled_time (str): Daily scheduled time for running a task (default: "14:30").
    """

    database_url: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    scheduled_time: str = "14:30"

    class Config:
        """
        Pydantic configuration class.

        Attributes:
            env_file (str): Path to the .env file containing environment variables.
            case_sensitive (bool): Whether environment variable names must match case.
        """

        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of Settings.

    Using `lru_cache()` ensures that the Settings object is created only once,
    improving performance and preventing repeated loading/parsing of environment variables.

    Returns:
        Settings: The application's configuration settings.
    """
    return Settings()
