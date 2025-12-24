# ------------------------------------------------------------------
# Kudi SMS replacement for Termii
# ------------------------------------------------------------------
from django.http import JsonResponse
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
def send_due_messages(request):
    logger.info("Running scheduled message job...")
    due = Message.objects.filter(
        scheduled_time__lte=timezone.now(),
        sent_at__isnull=True
    )
    logger.info(f"Found {due.count()} pending messages")

    sent_count = 0
    for msg in due:
        try:
            sms_text = f"Hi {msg.receiver_name},\n\n{msg.message}\n\n- {msg.sender_name}"
            payload = {
                "token": API_KEY,
                "gateway": 2,
                "data": [[SENDER_ID, msg.receiver_phone, sms_text]]
            }

            resp = requests.post(BASE_URL, json=payload, timeout=15)
            if resp.status_code == 200 and resp.json().get("error_code") == "000":
                msg.sent_at = timezone.now()
                msg.save(update_fields=['sent_at'])
                logger.info(f"Message {msg.id} sent successfully via Kudi.")
                sent_count += 1
            else:
                logger.error(f"Kudi error for message {msg.id}: {resp.text}")
        except Exception:
            logger.exception(f"Failed to send message {msg.id}")

    # -----  RETURN A RESPONSE  -----
    return JsonResponse({"status": "ok", "sent": sent_count})

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
