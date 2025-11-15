"""
blockchain_service.py
Servicio para interactuar con el smart contract ProofOfPresence.
Solo lectura y verificación de transacciones - NO firma transacciones.
"""

from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de conexión
RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
print(f"🔗 Conectando a RPC_URL: {RPC_URL}")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Cargar el contrato
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


# ============================================
# FUNCIONES DE LECTURA
# ============================================

def get_user_checkins(user_address: str) -> list:
    """
    Obtiene todos los check-ins de un usuario desde blockchain.
    
    Args:
        user_address: Dirección de wallet del usuario
        
    Returns:
        Lista de check-ins con formato:
        [
            {
                "user": "0x...",
                "location": "Santiago, Chile",
                "timestamp": 1234567890,
                "eventId": 1
            }
        ]
    """
    try:
        if not Web3.is_address(user_address):
            print(f"⚠️ Dirección inválida: {user_address}")
            return []
        
        checkins_raw = contract.functions.getUserCheckIns(user_address).call()
        
        # Convertir tuplas a diccionarios
        checkins = []
        for checkin in checkins_raw:
            checkins.append({
                "user": checkin[0],
                "location": checkin[1],
                "timestamp": int(checkin[2]),
                "eventId": int(checkin[3])
            })
        
        return checkins
        
    except Exception as e:
        print(f"⚠️ Error obteniendo check-ins: {e}")
        return []


def get_last_checkin(user_address: str) -> dict:
    """
    Obtiene el último check-in de un usuario.
    
    Returns:
        Dict con el último check-in o None si no hay check-ins
    """
    try:
        checkins = get_user_checkins(user_address)
        if checkins:
            return checkins[-1]
        return None
    except Exception as e:
        print(f"⚠️ Error obteniendo último check-in: {e}")
        return None


def has_user_checked_in(wallet_address: str, event_id: int) -> bool:
    """
    Verifica si un usuario ya hizo check-in a un evento específico.
    
    Args:
        wallet_address: Dirección de wallet del usuario
        event_id: ID del evento
        
    Returns:
        True si ya hizo check-in, False en caso contrario
    """
    try:
        return contract.functions.hasUserCheckedIn(wallet_address, event_id).call()
    except Exception as e:
        print(f"⚠️ Error verificando check-in: {e}")
        return False


def get_event_stats(event_id: int) -> dict:
    """
    Obtiene estadísticas de un evento desde blockchain.
    
    Returns:
        {
            "totalCheckIns": int,
            "uniqueUsers": int,
            "exists": bool
        }
    """
    try:
        stats = contract.functions.getEventStats(event_id).call()
        return {
            "totalCheckIns": int(stats[0]),
            "uniqueUsers": int(stats[1]),
            "exists": bool(stats[2])
        }
    except Exception as e:
        print(f"⚠️ Error obteniendo estadísticas: {e}")
        return {"totalCheckIns": 0, "uniqueUsers": 0, "exists": False}


# ============================================
# VERIFICACIÓN DE TRANSACCIONES
# ============================================

def verify_transaction(tx_hash: str, expected_wallet: str, expected_event_id: int = None) -> dict:
    """
    Verifica que una transacción sea válida y corresponda al check-in esperado.
    
    Validaciones:
    1. Formato del hash correcto
    2. Transacción existe en blockchain
    3. Transacción fue exitosa (status = 1)
    4. Se envió al contrato correcto
    5. El remitente coincide con el esperado
    6. (Opcional) El eventId coincide
    
    Args:
        tx_hash: Hash de la transacción (0x...)
        expected_wallet: Dirección esperada del usuario
        expected_event_id: ID del evento esperado (opcional)
        
    Returns:
        {
            "valid": bool,
            "error": str (si valid=False),
            "tx_hash": str,
            "from": str,
            "block_number": int,
            "gas_used": int,
            "timestamp": int
        }
    """
    try:
        # 1. Validar formato del hash
        if not tx_hash or not isinstance(tx_hash, str):
            return {"valid": False, "error": "Transaction hash is required"}
        
        if not tx_hash.startswith('0x'):
            return {"valid": False, "error": "Transaction hash must start with 0x"}
        
        if len(tx_hash) != 66:
            return {"valid": False, "error": "Transaction hash must be 66 characters"}
        
        # Verificar que sea hexadecimal
        try:
            int(tx_hash, 16)
        except ValueError:
            return {"valid": False, "error": "Transaction hash must be hexadecimal"}
        
        # 2. Obtener receipt de la transacción
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
        except Exception:
            return {"valid": False, "error": "Transaction not found in blockchain"}
        
        if not receipt:
            return {"valid": False, "error": "Transaction receipt is null"}
        
        # 3. Verificar que fue exitosa
        if receipt.status != 1:
            return {"valid": False, "error": "Transaction failed on blockchain (status != 1)"}
        
        # 4. Verificar que se hizo al contrato correcto
        if not receipt.to or receipt.to.lower() != CONTRACT_ADDRESS.lower():
            return {
                "valid": False,
                "error": f"Transaction not sent to correct contract. Expected: {CONTRACT_ADDRESS}, Got: {receipt.to}"
            }
        
        # 5. Obtener la transacción para verificar el sender
        tx = w3.eth.get_transaction(tx_hash)
        
        if not tx:
            return {"valid": False, "error": "Transaction data not found"}
        
        if tx['from'].lower() != expected_wallet.lower():
            return {
                "valid": False,
                "error": f"Transaction sender doesn't match. Expected: {expected_wallet}, Got: {tx['from']}"
            }
        
        # 6. (Opcional) Verificar el eventId en los logs
        if expected_event_id is not None:
            try:
                logs = contract.events.EventCheckedIn().process_receipt(receipt)
                
                if not logs:
                    return {"valid": False, "error": "Transaction did not emit EventCheckedIn event"}
                
                event_found = False
                for log in logs:
                    if log['args']['eventId'] == expected_event_id:
                        event_found = True
                        break
                
                if not event_found:
                    return {
                        "valid": False,
                        "error": f"Transaction doesn't contain check-in for event {expected_event_id}"
                    }
            except Exception as e:
                return {"valid": False, "error": f"Error processing event logs: {str(e)}"}
        
        # 7. Obtener timestamp del bloque
        block = w3.eth.get_block(receipt.blockNumber)
        
        # ✅ Todo OK
        return {
            "valid": True,
            "tx_hash": tx_hash,
            "from": tx['from'],
            "to": receipt.to,
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
            "timestamp": block.timestamp
        }
        
    except Exception as e:
        return {"valid": False, "error": f"Verification error: {str(e)}"}


def verify_event_checkin_tx(tx_hash: str, wallet_address: str, event_id: int) -> dict:
    """
    Función específica para verificar check-ins a eventos.
    Wrapper de verify_transaction con validaciones adicionales.
    
    Returns:
        Dict con datos del evento si es válido, raise Exception si no
    """
    # Validar formato de wallet
    if not Web3.is_address(wallet_address):
        raise ValueError("Invalid wallet address format")
    
    # Validar event_id
    try:
        event_id = int(event_id)
        if event_id <= 0:
            raise ValueError("Event ID must be positive")
    except (ValueError, TypeError):
        raise ValueError("Invalid event ID")
    
    # Verificar la transacción
    result = verify_transaction(tx_hash, wallet_address, event_id)
    
    if not result["valid"]:
        raise ValueError(result["error"])
    
    # Obtener datos del evento desde los logs
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        logs = contract.events.EventCheckedIn().process_receipt(receipt)
        
        if logs:
            event_data = logs[0]["args"]
            return {
                "user": event_data["user"],
                "eventId": int(event_data["eventId"]),
                "location": event_data["location"],
                "timestamp": int(event_data["timestamp"]),
                "block_number": result["block_number"],
                "tx_hash": tx_hash
            }
        else:
            raise ValueError("No event data found in transaction")
            
    except Exception as e:
        raise ValueError(f"Error extracting event data: {str(e)}")


# ============================================
# UTILIDADES
# ============================================

def is_blockchain_connected() -> bool:
    """
    Verifica si hay conexión con el nodo de blockchain.
    """
    try:
        return w3.is_connected()
    except Exception:
        return False


def get_block_number() -> int:
    """
    Obtiene el número del último bloque.
    """
    try:
        return w3.eth.block_number
    except Exception as e:
        print(f"⚠️ Error obteniendo block number: {e}")
        return 0


def get_contract_info() -> dict:
    """
    Retorna información del contrato.
    """
    return {
        "address": CONTRACT_ADDRESS,
        "rpc_url": RPC_URL,
        "connected": is_blockchain_connected(),
        "block_number": get_block_number()
    }


# ============================================
# INICIALIZACIÓN
# ============================================

# Verificar conexión al iniciar
if is_blockchain_connected():
    print(f"✅ Conectado a blockchain - Bloque: {get_block_number()}")
else:
    print("⚠️ No se pudo conectar a blockchain")