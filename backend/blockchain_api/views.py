from rest_framework.decorators import api_view
from rest_framework.response import Response
from .blockchain_service import get_last_location, check_in

@api_view(['GET'])
def obtener_ubicacion(request, address):
    ubicacion = get_last_location(address)
    return Response({"address": address, "ultima_ubicacion": ubicacion})

@api_view(['POST'])
def registrar_checkin(request):
    data = request.data
    location = data.get("location")
    private_key = data.get("private_key")
    tx_hash = check_in(location, private_key)
    return Response({"status": "success", "tx_hash": tx_hash})
