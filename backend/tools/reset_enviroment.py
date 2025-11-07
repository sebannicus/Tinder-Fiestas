import os
import shutil
import django

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("🧱 Restaurando entorno Django...")

# Eliminar base de datos SQLite (si existe)
db_path = os.path.join(BASE_DIR, "db.sqlite3")
if os.path.exists(db_path):
    os.remove(db_path)
    print("🗑️  Base de datos eliminada.")

# Eliminar todas las migraciones excepto __init__.py
migrations_dir = os.path.join(BASE_DIR, "blockchain_api", "migrations")
if os.path.exists(migrations_dir):
    for file in os.listdir(migrations_dir):
        if file != "__init__.py":
            os.remove(os.path.join(migrations_dir, file))
    print("🧹 Migraciones eliminadas.")

# Ejecutar nuevamente las migraciones
os.system("python manage.py makemigrations blockchain_api")
os.system("python manage.py migrate")

print("✅ Entorno restaurado correctamente.")
