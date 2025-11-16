import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from blockchain_api.models import Event, UserProfile, EventAttendance, CheckIn


@pytest.mark.django_db
class TestCheckIn:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("event_checkin")

        start = timezone.now()
        end = start + timedelta(hours=2)

        self.event = Event.objects.create(
            name="Test",
            description="desc",
            location="loc",
            latitude=1.0,
            longitude=1.0,
            start_date=start,
            end_date=end,
        )

        self.wallet_address = "0x1111111111111111111111111111111111111111"
        self.tx_hash = "0x" + "a" * 64

    @patch("blockchain_api.views.Web3.is_address", return_value=True)
    @patch("blockchain_api.views.verify_event_checkin_tx")
    def test_checkin_success(self, mock_verify_tx, _mock_is_address):
        mock_verify_tx.return_value = {
            "tx_hash": self.tx_hash,
            "block_number": 1,
            "timestamp": 1234567890,
        }

        payload = {
            "event_id": self.event.id,
            "wallet_address": self.wallet_address,
            "tx_hash": self.tx_hash,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == 201
        assert response.data["status"] == "success"

        assert EventAttendance.objects.count() == 1
        assert CheckIn.objects.count() == 1

    def test_checkin_invalid_hash_format(self):
        payload = {
            "event_id": self.event.id,
            "wallet_address": self.wallet_address,
            "tx_hash": "0x1234",
        }

        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == 400
        assert "Invalid transaction hash format" in response.data["error"]

    def test_checkin_event_not_found(self):
        payload = {
            "event_id": 9999,
            "wallet_address": self.wallet_address,
            "tx_hash": "0x" + "b" * 64,
        }

        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == 404
        assert "Event not found" in response.data["error"]

    @patch("blockchain_api.views.Web3.is_address", return_value=True)
    @patch("blockchain_api.views.verify_event_checkin_tx")
    def test_checkin_duplicate(self, mock_verify_tx, _mock_is_address):
        mock_verify_tx.return_value = {
            "tx_hash": self.tx_hash,
            "block_number": 1,
            "timestamp": 1234567890,
        }

        user = UserProfile.objects.create(wallet_address=self.wallet_address)

        # Primera asistencia ya registrada
        EventAttendance.objects.create(
            user=user,
            event=self.event,
            tx_hash=self.tx_hash,
        )

        payload = {
            "event_id": self.event.id,
            "wallet_address": self.wallet_address,
            "tx_hash": self.tx_hash,
        }

        response = self.client.post(self.url, payload, format="json")
        # Tu código retorna 400 como duplicado
        assert response.status_code == 400
        assert "already" in response.data["error"].lower()
