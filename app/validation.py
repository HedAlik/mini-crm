"""Validación de entrada. Devuelve un dict de errores por campo (vacío = válido)."""
import re

ESTADOS_VALIDOS = ("pendiente", "en_proceso", "resuelta")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# SQLite guarda enteros de 64 bits con signo; un id mayor provoca OverflowError al consultar.
MAX_ID = 2**63 - 1


def id_valido(valor) -> bool:
    # bool es subclase de int en Python (True == 1): se excluye explícitamente.
    return isinstance(valor, int) and not isinstance(valor, bool) and 0 < valor <= MAX_ID


def parsear_id(texto: str) -> int | None:
    """Convierte un id recibido como texto (query string). None si no es válido."""
    # Solo dígitos ASCII: "²".isdigit() es True pero int("²") falla.
    if not re.fullmatch(r"[0-9]+", texto):
        return None
    valor = int(texto)
    return valor if id_valido(valor) else None


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
    if not id_valido(data.get("cliente_id")):
        errores["cliente_id"] = "es obligatorio y debe ser un entero positivo"
    _texto(data.get("descripcion"), "descripcion", errores, 1000)
    if "estado" in data:
        validar_estado(data["estado"], errores)
    return errores
