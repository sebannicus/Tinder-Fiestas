import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.urls import reverse


@pytest.mark.django_db
class TestStats:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("activity_stats")

    @patch("blockchain_api.views.get_activity_stats")
    def test_stats_default(self, mock_get_stats):
        mock_get_stats.return_value = {
            "total_checkins": 10,
            "unique_users": 3,
            "top_locations": [
                {"location": "Bellavista", "visits": 5},
            ],
        }

        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.data["status"] == "success"
        assert response.data["period_days"] == 7
        assert response.data["total_checkins"] == 10
        assert response.data["unique_users"] == 3

    def test_stats_invalid_days(self):
        response = self.client.get(self.url + "?days=abc")
        assert response.status_code == 400
        assert "Invalid days parameter" in response.data["error"]
