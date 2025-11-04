from django.urls import path
from . import views

urlpatterns = [
    path('checkins/<str:address>/', views.obtener_ubicacion),
    path('checkin/', views.registrar_checkin),
    path('heatmap/', views.heatmap_view, name='heatmap_view'),
]
