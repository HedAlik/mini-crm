"""Inicializa la base de datos aplicando las migraciones pendientes.

Uso:
    python scripts/init_db.py            # usa DATABASE_PATH o data/crm.db
    python scripts/init_db.py --seed     # además inserta datos ficticios de ejemplo
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import connect, run_migrations  # noqa: E402


def main() -> None:
    path = os.environ.get("DATABASE_PATH", "data/crm.db")
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    nuevas = run_migrations(path)
    print(f"Base de datos: {path}")
    print("Migraciones aplicadas: " + (", ".join(nuevas) if nuevas else "ninguna (ya estaba al día)"))

    if "--seed" in sys.argv:
        conn = connect(path)
        # Datos 100% ficticios (dominio reservado example.com).
        conn.execute("INSERT OR IGNORE INTO clientes (nombre, email) VALUES ('Cliente Demo Uno', 'demo1@example.com')")
        conn.execute("INSERT OR IGNORE INTO clientes (nombre, email) VALUES ('Cliente Demo Dos', 'demo2@example.com')")
        conn.execute(
            "INSERT INTO solicitudes (cliente_id, descripcion) "
            "SELECT id, 'Solicitud de ejemplo' FROM clientes WHERE email = 'demo1@example.com'"
        )
        conn.commit()
        conn.close()
        print("Datos de ejemplo insertados.")


if __name__ == "__main__":
    main()
