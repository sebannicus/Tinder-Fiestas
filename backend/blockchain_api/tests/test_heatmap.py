import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.urls import reverse


@pytest.mark.django_db
class TestHeatmap:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("heatmap_data")

    @patch("blockchain_api.views.get_heatmap_data")
    def test_heatmap_points(self, mock_get_heatmap_data):
        mock_get_heatmap_data.return_value = [
            {"latitude": -33.44, "longitude": -70.66, "count": 3}
        ]

        response = self.client.get(self.url)
        assert response.status_code == 200

        # Debe ser un array directo
        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0]["count"] == 3
