"""
This module defines the SQLAlchemy ORM model for representing scheduled SMS
messages in the database.

The `ScheduledMessage` model stores all information needed to schedule, send,
and track the status of outgoing messages, including receiver details, message
content, scheduled time, and timestamps.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.database import Base


class ScheduledMessage(Base):
    """
    SQLAlchemy ORM model for representing a scheduled message.

    Attributes:
        id (int): Primary key identifier for the message.
        sender_name (str): Name of the sender (used for personalization).
        receiver_name (str): Name of the message recipient.
        receiver_phone (str): Phone number of the message recipient.
        message (str): The SMS content to be delivered.
        scheduled_time (datetime): The exact date and time when the message
            should be sent.
        is_sent (bool): Indicates whether the message has already been sent.
        sent_at (datetime | None): Timestamp of when the message was actually sent.
        created_at (datetime): Timestamp when the message record was created.
    """

    __tablename__ = "scheduled_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_name = Column(String(100), nullable=False)
    receiver_name = Column(String(100), nullable=False)
    receiver_phone = Column(String(20), nullable=False)
    message = Column(String(1600), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """
        Returns a readable string representation of the model instance.

        Useful for debugging and logging.
        """
        return f"<ScheduledMessage {self.id}: {self.receiver_name}>"
