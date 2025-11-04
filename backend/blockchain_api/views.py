from rest_framework.decorators import api_view
from rest_framework.response import Response
from .blockchain_service import get_last_location, check_in
from .models import UserProfile, CheckIn
from .analytics_service import get_heatmap_data, get_activity_stats
from django.http import JsonResponse
from .models import CheckIn

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

    checkin = CheckIn.objects.create(
                user_id=user_id,
                location=location,
                tx_hash=tx_hash,
            )   
    return Response({
        "status": "success",
        "mensaje": f"Check-in registrado en blockchain y base local: {location}",
        "tx_hash": tx_hash
    })

@api_view(["GET"])
def heatmap_data(request):
    """
    Endpoint: /api/heatmap/
    Retorna los puntos de calor agrupados por coordenadas.
    """
    data = get_heatmap_data()
    return Response(data)


@api_view(["GET"])
def activity_stats(request):
    """
    Endpoint: /api/stats/
    Retorna estadísticas de actividad (check-ins, usuarios, top lugares).
    """
    days = int(request.GET.get("days", 7))
    stats = get_activity_stats(days=days)
    return Response(stats)
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
