from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from api.models import Message
from app.settings import TERMII_API_KEY, TERMII_SENDER_ID
import logging, requests
logger = logging.getLogger()

TERMII_URL = "https://v3.api.termii.com/api/sms/send"
def send_due_messages():
    logger.info("Running scheduled message job...")
    due = Message.objects.filter(
    scheduled_time__lte=timezone.now(),
    sent_at__isnull=True
    )
    logger.info(f"Found {due.count()} pending messages")
    for msg in due:
        try:
            payload = {
            "api_key": TERMII_API_KEY,
            "to": msg.receiver_phone,
            "from": TERMII_SENDER_ID,
            "sms": f"Hi {msg.receiver_name},\n\n{msg.message}\n\n- {msg.sender_name}",
            "type": "plain",
            "channel": "generic"
            }
            resp = requests.post(TERMII_URL, json=payload, timeout=15)
            if resp.status_code == 200 and resp.json().get("code") == "ok":
                msg.sent_at = timezone.now()
                msg.save(update_fields=['sent_at'])
                logger.info(f"Message {msg.id} sent successfully via Termii.")
            else:
                logger.error(f"Termii error for message {msg.id}: {resp.text}")
        except Exception as exc:
            logger.exception(f"Failed to send message {msg.id}")
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