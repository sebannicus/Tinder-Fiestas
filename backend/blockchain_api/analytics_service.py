from django.db.models import Count
from .models import CheckIn
from datetime import datetime, timedelta

# 🧠 Servicio de analítica: obtiene la densidad de check-ins por ubicación
def get_heatmap_data():
    """
    Retorna solo check-ins con coordenadas válidas para el mapa de calor.
    """
    data = (
        CheckIn.objects
        .filter(latitude__isnull=False, longitude__isnull=False)
        .values("latitude", "longitude")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    return list(data)


# 📈 Servicio de analítica: obtiene estadísticas generales
def get_activity_stats(days=7):
    """
    Retorna estadísticas generales de actividad en los últimos X días.
    """
    since = datetime.now() - timedelta(days=days)
    total_checkins = CheckIn.objects.filter(timestamp__gte=since).count()

    # Top 5 lugares más visitados
    top_locations = (
        CheckIn.objects.filter(timestamp__gte=since)
        .values("location")
        .annotate(visits=Count("id"))
        .order_by("-visits")[:5]
    )

    # Total de usuarios únicos
    unique_users = (
        CheckIn.objects.filter(timestamp__gte=since)
        .values("user")
        .distinct()
        .count()
    )

    return {
        "total_checkins": total_checkins,
        "unique_users": unique_users,
        "top_locations": list(top_locations),
        "period_days": days
    }
