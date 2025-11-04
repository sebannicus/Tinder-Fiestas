from rest_framework.decorators import api_view
from rest_framework.response import Response
from .blockchain_service import get_last_location, check_in
from .models import UserProfile, CheckIn
from .analytics_service import get_heatmap_data, get_activity_stats
from django.http import JsonResponse
from .models import Event, CheckIn
from .serializers import EventSerializer
from rest_framework import status

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

@api_view(["GET", "POST"])
def events_view(request):
    """
    GET → lista todos los eventos
    POST → crea un nuevo evento
    """
    if request.method == "GET":
        eventos = Event.objects.all().order_by("-start_date")
        serializer = EventSerializer(eventos, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "evento": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def mapa_completo(request):
    """
    Devuelve datos combinados:
    - Eventos (marcadores)
    - Check-ins (puntos de calor)
    """
    from .models import Event, CheckIn
    from .serializers import EventSerializer

    # Eventos
    eventos = Event.objects.all()
    eventos_data = EventSerializer(eventos, many=True).data

    # Check-ins (solo los que tienen coordenadas)
    checkins = CheckIn.objects.filter(latitude__isnull=False, longitude__isnull=False)
    checkins_data = [
        {"latitude": c.latitude, "longitude": c.longitude, "count": 1}
        for c in checkins
    ]

    return Response({
        "eventos": eventos_data,
        "checkins": checkins_data
    })

@api_view(["POST"])
def event_checkin(request):
    """
    Registra la asistencia de un usuario (wallet) a un evento.
    Si no hay fondos en la wallet, se registra igual con tx_hash simulado.
    """
    event_id = request.data.get("event_id")
    private_key = request.data.get("private_key")

    if not event_id or not private_key:
        return Response({"status": "error", "message": "Faltan parámetros"}, status=400)

    from web3 import Web3
    from .blockchain_service import check_in
    from .models import Event, EventAttendance, UserProfile
    import uuid

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"status": "error", "message": "Evento no encontrado"}, status=404)

    # Conectar al nodo local
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    user_address = w3.eth.account.from_key(private_key).address

    # Crear o recuperar usuario
    user, _ = UserProfile.objects.get_or_create(wallet_address=user_address)

    # Intentar registrar en blockchain
    tx_hash = None
    try:
        tx_hash = check_in(event.location, private_key)
    except Exception as e:
        print(f"⚠️ Error en blockchain: {e}")
        # Simulación local si no hay fondos
        tx_hash = f"SIMULATED_TX_{uuid.uuid4().hex[:10]}"

    # Guardar asistencia en base local
    asistencia = EventAttendance.objects.create(
        user=user,
        event=event,
        tx_hash=tx_hash
    )

    return Response({
        "status": "success",
        "message": f"Asistencia registrada para {event.name}",
        "tx_hash": tx_hash,
        "wallet": user.wallet_address
    })
