"""
This module defines the Pydantic schemas used for validating and structuring
data related to scheduled messages. These schemas ensure that incoming request
data is clean, properly formatted, and safe before it interacts with the
database or application logic.

Two schemas are defined:
- MessageCreate: Used for validating data when creating a new scheduled message.
- MessageResponse: Used for shaping data returned from the API.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
import re


class MessageCreate(BaseModel):
    """
    Schema for creating a new scheduled message.

    Validates:
        - sender and receiver names
        - phone number format
        - message length
        - scheduled time must be in the future

    Attributes:
        sender_name (str): Name of the sender.
        receiver_name (str): Name of the recipient.
        receiver_phone (str): Phone number of the recipient. Must be in an
            international format (e.g., +1234567890).
        message (str): Content of the message (up to 1600 chars).
        scheduled_time (datetime): Future date and time when the message should be sent.
    """

    sender_name: str = Field(..., min_length=2, max_length=100)
    receiver_name: str = Field(..., min_length=2, max_length=100)
    receiver_phone: str = Field(..., min_length=10, max_length=20)
    message: str = Field(..., min_length=1, max_length=1600)
    scheduled_time: datetime

    @validator('receiver_phone')
    def validate_phone(cls, v):
        """
        Validates and normalizes the phone number format.

        Steps:
            1. Removes spaces, dashes, and parentheses.
            2. Ensures the value contains only digits (with an optional leading '+').
            3. Ensures the number starts with '+'.
        """
        cleaned = re.sub(r'[\s\-\(\)]', '', v)

        if not re.match(r'^\+?\d{10,15}$', cleaned):
            raise ValueError('Phone number must be in format: +1234567890')

        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned

        return cleaned

    @validator('scheduled_time')
    def validate_future_time(cls, v):
        """
        Ensures that the scheduled time is in the future.

        Raises:
            ValueError: If the scheduled time is not greater than the current UTC time.
        """
        if v <= datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v


class MessageResponse(BaseModel):
    """
    Schema for representing a scheduled message returned to the client.

    Attributes:
        id (int): Unique identifier of the message.
        sender_name (str): Name of the sender.
        receiver_name (str): Name of the recipient.
        receiver_phone (str): Recipient's phone number in international format.
        message (str): The SMS content.
        scheduled_time (datetime): When the message was scheduled to be sent.
        is_sent (bool): Whether the message has been sent.
        sent_at (datetime | None): Timestamp when the message was sent, if applicable.
        created_at (datetime): Timestamp when the message was created.
    """

    id: int
    sender_name: str
    receiver_name: str
    receiver_phone: str
    message: str
    scheduled_time: datetime
    is_sent: bool
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        # Allows converting SQLAlchemy ORM objects into this Pydantic model
        from_attributes = True
