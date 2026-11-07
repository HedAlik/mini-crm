"""Fábrica de la aplicación Flask del Mini CRM."""
import os

from flask import Flask, jsonify, send_from_directory

from . import db
from .routes import bp


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__, static_folder="static")
    app.config["DATABASE"] = os.environ.get("DATABASE_PATH", "data/crm.db")
    app.json.ensure_ascii = False  # acentos legibles en las respuestas
    app.json.sort_keys = False
    if config:
        app.config.update(config)

    db_dir = os.path.dirname(app.config["DATABASE"])
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    db.run_migrations(app.config["DATABASE"])

    app.teardown_appcontext(db.close_db)
    app.register_blueprint(bp)

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/docs")
    def docs():
        # Swagger UI para explorar y probar la API.
        return send_from_directory(app.static_folder, "docs.html")

    @app.get("/openapi.json")
    def openapi():
        # Especificación escrita a mano; una prueba verifica que cubra todas las rutas.
        return send_from_directory(app.static_folder, "openapi.json")

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return jsonify({"error": "Método no permitido"}), 405

    @app.errorhandler(500)
    def internal_error(_e):
        # No se exponen trazas ni detalles internos al cliente.
        return jsonify({"error": "Error interno del servidor"}), 500

    return app
