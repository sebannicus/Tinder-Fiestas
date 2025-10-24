from web3 import Web3
import json
import os
from dotenv import load_dotenv

# Cargar variables del entorno (.env)
load_dotenv()

# URL del nodo Hardhat (local por defecto)
RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Ruta al archivo JSON generado automáticamente por Hardhat
contract_json_path = os.path.join(
    os.path.dirname(__file__),
    "../../blockchain/deployed/ProofOfPresence.json"
)

# Cargar dirección y ABI del contrato desde el JSON
with open(contract_json_path, "r") as f:
    contract_data = json.load(f)
    CONTRACT_ADDRESS = contract_data["address"]
    CONTRACT_ABI = contract_data["abi"]

# Crear instancia del contrato inteligente
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# 🧩 Función: leer última ubicación de un usuario
def get_last_location(user_address):
    try:
        return contract.functions.getLastLocation(user_address).call()
    except Exception as e:
        print(f"⚠️ Error al obtener ubicación: {e}")
        return None

# 🧩 Función: registrar una nueva ubicación en blockchain
def check_in(location, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        nonce = w3.eth.get_transaction_count(account.address)

        txn = contract.functions.checkIn(location).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 3000000,
            'gasPrice': w3.to_wei('5', 'gwei')
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return tx_hash.hex()

    except Exception as e:
        print(f"⚠️ Error al registrar ubicación: {e}")
        return None
