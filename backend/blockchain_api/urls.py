from django.urls import path
from . import views

urlpatterns = [
    path('checkins/<str:address>/', views.obtener_ubicacion),
    path('checkin/', views.register_checkin),
    path("heatmap/", views.heatmap_data, name='heatmap_data'),
    path("stats/", views.activity_stats),
    path("events/", views.events_view),
    path("mapa/", views.mapa_completo),
    path("event_checkin/", views.event_checkin),
    path('login_wallet/', views.login_wallet, name='login_wallet'),
]
