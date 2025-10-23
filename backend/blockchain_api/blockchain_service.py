from web3 import Web3
import json, os
from dotenv import load_dotenv

load_dotenv()

# Cargar variables del entorno
RPC_URL = os.getenv("RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Conexión a la red local Hardhat
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Cargar ABI
with open("../blockchain/artifacts/contracts/ProofOfPresence.sol/ProofOfPresence.json") as f:
    contract_json = json.load(f)
    abi = contract_json["abi"]

# Crear instancia del contrato
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# Función: leer última ubicación de un usuario
def get_last_location(user_address):
    return contract.functions.getLastLocation(user_address).call()

# Función: registrar una nueva ubicación
def check_in(location, private_key):
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    txn = contract.functions.checkIn(location).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 3000000,
        'gasPrice': w3.to_wei('5', 'gwei')
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return tx_hash.hex()
