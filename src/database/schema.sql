-- Archivo: actaclara.db schema
-- Ubicación: src/database/schema.sql

CREATE TABLE IF NOT EXISTS actas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    idioma TEXT DEFAULT 'es-CL',
    duracion_segundos INTEGER,
    archivo_audio_ruta TEXT,
    archivo_docx_ruta TEXT,
    wer_medido REAL,
    version_diccionario TEXT DEFAULT '1.0'
);

CREATE TABLE IF NOT EXISTS modismos_detectados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    acta_id INTEGER,
    expresion_original TEXT,
    expresion_normalizada TEXT,
    posicion_inicio INTEGER,
    posicion_fin INTEGER,
    accion_usuario TEXT CHECK(accion_usuario IN ('ACEPTADA', 'RECHAZADA', 'EDITADA')),
    FOREIGN KEY (acta_id) REFERENCES actas(id)
);

CREATE INDEX IF NOT EXISTS idx_acta_fecha ON actas(fecha_creacion);
CREATE INDEX IF NOT EXISTS idx_modismo_acta ON modismos_detectados(acta_id);
