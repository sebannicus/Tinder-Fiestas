"""
urls.py
Rutas de la API para blockchain_api app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # USER ENDPOINTS
    path('checkins/<str:address>/', views.get_user_checkins_view, name='get_user_checkins'),
    path('login_wallet/', views.login_wallet, name='login_wallet'),
    
    # EVENT ENDPOINTS
    path('events/', views.events_view, name='events'),
    path('event_checkin/', views.event_checkin, name='event_checkin'),
    
    # ANALYTICS ENDPOINTS
    path('heatmap/', views.heatmap_data, name='heatmap_data'),
    path('stats/', views.activity_stats, name='activity_stats'),
    path('mapa/', views.mapa_completo, name='mapa_completo'),
    
    # INFO & HEALTH ENDPOINTS
    path('blockchain/info/', views.blockchain_info, name='blockchain_info'),
    path('health/', views.health_check, name='health_check'),
]