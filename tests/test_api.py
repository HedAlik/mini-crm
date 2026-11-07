"""Pruebas automatizadas de la API (cada prueba usa una BD temporal aislada)."""
import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "test.db"), "TESTING": True})
    with app.test_client() as c:
        yield c


def crear_cliente(client, email="ana@example.com"):
    resp = client.post("/clientes", json={"nombre": "Ana Prueba", "email": email})
    assert resp.status_code == 201
    return resp.get_json()


# ---------- Camino exitoso ----------

def test_flujo_completo_cliente_solicitud_y_cambio_de_estado(client):
    cliente = crear_cliente(client)

    resp = client.post("/solicitudes", json={"cliente_id": cliente["id"], "descripcion": "No llega mi factura"})
    assert resp.status_code == 201
    solicitud = resp.get_json()
    assert solicitud["estado"] == "pendiente"  # estado por defecto
    assert solicitud["cliente_id"] == cliente["id"]

    resp = client.patch(f"/solicitudes/{solicitud['id']}/estado", json={"estado": "en_proceso"})
    assert resp.status_code == 200
    assert resp.get_json()["estado"] == "en_proceso"

    listado = client.get("/solicitudes").get_json()
    assert len(listado) == 1
    assert listado[0]["estado"] == "en_proceso"
    assert listado[0]["cliente_nombre"] == "Ana Prueba"


def test_listar_clientes_y_filtrar_solicitudes_por_estado(client):
    c = crear_cliente(client)
    client.post("/solicitudes", json={"cliente_id": c["id"], "descripcion": "A"})
    client.post("/solicitudes", json={"cliente_id": c["id"], "descripcion": "B", "estado": "resuelta"})

    assert len(client.get("/clientes").get_json()) == 1
    resueltas = client.get("/solicitudes?estado=resuelta").get_json()
    assert [s["descripcion"] for s in resueltas] == ["B"]


# ---------- Errores ----------

def test_rechaza_solicitud_con_cliente_inexistente(client):
    resp = client.post("/solicitudes", json={"cliente_id": 999, "descripcion": "Sin cliente"})
    assert resp.status_code == 422
    assert "cliente_id" in resp.get_json()["detalles"]
    assert client.get("/solicitudes").get_json() == []  # no se guardó nada


def test_rechaza_estado_invalido_al_actualizar(client):
    c = crear_cliente(client)
    s = client.post("/solicitudes", json={"cliente_id": c["id"], "descripcion": "X"}).get_json()

    resp = client.patch(f"/solicitudes/{s['id']}/estado", json={"estado": "cerrada"})
    assert resp.status_code == 422
    assert "estado" in resp.get_json()["detalles"]
    # El estado original se conserva
    assert client.get("/solicitudes").get_json()[0]["estado"] == "pendiente"


def test_rechaza_estado_invalido_al_crear(client):
    c = crear_cliente(client)
    resp = client.post("/solicitudes", json={"cliente_id": c["id"], "descripcion": "X", "estado": "PENDIENTE"})
    assert resp.status_code == 422


def test_actualizar_solicitud_inexistente_devuelve_404(client):
    resp = client.patch("/solicitudes/12345/estado", json={"estado": "resuelta"})
    assert resp.status_code == 404


def test_email_duplicado_devuelve_409(client):
    crear_cliente(client, "dup@example.com")
    resp = client.post("/clientes", json={"nombre": "Otro", "email": "DUP@example.com"})
    assert resp.status_code == 409


@pytest.mark.parametrize("body", [
    {"nombre": "", "email": "a@example.com"},
    {"nombre": "Sin email"},
    {"nombre": "Email malo", "email": "no-es-correo"},
])
def test_cliente_con_datos_invalidos_devuelve_422(client, body):
    assert client.post("/clientes", json=body).status_code == 422


def test_cuerpo_no_json_devuelve_400(client):
    resp = client.post("/clientes", data="no soy json", content_type="text/plain")
    assert resp.status_code == 400


def test_cliente_id_booleano_es_rechazado(client):
    crear_cliente(client)  # id = 1; True == 1 en Python, no debe colarse
    resp = client.post("/solicitudes", json={"cliente_id": True, "descripcion": "X"})
    assert resp.status_code == 422


def test_la_base_de_datos_tambien_impone_las_restricciones(tmp_path):
    """Defensa en profundidad: aunque se salte la API, SQLite rechaza FK y estados inválidos."""
    import sqlite3
    from app.db import connect, run_migrations

    path = str(tmp_path / "raw.db")
    run_migrations(path)
    conn = connect(path)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO solicitudes (cliente_id, descripcion) VALUES (999, 'x')")
    conn.execute("INSERT INTO clientes (nombre, email) VALUES ('A', 'a@example.com')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO solicitudes (cliente_id, descripcion, estado) VALUES (1, 'x', 'otro')")
    conn.close()
