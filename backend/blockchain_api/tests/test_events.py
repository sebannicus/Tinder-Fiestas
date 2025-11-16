import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from blockchain_api.models import Event


@pytest.mark.django_db
class TestEvents:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("events")

    def test_get_events(self):
        start = timezone.now()
        end = start + timedelta(hours=2)

        Event.objects.create(
            name="Fiesta Test",
            description="desc",
            location="loc",
            latitude=1.0,
            longitude=1.0,
            start_date=start,
            end_date=end,
        )

        response = self.client.get(self.url)
        assert response.status_code == 200

        # Debe ser un array directo
        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Fiesta Test"

    def test_create_event_success(self):
        start = timezone.now()
        end = start + timedelta(hours=2)

        payload = {
            "name": "Evento Nuevo",
            "description": "Descripción",
            "location": "Bellavista",
            "latitude": -33.44,
            "longitude": -70.66,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == 201
        assert response.data["status"] == "success"
        assert Event.objects.count() == 1

    def test_create_event_invalid(self):
        # Falta campo obligatorio "name"
        payload = {
            "location": "Bellavista",
            "latitude": -33.44,
            "longitude": -70.66,
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == 400
        assert "error" in response.data
        assert "details" in response.data
        assert "name" in response.data["details"]
