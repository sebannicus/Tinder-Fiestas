from eth_account.messages import encode_defunct
from web3 import Web3

def verify_signature(address: str, signature: str, nonce: str) -> bool:
    """
    Verifica si la firma de MetaMask corresponde al address indicado.
    """
    try:
        message = encode_defunct(text=nonce)
        recovered_address = Web3().eth.account.recover_message(message, signature=signature)
        return recovered_address.lower() == address.lower()
    except Exception as e:
        print("❌ Error verificando firma:", e)
        return False
