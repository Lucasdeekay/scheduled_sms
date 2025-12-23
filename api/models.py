from django.db import models
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+[1-9]\d{1,14}$',
    message="Phone must be in E.164 format (+1234567890)"
)


class Message(models.Model):
    sender_name   = models.CharField(max_length=100)
    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=20, validators=[phone_validator])
    message       = models.TextField(max_length=1600)
    scheduled_time = models.DateTimeField()
    sent_at       = models.DateTimeField(null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Msg to {self.receiver_name} at {self.scheduled_time}"