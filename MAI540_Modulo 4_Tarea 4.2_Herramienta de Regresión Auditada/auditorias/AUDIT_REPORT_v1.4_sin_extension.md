# Informe de auditoría — Herramienta de Regresión Auditada — Emisiones de CO₂

- **Archivos auditados:** `Herramienta_Regresion_CO2.ipynb`
- **Archivos de apoyo leídos:** `context.md`
- **Columna objetivo:** `CO2 Emissions(g/km)` — variable continua en g/km, sin codificación de clases (evidencia: celda [3] (id=3749828d) `TARGET = "CO2 Emissions(g/km)"`)
- **Tipo de problema:** regresión (evidencia: celda [15] (id=11daaa64) `"Referencia (media)": DummyRegressor(strategy="mean")` junto con `LinearRegression()` y `RandomForestRegressor(...)`; context.md:3 "Construir y evaluar un modelo de regresión supervisada...")
- **Subgrupos:** `Fuel Type` (origen: no se entregó el argumento; encontrado en celda [3] (id=3749828d) `SUBGRUPO = "Fuel Type"` y en context.md:33)
- **Skill:** auditoria-modelos v1.4 — fecha: 2026-09-25
- **Modificaciones al proyecto:** ninguna (auditoría de solo lectura)

## Resumen

| Verificación | Resultado |
|---|---|
| V1 Métricas reportadas | NO SE PUEDE DETERMINAR |
| V2 Partición de datos | NO SE PUEDE DETERMINAR |
| V3 Fuga de información | PASA |
| V4 Disparidad entre subgrupos | FALLA |
| V5 Validez de datos de entrada | PASA |
| V6 Variables no admisibles | PASA |

## Tabla de verificación

| ID | Verificación | Resultado | Evidencia | Observación |
|---|---|---|---|---|
| V1.1 | Rango válido | NO SE PUEDE DETERMINAR | celda [15] (id=11daaa64) `"Referencia (media)": DummyRegressor(strategy="mean")` — no hay accuracy, precisión, exhaustividad, F1 ni AUC en ninguna salida | El proyecto es de regresión; las métricas de tipo proporción de V1.1 (accuracy, precisión, exhaustividad, F1, AUC) no aparecen porque no aplican a este tipo de problema. |
| V1.2 | Consistencia con la matriz | NO SE PUEDE DETERMINAR | Ninguna celda contiene una matriz de confusión (búsqueda en las 36 celdas) | No hay matriz de confusión porque el problema es de regresión, no de clasificación. |
| V1.3 | Clase positiva correcta | NO SE PUEDE DETERMINAR | celda [3] (id=3749828d) `TARGET = "CO2 Emissions(g/km)"` | La variable objetivo es continua; no existen clases ni "clase positiva" que codificar. |
| V1.4 | No solo accuracy con desbalance | NO SE PUEDE DETERMINAR | celda [19] (id=aaf0fe1c) `mse_te = mean_squared_error(y_test, pred_test[nombre])` | El criterio exige desbalance de clases y uso de accuracy; el objetivo es continuo, no hay clases que desbalancear ni se calcula accuracy. |
| V1.5 | Métrica acorde al costo | NO SE PUEDE DETERMINAR | context.md:106 `\| RMSE (g/km) \| PRINCIPAL \| Error típico en las unidades del problema. \|` | Es un problema de regresión sin clases; no se declara un costo asimétrico entre sobreestimar y subestimar el CO₂ (el criterio está definido en términos de FN/FP de clasificación). RMSE, simétrico, es la métrica principal declarada. |
| V2.1 | División antes del preprocesamiento que aprende | PASA | celda [15] (id=11daaa64) `pipe.fit(X_train, y_train)          # ajuste SOLO con entrenamiento` | El `ColumnTransformer` (imputar/codificar/escalar, celda [13] id=c77cd786) vive dentro del `Pipeline` y se ajusta después de la partición (celda [11] id=2f47fbd4). Verificado en celda [17] (id=63559f8b): la media aprendida por el escalador coincide con la del entrenamiento, no con la del dataset completo. |
| V2.2 | Semilla fija | PASA | celda [3] (id=3749828d) `RANDOM_STATE = 42` | Se usa en `train_test_split` (celda [11] id=2f47fbd4, `random_state=RANDOM_STATE`) y en `RandomForestRegressor` (celda [15] id=11daaa64, `random_state=RANDOM_STATE`). No hay otras operaciones aleatorias en el proyecto. |
| V2.3 | Estratificación | NO SE PUEDE DETERMINAR | celda [15] (id=11daaa64) estimadores de regresión (`DummyRegressor`, `LinearRegression`, `RandomForestRegressor`) | El criterio V2.3 exige `stratify=y` solo en clasificación; aquí el objetivo es continuo, por lo que no aplica. (El proyecto sí estratifica `train_test_split` por la variable de subgrupo `Fuel Type`, celda [11] id=2f47fbd4 `stratify=X.loc[~es_n, SUBGRUPO]`, una práctica adicional no exigida por este criterio). |
| V2.4 | Misma partición para los modelos comparados | PASA | celda [15] (id=11daaa64) `for nombre, modelo in modelos.items(): pipe = Pipeline([("prep", crear_preprocesador()), ("modelo", modelo)])` | Los tres modelos (Referencia, Regresión lineal, Random Forest) se entrenan en el mismo bucle con el mismo `X_train`/`y_train` y se evalúan con el mismo `X_test`/`y_test`, cada uno con su propio preprocesamiento dentro de su propio `Pipeline`. |
| V3.1 | Nada se ajusta con datos de prueba | PASA | celda [17] (id=63559f8b) `Media aprendida por el escalador: [3.1562 5.6101]` / `Media del entrenamiento:          [3.1562 5.6101]` | El pipeline se ajusta solo con `X_train` (celda [15]); no hay `GridSearchCV` ni selección de umbral que use el conjunto de prueba. Los hiperparámetros del Random Forest (`n_estimators=300`) están fijados de antemano, no ajustados por CV. |
| V3.2 | Ninguna columna posterior a la predicción | PASA | celda [3] (id=3749828d) `"Fuel Consumption Comb (L/100 km)",   # fuga: el CO2 se calcula a partir de este consumo` | Las cuatro columnas de consumo (fuente de fuga) están en `PROHIBIDAS` y se eliminan antes de separar `y` (celda [9] id=87af10e2). Justificación cuantitativa en context.md:35-54 (R² ≥ 0.98 de CO₂ contra consumo combinado por tipo de combustible). Las 5 predictoras finales son especificaciones conocidas antes de la homologación (context.md:31). No hay señal de alarma: R² de prueba máximo = 0.9334 (Random Forest, celda [19] id=aaf0fe1c), muy por debajo de 0.99. |
| V4.1 | Métrica por subgrupo | PASA | celda [35] (id=1211b909), salida: `D                37               19.0633` | El RMSE de prueba se calcula por separado para cada valor de `Fuel Type` (X, Z, E, D, N) y para los tres modelos, en una salida guardada. |
| V4.2 | Disparidad dentro del umbral | FALLA | celda [35] (id=1211b909), salida: `D                           1.2407` | Umbral propio y justificado del proyecto (context.md:114): "el RMSE de prueba de un subgrupo de `Fuel Type` dividido por el RMSE global de prueba del mismo modelo debe ser ≤ 1,10". Para Random Forest (el modelo declarado como mejor, celda [21] id=86b5b495), el subgrupo Diésel (D, n=37 en prueba, ≥ 20) tiene razón 19.0633/15.3653 = 1.2407 (RMSE global de prueba de Random Forest: celda [19] id=aaf0fe1c, `Random Forest                 236.0910             15.3653     0.9334`), 24.07 % por encima del global, superando el umbral de 1.10. Los subgrupos X, Z y E (todos con ≥ 20 casos) sí cumplen el umbral, y ningún subgrupo de Referencia ni de Regresión lineal lo supera. |
| V5.1 | Sin `inf`/`NaN` al entrenar | PASA | celda [9] (id=87af10e2), salida: `Nulos en X: 0 \| Nulos en y: 0` | No hay operaciones de división ni uniones que puedan generar `inf`/`NaN` en la construcción de `X`; los predictores se toman directamente de las columnas del CSV (celda [9]). Se usa `SimpleImputer` (mediana/moda) dentro del pipeline (celda [13] id=c77cd786) como protección ante datos nuevos, aunque hoy no hay nulos (decisión declarada en la celda [2] id=94ff82c0). |
| V6.1 | Sin identificadores ni atributos prohibidos | PASA | celda [9] (id=87af10e2), salida: `Predictoras: ['Vehicle Class', 'Engine Size(L)', 'Cylinders', 'Transmission', 'Fuel Type']` | `Make` y `Model` (identificador casi único, 2.053 valores) están excluidos (context.md:32); las cuatro variables de consumo prohibidas por fuga también están excluidas (celda [3] id=3749828d, lista `PROHIBIDAS`). Ninguna de las 5 predictoras finales es un identificador ni un atributo declarado prohibido. |

## Acciones recomendadas

1. **[V4.2]** Investigar la disparidad de RMSE del subgrupo Diésel (D) en Random Forest (razón 1.2407, 24.07 % por encima del RMSE global de prueba), que supera el umbral de ≤ 1.10 que el propio proyecto declaró en context.md:114. Posibles causas a revisar: el tamaño reducido de D (147 filas totales, 37 en prueba) o una relación motor/combustible mal representada para diésel en el entrenamiento. Si no se corrige, documentar explícitamente esta limitación de desempeño por tipo de combustible en las conclusiones del proyecto, ya que afecta directamente la decisión de homologación que la herramienta pretende apoyar. (prioridad: alta)
2. **[V1.1]** No requiere acción de código: registrar explícitamente en el proyecto que las métricas de proporción de V1.1 (accuracy, precisión, exhaustividad, F1, AUC) no aplican por ser un problema de regresión, para que auditorías futuras no repitan la misma pregunta. (prioridad: media)
3. **[V1.2]** No requiere acción de código: no existe matriz de confusión porque no es un problema de clasificación; dejarlo señalado en el proyecto. (prioridad: media)
4. **[V1.3]** No requiere acción de código: no hay codificación de clase positiva que verificar en un objetivo continuo; dejarlo señalado en el proyecto. (prioridad: media)
5. **[V1.4]** No requiere acción de código: no hay clases que desbalancear ni se usa accuracy; dejarlo señalado en el proyecto. (prioridad: media)
6. **[V1.5]** Si en algún uso futuro de la herramienta sobreestimar el CO₂ (posible rechazo injustificado de una configuración que sí cumple) y subestimarlo (riesgo de aprobar una configuración que no cumple) tuvieran costos distintos para la decisión de homologación, declarar explícitamente cuál pesa más y considerar una métrica o un margen de decisión asimétrico en vez de RMSE simétrico. (prioridad: media)
7. **[V2.3]** No requiere acción de código: `stratify=y` no aplica a un objetivo continuo; dejarlo señalado en el proyecto para que quede claro por qué V2.3 no se evalúa como PASA/FALLA. (prioridad: media)

## Limitaciones de esta auditoría

- Los subcriterios V1.1 a V1.4 y V2.3 de esta Skill están formulados en términos de clasificación (clases, accuracy, matriz de confusión, `stratify=y`). Como este proyecto es de regresión, esos subcriterios se registraron como NO SE PUEDE DETERMINAR con el motivo "no aplica", siguiendo la regla 3 de la Skill; no reflejan un defecto del proyecto.
- El umbral de disparidad de V4.2 en esta Skill está definido como diferencia absoluta de 0.10 sobre una métrica de proporción en [0, 1]. Como la métrica prioritaria aquí es RMSE (en g/km, sin cota superior), se usó en su lugar el umbral relativo que el propio proyecto declaró y justificó en context.md:114 (razón subgrupo/global ≤ 1.10), equivalente en espíritu al umbral de 0.10 del proyecto Telco citado ahí mismo.
- El notebook no tiene, después de la celda [35] (id=1211b909), ninguna celda de interpretación escrita sobre si algún subgrupo supera el umbral de disparidad declarado; esta auditoría evaluó el umbral directamente sobre la salida numérica de esa celda.
- No se leyó `data/raw/Data Description.csv` (es un diccionario de datos, no un informe de contexto del autor); no afecta los veredictos porque las columnas relevantes ya están descritas y justificadas en `context.md`.
