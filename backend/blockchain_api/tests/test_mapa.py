import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from blockchain_api.models import Event


@pytest.mark.django_db
class TestMapa:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("mapa_completo")

        start = timezone.now()
        end = start + timedelta(hours=2)

        Event.objects.create(
            name="Test",
            description="desc",
            location="loc",
            latitude=1.0,
            longitude=1.0,
            start_date=start,
            end_date=end,
        )

    def test_mapa(self):
        response = self.client.get(self.url)
        assert response.status_code == 200

        data = response.data
        assert isinstance(data, dict)
        assert data["status"] == "success"
        assert "eventos" in data
        assert isinstance(data["eventos"], list)
        assert data["total_events"] == len(data["eventos"])
