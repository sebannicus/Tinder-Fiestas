from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    wallet_address = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or self.wallet_address


class CheckIn(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="checkins")
    location = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    tx_hash = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.wallet_address} → {self.location}"


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.start_date.date()} - {self.end_date.date()})"

class EventAttendance(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="attendances")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendees")
    tx_hash = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.wallet_address} asistió a {self.event.name}"
