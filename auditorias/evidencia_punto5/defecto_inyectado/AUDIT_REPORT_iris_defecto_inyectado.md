# Informe de auditoría — Iris_con_defecto_escalado

- **Archivos auditados:** `Iris_con_defecto_escalado.ipynb`
- **Archivos de apoyo leídos:** ninguno (no hay `README.md`, `context.md`, `DESCRIPCION.md` ni informes `.md` del autor en la carpeta del proyecto)
- **Columna objetivo:** `target` (especie de flor) — codificación: 0 = setosa, 1 = versicolor, 2 = virginica (evidencia: celda [4] (id=4abcd0e9) `df['especie'] = df['target'].map(dict(enumerate(iris.target_names)))`, `y = iris.target.values`)
- **Tipo de problema:** clasificación multiclase (3 clases) (evidencia: celda [4] (id=4abcd0e9) `y = iris.target.values`; celda [2] (id=a16e5791) importa `LogisticRegression`, `DecisionTreeClassifier`, `GaussianNB` como clasificadores)
- **Subgrupos:** ninguno (origen: argumento `target: ninguna` entregado por el usuario; confirmado por inspección — las predictoras del proyecto son mediciones florales (`sepal length`, `sepal width`, `petal length`, `petal width`), sin atributos protegidos ni proxies)
- **Skill:** auditoria-modelos v1.1 — fecha: 2026-09-24
- **Modificaciones al proyecto:** ninguna (auditoría de solo lectura)

## Resumen

| Verificación | Resultado |
|---|---|
| V1 Métricas reportadas | NO SE PUEDE DETERMINAR |
| V2 Partición de datos | FALLA |
| V3 Fuga de información | FALLA |
| V4 Disparidad entre subgrupos | NO SE PUEDE DETERMINAR |
| V5 Validez de datos de entrada | PASA |
| V6 Variables no admisibles | PASA |

## Tabla de verificación

| ID | Verificación | Resultado | Evidencia | Observación |
|---|---|---|---|---|
| V1.1 | Rango válido | PASA | celda [13] (id=baf5d90f), salida: `Regresión logística: media=0.9667 ... mínimo=0.933 máximo=1.000`; celda [15] (id=m41_knn_rf_code), salida: `KNN (...): media=0.9600 ... mínimo=0.867 máximo=1.000`; celda [19] (id=534deae5), salida: `Árbol (max_depth=2): media=0.9200 ...` | Todas las cifras de accuracy reportadas (medias, mínimos, máximos de las 10 particiones, y las de las cinco comparaciones adicionales) están dentro de [0, 1]. |
| V1.2 | Consistencia con la matriz | NO SE PUEDE DETERMINAR | — | No hay matriz de confusión en ninguna salida guardada del notebook; solo se reporta accuracy vía `cross_val_score`. No es posible recalcular ninguna métrica desde una matriz que no existe. |
| V1.3 | Clase positiva correcta | NO SE PUEDE DETERMINAR | — | El notebook no reporta ninguna métrica atribuida a una clase específica (no hay `classification_report` ni precisión/exhaustividad por clase; solo accuracy global sobre las 3 clases). No aplica verificar `pos_label` porque no existe ninguna métrica de ese tipo en las salidas. |
| V1.4 | No solo accuracy con desbalance | NO SE PUEDE DETERMINAR | — | Ninguna salida guardada del notebook muestra la distribución de `target`/`especie` (el `df.head()` de la celda [4] (id=4abcd0e9) solo muestra las primeras 5 filas, todas `setosa`). Sin esa distribución citada, no se puede calcular la razón mayoritaria/minoritaria exigida por la definición de desbalance de esta auditoría. |
| V1.5 | Métrica acorde al costo | NO SE PUEDE DETERMINAR | — | Es un problema multiclase (clasificar especie) sin una clase de interés declarada ni costos distintos de FN/FP entre especies en el texto del notebook (celda [0] (id=2c087a52) solo describe el objetivo como "automatizar la clasificación de especies", sin priorizar ninguna). |
| V2.1 | División antes del preprocesamiento que aprende | FALLA | celda [15] (id=m41_knn_rf_code): `flujo = Pipeline([('knn', KNeighborsClassifier()),])` (sin paso de escalado) y luego `X_escalado = StandardScaler().fit_transform(X)  # escalado de todo X antes de la validación cruzada` seguido de `scores_knn = evaluar_con_cv(construir_knn_con_seleccion_de_k(), X_escalado, y, ...)` | El `Pipeline` que se pasa a `evaluar_con_cv`/`cross_val_score` **no contiene** `StandardScaler` (solo tiene el paso `'knn'`). El escalado se hace una sola vez sobre las 150 muestras completas de `X` **antes** de que `cross_val_score` divida en las 10 particiones, así que cada partición de entrenamiento se beneficia de una media y desviación estándar calculadas incluyendo los datos que luego actúan como validación en esa misma partición. |
| V2.2 | Semilla fija | PASA | celda [2] (id=a16e5791): `RANDOM_STATE = 42`; celda [12] (id=a37aa1ce): `cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)`; celda [15] (id=m41_knn_rf_code): `cv_interna = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)` y `cv_externa = StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)` | Todas las particiones (`StratifiedKFold` externa e interna) y los modelos con componente aleatorio (`DecisionTreeClassifier`, `RandomForestClassifier`) usan `random_state=RANDOM_STATE`, un entero fijo (42) definido una sola vez, no un `RandomState` global que avance entre llamadas. |
| V2.3 | Estratificación | PASA | celda [12] (id=a37aa1ce): `cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)`; celda [15] (id=m41_knn_rf_code): `cv_interna = StratifiedKFold(...)`, `cv_externa = StratifiedKFold(...)` | Es clasificación (multiclase) y no se usa ningún `train_test_split` en el notebook (sin coincidencias al buscarlo); toda partición, externa e interna, es `StratifiedKFold`. |
| V2.4 | Misma partición para los modelos comparados | PASA | celda [13] (id=baf5d90f) y celda [15] (id=m41_knn_rf_code): los 5 modelos (regresión logística, árbol, Naive Bayes, KNN, Random Forest) se evalúan con la misma función `evaluar_con_cv(modelo, X_o_X_escalado, y, nombre)`, que internamente crea `StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)` | Los 5 modelos pasan por la misma función de evaluación, el mismo `y` y el mismo esquema/semilla de partición (`StratifiedKFold` estratifica por `y`, así que los índices de cada partición son iguales para los 5 modelos). La única diferencia es que KNN recibe `X_escalado` en vez de `X` crudo (mismas 150 filas, transformadas) — esto no cambia el esquema de partición, pero la fuga que contiene `X_escalado` ya se registra en V2.1 y V3.1. |
| V3.1 | Nada se ajusta con datos de prueba | FALLA | celda [15] (id=m41_knn_rf_code): `X_escalado = StandardScaler().fit_transform(X)  # escalado de todo X antes de la validación cruzada` | El `StandardScaler` se ajusta (`fit_transform`) sobre las 150 muestras completas, incluidas las que en cada una de las 10 particiones externas de `cross_val_score` actúan como conjunto de validación. Esto contradice lo que la celda [14] (id=m41_knn_rf_md) documenta como diseño ("el escalador se ajusta solo con los datos de entrenamiento de esa partición"): el código no hace lo que el texto describe. La selección de `k` sí está correctamente anidada (el `GridSearchCV` se clona y ajusta dentro de cada partición externa), pero eso no evita la fuga del escalado, que ocurre antes de cualquier partición. |
| V3.2 | Ninguna columna posterior a la predicción | PASA | celda [4] (id=4abcd0e9): `X = iris.data.values`, `y = iris.target.values` | Las 4 predictoras (`sepal length`, `sepal width`, `petal length`, `petal width`) provienen de `iris.data`, un arreglo fijo del dataset, independiente de `iris.target`/`df['especie']`. Ninguna predictora se construye a partir de la variable objetivo. |
| V4.1 | Métrica por subgrupo | NO SE PUEDE DETERMINAR | — | No hay ninguna variable de subgrupo en el proyecto: las únicas columnas son mediciones florales (`sepal length/width`, `petal length/width`), y el usuario indicó explícitamente `target: ninguna`. No existen atributos protegidos ni proxies aplicables a este dataset. |
| V4.2 | Disparidad dentro del umbral | NO SE PUEDE DETERMINAR | — | Depende de V4.1, que es NO SE PUEDE DETERMINAR por ausencia de variables de subgrupo. |
| V5.1 | Sin `inf`/`NaN` al entrenar | PASA | celda [4] (id=4abcd0e9): `iris = load_iris(as_frame=True)`, `X = iris.data.values`; salida de `df.head()` muestra valores numéricos válidos (p. ej. `5.1  3.5  1.4  0.2`) | Los datos provienen directamente de `load_iris`, sin divisiones entre columnas, sin `errors="coerce"` ni uniones externas que puedan producir `inf`/`NaN`. No existe ninguna operación de ese tipo en el notebook. |
| V6.1 | Sin identificadores ni atributos prohibidos | PASA | celda [4] (id=4abcd0e9), salida `df.head()`: columnas `sepal length (cm)`, `sepal width (cm)`, `petal length (cm)`, `petal width (cm)` | Las predictoras son medidas morfológicas continuas, no identificadores únicos por fila, y el proyecto no declara ningún atributo prohibido. |

## Acciones recomendadas

1. **[V2.1 / V3.1]** Corregir la fuga de información en la evaluación de KNN: agregar `('scaler', StandardScaler())` como paso dentro del `Pipeline` de `construir_knn_con_seleccion_de_k()` (antes del paso `'knn'`), y pasar `X` sin escalar previamente a `evaluar_con_cv(...)`, eliminando la línea `X_escalado = StandardScaler().fit_transform(X)`. Así el escalador se ajustará solo con los datos de entrenamiento de cada partición, tal como ya describe (incorrectamente, respecto al código actual) la celda [14] (id=m41_knn_rf_md). Prioridad: alta.
2. **[V1.2]** Agregar una matriz de confusión (p. ej. con `cross_val_predict` + `confusion_matrix`) a las salidas guardadas, para poder verificar que las métricas reportadas son consistentes con los aciertos/errores reales. Prioridad: media.
3. **[V1.3]** Si en el futuro se reportan métricas por clase (precisión, exhaustividad, F1 de una especie particular), usar `classification_report` con `target_names` o especificar `pos_label`/`labels` explícitamente, y guardar esa salida. Prioridad: media.
4. **[V1.4]** Guardar en una salida la distribución de `target`/`especie` (p. ej. `df['especie'].value_counts()`), para poder documentar si el dataset está balanceado y así justificar el uso de accuracy sola. Prioridad: media.
5. **[V1.5]** Si el proyecto tiene una especie cuya mala clasificación sea más costosa que las otras (p. ej. por riesgo operativo del vivero), declararlo explícitamente en el texto y ajustar la métrica prioritaria; si no la hay, dejar constancia explícita de que las tres especies tienen igual costo de error. Prioridad: media.

## Limitaciones de esta auditoría

- El notebook solo reporta accuracy (vía `cross_val_score`); no hay matriz de confusión ni métricas por clase guardadas, lo que impide verificar V1.2 y V1.3 con evidencia.
- No hay ninguna salida guardada que muestre la distribución de la variable objetivo por especie, lo que impide calcular la razón de desbalance exigida por V1.4 (aunque el texto menciona "150 muestras, 3 especies", no especifica cuántas por especie).
- El problema es multiclase sin clase de interés ni costos de error declarados, lo que deja V1.5 sin poder determinarse.
- El dataset (mediciones florales) no contiene atributos protegidos ni proxies, y el usuario confirmó `target: ninguna`, por lo que V4.1 y V4.2 no se pueden evaluar.
