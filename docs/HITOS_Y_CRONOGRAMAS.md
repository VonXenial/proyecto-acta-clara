Actividades/Hitos  	Fecha	Duración
Prototipo 0: Configuración del Entorno y Arquitectura Base	05-01-2026	2 semanas
Prototipo 1: Motor de Transcripción Básico (Núcleo STT) del Motor de Transcripción (MVP Core)	19-01-2026	3 semanas
Prototipo 2: Normalización de Modismos (Núcleo NLP)	09-02-2026	2 semanas
Prototipo 3: Interfaz Gráfica Básica (UI Desktop)	23-02-2026	2 semanas
Prototipo 4: Exportación y Repositorio (IntegraciónCompleta)	09-03-2026	2 semanas
Prototipo 5: MVP Validado y Refinado (Producto Final)	23-03-2026	2 semanas


ID	Actividad	Duración (semanas)	Fecha Inicio	Fecha Fin	Dependencias	Prototipo
PROTOTIPO 0: CONFIGURACIÓN Y ARQUITECTURA BASE
0.1	Instalación y configuración del entorno Python (3.10+, venv, librerías)	0.5	05-01-2026	08-01-2026	-	P0
0.2	Diseño de arquitectura modular (diagrama de componentes y clases)	0.5	09-01-2026	12-01-2026	0.1	P0
0.3	Inicialización de repositorio Git y estructura de carpetas	0.25	13-01-2026	14-01-2026	0.2	P0
0.4	Creación de diccionario inicial de modismos (50 expresiones ES-CL)	0.75	15-01-2026	18-01-2026	0.2	P0
PROTOTIPO 1: MOTOR DE TRANSCRIPCIÓN BÁSICO (CLI)
1.1	Investigación e integración de Whisper/faster-whisper (modo local)	1.0	19-01-2026	25-01-2026	0.3	P1
1.2	Desarrollo de módulo de procesamiento de audio (FFmpeg/pydub)	0.5	26-01-2026	29-01-2026	1.1	P1
1.3	Implementación de CLI para transcripción (entrada: WAV/MP3, salida: TXT)	1.0	30-01-2026	05-02-2026	1.2	P1
1.4	Validación de P1: Pruebas con 5 audios reales (medición WER)	0.5	06-02-2026	08-02-2026	1.3	P1
PROTOTIPO 2: NORMALIZACIÓN DE MODISMOS (CLI MEJORADO)
2.1	Diseño de estructura de diccionarios (JSON/YAML, schema de datos)	0.5	09-02-2026	12-02-2026	1.4	P2
2.2	Desarrollo de motor de detección de modismos (regex, pattern matching)	1.0	13-02-2026	19-02-2026	2.1	P2
2.3	Expansión de diccionarios a 150+ modismos (ES-CL, ES-MX, ES-AR)	0.5	20-02-2026	22-02-2026	2.2	P2
2.4	Validación de P2: Pruebas de precisión de detección de modismos	0.5	23-02-2026	25-02-2026	2.3	P2
PROTOTIPO 3: INTERFAZ GRÁFICA BÁSICA (UI DESKTOP)
3.1	Diseño de mockups de interfaz (3 pantallas principales)	0.5	23-02-2026	26-02-2026	-	P3
3.2	Implementación de UI Dashboard y pantalla de ingesta de audio	1.0	27-02-2026	05-03-2026	3.1, 2.4	P3
3.3	Implementación de pantalla de transcripción y visualización de modismos	1.0	06-03-2026	12-03-2026	3.2	P3
3.4	Validación de P3: Pruebas de usabilidad con usuarios (tiempo de aprendizaje)	0.5	13-03-2026	15-03-2026	3.3	P3
PROTOTIPO 4: EXPORTACIÓN Y REPOSITORIO (INTEGRACIÓN COMPLETA)
4.1	Desarrollo de generador de documentos DOCX/PDF (con plantillas)	1.0	09-03-2026	15-03-2026	2.4	P4
4.2	Implementación de repositorio SQLite (metadatos, historial de actas)	0.5	16-03-2026	18-03-2026	4.1	P4
4.3	Integración de pantalla de exportación y consulta de historial en UI	0.5	19-03-2026	21-03-2026	4.2, 3.4	P4
4.4	Validación de P4: Pruebas de exportación (10 actas, formatos variados)	0.5	22-03-2026	24-03-2026	4.3	P4
PROTOTIPO 5: MVP VALIDADO Y REFINADO (PRODUCTO FINAL)
5.1	Piloto con grabaciones reales (8-10 reuniones de 30-60 min)	1.0	23-03-2026	29-03-2026	4.4	P5
5.2	Medición de KPIs finales (tiempo, WER, precisión, satisfacción)	0.5	30-03-2026	01-04-2026	5.1	P5
5.3	Corrección de bugs críticos identificados en el piloto	0.5	02-04-2026	04-04-2026	5.2	P5
5.4	Refinamiento de UI y UX según retroalimentación de usuarios	0.5	02-04-2026	04-04-2026	5.2	P5
5.5	Redacción de documentación técnica completa y manual de usuario	0.5	05-04-2026	07-04-2026	5.3, 5.4	P5
5.6	Empaquetado final en ejecutable portable (PyInstaller, instalador)	0.5	08-04-2026	10-04-2026	5.5	P5
5.7	Preparación de presentación final y entrega de informe	0.5	11-04-2026	13-04-2026	5.6	P5
Tabla 4.2: Cronograma detallado de 27 actividades
