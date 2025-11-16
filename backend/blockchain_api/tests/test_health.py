import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.urls import reverse


@pytest.mark.django_db
class TestHealthCheck:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("health_check")

    @patch("blockchain_api.views.is_blockchain_connected", return_value=True)
    @patch("blockchain_api.views.get_contract_info")
    def test_health_ok(self, mock_get_contract_info, _mock_is_blockchain_connected):
        mock_get_contract_info.return_value = {
            "address": "0x123",
            "rpc_url": "http://127.0.0.1:8545",
            "connected": True,
            "block_number": 5,
        }

        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.data["status"] == "healthy"
        assert response.data["blockchain"] == "connected"
        assert response.data["database"] == "connected"
