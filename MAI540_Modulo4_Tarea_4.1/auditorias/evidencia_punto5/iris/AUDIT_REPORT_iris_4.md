# Informe de auditoría — Comparación de Clasificadores Iris

- **Archivos auditados:** `C:\Users\jaimelopez\Documents\ATLANTIS UNIVERSITY 2026 - 2027\MAI540 - SEP 01 2026 - OCT 08 2026\MODULO 3\iris-clasificadores-repo\App_Comparacion_Clasificadores_Iris.ipynb`
- **Archivos de apoyo leídos:** `README.md` (no se encontró `context.md` ni `DESCRIPCION.md` en la carpeta del proyecto)
- **Columna objetivo:** `target` (mapeada a `especie`) — codificación: 0 = setosa, 1 = versicolor, 2 = virginica (evidencia: celda [4] (id=4abcd0e9), código `df['especie'] = df['target'].map(dict(enumerate(iris.target_names)))`, salida `df.head()`: fila con `target=0, especie=setosa`)
- **Tipo de problema:** clasificación multiclase (3 especies) (evidencia: celda [4] (id=4abcd0e9) `y = iris.target.values`; celda [12] (id=a37aa1ce) usa `StratifiedKFold` con clasificadores)
- **Subgrupos:** ninguno (origen: argumento `target ninguna`; no se encontraron atributos protegidos ni proxies en las columnas del proyecto — celda [4] (id=4abcd0e9) solo contiene medidas florales)
- **Skill:** auditoria-modelos v1.3 — fecha: 2026-09-24
- **Modificaciones al proyecto:** ninguna (auditoría de solo lectura)

## Resumen

| Verificación | Resultado |
|---|---|
| V1 Métricas reportadas | NO SE PUEDE DETERMINAR |
| V2 Partición de datos | PASA |
| V3 Fuga de información | PASA |
| V4 Disparidad entre subgrupos | NO SE PUEDE DETERMINAR |
| V5 Validez de datos de entrada | PASA |
| V6 Variables no admisibles | PASA |

## Tabla de verificación

| ID | Verificación | Resultado | Evidencia | Observación |
|---|---|---|---|---|
| V1.1 | Rango válido | PASA | celda [13] (id=baf5d90f), salida: `Regresión logística: media=0.9667 desviación estándar=0.0333 mínimo=0.933 máximo=1.000` | Todas las cifras de accuracy reportadas (medias, mínimos, máximos) para los 5 clasificadores están en [0, 1]. |
| V1.2 | Consistencia con la matriz | NO SE PUEDE DETERMINAR | — | No hay ninguna matriz de confusión (`confusion_matrix`) en las salidas guardadas del notebook; solo se reportan accuracy promedio, desviación estándar, mínimo y máximo de `cross_val_score`. |
| V1.3 | Clase positiva correcta | NO SE PUEDE DETERMINAR | celda [4] (id=4abcd0e9): `target=0` ↔ `especie=setosa` | La codificación de clases sí se conoce, pero el notebook nunca reporta una métrica atribuida a una clase específica (no hay `classification_report`, ni precisión/exhaustividad por especie); solo accuracy global multiclase. El subcriterio no tiene sobre qué evaluarse. |
| V1.4 | No solo accuracy con desbalance | NO SE PUEDE DETERMINAR | — | El notebook nunca muestra la distribución de clases (no hay salida de `value_counts()` ni equivalente sobre `target`/`especie`), así que no se puede calcular la razón de desbalance según la regla de la Skill (debe venir de una salida citada del propio proyecto). |
| V1.5 | Métrica acorde al costo | NO SE PUEDE DETERMINAR | celdas [27]-[28] (id=e898a578, id=4c3a4d58) | El proyecto es de clasificación multiclase balanceada (3 especies de flores) sin ninguna clase de interés declarada ni costos distintos por tipo de error (confundir *versicolor* con *virginica* no se trata como más o menos costoso que cualquier otro error). No hay clase de interés ni costos declarados. |
| V2.1 | División antes del preprocesamiento que aprende | PASA | celda [15] (id=m41_knn_rf_code): `Pipeline([('escalador', StandardScaler()), ('knn', KNeighborsClassifier())])` dentro de `GridSearchCV(flujo, ..., cv=cv_interna)`, pasado sin ajustar a `evaluar_con_cv` (celda [12], id=a37aa1ce) que lo evalúa con `cross_val_score` | El único transformador que aprende de los datos (`StandardScaler`, para KNN) está dentro de un `Pipeline`/`GridSearchCV` que `cross_val_score` clona y ajusta en cada partición de entrenamiento. Los demás modelos (regresión logística, árbol, Naive Bayes, Random Forest) no usan preprocesamiento que aprenda de los datos. |
| V2.2 | Semilla fija | PASA | celda [2] (id=a16e5791): `RANDOM_STATE = 42`; celda [12] (id=a37aa1ce): `StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)`; celda [9] (id=ddd20eb3): `DecisionTreeClassifier(max_depth=3, random_state=RANDOM_STATE)` | `RANDOM_STATE=42` es un entero (no un objeto `RandomState` compartido que avance entre llamadas) y se pasa consistentemente a `StratifiedKFold`, `DecisionTreeClassifier` y `RandomForestClassifier`, tanto en la CV externa como en la interna (celda [15]). |
| V2.3 | Estratificación | PASA | celda [12] (id=a37aa1ce): `StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)`; celda [15] (id=m41_knn_rf_code): `cv_interna = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)` | Es clasificación multiclase y todas las particiones (externa e interna del `GridSearchCV` de KNN) usan `StratifiedKFold`. No hay ningún `train_test_split` sin estratificar en el notebook. |
| V2.4 | Misma partición para los modelos comparados | PASA | celda [13] (id=baf5d90f) y celda [15] (id=m41_knn_rf_code): `evaluar_con_cv(modelo, X, y, nombre)` para los 5 modelos, con `X`, `y` definidos una sola vez en celda [4] (id=4abcd0e9) | Los cinco clasificadores (regresión logística, árbol, Naive Bayes, KNN, Random Forest) se evalúan con la misma función `evaluar_con_cv`, el mismo `X`/`y` sin transformar fuera del estimador, y el mismo esquema y semilla de partición. El escalado de KNN va dentro del `Pipeline` evaluado, lo cual es la excepción válida de la regla. |
| V3.1 | Nada se ajusta con datos de prueba | PASA | celda [15] (id=m41_knn_rf_code): `for idx_train, _ in cv_externa.split(X, y): gs = construir_knn_con_seleccion_de_k().fit(X[idx_train], y[idx_train])` | El escalado y la elección de k para KNN ocurren dentro de una CV anidada: `cross_val_score` clona y ajusta el `GridSearchCV` (con su `Pipeline` interno) en cada partición externa de entrenamiento; el propio notebook lo verifica explícitamente mostrando qué k se elige en cada partición externa usando solo los datos de entrenamiento de esa partición. |
| V3.2 | Ninguna columna posterior a la predicción | PASA | celda [4] (id=4abcd0e9): `X = iris.data.values` / `y = iris.target.values` | Las cuatro predictoras (longitud/ancho de sépalo y pétalo) son medidas físicas independientes de `y`; ninguna se construye a partir de la variable objetivo. |
| V4.1 | Métrica por subgrupo | NO SE PUEDE DETERMINAR | celda [4] (id=4abcd0e9) | No se entregó ninguna variable de subgrupo (`target ninguna`) y el dataset Iris no contiene atributos protegidos ni proxies (sexo, edad, estado civil, situación familiar): solo mide 4 variables florales. No aplica disparidad demográfica a este problema. |
| V4.2 | Disparidad dentro del umbral | NO SE PUEDE DETERMINAR | — | Depende de V4.1, que no es PASA (no hay subgrupos que evaluar). |
| V5.1 | Sin `inf`/`NaN` al entrenar | PASA | celda [4] (id=4abcd0e9): `iris = load_iris(as_frame=True)` | Los datos provienen directamente de `load_iris()` (dataset limpio de scikit-learn); no hay divisiones entre columnas, `errors="coerce"` ni uniones que puedan producir `inf`/`NaN`. |
| V6.1 | Sin identificadores ni atributos prohibidos | PASA | celda [4] (id=4abcd0e9), salida `df.head()`: columnas `sepal length (cm)`, `sepal width (cm)`, `petal length (cm)`, `petal width (cm)` | `X = iris.data.values` contiene únicamente las 4 medidas florales; no incluye ningún identificador único ni atributo declarado como prohibido. |

## Acciones recomendadas

1. **[V1.2]** Agregar una matriz de confusión (`confusion_matrix`) en al menos una salida guardada (por ejemplo, sobre las predicciones de un fold o de un conjunto de prueba separado), para poder verificar la consistencia de las métricas reportadas. (prioridad: media)
2. **[V1.3]** Reportar al menos un `classification_report` o métricas por especie, para poder verificar que se atribuyen a la clase correcta. Actualmente el notebook solo reporta accuracy global, por lo que este subcriterio no tiene evidencia sobre la cual evaluarse. (prioridad: media)
3. **[V1.4]** Mostrar la distribución de la variable objetivo en una salida guardada (p. ej. `df['especie'].value_counts()`), para poder calcular la razón de desbalance y confirmar si V1.4 aplica y en qué sentido. (prioridad: media)
4. **[V1.5]** Si existiera una prioridad de negocio entre confundir especies (p. ej. que un vivero considere más costoso vender *virginica* como *versicolor* que al revés), declararla explícitamente en una celda de texto y elegir la métrica prioritaria en consecuencia; de lo contrario, dejar constancia explícita de que el problema no tiene clase de interés ni costos diferenciados. (prioridad: media)
5. **[V4.1]** Si se quisiera auditar equidad entre subgrupos, sería necesario aportar una variable de subgrupo relevante; el dataset Iris (medidas florales) no contiene ninguna, por lo que esta verificación no aplica a este proyecto tal como está planteado. (prioridad: media)
6. **[V4.2]** Sin acción propia: depende de que V4.1 tenga subgrupos que evaluar. (prioridad: media)

## Limitaciones de esta auditoría

- El notebook nunca reporta una matriz de confusión, un `classification_report`, ni la distribución de clases de `target`/`especie`, por lo que V1.2, V1.3 y V1.4 no se pudieron evaluar con evidencia propia del proyecto (V1.3 tiene la codificación de clases pero ninguna métrica atribuida a una clase específica sobre la cual aplicarla).
- El problema es multiclase balanceado sin una "clase de interés" declarada, por lo que V1.5 queda en NO SE PUEDE DETERMINAR según la propia regla del criterio (no aplica a un problema sin costos diferenciados de error).
- El dataset Iris no contiene atributos protegidos ni proxies, y no se entregó ninguna variable de subgrupo, por lo que V4.1 y V4.2 no aplican a este proyecto.
