"""
This module provides CRUD (Create, Read, Update, Delete) operations for the
ScheduledMessage model. These helper functions interact with the database
through SQLAlchemy sessions and are used by the API routes and background
scheduler to manage scheduled messages.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from app.models import ScheduledMessage
from app.schemas import MessageCreate


def create_message(db: Session, message: MessageCreate):
    """
    Create and save a new scheduled message in the database.

    Args:
        db (Session): Active database session.
        message (MessageCreate): Validated schema containing message details.

    Returns:
        ScheduledMessage: The newly created message instance.
    """
    db_message = ScheduledMessage(
        sender_name=message.sender_name,
        receiver_name=message.receiver_name,
        receiver_phone=message.receiver_phone,
        message=message.message,
        scheduled_time=message.scheduled_time
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_pending_messages(db: Session):
    """
    Retrieve all scheduled messages that are due but not yet sent.

    A message is considered 'pending' if:
        - `is_sent` is False
        - `scheduled_time` is less than or equal to the current UTC time

    Args:
        db (Session): Active database session.

    Returns:
        List[ScheduledMessage]: All due unsent messages.
    """
    current_time = datetime.utcnow()
    return db.query(ScheduledMessage).filter(
        ScheduledMessage.is_sent == False,
        ScheduledMessage.scheduled_time <= current_time
    ).all()


def mark_as_sent(db: Session, message_id: int):
    """
    Mark a specific message as sent and record the timestamp.

    Args:
        db (Session): Active database session.
        message_id (int): ID of the message to update.

    Returns:
        ScheduledMessage | None: Updated message object, or None if not found.
    """
    message = db.query(ScheduledMessage).filter(
        ScheduledMessage.id == message_id
    ).first()

    if message:
        message.is_sent = True
        message.sent_at = datetime.utcnow()
        db.commit()
        db.refresh(message)

    return message


def get_all_messages(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve all messages with pagination support.

    Args:
        db (Session): Active database session.
        skip (int): Number of records to skip (default: 0).
        limit (int): Maximum records to return (default: 100).

    Returns:
        List[ScheduledMessage]: List of messages.
    """
    return db.query(ScheduledMessage).offset(skip).limit(limit).all()


def get_message_by_id(db: Session, message_id: int):
    """
    Retrieve a single message by its ID.

    Args:
        db (Session): Active database session.
        message_id (int): ID of the message to retrieve.

    Returns:
        ScheduledMessage | None: The message if found, otherwise None.
    """
    return db.query(ScheduledMessage).filter(
        ScheduledMessage.id == message_id
    ).first()
