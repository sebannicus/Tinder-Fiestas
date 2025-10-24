from rest_framework.decorators import api_view
from rest_framework.response import Response
from .blockchain_service import get_last_location, check_in
from .models import UserProfile, CheckIn

# ✅ GET: obtener última ubicación
@api_view(['GET'])
def obtener_ubicacion(request, address):
    """
    Devuelve la última ubicación registrada en blockchain para una dirección dada.
    """
    try:
        ubicacion = get_last_location(address)
        return Response({
            "status": "success",
            "address": address,
            "ultima_ubicacion": ubicacion
        })
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)


# ✅ POST: registrar nueva ubicación
@api_view(["POST"])
def register_checkin(request):
    location = request.data.get("location")
    private_key = request.data.get("private_key")

    if not location or not private_key:
        return Response({"status": "error", "message": "Parámetros inválidos"}, status=400)

    tx_hash = check_in(location, private_key)
    if not tx_hash:
        return Response({"status": "error", "message": "No se pudo registrar en blockchain"}, status=500)

    # Obtener dirección del usuario a partir de la clave
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    user_address = w3.eth.account.from_key(private_key).address

    # Crear o actualizar usuario local
    user, _ = UserProfile.objects.get_or_create(wallet_address=user_address)

    # Registrar check-in local
    CheckIn.objects.create(user=user, location=location, tx_hash=tx_hash)

    return Response({
        "status": "success",
        "mensaje": f"Check-in registrado en blockchain y base local: {location}",
        "tx_hash": tx_hash
    })