"""
views.py
API endpoints para la aplicación Tinder de Fiestas.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from web3 import Web3
from eth_account.messages import encode_defunct

from .blockchain_service import (
    get_user_checkins,
    verify_event_checkin_tx,
    get_contract_info,
    is_blockchain_connected,
    get_last_checkin
)
from .analytics_service import get_heatmap_data, get_activity_stats
from .models import UserProfile, CheckIn, Event, EventAttendance
from .serializers import EventSerializer


# ============================================
# BLOCKCHAIN INFO
# ============================================

@api_view(["GET"])
def blockchain_info(request):
    """
    Retorna información del estado de la blockchain.
    Útil para debugging.
    """
    info = get_contract_info()
    return Response({
        "status": "success",
        "blockchain": info
    })


# ============================================
# USER ENDPOINTS
# ============================================

@api_view(["GET"])
def get_user_checkins_view(request, address):
    """
    GET /api/checkins/<address>/
    Obtiene todos los check-ins de un usuario desde blockchain.
    """

    if not Web3.is_address(address):
        return Response({"error": "Invalid wallet address format"}, status=400)

    try:
        checkins = get_user_checkins(address)

        for checkin in checkins:
            try:
                event = Event.objects.get(id=checkin["eventId"])
                checkin["event_name"] = event.name
                checkin["event_description"] = event.description
                checkin["event_location"] = event.location
            except Event.DoesNotExist:
                checkin["event_name"] = f"Event #{checkin['eventId']}"

        return Response({
            "status": "success",
            "wallet_address": address,
            "total_checkins": len(checkins),
            "checkins": checkins
        })

    except Exception as e:
        return Response({"error": f"Error fetching check-ins: {str(e)}"}, status=500)


@api_view(["POST"])
def login_wallet(request):
    """
    POST /api/login_wallet/
    Autentica mediante firma de MetaMask.
    """

    try:
        address = request.data.get("address")
        signature = request.data.get("signature")
        nonce = request.data.get("nonce")

        if not all([address, signature, nonce]):
            return Response({"error": "Missing required parameters"}, status=400)

        if not Web3.is_address(address):
            return Response({"error": "Invalid wallet address format"}, status=400)

        message = encode_defunct(text=nonce)
        w3 = Web3()

        try:
            recovered = w3.eth.account.recover_message(message, signature=signature)
        except Exception as e:
            return Response({"error": f"Invalid signature: {str(e)}"}, status=401)

        if recovered.lower() != address.lower():
            return Response({"error": "Signature verification failed"}, status=401)

        user, created = UserProfile.objects.get_or_create(wallet_address=address)

        return Response({
            "status": "success",
            "message": "Wallet authenticated successfully",
            "user": {
                "wallet_address": user.wallet_address,
                "username": user.username,
                "created": created,
                "total_checkins": user.checkins.count()
            }
        })

    except Exception as e:
        return Response({"error": f"Authentication error: {str(e)}"}, status=500)


# ============================================
# EVENT ENDPOINTS
# ============================================

@api_view(["GET", "POST"])
def events_view(request):
    """
    GET → Lista todos los eventos (solo array)
    POST → Crea evento
    """

    if request.method == "GET":
        eventos = Event.objects.all().order_by("-start_date")
        serializer = EventSerializer(eventos, many=True)
        return Response(serializer.data)  # SOLO EL ARRAY ✔

    elif request.method == "POST":
        serializer = EventSerializer(data=request.data)

        if serializer.is_valid():
            event = serializer.save()
            return Response({
                "status": "success",
                "message": "Event created successfully",
                "event": EventSerializer(event).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "error": "Invalid event data",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def event_checkin(request):
    """
    POST /api/event_checkin/
    Registra asistencia verificando TX en blockchain.
    """

    event_id = request.data.get("event_id")
    wallet_address = request.data.get("wallet_address")
    tx_hash = request.data.get("tx_hash")

    if not all([event_id, wallet_address, tx_hash]):
        return Response({"error": "Missing required parameters"}, status=400)

    if not Web3.is_address(wallet_address):
        return Response({"error": "Invalid wallet address format"}, status=400)

    if not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return Response({"error": "Invalid transaction hash format"}, status=400)

    try:
        event_id = int(event_id)
        if event_id <= 0:
            raise ValueError()
    except:
        return Response({"error": "Invalid event ID"}, status=400)

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=404)

    user, created_user = UserProfile.objects.get_or_create(wallet_address=wallet_address)

    if EventAttendance.objects.filter(tx_hash=tx_hash).exists():
        return Response({"error": "This transaction has already been recorded"}, status=400)

    if EventAttendance.objects.filter(user=user, event=event).exists():
        return Response({"error": "User has already checked in to this event"}, status=400)

    try:
        blockchain_data = verify_event_checkin_tx(
            tx_hash=tx_hash,
            wallet_address=wallet_address,
            event_id=event_id
        )
    except Exception as e:
        return Response({"error": f"Blockchain verification failed: {str(e)}"}, status=400)

    attendance = EventAttendance.objects.create(
        user=user,
        event=event,
        tx_hash=tx_hash
    )

    CheckIn.objects.create(
        user=user,
        location=event.location,
        latitude=event.latitude,
        longitude=event.longitude,
        tx_hash=tx_hash
    )

    return Response({
        "status": "success",
        "message": f"Check-in verified and registered for {event.name}",
        "attendance_id": attendance.id,
        "event": EventSerializer(event).data,
        "blockchain": blockchain_data,
        "user": {
            "wallet_address": user.wallet_address,
            "new_user": created_user,
            "total_checkins": user.checkins.count()
        }
    }, status=201)


# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@api_view(["GET"])
def heatmap_data(request):
    """
    GET /api/heatmap/
    Devuelve SOLO EL ARRAY ✔
    """
    try:
        data = get_heatmap_data()
        return Response(data)  # SOLO EL ARRAY ✔
    except Exception as e:
        return Response({"error": f"Error fetching heatmap data: {str(e)}"}, status=500)


@api_view(["GET"])
def activity_stats(request):
    """
    GET /api/stats/
    """

    try:
        days = int(request.GET.get("days", 7))

        if days <= 0:
            return Response({"error": "Days must be positive"}, status=400)

        stats = get_activity_stats(days=days)

        return Response({
            "status": "success",
            "period_days": days,
            **stats
        })

    except ValueError:
        return Response({"error": "Invalid days parameter"}, status=400)
    except Exception as e:
        return Response({"error": f"Error fetching stats: {str(e)}"}, status=500)


@api_view(["GET"])
def mapa_completo(request):
    """
    GET /api/mapa/
    Combina eventos + check-ins
    """

    try:
        eventos = Event.objects.all()
        eventos_data = EventSerializer(eventos, many=True).data

        checkins = CheckIn.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        )

        checkins_data = [
            {
                "latitude": c.latitude,
                "longitude": c.longitude,
                "count": 1,
                "location": c.location
            }
            for c in checkins
        ]

        return Response({
            "status": "success",
            "total_events": len(eventos_data),
            "total_checkins": len(checkins_data),
            "eventos": eventos_data,
            "checkins": checkins_data
        })

    except Exception as e:
        return Response({"error": f"Error fetching map data: {str(e)}"}, status=500)


# ============================================
# HEALTH CHECK
# ============================================

@api_view(["GET"])
def health_check(request):
    """
    GET /api/health/
    """

    blockchain_status = "connected" if is_blockchain_connected() else "disconnected"

    try:
        Event.objects.count()
        db_status = "connected"
    except:
        db_status = "disconnected"

    overall_status = "healthy" if (
        blockchain_status == "connected" and db_status == "connected"
    ) else "degraded"

    return Response({
        "status": overall_status,
        "blockchain": blockchain_status,
        "database": db_status,
        "contract_info": get_contract_info()
    })
