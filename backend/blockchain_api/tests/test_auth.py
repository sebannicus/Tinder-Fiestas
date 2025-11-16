import pytest
from unittest.mock import MagicMock, patch
from rest_framework.test import APIClient
from django.urls import reverse
from blockchain_api.models import UserProfile


@pytest.mark.django_db
class TestAuth:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("login_wallet")

    def test_login_wallet_missing_params(self):
        response = self.client.post(self.url, {}, format="json")
        assert response.status_code == 400
        assert "error" in response.data

    def test_login_wallet_invalid_address(self):
        payload = {
            "address": "not_an_address",
            "signature": "0x1234",
            "nonce": "TinderFiestas_123",
        }
        response = self.client.post(self.url, payload, format="json")
        assert response.status_code == 400
        assert response.data["error"] == "Invalid wallet address format"

    @patch("blockchain_api.views.Web3")
    def test_login_wallet_success(self, mock_web3_class):
        client = self.client
        address = "0x1111111111111111111111111111111111111111"

        # Configuramos el mock de Web3
        mock_web3 = MagicMock()
        mock_web3.eth.account.recover_message.return_value = address
        mock_web3_class.return_value = mock_web3
        mock_web3_class.is_address.return_value = True

        payload = {
            "address": address,
            "signature": "0xFAKE_SIGNATURE",
            "nonce": "TinderFiestas_987654321",
        }

        response = client.post(self.url, payload, format="json")

        assert response.status_code == 200
        assert response.data["status"] == "success"
        assert response.data["user"]["wallet_address"] == address

        # Usuario creado en BD
        assert UserProfile.objects.filter(wallet_address=address).exists()

    @patch("blockchain_api.views.Web3")
    def test_login_wallet_invalid_signature(self, mock_web3_class):
        client = self.client
        address = "0x1111111111111111111111111111111111111111"

        mock_web3 = MagicMock()
        # Fuerza a devolver otra address para que falle la comparación
        mock_web3.eth.account.recover_message.return_value = (
            "0x2222222222222222222222222222222222222222"
        )
        mock_web3_class.return_value = mock_web3
        mock_web3_class.is_address.return_value = True

        payload = {
            "address": address,
            "signature": "0xFAKE_SIGNATURE",
            "nonce": "TinderFiestas_123",
        }

        response = client.post(self.url, payload, format="json")

        assert response.status_code == 401
        assert "Signature verification failed" in response.data["error"]
