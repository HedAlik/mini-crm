"""Validación de entrada. Devuelve un dict de errores por campo (vacío = válido)."""
import re

ESTADOS_VALIDOS = ("pendiente", "en_proceso", "resuelta")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _texto(valor, campo, errores, max_len):
    if not isinstance(valor, str) or not valor.strip():
        errores[campo] = "es obligatorio y debe ser texto no vacío"
    elif len(valor) > max_len:
        errores[campo] = f"no debe exceder {max_len} caracteres"


def validar_cliente(data: dict) -> dict:
    errores = {}
    _texto(data.get("nombre"), "nombre", errores, 120)
    email = data.get("email")
    if not isinstance(email, str) or not EMAIL_RE.match(email.strip()):
        errores["email"] = "debe ser un correo válido"
    return errores


def validar_estado(estado, errores: dict) -> None:
    if estado not in ESTADOS_VALIDOS:
        errores["estado"] = f"debe ser uno de: {', '.join(ESTADOS_VALIDOS)}"


def validar_solicitud(data: dict) -> dict:
    errores = {}
    cliente_id = data.get("cliente_id")
    # bool es subclase de int en Python: se excluye explícitamente.
    if not isinstance(cliente_id, int) or isinstance(cliente_id, bool) or cliente_id <= 0:
        errores["cliente_id"] = "es obligatorio y debe ser un entero positivo"
    _texto(data.get("descripcion"), "descripcion", errores, 1000)
    if "estado" in data:
        validar_estado(data["estado"], errores)
    return errores
