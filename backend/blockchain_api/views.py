from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from web3 import Web3
import uuid
from eth_account.messages import encode_defunct
from .services.auth_service import verify_signature

from .blockchain_service import get_last_location, check_in
from .analytics_service import get_heatmap_data, get_activity_stats
from .models import (
    UserProfile,
    CheckIn,
    Event,
    EventAttendance
)
from .serializers import EventSerializer


# ✅ GET: obtener última ubicación de un usuario
@api_view(["GET"])
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


# ✅ POST: registrar un nuevo check-in (geolocalización general)
@api_view(["POST"])
def register_checkin(request):
    """
    Registra un check-in general (no asociado a un evento).
    Guarda tanto en blockchain como en la base de datos local.
    """
    location = request.data.get("location")
    private_key = request.data.get("private_key")

    if not location or not private_key:
        return Response({"status": "error", "message": "Parámetros inválidos"}, status=400)

    # 🔗 Intentar registro en blockchain
    tx_hash = check_in(location, private_key)
    if not tx_hash:
        return Response({"status": "error", "message": "No se pudo registrar en blockchain"}, status=500)

    # 🧩 Obtener dirección del usuario
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    user_address = w3.eth.account.from_key(private_key).address

    # 👤 Crear o actualizar perfil local
    user, _ = UserProfile.objects.get_or_create(wallet_address=user_address)

    # 🗺️ Registrar check-in local
    CheckIn.objects.create(user=user, location=location, tx_hash=tx_hash)

    return Response({
        "status": "success",
        "mensaje": f"Check-in registrado en blockchain y base local: {location}",
        "tx_hash": tx_hash
    })


# ✅ GET: puntos de calor
@api_view(["GET"])
def heatmap_data(request):
    """
    Endpoint: /api/heatmap/
    Retorna los puntos de calor agrupados por coordenadas.
    """
    data = get_heatmap_data()
    return Response(data)


# ✅ GET: estadísticas de actividad
@api_view(["GET"])
def activity_stats(request):
    """
    Endpoint: /api/stats/
    Retorna estadísticas de actividad (check-ins, usuarios, top lugares).
    """
    days = int(request.GET.get("days", 7))
    stats = get_activity_stats(days=days)
    return Response(stats)


# ✅ GET / POST: eventos
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


# ✅ GET: mapa combinado (eventos + check-ins)
@api_view(["GET"])
def mapa_completo(request):
    """
    Devuelve datos combinados:
    - Eventos (marcadores)
    - Check-ins (puntos de calor)
    """
    eventos = Event.objects.all()
    eventos_data = EventSerializer(eventos, many=True).data

    checkins = CheckIn.objects.filter(latitude__isnull=False, longitude__isnull=False)
    checkins_data = [
        {"latitude": c.latitude, "longitude": c.longitude, "count": 1}
        for c in checkins
    ]

    return Response({
        "eventos": eventos_data,
        "checkins": checkins_data
    })


# ✅ POST: registrar asistencia a un evento
@api_view(["POST"])
def event_checkin(request):
    """
    Registra la asistencia de un usuario (wallet) a un evento.
    Si no hay fondos en la wallet, simula el tx_hash para permitir el registro local.
    """
    event_id = request.data.get("event_id")
    wallet_address = request.data.get("wallet_address")

    if not event_id or not wallet_address:
        return Response({"status": "error", "message": "Faltan parámetros"}, status=400)

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"status": "error", "message": "Evento no encontrado"}, status=404)

    # 👤 Crear o recuperar usuario local
    user, _ = UserProfile.objects.get_or_create(wallet_address=wallet_address)

    # 🚫 Evitar asistencia duplicada
    if EventAttendance.objects.filter(user=user, event=event).exists():
        return Response({
            "status": "error",
            "message": "El usuario ya asistió a este evento"
        }, status=400)

    # ⚙️ Simular TX hash (sin necesidad de firmar)
    tx_hash = f"SIMULATED_TX_{uuid.uuid4().hex[:10]}"

    # 💾 Guardar asistencia local
    EventAttendance.objects.create(
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


# ✅ POST: autenticación mediante MetaMask
@api_view(["POST"])
def login_wallet(request):
    """
    Autentica un usuario mediante firma con MetaMask.
    Recibe: { "address": "0x...", "signature": "...", "nonce": "..." }
    """
    try:
        data = request.data
        address = data.get("address")
        signature = data.get("signature")
        nonce = data.get("nonce")

        if not all([address, signature, nonce]):
            return Response(
                {"status": "error", "message": "Faltan parámetros"},
                status=400
            )

        # ✅ Crear objeto mensaje firmado (según formato EIP-191)
        message = encode_defunct(text=nonce)

        # ✅ Verificar firma usando Web3.py
        w3 = Web3()
        recovered_address = w3.eth.account.recover_message(
            message,
            signature=signature
        )

        if recovered_address.lower() != address.lower():
            return Response(
                {"status": "error", "message": "Firma inválida"},
                status=401
            )

        # ✅ Crear o recuperar usuario local
        user, created = UserProfile.objects.get_or_create(wallet_address=address)

        return Response({
            "status": "success",
            "message": "Wallet autenticada correctamente",
            "user": {
                "wallet_address": user.wallet_address,
                "created": created
            }
        })

    except Exception as e:
        print(f"⚠️ Error en autenticación: {e}")
        return Response(
            {"status": "error", "message": str(e)},
            status=500
        )
