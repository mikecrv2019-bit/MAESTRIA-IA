# Informe de auditoría — housing.csv

- **Archivos auditados:** `C:\Users\jaimelopez\Documents\ATLANTIS UNIVERSITY 2026 - 2027\MAI540 - SEP 01 2026 - OCT 08 2026\MODULO 4\housing.csv`
- **Archivos de apoyo leídos:** ninguno (no hay `README.md`, `context.md`, `DESCRIPCION.md` ni informes `.md` del autor en la carpeta)
- **Columna objetivo:** `median_house_value` — codificación: variable continua (valor monetario), no aplica codificación de clases (evidencia: `housing.csv:1` encabezado, `housing.csv:2` `...,8.3252,452600.0,NEAR BAY`)
- **Tipo de problema:** regresión (evidencia: `housing.csv:2-30`, la columna `median_house_value` toma valores numéricos continuos distintos fila a fila, p. ej. `452600.0`, `358500.0`, `352100.0`)
- **Subgrupos:** `ocean_proximity` (origen: argumento entregado; evidencia: `housing.csv:1` encabezado, `housing.csv:2` valor `NEAR BAY`)
- **Skill:** auditoria-modelos v1.4 — fecha: 2026-09-24
- **Modificaciones al proyecto:** ninguna (auditoría de solo lectura)

## Resumen

| Verificación | Resultado |
|---|---|
| V1 Métricas reportadas | NO SE PUEDE DETERMINAR |
| V2 Partición de datos | NO SE PUEDE DETERMINAR |
| V3 Fuga de información | NO SE PUEDE DETERMINAR |
| V4 Disparidad entre subgrupos | NO SE PUEDE DETERMINAR |
| V5 Validez de datos de entrada | NO SE PUEDE DETERMINAR |
| V6 Variables no admisibles | NO SE PUEDE DETERMINAR |

## Tabla de verificación

| ID | Verificación | Resultado | Evidencia | Observación |
|---|---|---|---|---|
| V1.1 | Rango válido | NO SE PUEDE DETERMINAR | `housing.csv` (archivo de datos, sin salidas de modelo) | No hay código de modelo que auditar; `housing.csv` solo contiene datos crudos, ninguna métrica reportada. |
| V1.2 | Consistencia con la matriz | NO SE PUEDE DETERMINAR | — | No hay código de modelo que auditar; no existe matriz de confusión. |
| V1.3 | Clase positiva correcta | NO SE PUEDE DETERMINAR | `housing.csv:1-2` | El problema es de regresión (target continuo), no aplica el concepto de clase positiva. |
| V1.4 | No solo accuracy con desbalance | NO SE PUEDE DETERMINAR | `housing.csv:1-2` | El problema es de regresión; el concepto de desbalance de clases y accuracy no aplica. Además, no hay código de modelo que auditar. |
| V1.5 | Métrica acorde al costo | NO SE PUEDE DETERMINAR | — | No hay código de modelo que auditar; el proyecto no declara costos de error (no hay archivos de apoyo ni código). |
| V2.1 | División antes del preprocesamiento que aprende | NO SE PUEDE DETERMINAR | — | No hay código de modelo que auditar; no existe ningún `fit`/`fit_transform`. |
| V2.2 | Semilla fija | NO SE PUEDE DETERMINAR | — | No hay código de modelo que auditar; no existe ninguna operación aleatoria. |
| V2.3 | Estratificación | NO SE PUEDE DETERMINAR | `housing.csv:1-30` | El problema es de regresión (evidencia arriba); la estratificación de clases no aplica. Además, no hay código de partición que auditar. |
| V2.4 | Misma partición para los modelos comparados | NO SE PUEDE DETERMINAR | — | No hay código de modelo que auditar; no hay ningún modelo ni comparación entre modelos. |
| V3.1 | Nada se ajusta con datos de prueba | NO SE PUEDE DETERMINAR | — | No hay código de modelo que auditar; no existe partición entrenamiento/prueba. |
| V3.2 | Ninguna columna posterior a la predicción | NO SE PUEDE DETERMINAR | `housing.csv:1` encabezado: `longitude,latitude,housing_median_age,total_rooms,total_bedrooms,population,households,median_income,median_house_value,ocean_proximity` | No hay código ni documentación que indique cuándo se conoce cada columna respecto al momento de predicción; no hay código de modelo que auditar. |
| V4.1 | Métrica por subgrupo | NO SE PUEDE DETERMINAR | `housing.csv:1-2` (existe la columna `ocean_proximity`) | La variable de subgrupo existe en los datos, pero no hay código de modelo que auditar, por lo que no se puede calcular ninguna métrica por subgrupo. |
| V4.2 | Disparidad dentro del umbral | NO SE PUEDE DETERMINAR | — | V4.1 no es PASA (no hay código de modelo que auditar). |
| V5.1 | Sin `inf`/`NaN` al entrenar | NO SE PUEDE DETERMINAR | `housing.csv:292`: `-122.16,37.77,47.0,1256.0,,570.0,218.0,4.375,161900.0,NEAR BAY` (valor vacío en `total_bedrooms`; se cuentan 207 filas con este patrón en todo el archivo) | Los datos crudos contienen valores faltantes en `total_bedrooms` (evidencia citada), pero no hay código de modelo que muestre si se tratan (imputación, eliminación) antes de un `fit`. |
| V6.1 | Sin identificadores ni atributos prohibidos | NO SE PUEDE DETERMINAR | `housing.csv:1` encabezado: `longitude,latitude,housing_median_age,total_rooms,total_bedrooms,population,households,median_income,median_house_value,ocean_proximity` | No hay código que defina la lista final de predictoras ni documentación que declare atributos prohibidos; el encabezado no muestra un identificador único evidente, pero no se puede confirmar la lista de predictoras sin código. |

## Acciones recomendadas

1. **[V1.1]** Agregar el código de entrenamiento/evaluación del modelo (notebook o script) y ejecutar sus celdas para dejar salidas guardadas con las métricas reportadas. (prioridad: media)
2. **[V1.2]** Incluir en el código el cálculo de la matriz de confusión y de las métricas derivadas de ella, con las salidas guardadas. (prioridad: media)
3. **[V1.3]** Documentar en el código la codificación de `median_house_value` o, si se transforma a clasificación, la codificación de las clases y confirmar qué etiqueta corresponde a `pos_label`. (prioridad: media)
4. **[V1.4]** Si el problema se plantea como clasificación en algún momento, calcular y reportar exhaustividad, precisión o F1 además de accuracy cuando exista desbalance. (prioridad: media)
5. **[V1.5]** Declarar en un archivo de apoyo (`context.md` o similar) o en una celda de texto cuál error (sobreestimar vs. subestimar `median_house_value`) es más costoso, y alinear la métrica prioritaria (p. ej. MAE, RMSE) con ese costo. (prioridad: media)
6. **[V2.1]** Agregar el código de preprocesamiento (imputación de `total_bedrooms`, escalado, codificación de `ocean_proximity`) dentro de un `Pipeline` ajustado solo con datos de entrenamiento. (prioridad: media)
7. **[V2.2]** Fijar `random_state` en cualquier `train_test_split` u operación aleatoria que se agregue. (prioridad: media)
8. **[V2.3]** Si se deriva una variable categórica del `median_house_value` para convertirlo en clasificación, usar `stratify=y` en la partición. (prioridad: media)
9. **[V2.4]** Si se comparan varios modelos, usar la misma `X`, `y`, esquema de partición y semilla para todos. (prioridad: media)
10. **[V3.1]** Asegurar que ninguna decisión de preprocesamiento, selección de variables o umbral se tome mirando el conjunto de prueba. (prioridad: media)
11. **[V3.2]** Documentar, para cada predictora, que se conoce en el momento de predecir (todas las columnas del censo parecen conocerse antes de la venta, pero esto debe declararse explícitamente). (prioridad: media)
12. **[V4.1]** Calcular la métrica de evaluación por separado para cada valor de `ocean_proximity` y guardar la salida. (prioridad: media)
13. **[V4.2]** Con la métrica por subgrupo ya calculada, verificar que ningún subgrupo con ≥ 20 casos supere 0.10 de diferencia frente a la métrica global. (prioridad: media)
14. **[V5.1]** Tratar los valores faltantes de `total_bedrooms` (207 filas, evidencia citada) mediante imputación dentro del pipeline de entrenamiento, ajustada solo con datos de entrenamiento. (prioridad: alta)
15. **[V6.1]** Al definir la lista final de predictoras en el código, confirmar que no se incluya ningún identificador único ni atributo declarado prohibido. (prioridad: media)

## Limitaciones de esta auditoría

- `housing.csv` es únicamente un archivo de datos crudos; no contiene ningún notebook (`.ipynb`) ni script (`.py`) que cargue, entrene o evalúe un modelo. Por esta razón, los 15 subcriterios quedan en NO SE PUEDE DETERMINAR: no existe código que auditar para partición, preprocesamiento, fuga de información, métricas ni variables finalmente usadas por un modelo.
- No se encontraron archivos de apoyo (`README.md`, `context.md`, `DESCRIPCION.md` o informes `.md`) en la carpeta `MODULO 4` que declaren el costo de los errores, las variables prohibidas o el momento en que se conoce cada columna.
- Se verificó directamente sobre los datos (sin ejecutar código) que la columna `total_bedrooms` tiene 207 filas con valor vacío (NaN al cargar), lo cual deberá tratarse cuando exista un pipeline de entrenamiento.
