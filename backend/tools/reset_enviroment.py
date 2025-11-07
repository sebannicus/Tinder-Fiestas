"""
🔄 reset_environment.py
Script de restauración automática del entorno Django + DB local.

Ejecuta:
  python tools/reset_environment.py

Acciones:
  - Elimina base de datos local
  - Elimina migraciones anteriores
  - Recrea migraciones y tablas
  - Carga datos iniciales (usuario + evento de ejemplo)
"""

import os
import django
import shutil
from django.utils import timezone
from datetime import timedelta

# Configuración base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")
MIGRATIONS_DIR = os.path.join(BASE_DIR, "blockchain_api", "migrations")

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from blockchain_api.models import UserProfile, CheckIn, Event  # noqa


def clean_database():
    """Elimina DB y migraciones viejas"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🧹 Base de datos eliminada.")

    if os.path.exists(MIGRATIONS_DIR):
        shutil.rmtree(MIGRATIONS_DIR)
        print("🧩 Migraciones eliminadas.")


def rebuild_migrations():
    """Recrea migraciones limpias"""
    os.system("python manage.py makemigrations blockchain_api")
    os.system("python manage.py migrate")
    print("✅ Migraciones aplicadas correctamente.")


def load_sample_data():
    """Carga datos de prueba"""
    user = UserProfile.objects.create(wallet_address="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266", username="Sebas")

    Event.objects.create(
        name="Fiesta en La Serena",
        description="Evento en la playa con música en vivo.",
        location="La Serena, Chile",
        latitude=-29.9027,
        longitude=-71.2519,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(hours=6)
    )

    CheckIn.objects.create(
        user=user,
        location="La Serena",
        latitude=-29.9027,
        longitude=-71.2519,
        tx_hash="TEST_TX_HASH"
    )

    print("🎉 Datos de prueba creados (usuario, evento, checkin).")


if __name__ == "__main__":
    print("🔁 Iniciando restauración de entorno...")
    clean_database()
    rebuild_migrations()
    load_sample_data()
    print("🚀 Entorno restaurado con éxito. ¡Listo para ejecutar el servidor!")
