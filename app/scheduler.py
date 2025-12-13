"""
This module sets up and manages the background scheduler responsible for sending
scheduled SMS messages. It uses APScheduler to periodically check for messages
that are due and Termii's API to deliver them.

Functions included:
- send_scheduled_messages: Executes the logic to send all pending messages.
- start_scheduler: Initializes and starts the background scheduler.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.crud import get_pending_messages, mark_as_sent
from app.config import get_settings
import logging
import requests

# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load application settings
settings = get_settings()

# ---------------------------------------------------------
# Termii API Configuration
# ---------------------------------------------------------
TERMIi_BASE_URL = "https://v3.api.termii.com/api/sms/send"


def send_scheduled_messages():
    """
    Background job function that sends all pending scheduled messages.

    Workflow:
        1. Retrieve unsent messages that are due (scheduled_time <= now).
        2. For each message:
            - Send SMS using Termii’s API.
            - Mark the message as sent in the database.
        3. Log successes and failures for debugging.

    This function is triggered automatically by APScheduler.
    """
    logger.info("Running scheduled message job...")

    db = SessionLocal()
    try:
        pending_messages = get_pending_messages(db)
        logger.info(f"Found {len(pending_messages)} pending messages")

        for msg in pending_messages:
            try:
                # Prepare Termii payload
                payload = {
                    "api_key": settings.termii_api_key,
                    "to": msg.receiver_phone,
                    "from": settings.termii_sender_id,
                    "sms": f"Hi {msg.receiver_name},\n\n{msg.message}\n\n- {msg.sender_name}",
                    "type": "plain",
                    "channel": "generic"
                }

                # Send request
                response = requests.post(TERMIi_BASE_URL, json=payload, timeout=15)

                # Validate Termii response
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == "ok":
                        mark_as_sent(db, msg.id)
                        logger.info(f"Message {msg.id} sent successfully via Termii.")
                    else:
                        logger.error(f"Termii error for message {msg.id}: {data}")
                else:
                    logger.error(
                        f"HTTP error sending message {msg.id}: Status {response.status_code}"
                    )

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
        - Uses `replace_existing=True` to prevent duplicate job registration.

    Returns:
        BackgroundScheduler: The started scheduler instance.
    """
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        send_scheduled_messages,
        'interval',
        minutes=1,
        id='send_messages_job',
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started successfully")
    return scheduler
