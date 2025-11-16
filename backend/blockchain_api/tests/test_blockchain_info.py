import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.urls import reverse


@pytest.mark.django_db
class TestBlockchainInfo:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("blockchain_info")

    @patch("blockchain_api.views.get_contract_info")
    def test_blockchain_info(self, mock_get_contract_info):
        mock_get_contract_info.return_value = {
            "address": "0x123",
            "rpc_url": "http://127.0.0.1:8545",
            "connected": True,
            "block_number": 10,
        }

        response = self.client.get(self.url)

        assert response.status_code == 200
        assert response.data["status"] == "success"
        assert response.data["blockchain"]["address"] == "0x123"
        assert response.data["blockchain"]["connected"] is True
