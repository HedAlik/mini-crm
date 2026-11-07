"""Acceso a SQLite: conexión por petición y ejecución de migraciones."""
import sqlite3
from pathlib import Path

from flask import current_app, g

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    # SQLite NO aplica llaves foráneas por defecto: hay que activarlas en cada conexión.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE"])
    return g.db


def close_db(_exc=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def run_migrations(path: str) -> list[str]:
    """Aplica en orden los .sql de migrations/ que no se hayan aplicado aún."""
    conn = connect(path)
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " nombre TEXT PRIMARY KEY,"
            " aplicada_en TEXT NOT NULL DEFAULT (datetime('now')))"
        )
        aplicadas = {r["nombre"] for r in conn.execute("SELECT nombre FROM schema_migrations")}
        nuevas = []
        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if sql_file.name in aplicadas:
                continue
            conn.executescript(sql_file.read_text(encoding="utf-8"))
            conn.execute("INSERT INTO schema_migrations (nombre) VALUES (?)", (sql_file.name,))
            conn.commit()
            nuevas.append(sql_file.name)
        return nuevas
    finally:
        conn.close()
