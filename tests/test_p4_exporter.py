"""
Test de integración para P4 - DocxExporter.

Verifica que ``DocxExporter`` genere un archivo DOCX real,
lo guarde en disco y actualice la tabla ``actas`` en SQLite.

Ejecución:
    python tests/test_p4_exporter.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Añadir raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database.db_manager import DBManager
from src.models.acta import Acta
from src.models.modismo import ModismoDetectado
from src.services.exporter import ActaMetadata, DocxExporter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _crear_acta_de_prueba(db: DBManager) -> int:
    """Crea y persiste un acta de prueba en la BD, devuelve su ID."""
    modismo = ModismoDetectado(
        expresion_original="al tiro",
        expresion_normalizada="inmediatamente",
        posicion_inicio=47,
        posicion_fin=54,
        accion_usuario="ACEPTADA",
    )
    acta = Acta(
        titulo="Reunión de Diseño ActaClara P4",
        idioma="es-CL",
        duracion_segundos=300,
        archivo_audio_ruta="data/audio/p4_test.mp3",
        wer_medido=0.03,
        fecha_creacion=datetime.now(),
        modismos_detectados=[modismo],
    )
    acta_id = db.insert_acta(acta)
    print(f"  ✓ Acta insertada con ID: {acta_id}")
    return acta_id


def _construir_metadata() -> ActaMetadata:
    """Retorna los metadatos de ejemplo capturados desde la UI."""
    return ActaMetadata(
        proyecto="ActaClara — Tesis USACH 2026",
        objetivo="Validar la exportación DOCX del módulo P4.",
        asistentes=[
            "Dr. Rodrigo Castillo (Director Tesis)",
            "Equipo de Desarrollo ActaClara",
            "Agente A3 (Backend)",
        ],
        acuerdos=[
            "Verificar compatibilidad del DOCX en Microsoft Word y LibreOffice.",
            "Registrar la ruta del archivo en la base de datos SQLite.",
        ],
        compromisos=[
            "A3: entregar implementación completa antes del 21/03/2026.",
            "A2: revisar la arquitectura de ExporterInterface para PDF.",
        ],
    )


# ---------------------------------------------------------------------------
# Prueba principal
# ---------------------------------------------------------------------------

def test_exportar_docx_real():
    """Prueba de integración completa: genera, guarda y verifica un DOCX real."""
    print("\n" + "=" * 60)
    print("  P4 — Test de Exportación DOCX (DocxExporter)")
    print("=" * 60)

    # 1. Inicializar BD
    print("\n[1/6] Inicializando base de datos...")
    db = DBManager()
    db.initialize_db()

    # 2. Crear acta en BD
    print("[2/6] Creando acta de prueba en SQLite...")
    acta_id = _crear_acta_de_prueba(db)

    # 3. Recuperar acta (simular flujo real desde UI)
    print("[3/6] Recuperando acta desde la BD...")
    acta = db.get_acta_by_id(acta_id)
    assert acta is not None, "ERROR: No se pudo recuperar el acta."
    print(f"  ✓ Acta recuperada: '{acta.titulo}'")

    # 4. Construir metadatos y exportador
    print("[4/6] Construyendo DocxExporter con metadatos...")
    metadata = _construir_metadata()
    exporter = DocxExporter(acta=acta, metadata=metadata, db_manager=db)

    # 5. Generar el documento
    print("[5/6] Generando DOCX...")
    texto_normalizado = (
        "El equipo revisó el módulo de exportación. "
        "La reunión comenzó inmediatamente a las 10:00 hs. "
        "Se validaron los criterios de aceptación del P4."
    )

    exporter.apply_template()
    exporter._build_all_sections(texto_normalizado)

    # Ruta de salida según especificación del proyecto
    fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"ReunionDisenoActaClara_P4_{fecha_str}.docx"
    output_path = Path("data") / "actas_exportadas" / nombre_archivo

    path_final = exporter.save_and_record(
        acta_id=acta_id,
        output_path=output_path,
    )

    # 6. Verificaciones
    print("[6/6] Verificando resultados...")

    # 6a. Archivo existe en disco
    assert path_final.exists(), f"ERROR: El archivo DOCX no existe en {path_final}"
    assert path_final.suffix == ".docx", "ERROR: La extensión del archivo no es .docx"
    print(f"  ✓ Archivo DOCX generado: {path_final}")
    print(f"  ✓ Tamaño: {path_final.stat().st_size:,} bytes")

    # 6b. Ruta registrada en la BD
    acta_actualizada = db.get_acta_by_id(acta_id)
    assert acta_actualizada is not None
    assert acta_actualizada.archivo_docx_ruta is not None, (
        "ERROR: archivo_docx_ruta no fue actualizado en la BD."
    )
    assert str(output_path) in acta_actualizada.archivo_docx_ruta, (
        f"ERROR: la ruta guardada '{acta_actualizada.archivo_docx_ruta}' "
        f"no corresponde a '{output_path}'."
    )
    print(f"  ✓ Ruta registrada en BD: {acta_actualizada.archivo_docx_ruta}")

    print("\n" + "=" * 60)
    print("  ✅  PRUEBA EXITOSA — DocxExporter P4 OK")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Test adicional: solo estructura (sin BD)
# ---------------------------------------------------------------------------

def test_add_section_sin_db():
    """Prueba unitaria ligera que verifica add_section sin depender de SQLite."""
    print("\n[Unit] test_add_section_sin_db...")
    acta = Acta(titulo="Test Unitario", idioma="es-CL", version_diccionario="1.0")
    metadata = ActaMetadata(proyecto="Test", objetivo="Verificar secciones")
    exporter = DocxExporter(acta=acta, metadata=metadata)

    exporter.apply_template()
    exporter.add_section("Sección de Prueba", "Contenido de prueba para verificar formato.")

    # El documento debe tener al menos 3 párrafos: título, separador, sección
    assert len(exporter.document.paragraphs) >= 3
    textos = [p.text for p in exporter.document.paragraphs]
    assert any("Sección de Prueba" in t for t in textos), (
        "ERROR: El título de la sección no fue encontrado en el documento."
    )
    print("  ✓ add_section funciona correctamente.")


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_add_section_sin_db()
    test_exportar_docx_real()
