from rest_framework.decorators import api_view
from rest_framework.response import Response
from .blockchain_service import get_last_location, check_in
from django.http import JsonResponse
from .models import CheckIn

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

def heatmap_view(request):
    """
    Devuelve los puntos de calor (latitud, longitud, count)
    agrupados por ubicación.
    """
    # Filtrar registros válidos (con coordenadas)
    checkins = CheckIn.objects.filter(latitude__isnull=False, longitude__isnull=False)

    # Agrupar por coordenadas y contar cuántos check-ins hay por punto
    data = {}
    for c in checkins:
        key = (c.latitude, c.longitude)
        if key in data:
            data[key] += 1
        else:
            data[key] = 1

    # Convertir a formato JSON
    response = [
        {"latitude": lat, "longitude": lon, "count": count}
        for (lat, lon), count in data.items()
    ]

    return JsonResponse(response, safe=False)
