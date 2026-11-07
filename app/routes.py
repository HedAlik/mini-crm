"""Endpoints REST del Mini CRM."""
import sqlite3

from flask import Blueprint, jsonify, request

from .db import get_db
from .validation import ESTADOS_VALIDOS, validar_cliente, validar_estado, validar_solicitud

bp = Blueprint("api", __name__)


def error(status: int, mensaje: str, detalles: dict | None = None):
    cuerpo = {"error": mensaje}
    if detalles:
        cuerpo["detalles"] = detalles
    return jsonify(cuerpo), status


def json_body():
    """Devuelve el cuerpo JSON como dict o None si no es un objeto JSON válido."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def fila_a_dict(row: sqlite3.Row) -> dict:
    return dict(row)


@bp.get("/health")
def health():
    get_db().execute("SELECT 1")
    return jsonify({"status": "ok"})


# ---------- Clientes ----------

@bp.post("/clientes")
def crear_cliente():
    data = json_body()
    if data is None:
        return error(400, "El cuerpo debe ser un objeto JSON")
    errores = validar_cliente(data)
    if errores:
        return error(422, "Datos inválidos", errores)

    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO clientes (nombre, email) VALUES (?, ?)",
            (data["nombre"].strip(), data["email"].strip().lower()),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return error(409, "Ya existe un cliente con ese email")

    row = db.execute("SELECT * FROM clientes WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(fila_a_dict(row)), 201


@bp.get("/clientes")
def listar_clientes():
    rows = get_db().execute("SELECT * FROM clientes ORDER BY id").fetchall()
    return jsonify([fila_a_dict(r) for r in rows])


# ---------- Solicitudes ----------

@bp.post("/solicitudes")
def crear_solicitud():
    data = json_body()
    if data is None:
        return error(400, "El cuerpo debe ser un objeto JSON")
    errores = validar_solicitud(data)
    if errores:
        return error(422, "Datos inválidos", errores)

    db = get_db()
    existe = db.execute("SELECT 1 FROM clientes WHERE id = ?", (data["cliente_id"],)).fetchone()
    if not existe:
        return error(422, "Datos inválidos", {"cliente_id": "el cliente no existe"})

    try:
        cur = db.execute(
            "INSERT INTO solicitudes (cliente_id, descripcion, estado) VALUES (?, ?, ?)",
            (data["cliente_id"], data["descripcion"].strip(), data.get("estado", "pendiente")),
        )
        db.commit()
    except sqlite3.IntegrityError:
        # Segunda línea de defensa: FK / CHECK de la base de datos.
        return error(422, "La solicitud viola una restricción de integridad")

    row = db.execute("SELECT * FROM solicitudes WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(fila_a_dict(row)), 201


@bp.get("/solicitudes")
def listar_solicitudes():
    filtros, params = [], []

    estado = request.args.get("estado")
    if estado is not None:
        if estado not in ESTADOS_VALIDOS:
            return error(422, "Filtro inválido", {"estado": f"debe ser uno de: {', '.join(ESTADOS_VALIDOS)}"})
        filtros.append("s.estado = ?")
        params.append(estado)

    cliente_id = request.args.get("cliente_id")
    if cliente_id is not None:
        if not cliente_id.isdigit():
            return error(422, "Filtro inválido", {"cliente_id": "debe ser un entero positivo"})
        filtros.append("s.cliente_id = ?")
        params.append(int(cliente_id))

    where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
    rows = get_db().execute(
        f"""SELECT s.*, c.nombre AS cliente_nombre
            FROM solicitudes s JOIN clientes c ON c.id = s.cliente_id
            {where}
            ORDER BY s.id""",
        params,
    ).fetchall()
    return jsonify([fila_a_dict(r) for r in rows])


@bp.patch("/solicitudes/<int:solicitud_id>/estado")
def actualizar_estado(solicitud_id: int):
    data = json_body()
    if data is None:
        return error(400, "El cuerpo debe ser un objeto JSON")
    errores = {}
    validar_estado(data.get("estado"), errores)
    if errores:
        return error(422, "Datos inválidos", errores)

    db = get_db()
    cur = db.execute(
        "UPDATE solicitudes SET estado = ?, actualizado_en = datetime('now') WHERE id = ?",
        (data["estado"], solicitud_id),
    )
    db.commit()
    if cur.rowcount == 0:
        return error(404, "Solicitud no encontrada")

    row = db.execute("SELECT * FROM solicitudes WHERE id = ?", (solicitud_id,)).fetchone()
    return jsonify(fila_a_dict(row))
