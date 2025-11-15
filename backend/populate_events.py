
from datetime import datetime, timedelta
from django.utils import timezone
from blockchain_api.models import Event

# 🗑️ Limpiar eventos existentes (opcional)
# Event.objects.all().delete()

# 📍 Eventos de prueba en Santiago, Chile
eventos = [
    {
        "name": "Lollapalooza Chile 2025",
        "description": "Festival de música con artistas internacionales. Rock, pop, electrónica y más.",
        "location": "Parque Bicentenario Cerrillos, Santiago",
        "latitude": -33.4979,
        "longitude": -70.7069,
        "start_date": timezone.now() + timedelta(days=15),
        "end_date": timezone.now() + timedelta(days=17),
    },
    {
        "name": "Fiesta Electrónica - Club La Feria",
        "description": "Noche de música electrónica con los mejores DJs locales e internacionales.",
        "location": "Club La Feria, Providencia",
        "latitude": -33.4245,
        "longitude": -70.6110,
        "start_date": timezone.now() + timedelta(days=2),
        "end_date": timezone.now() + timedelta(days=2, hours=6),
    },
    {
        "name": "Festival Gastronómico Bellavista",
        "description": "Degustación de comida chilena e internacional con música en vivo.",
        "location": "Barrio Bellavista, Santiago",
        "latitude": -33.4320,
        "longitude": -70.6344,
        "start_date": timezone.now() + timedelta(days=5),
        "end_date": timezone.now() + timedelta(days=7),
    },
    {
        "name": "Noche de Salsa - Club Havana",
        "description": "Baile y música latina toda la noche. Clases de salsa incluidas.",
        "location": "Club Havana, Santiago Centro",
        "latitude": -33.4425,
        "longitude": -70.6506,
        "start_date": timezone.now() + timedelta(days=1),
        "end_date": timezone.now() + timedelta(days=1, hours=5),
    },
    {
        "name": "Feria de Arte Lastarria",
        "description": "Exposición de arte urbano, música indie y foodtrucks.",
        "location": "Barrio Lastarria, Santiago",
        "latitude": -33.4378,
        "longitude": -70.6395,
        "start_date": timezone.now() + timedelta(days=3),
        "end_date": timezone.now() + timedelta(days=3, hours=8),
    },
    {
        "name": "Concierto de Jazz - Teatro Municipal",
        "description": "Noche de jazz con músicos nacionales e internacionales.",
        "location": "Teatro Municipal de Santiago",
        "latitude": -33.4372,
        "longitude": -70.6506,
        "start_date": timezone.now() + timedelta(days=10),
        "end_date": timezone.now() + timedelta(days=10, hours=3),
    },
    {
        "name": "Fiesta Reggaeton - Club Blondie",
        "description": "La mejor música urbana y reggaeton. Open bar hasta las 2 AM.",
        "location": "Club Blondie, Las Condes",
        "latitude": -33.4172,
        "longitude": -70.5843,
        "start_date": timezone.now() + timedelta(days=4),
        "end_date": timezone.now() + timedelta(days=4, hours=6),
    },
    {
        "name": "Festival de Cerveza Artesanal",
        "description": "Más de 50 cervecerías artesanales chilenas. Música en vivo y foodtrucks.",
        "location": "Parque Araucano, Las Condes",
        "latitude": -33.4057,
        "longitude": -70.5774,
        "start_date": timezone.now() + timedelta(days=8),
        "end_date": timezone.now() + timedelta(days=9),
    },
    {
        "name": "Noche de Rock - Bar The Clinic",
        "description": "Bandas emergentes de rock chileno. Tributo a clásicos del rock.",
        "location": "The Clinic Bar, Providencia",
        "latitude": -33.4294,
        "longitude": -70.6106,
        "start_date": timezone.now() + timedelta(days=6),
        "end_date": timezone.now() + timedelta(days=6, hours=5),
    },
    {
        "name": "Fiesta Años 80s y 90s - Club Eve",
        "description": "Nostalgia total con los mejores hits de los 80s y 90s.",
        "location": "Club Eve, Vitacura",
        "latitude": -33.3969,
        "longitude": -70.5695,
        "start_date": timezone.now() + timedelta(days=12),
        "end_date": timezone.now() + timedelta(days=12, hours=6),
    },
]

# 💾 Crear eventos en la base de datos
eventos_creados = []
for evento_data in eventos:
    evento, created = Event.objects.get_or_create(
        name=evento_data["name"],
        defaults=evento_data
    )
    if created:
        eventos_creados.append(evento.name)
        print(f"✅ Evento creado: {evento.name}")
    else:
        print(f"⚠️ Evento ya existe: {evento.name}")

print(f"\n🎉 Total de eventos creados: {len(eventos_creados)}")
print(f"📊 Total de eventos en BD: {Event.objects.count()}")

# 📋 Listar todos los eventos
print("\n📍 Eventos disponibles:")
print("-" * 80)
for evento in Event.objects.all().order_by("start_date"):
    print(f"• {evento.name}")
    print(f"  📍 {evento.location}")
    print(f"  📅 {evento.start_date.strftime('%d/%m/%Y %H:%M')} - {evento.end_date.strftime('%d/%m/%Y %H:%M')}")
    print(f"  🌐 Lat: {evento.latitude}, Lng: {evento.longitude}")
    print()