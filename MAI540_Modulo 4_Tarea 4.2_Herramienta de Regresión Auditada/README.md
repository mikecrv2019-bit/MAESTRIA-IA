# Herramienta de Regresión Auditada — Emisiones de CO₂ de Vehículos

MAI 540 — Machine Learning | Módulo 4 | Tarea 4.2

Herramienta que estima las emisiones de CO₂ (g/km) de un vehículo ligero a partir de sus especificaciones técnicas, para apoyar la decisión de un fabricante o importador de estimar el CO₂ de una configuración nueva **antes** de la prueba oficial de homologación. Construida con [scikit-learn](https://scikit-learn.org/) y auditada con la Skill `auditoria-modelos` (extendida a regresión en esta tarea).

## Cómo ejecutarla

**Opción recomendada — Google Colab (sin instalar nada):**

1. Abre [`Herramienta_Regresion_CO2.ipynb`](Herramienta_Regresion_CO2.ipynb) en GitHub y haz clic en el botón "Open in Colab" de la primera celda, o entra directamente a:
   `https://colab.research.google.com/github/mikecrv2019-bit/MAESTRIA-IA/blob/main/MAI540_Modulo%204_Tarea%204.2_Herramienta%20de%20Regresi%C3%B3n%20Auditada/Herramienta_Regresion_CO2.ipynb`
2. Menú **Entorno de ejecución → Ejecutar todas**.
3. El cuaderno descarga el CSV automáticamente desde este repositorio (no hay que subir ningún archivo). Todas las librerías (`pandas`, `scikit-learn`, `matplotlib`) ya vienen instaladas en Colab.

**Opción local:**

```bash
pip install pandas scikit-learn matplotlib jupyter
jupyter notebook Herramienta_Regresion_CO2.ipynb
```

Ejecutar todas las celdas en orden (Kernel → Restart & Run All). El cuaderno detecta automáticamente si `data/raw/CO2 Emissions_Canada.csv` existe junto a él (repositorio clonado) y lo usa; si no, descarga el mismo archivo desde GitHub.

No se necesita ninguna clave, cuenta ni variable de entorno. El cuaderno no escribe nada fuera de `figuras/` (las dos imágenes de residuos).

## Qué hay en esta carpeta

| Archivo / carpeta | Contenido |
|---|---|
| [`Herramienta_Regresion_CO2.ipynb`](Herramienta_Regresion_CO2.ipynb) | El cuaderno completo: carga y limpieza de datos, partición, los tres modelos, métricas, residuos, corrección de un defecto de datos y limitaciones. Se ejecuta de principio a fin sin errores. |
| [`context.md`](context.md) | Archivo de contexto: qué se predice, qué columnas están prohibidas por fuga de información, reglas de partición, variable de subgrupos y umbral de disparidad. Es la fuente de verdad de las decisiones del proyecto — la Skill de auditoría lo lee como archivo de apoyo. |
| [`AUDIT_REPORT.md`](AUDIT_REPORT.md) | Informe **final** de auditoría (Skill v2.0), sobre el modelo ya corregido: los 15 subcriterios dan PASA. |
| [`auditorias/`](auditorias/) | Todos los informes de auditoría, sin editar, en orden cronológico: la Skill v1.4 sin extender (evidencia de qué tan reutilizable era), la v2.0 antes de la corrección (V4.2 FALLA) y la v2.0 después (PASA). También quedan los registros JSON de cada ejecución (`claude -p ... --output-format json`). |
| [`.claude/skills/auditoria-modelos/`](.claude/skills/auditoria-modelos/) | La Skill de auditoría, versión 2.0 (extendida para regresión en esta tarea; su `README.md` documenta qué cambió y por qué, y el historial completo desde la v1.0 de la Tarea 4.1). |
| [`data/raw/`](data/raw/) | El CSV original (`CO2 Emissions_Canada.csv`, 7.385 filas) y su diccionario de datos (`Data Description.csv`), sin modificar. |
| [`figuras/`](figuras/) | Gráficas de residuos guardadas por el cuaderno. |

## Resumen de resultados

- **Predice:** `CO2 Emissions(g/km)`. **Predictoras:** clase de vehículo, cilindrada, cilindros, transmisión y tipo de combustible.
- **Modelo final:** Random Forest (`n_estimators=300`, `random_state=42`), entrenado con los datos corregidos (ver más abajo). RMSE de prueba ≈ 15,91 g/km, R² de prueba ≈ 0,9313.
- **Auditoría:** la primera ejecución (Skill v2.0) encontró disparidad de error en el subgrupo diésel (V4.2 FALLA, razón RMSE 1,24 sobre un umbral de 1,10). La causa era un defecto de datos: 292 filas eran el mismo vehículo escrito con distinta capitalización en `Make`/`Model`, sin detectar por `drop_duplicates()`. Al normalizarlas antes de la partición, la disparidad desaparece (razón 1,00) y la segunda auditoría da los 15 subcriterios PASA.
- Los detalles completos (interpretación de métricas, residuos, dos intentos de corrección que no funcionaron y el que sí, y limitaciones) están en el propio cuaderno y en el informe técnico en PDF/DOCX de esta entrega.

## Ejecutar la Skill de auditoría sobre esta herramienta

Desde una terminal de Claude Code abierta en esta carpeta (la que contiene `.claude/skills/`):

```
/auditoria-modelos Herramienta_Regresion_CO2.ipynb "CO2 Emissions(g/km)" "Fuel Type"
```

O sin interfaz, como se ejecutó en esta tarea:

```bash
claude -p '/auditoria-modelos Herramienta_Regresion_CO2.ipynb "CO2 Emissions(g/km)" "Fuel Type"' \
  --allowedTools "Skill(auditoria-modelos)" "Read" "Glob" "Grep" "Write" \
  --permission-mode dontAsk
```

El informe se guarda como `AUDIT_REPORT.md` en esta misma carpeta; si ya existe, se crea con sufijo (`_2`, `_3`, …) en vez de sobrescribirlo.

## Licencia y datos

El dataset es público: [*CO2 Emission by Vehicles*](https://www.kaggle.com/datasets/debajyotipodder/co2-emission-by-vehicles) (Kaggle), tomado de los [datos abiertos del Gobierno de Canadá](https://open.canada.ca/data/en/dataset/98f1a129-f628-4ce4-b24d-6f16bf24dd64) sobre calificaciones de consumo de combustible. No contiene datos personales.
