from django.urls import path
from . import views

urlpatterns = [
    path('checkins/<str:address>/', views.obtener_ubicacion),
    path('checkin/', views.register_checkin),
    path("heatmap/", views.heatmap_data),
    path("stats/", views.activity_stats),
]
