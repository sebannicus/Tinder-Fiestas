from django.db import models
from django.utils import timezone

class CheckIn(models.Model):
    user_id = models.IntegerField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    tx_hash = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user_id} → {self.location}"
