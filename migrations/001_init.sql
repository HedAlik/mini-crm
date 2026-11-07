-- Migración 001: esquema inicial del Mini CRM
-- Dos tablas relacionadas: clientes (1) -> solicitudes (N)

CREATE TABLE IF NOT EXISTS clientes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    NOT NULL CHECK (length(trim(nombre)) > 0),
    email       TEXT    NOT NULL UNIQUE,
    creado_en   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS solicitudes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id      INTEGER NOT NULL,
    descripcion     TEXT    NOT NULL CHECK (length(trim(descripcion)) > 0),
    estado          TEXT    NOT NULL DEFAULT 'pendiente'
                    CHECK (estado IN ('pendiente', 'en_proceso', 'resuelta')),
    creado_en       TEXT    NOT NULL DEFAULT (datetime('now')),
    actualizado_en  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_solicitudes_cliente ON solicitudes (cliente_id);
CREATE INDEX IF NOT EXISTS idx_solicitudes_estado  ON solicitudes (estado);
