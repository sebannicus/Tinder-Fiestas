"""
validators.py
Funciones de validación para datos de entrada.
"""

from web3 import Web3


def validate_wallet_address(address: str) -> tuple[bool, str]:
    """
    Valida formato de dirección Ethereum.
    
    Args:
        address: Dirección de wallet a validar
        
    Returns:
        (is_valid, error_message)
        
    Examples:
        >>> validate_wallet_address("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
        (True, "")
        
        >>> validate_wallet_address("invalid")
        (False, "Invalid Ethereum address format")
    """
    if not address:
        return False, "Wallet address is required"
    
    if not isinstance(address, str):
        return False, "Wallet address must be a string"
    
    if not Web3.is_address(address):
        return False, "Invalid Ethereum address format"
    
    return True, ""


def validate_tx_hash(tx_hash: str) -> tuple[bool, str]:
    """
    Valida formato de transaction hash.
    
    Args:
        tx_hash: Hash de transacción (0x...)
        
    Returns:
        (is_valid, error_message)
        
    Examples:
        >>> validate_tx_hash("0x" + "a" * 64)
        (True, "")
        
        >>> validate_tx_hash("0xabcd")
        (False, "Transaction hash must be 66 characters long")
    """
    if not tx_hash:
        return False, "Transaction hash is required"
    
    if not isinstance(tx_hash, str):
        return False, "Transaction hash must be a string"
    
    if not tx_hash.startswith('0x'):
        return False, "Transaction hash must start with 0x"
    
    if len(tx_hash) != 66:  # 0x + 64 caracteres hex
        return False, "Transaction hash must be 66 characters long"
    
    # Verificar que sea hexadecimal
    try:
        int(tx_hash, 16)
    except ValueError:
        return False, "Transaction hash must be hexadecimal"
    
    return True, ""


def validate_event_id(event_id: any) -> tuple[bool, str]:
    """
    Valida formato de event ID.
    
    Args:
        event_id: ID del evento
        
    Returns:
        (is_valid, error_message)
        
    Examples:
        >>> validate_event_id(1)
        (True, "")
        
        >>> validate_event_id("1")
        (True, "")
        
        >>> validate_event_id(-1)
        (False, "Event ID must be positive")
    """
    if event_id is None:
        return False, "Event ID is required"
    
    try:
        event_id_int = int(event_id)
        if event_id_int <= 0:
            return False, "Event ID must be positive"
    except (ValueError, TypeError):
        return False, "Event ID must be a number"
    
    return True, ""


def validate_coordinates(latitude: float, longitude: float) -> tuple[bool, str]:
    """
    Valida coordenadas geográficas.
    
    Args:
        latitude: Latitud (-90 a 90)
        longitude: Longitud (-180 a 180)
        
    Returns:
        (is_valid, error_message)
        
    Examples:
        >>> validate_coordinates(-33.4489, -70.6693)
        (True, "")
        
        >>> validate_coordinates(100, 0)
        (False, "Latitude must be between -90 and 90")
    """
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90"
        
        if not (-180 <= lng <= 180):
            return False, "Longitude must be between -180 and 180"
        
        return True, ""
        
    except (ValueError, TypeError):
        return False, "Coordinates must be numbers"


def validate_signature(signature: str) -> tuple[bool, str]:
    """
    Valida formato de firma de MetaMask.
    
    Args:
        signature: Firma en formato hexadecimal
        
    Returns:
        (is_valid, error_message)
    """
    if not signature:
        return False, "Signature is required"
    
    if not isinstance(signature, str):
        return False, "Signature must be a string"
    
    if not signature.startswith('0x'):
        return False, "Signature must start with 0x"
    
    # Las firmas típicamente tienen 132 caracteres (0x + 130)
    if len(signature) != 132:
        return False, "Invalid signature length"
    
    try:
        int(signature, 16)
    except ValueError:
        return False, "Signature must be hexadecimal"
    
    return True, ""


def validate_location_string(location: str, max_length: int = 255) -> tuple[bool, str]:
    """
    Valida string de ubicación.
    
    Args:
        location: Nombre de ubicación
        max_length: Longitud máxima permitida
        
    Returns:
        (is_valid, error_message)
    """
    if not location:
        return False, "Location is required"
    
    if not isinstance(location, str):
        return False, "Location must be a string"
    
    location = location.strip()
    
    if len(location) == 0:
        return False, "Location cannot be empty"
    
    if len(location) > max_length:
        return False, f"Location must be less than {max_length} characters"
    
    return True, ""