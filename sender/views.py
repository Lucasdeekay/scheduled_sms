# ------------------------------------------------------------------
# Kudi SMS replacement for Termii
# ------------------------------------------------------------------
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from api.models import Message
from app.settings import (
    API_KEY,        # re-use this field for Kudi token
    SENDER_ID       # re-use this field for Kudi senderID
)
import logging, requests

logger = logging.getLogger()

# Kudi: new endpoint
BASE_URL = "https://my.kudisms.net/api/autocomposesms"

@csrf_exempt
def send_due_messages():
    logger.info("Running scheduled message job...")
    due = Message.objects.filter(
        scheduled_time__lte=timezone.now(),
        sent_at__isnull=True
    )
    logger.info(f"Found {due.count()} pending messages")

    for msg in due:
        try:
            # Kudi: build the 3-column array it expects
            sms_text = f"Hi {msg.receiver_name},\n\n{msg.message}\n\n- {msg.sender_name}"
            payload = {
                "token": API_KEY,          # your Kudi API key
                "gateway": 2,                     # 2 = generic route (adjust if you need another)
                "data": [
                    [SENDER_ID, msg.receiver_phone, sms_text]
                ]
            }

            # Kudi: POST JSON (not form-data)
            resp = requests.post(BASE_URL, json=payload, timeout=15)
            logger.debug(f"Kudi raw response: {resp.text}")

            # Kudi: success when HTTP 200 AND error_code == "000"
            if resp.status_code == 200:
                kudi_json = resp.json()
                if kudi_json.get("error_code") == "000":
                    msg.sent_at = timezone.now()
                    msg.save(update_fields=['sent_at'])
                    logger.info(f"Message {msg.id} sent successfully via Kudi.")
                    continue

            # anything else is a failure
            logger.error(f"Kudi error for message {msg.id}: {resp.text}")

        except Exception as exc:
            logger.exception(f"Failed to send message {msg.id}")

# ------------------------------------------------------------------
# Scheduler boot code (unchanged)
# ------------------------------------------------------------------
_scheduler = None

def start_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        return _scheduler
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        send_due_messages,
        'interval',
        minutes=1,
        id='send_messages_job',
        replace_existing=True
    )
    _scheduler.start()
    logger.info("Scheduler started successfully")
    return _scheduler
