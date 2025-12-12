"""
This module sets up and manages the background scheduler responsible for sending
scheduled SMS messages. It uses APScheduler to periodically check for messages
that are due and Twilio's API to deliver them.

Functions included:
- send_scheduled_messages: Executes the logic to send all pending messages.
- start_scheduler: Initializes and starts the background scheduler.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
from app.database import SessionLocal
from app.crud import get_pending_messages, mark_as_sent
from app.config import get_settings
import logging

# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load application settings
settings = get_settings()

# ---------------------------------------------------------
# Initialize Twilio Client
# ---------------------------------------------------------
# The Twilio client is created once and reused for sending messages.
# It uses credentials loaded from environment variables.
twilio_client = Client(
    settings.twilio_account_sid,
    settings.twilio_auth_token
)


def send_scheduled_messages():
    """
    Background job function that sends all pending scheduled messages.

    Workflow:
        1. Retrieve unsent messages that are due (scheduled_time <= now).
        2. For each message:
            - Send an SMS using Twilio.
            - Mark the message as sent in the database.
        3. Log successes and failures for visibility and debugging.

    This function is intended to be run periodically by APScheduler.
    """
    logger.info("Running scheduled message job...")

    db = SessionLocal()
    try:
        # Retrieve pending messages
        pending_messages = get_pending_messages(db)
        logger.info(f"Found {len(pending_messages)} pending messages")

        for msg in pending_messages:
            try:
                # Send SMS via Twilio API
                twilio_message = twilio_client.messages.create(
                    body=f"Hi {msg.receiver_name},\n\n{msg.message}\n\n- {msg.sender_name}",
                    from_=settings.twilio_phone_number,
                    to=msg.receiver_phone
                )

                # Update message status
                mark_as_sent(db, msg.id)
                logger.info(f"Message {msg.id} sent successfully. SID: {twilio_message.sid}")

            except Exception as e:
                logger.error(f"Failed to send message {msg.id}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in scheduled job: {str(e)}")

    finally:
        db.close()


def start_scheduler():
    """
    Initialize and start the APScheduler background scheduler.

    The scheduler:
        - Runs in the background without blocking the main application.
        - Executes `send_scheduled_messages` every minute.
        - Uses `replace_existing=True` to avoid duplicate jobs if restarted.

    Returns:
        BackgroundScheduler: The started scheduler instance.
    """
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        send_scheduled_messages,
        'interval',
        minutes=1,          # Check for messages every minute
        id='send_messages_job',
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started successfully")

    return scheduler
