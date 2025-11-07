from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
print(f"🔗 Conectando a RPC_URL: {RPC_URL}")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

contract_json_path = os.path.join(
    os.path.dirname(__file__),
    "../../blockchain/deployed/ProofOfPresence.json"
)

print(f"📄 Cargando contrato desde: {contract_json_path}")

with open(contract_json_path, "r") as f:
    contract_data = json.load(f)
    CONTRACT_ADDRESS = contract_data["address"]
    CONTRACT_ABI = contract_data["abi"]

print(f"✅ Contrato cargado: {CONTRACT_ADDRESS}")

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)


def get_last_location(user_address):
    try:
        print(f"📍 Obteniendo ubicación para {user_address}")
        result = contract.functions.getLastLocation(user_address).call()
        print(f"✅ Última ubicación: {result}")
        return result
    except Exception as e:
        print(f"⚠️ Error al obtener ubicación: {e}")
        return None

def check_in(location, private_key):
    try:
        print(f"🚀 Iniciando check-in en blockchain: {location}")
        account = w3.eth.account.from_key(private_key)
        nonce = w3.eth.get_transaction_count(account.address)
        print(f"👤 Usando cuenta: {account.address}, nonce: {nonce}")

        txn = contract.functions.checkIn(location).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 3000000,
            "gasPrice": w3.to_wei("5", "gwei"),
        })

        print("✍️ Firmando transacción...")
        signed_txn = w3.eth.account.sign_transaction(txn, private_key)

        # ✅ Usa directamente el campo correcto
        raw_tx = signed_txn.raw_transaction

        print("📤 Enviando transacción...")
        tx_hash = w3.eth.send_raw_transaction(raw_tx)

        print(f"✅ Transacción enviada: {tx_hash.hex()}")
        return tx_hash.hex()


    except Exception as e:
        print(f"⚠️ Error al registrar ubicación: {e}")
        return None
