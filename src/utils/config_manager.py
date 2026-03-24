"""
Gestor de Configuración centralizado para ActaClara.

Carga los valores por defecto de ``src.config`` y permite sobreescribirlos
con un archivo ``config.json`` opcional ubicado en la raíz del proyecto.
Expone los ajustes a través de un Singleton de solo lectura.

Uso típico::

    from src.utils.config_manager import ConfigManager

    cfg = ConfigManager()
    print(cfg.get("DB_PATH"))
    print(cfg.get("WHISPER_MODEL"))
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from src import config as _defaults

logger = logging.getLogger("ConfigManager")


class ConfigManager:
    """Singleton que centraliza toda la configuración de ActaClara.

    Prioridad de valores (de mayor a menor):
        1. Sobrecargas en ``config.json`` (si existe).
        2. Constantes definidas en ``src/config.py``.
        3. Valor por defecto proporcionado en ``get(key, default)``.

    Attributes:
        _settings: Diccionario interno con todos los ajustes resueltos.
    """

    _instance: Optional[ConfigManager] = None
    _CONFIG_JSON_NAME = "config.json"

    # ------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------

    def __new__(cls) -> ConfigManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._settings: Dict[str, Any] = {}
        self._load_defaults()
        self._load_json_overrides()
        self._initialized = True
        logger.info(
            "ConfigManager inicializado con %d ajustes.", len(self._settings)
        )

    # ------------------------------------------------------------------
    # Carga de valores
    # ------------------------------------------------------------------

    def _load_defaults(self) -> None:
        """Importa todas las constantes UPPER_CASE de ``src/config.py``."""
        for attr in dir(_defaults):
            if attr.isupper():
                self._settings[attr] = getattr(_defaults, attr)

    def _load_json_overrides(self) -> None:
        """Si existe ``config.json`` en la raíz, sobrescribe los valores."""
        base_dir = self._settings.get("BASE_DIR", "")
        json_path = Path(base_dir) / self._CONFIG_JSON_NAME

        if not json_path.is_file():
            logger.debug("No se encontró %s; usando valores por defecto.", json_path)
            return

        try:
            with open(json_path, "r", encoding="utf-8") as fh:
                overrides: Dict[str, Any] = json.load(fh)

            if not isinstance(overrides, dict):
                logger.warning("%s no contiene un objeto JSON válido.", json_path)
                return

            applied = 0
            for key, value in overrides.items():
                upper_key = key.upper()
                self._settings[upper_key] = value
                applied += 1

            logger.info(
                "%d ajustes sobrescritos desde %s.", applied, json_path
            )
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Error al leer %s: %s", json_path, exc)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """Devuelve el valor de configuración para *key*.

        Args:
            key: Nombre del ajuste (se busca en UPPER_CASE).
            default: Valor retornado si la clave no existe.

        Returns:
            El valor configurado o *default*.
        """
        return self._settings.get(key.upper(), default)

    def set(self, key: str, value: Any) -> None:
        """Establece un valor y lo persiste en config.json.

        Args:
            key: Nombre del ajuste.
            value: Nuevo valor.
        """
        upper_key = key.upper()
        self._settings[upper_key] = value
        
        # Persistir a config.json
        base_dir = self._settings.get("BASE_DIR", "")
        json_path = Path(base_dir) / self._CONFIG_JSON_NAME
        
        try:
            # Leer actual para no borrar lo que no estamos tocando (aunque _settings ya tiene todo)
            # Simplemente guardamos _settings filtrando constantes de src/config que no queremos en el JSON?
            # En realidad, guardamos solo lo que ha cambiado respecto a los defaults?
            # Por simplicidad para el MVP, guardamos todo lo que hay en _settings que no sea BASE_DIR o cosas internas
            
            save_dict = {}
            for k, v in self._settings.items():
                # Solo guardamos lo que el usuario suele configurar
                if k in ["APPEARANCE", "LANGUAGE", "EXPORT_PATH", "WHISPER_MODEL"]:
                    save_dict[k.lower()] = v
            
            with open(json_path, "w", encoding="utf-8") as fh:
                json.dump(save_dict, fh, indent=4)
                
            logger.info("Ajuste '%s' guardado en %s.", upper_key, json_path)
        except OSError as exc:
            logger.error("Error al guardar configuración en %s: %s", json_path, exc)

    def all_settings(self) -> Dict[str, Any]:
        """Devuelve una **copia** de todos los ajustes actuales."""
        return dict(self._settings)

    def reload(self) -> None:
        """Recarga valores por defecto y sobrecargas JSON."""
        self._settings.clear()
        self._load_defaults()
        self._load_json_overrides()
        logger.info("Configuración recargada.")

    # ------------------------------------------------------------------
    # Helpers de conveniencia
    # ------------------------------------------------------------------

    @property
    def db_path(self) -> str:
        """Atajo para ``get('DB_PATH')``."""
        return self.get("DB_PATH", "data/actaclara.db")

    @property
    def whisper_model(self) -> str:
        """Atajo para ``get('WHISPER_MODEL')``."""
        return self.get("WHISPER_MODEL", "small")

    @property
    def dictionary_path(self) -> str:
        """Atajo para ``get('DICTIONARY_PATH')``."""
        return self.get("DICTIONARY_PATH", "")

    @property
    def version(self) -> str:
        """Versión de la aplicación."""
        return self.get("VERSION", "0.0")

    def __repr__(self) -> str:
        return f"<ConfigManager v{self.version} — {len(self._settings)} ajustes>"
