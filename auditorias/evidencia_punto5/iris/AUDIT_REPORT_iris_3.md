# Informe de auditoría — Comparación de Clasificadores Iris

- **Archivos auditados:** `C:\Users\jaimelopez\Documents\ATLANTIS UNIVERSITY 2026 - 2027\MAI540 - SEP 01 2026 - OCT 08 2026\MODULO 3\iris-clasificadores-repo\App_Comparacion_Clasificadores_Iris.ipynb`
- **Archivos de apoyo leídos:** `README.md`
- **Columna objetivo:** `target` (mapeada a `especie`) — codificación: 0 = setosa, 1 = versicolor, 2 = virginica (evidencia: celda [4] (id=4abcd0e9), `df['especie'] = df['target'].map(dict(enumerate(iris.target_names)))`, confirmado por la salida `df.head()` donde `target=0 → especie='setosa'`)
- **Tipo de problema:** clasificación multiclase, 3 clases (evidencia: celda [4] (id=4abcd0e9), `y = iris.target.values` con 3 valores posibles; celda [12] (id=a37aa1ce), evaluación con `StratifiedKFold` + `cross_val_score` con scoring por defecto = accuracy). Estimadores: `LogisticRegression`, `DecisionTreeClassifier`, `GaussianNB`, `KNeighborsClassifier` (en `Pipeline`+`GridSearchCV`), `RandomForestClassifier`.
- **Subgrupos:** ninguno (origen: indicado explícitamente por el usuario ("ninguna"); además no se encontró en el dataset ninguna columna de atributo protegido o proxy — solo las 4 medidas florales y la especie)
- **Skill:** auditoria-modelos v1.0 — fecha: 2026-09-24
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
| V1.1 | Rango válido | PASA | celda [13] (id=baf5d90f), salida: `Regresión logística: media=0.9667 ... mínimo=0.933 máximo=1.000`; celda [15] (id=m41_knn_rf_code), salida: `KNN (escalado en pipeline, k por CV anidada): media=0.9600 ... mínimo=0.867 máximo=1.000`; celda [19] (id=534deae5), salida: `Árbol (max_depth=2): media=0.9200 ... mínimo=0.800 máximo=1.000` | Todas las proporciones (accuracy) reportadas en salidas guardadas están dentro de [0, 1], sin NaN. |
| V1.2 | Consistencia con la matriz | NO SE PUEDE DETERMINAR | (sin evidencia — búsqueda de `confusion_matrix`/`classification_report` en todo el notebook sin resultados) | El notebook solo reporta accuracy vía `cross_val_score`/`.score()`; no hay matriz de confusión guardada en ninguna salida para recalcular las métricas. |
| V1.3 | Clase positiva correcta | NO SE PUEDE DETERMINAR | celda [4] (id=4abcd0e9), fija la codificación `0=setosa,1=versicolor,2=virginica`, pero ninguna salida reporta una métrica atribuida a una clase específica | No se reportan métricas por clase (precisión/exhaustividad de "virginica", etc.), solo accuracy global multiclase; no hay `pos_label` que verificar. |
| V1.4 | No solo accuracy con desbalance | NO SE PUEDE DETERMINAR | (sin evidencia — no hay `value_counts`, conteo ni gráfico de distribución de `target`/`especie` en ninguna salida guardada) | No se puede calcular la razón de desbalance con evidencia citada del proyecto. (El dataset Iris de scikit-learn es conocido por estar balanceado 50/50/50, pero esa cifra no aparece en ninguna salida del notebook, y la Skill exige evidencia citada, no conocimiento externo.) |
| V1.5 | Métrica acorde al costo | NO SE PUEDE DETERMINAR | (sin evidencia — ninguna celda de texto ni el `README.md` declara qué error, FN o FP, cuesta más) | Problema multiclase sin clase de interés identificada ni costos distintos por tipo de error declarados. |
| V2.1 | División antes del preprocesamiento que aprende | PASA | celda [12] (id=a37aa1ce), `cv = StratifiedKFold(...); scores = cross_val_score(modelo, X, y, cv=cv)`; celda [15] (id=m41_knn_rf_code), `StandardScaler` dentro de un `Pipeline` envuelto en `GridSearchCV`, pasado sin ajustar a `evaluar_con_cv` | Regresión logística, árbol y Naive Bayes no tienen preprocesamiento que aprenda de los datos. KNN escala dentro del pipeline, que `cross_val_score` ajusta solo con el entrenamiento de cada partición externa. |
| V2.2 | Semilla fija | PASA | celda [2] (id=a16e5791), `RANDOM_STATE = 42`; celda [12] (id=a37aa1ce) `StratifiedKFold(..., random_state=RANDOM_STATE)`; celda [15] (id=m41_knn_rf_code) `cv_interna`, `cv_externa`, `RandomForestClassifier` todos con `random_state=RANDOM_STATE`; celda [9] (id=ddd20eb3) `DecisionTreeClassifier(..., random_state=RANDOM_STATE)` | `RANDOM_STATE` es una constante entera reutilizada, no un objeto `RandomState` global que avance entre llamadas; cada `StratifiedKFold`/estimador aleatorio la recibe explícitamente. |
| V2.3 | Estratificación | PASA | celda [12] (id=a37aa1ce) y celda [15] (id=m41_knn_rf_code): toda partición usa `StratifiedKFold` | No se usa `train_test_split` ni `KFold` sin estratificar en ningún punto del notebook (verificado por búsqueda exhaustiva de esos símbolos). |
| V2.4 | Misma partición para los modelos comparados | PASA | celda [13] (id=baf5d90f) y celda [15] (id=m41_knn_rf_code): los cinco modelos se evalúan con `evaluar_con_cv(modelo, X, y, nombre)` (definida en celda [12]), con el mismo `X`, `y` | Como `evaluar_con_cv` crea `StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)` de forma determinista en cada llamada, las 10 particiones son idénticas para los cinco modelos. |
| V3.1 | Nada se ajusta con datos de prueba | PASA | celda [15] (id=m41_knn_rf_code), comentario y código: `construir_knn_con_seleccion_de_k()` (GridSearchCV sin ajustar) se pasa a `evaluar_con_cv`, que lo clona y ajusta por partición externa | La elección de k ocurre con validación cruzada anidada (5 particiones internas dentro de cada una de las 10 externas); la partición externa de validación no participa en elegir k ni en ajustar el escalador. |
| V3.2 | Ninguna columna posterior a la predicción | PASA | celda [4] (id=4abcd0e9), `X = iris.data.values` | Las 4 predictoras (longitud/ancho de sépalo y pétalo) provienen directamente del dataset `load_iris()` de scikit-learn; ninguna se deriva de `y`/`target`. |
| V4.1 | Métrica por subgrupo | NO SE PUEDE DETERMINAR | (sin evidencia — el dataset Iris solo tiene las 4 medidas florales y la especie) | No hay ninguna variable de subgrupo (atributo protegido o proxy) en el proyecto, y el usuario indicó explícitamente "ninguna". |
| V4.2 | Disparidad dentro del umbral | NO SE PUEDE DETERMINAR | (consecuencia de V4.1) | No aplica: V4.1 no es PASA. |
| V5.1 | Sin `inf`/`NaN` al entrenar | PASA | celda [4] (id=4abcd0e9), `X = iris.data.values`, `y = iris.target.values` | Los datos provienen directamente de `load_iris()` sin divisiones entre columnas, `errors="coerce"` ni uniones que puedan producir `inf`/`NaN`. |
| V6.1 | Sin identificadores ni atributos prohibidos | PASA | celda [4] (id=4abcd0e9), `X = iris.data.values` | Las predictoras son únicamente las 4 columnas de `iris.data` (medidas de sépalo y pétalo); ningún identificador único ni atributo declarado como prohibido (el `README.md` no declara ninguno). |

## Acciones recomendadas

1. **[V1.2]** Agregar una matriz de confusión sobre las predicciones de validación cruzada (p. ej. con `cross_val_predict` + `confusion_matrix`) para poder verificar la consistencia de las métricas reportadas con los conteos reales. (prioridad: media)
2. **[V1.3]** Si en el futuro se reportan métricas por clase (p. ej. exhaustividad de "virginica"), usar `classification_report(target_names=...)` o `pos_label` explícito para evitar ambigüedad sobre a qué clase corresponde cada cifra. (prioridad: media)
3. **[V1.4]** Agregar una salida guardada con la distribución de `target`/`especie` (p. ej. `df['especie'].value_counts()`) para poder verificar con evidencia del propio proyecto que el dataset está balanceado. (prioridad: media)
4. **[V1.5]** Declarar explícitamente (en una celda de texto o en el `README.md`) si hay una especie cuya clasificación errónea sería más costosa que las otras para el vivero, o documentar que las tres se tratan con el mismo costo. (prioridad: media)
5. **[V4.1]** Si en algún momento se desea auditar equidad, documentar explícitamente que el dataset no tiene atributos protegidos aplicables (información botánica sin datos demográficos), para que quede como evidencia y no dependa de conocimiento externo. (prioridad: media)
6. **[V4.2]** Sin acción propia: depende de V4.1. (prioridad: media)

## Limitaciones de esta auditoría

- El notebook nunca calcula ni guarda una matriz de confusión ni un `classification_report`; solo reporta accuracy (global, vía `cross_val_score`/`.score()`), lo que deja V1.2 y V1.3 sin poder verificarse con evidencia propia del proyecto.
- No hay ninguna salida guardada que muestre la distribución de clases de `target`/`especie`, por lo que V1.4 no se pudo calcular con evidencia citada, aunque el dataset Iris de scikit-learn es de conocimiento público que está balanceado (50/50/50).
- El proyecto no declara costos diferenciados de error entre las tres especies ni una clase de interés (es un problema multiclase simétrico desde la perspectiva del vivero), por lo que V1.5 queda sin determinar.
- No existen en el dataset Iris atributos protegidos o proxies aplicables a V4 (es un dataset de medidas florales); el usuario confirmó "ninguna" para subgrupos, por lo que V4.1 y V4.2 no aplican.
