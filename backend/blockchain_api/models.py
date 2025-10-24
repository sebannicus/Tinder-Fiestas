from django.db import models

class UserProfile(models.Model):
    wallet_address = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or self.wallet_address


class CheckIn(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="checkins")
    location = models.CharField(max_length=100)
    tx_hash = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.wallet_address} → {self.location}"
