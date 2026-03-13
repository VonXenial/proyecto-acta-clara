import sqlite3
import os
import logging
from datetime import datetime
from typing import Optional, List
from src.models.acta import Acta
from src.models.modismo import ModismoDetectado

# Configuración básica de logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/database.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DBManager")

class DBManager:
    """
    Gestor de base de datos SQLite para ActaClara.
    Implementa el patrón Singleton para asegurar una única conexión.
    """
    _instance = None
    _db_path = "data/actaclara.db"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            # Asegurar que el directorio data existe
            os.makedirs(os.path.dirname(cls._db_path), exist_ok=True)
        return cls._instance

    def _get_connection(self):
        """Obtiene una conexión a la base de datos."""
        return sqlite3.connect(self._db_path)

    def initialize_db(self, schema_path: str = "src/database/schema.sql"):
        """
        Lee el archivo de esquema y crea las tablas necesarias.
        """
        try:
            if not os.path.exists(schema_path):
                logger.error(f"Archivo de esquema no encontrado en: {schema_path}")
                raise FileNotFoundError(f"Esquema no encontrado: {schema_path}")

            with self._get_connection() as conn:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = f.read()
                conn.executescript(schema)
            logger.info("Base de datos inicializada correctamente.")
        except Exception as e:
            logger.error(f"Error al inicializar la base de datos: {e}")
            raise

    def insert_acta(self, acta: Acta) -> int:
        """
        Inserta un acta y sus modismos asociados en la base de datos.
        """
        query_acta = """
        INSERT INTO actas (
            titulo, idioma, duracion_segundos, archivo_audio_ruta, 
            archivo_docx_ruta, wer_medido, version_diccionario
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query_acta, (
                    acta.titulo, 
                    acta.idioma, 
                    acta.duracion_segundos,
                    acta.archivo_audio_ruta, 
                    acta.archivo_docx_ruta,
                    acta.wer_medido, 
                    acta.version_diccionario
                ))
                acta_id = cursor.lastrowid
                
                if acta.modismos_detectados:
                    for modismo in acta.modismos_detectados:
                        modismo.acta_id = acta_id
                        self._insert_modismo_internal(cursor, modismo)
                
            logger.info(f"Acta '{acta.titulo}' insertada con ID: {acta_id}")
            return acta_id
        except Exception as e:
            logger.error(f"Error al insertar acta '{acta.titulo}': {e}")
            raise

    def _insert_modismo_internal(self, cursor, modismo: ModismoDetectado):
        """Método interno para insertar un modismo usando un cursor existente."""
        query_modismo = """
        INSERT INTO modismos_detectados (
            acta_id, expresion_original, expresion_normalizada, 
            posicion_inicio, posicion_fin, accion_usuario
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query_modismo, (
            modismo.acta_id, 
            modismo.expresion_original,
            modismo.expresion_normalizada, 
            modismo.posicion_inicio,
            modismo.posicion_fin, 
            modismo.accion_usuario
        ))

    def get_acta_by_id(self, acta_id: int) -> Optional[Acta]:
        """
        Recupera un acta y sus modismos por su ID.
        """
        query_acta = "SELECT * FROM actas WHERE id = ?"
        query_modismos = "SELECT * FROM modismos_detectados WHERE acta_id = ?"
        
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Obtener Acta
                cursor.execute(query_acta, (acta_id,))
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"No se encontró acta con ID: {acta_id}")
                    return None
                
                # Obtener Modismos asociados
                cursor.execute(query_modismos, (acta_id,))
                modismos_rows = cursor.fetchall()
                modismos = [
                    ModismoDetectado(
                        id=m['id'],
                        acta_id=m['acta_id'],
                        expresion_original=m['expresion_original'],
                        expresion_normalizada=m['expresion_normalizada'],
                        posicion_inicio=m['posicion_inicio'],
                        posicion_fin=m['posicion_fin'],
                        accion_usuario=m['accion_usuario']
                    ) for m in modismos_rows
                ]
                
                # Manejo de la fecha (SQLite la guarda como string)
                fecha_str = row['fecha_creacion']
                fecha_obj = None
                if fecha_str:
                    try:
                        # SQLite DEFAULT CURRENT_TIMESTAMP usa el formato YYYY-MM-DD HH:MM:SS
                        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # Intentar formato ISO por si acaso
                        try:
                            fecha_obj = datetime.fromisoformat(fecha_str.replace(' ', 'T'))
                        except Exception:
                            logger.warning(f"Formato de fecha no reconocido: {fecha_str}")
                
                return Acta(
                    id=row['id'],
                    titulo=row['titulo'],
                    fecha_creacion=fecha_obj,
                    idioma=row['idioma'],
                    duracion_segundos=row['duracion_segundos'],
                    archivo_audio_ruta=row['archivo_audio_ruta'],
                    archivo_docx_ruta=row['archivo_docx_ruta'],
                    wer_medido=row['wer_medido'],
                    version_diccionario=row['version_diccionario'],
                    modismos_detectados=modismos
                )
        except Exception as e:
            logger.error(f"Error al obtener acta por ID {acta_id}: {e}")
            raise
