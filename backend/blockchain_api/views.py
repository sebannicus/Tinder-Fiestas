from rest_framework.decorators import api_view
from rest_framework.response import Response
from .blockchain_service import get_last_location, check_in

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
@api_view(['POST'])
def registrar_checkin(request):
    """
    Registra una nueva ubicación en blockchain mediante una transacción firmada.
    """
    try:
        data = request.data
        location = data.get("location")
        private_key = data.get("private_key")

        if not location or not private_key:
            return Response({"status": "error", "message": "Faltan parámetros."}, status=400)

        tx_hash = check_in(location, private_key)

        return Response({
            "status": "success",
            "mensaje": f"Check-in registrado en blockchain: {location}",
            "tx_hash": tx_hash
        })
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)
