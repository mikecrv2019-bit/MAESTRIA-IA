# Informe de auditoría — App_Comparacion_Clasificadores_Iris

- **Archivos auditados:** `App_Comparacion_Clasificadores_Iris.ipynb`
- **Archivos de apoyo leídos:** `README.md`
- **Columna objetivo:** `target` — codificación: 0 = setosa, 1 = versicolor, 2 = virginica (evidencia: celda [4] (id=4abcd0e9), código: `df['especie'] = df['target'].map(dict(enumerate(iris.target_names)))`; confirmado por la salida `df.head()` de la misma celda, que muestra `target=0` ↔ `especie=setosa` en las 5 primeras filas)
- **Tipo de problema:** clasificación multiclase (3 especies) (evidencia: celda [4] (id=4abcd0e9), `y = iris.target.values`, con 3 valores posibles según `iris.target_names`)
- **Subgrupos:** ninguno (origen: argumento entregado como "ninguna"; el dataset Iris solo contiene medidas florales — `sepal length`, `sepal width`, `petal length`, `petal width` — sin atributos protegidos ni proxies, según la salida `df.head()` de la celda [4] (id=4abcd0e9))
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
| V1.1 | Rango válido | PASA | celda [13] (id=baf5d90f), salida: `Regresión logística: media=0.9667 ... mínimo=0.933 máximo=1.000` | Todas las cifras de accuracy reportadas en las celdas [13], [15], [19], [22], [25] (medias, desviaciones, mínimos, máximos) están dentro de [0, 1]. No se reportan proporciones fuera de rango ni NaN. |
| V1.2 | Consistencia con la matriz | NO SE PUEDE DETERMINAR | — | El notebook nunca calcula `confusion_matrix` ni `classification_report` (sin coincidencias al buscar `confusion_matrix\|classification_report` en todo el archivo). Solo se reporta accuracy global vía `cross_val_score`/`.score()`. Sin matriz de confusión no hay con qué recalcular. |
| V1.3 | Clase positiva correcta | NO SE PUEDE DETERMINAR | — | No se reporta ninguna métrica atribuida a una clase específica (precisión/exhaustividad/F1 por especie); solo accuracy multiclase global. El criterio no tiene sobre qué aplicarse. |
| V1.4 | No solo accuracy con desbalance | NO SE PUEDE DETERMINAR | — | El notebook no muestra en ninguna salida la distribución de `target`/`especie` (no hay `value_counts`, `bincount` ni `groupby` en todo el archivo). Sin esa salida citable no se puede calcular la razón de desbalance, aunque el dataset Iris de `sklearn` es ampliamente conocido como balanceado (50/50/50), esa cifra no proviene de una salida ni de código de este proyecto. |
| V1.5 | Métrica acorde al costo | NO SE PUEDE DETERMINAR | celda [0] (id=2c087a52): `Un vivero quiere automatizar la clasificación de especies de flores...` | Es un problema multiclase de las 3 especies por igual; ni el notebook ni `README.md` identifican una clase de interés (p. ej. una especie cuya confusión sea más costosa) ni declaran qué error (FN/FP) cuesta más. No aplica un costo diferenciado por tipo de error. |
| V2.1 | División antes del preprocesamiento que aprende | PASA | celda [15] (id=m41_knn_rf_code): `flujo = Pipeline([('escalador', StandardScaler()), ('knn', KNeighborsClassifier())])`, evaluado con `evaluar_con_cv(construir_knn_con_seleccion_de_k(), X, y, ...)` | El único transformador que aprende de los datos (`StandardScaler`) está dentro de un `Pipeline` envuelto en `GridSearchCV`, y ese objeto sin ajustar se pasa a `cross_val_score` (celda [12], id=a37aa1ce), que lo clona y ajusta por partición. Ningún escalador se ajusta con el conjunto completo antes de evaluar. El notebook explica este diseño en la celda [14] (id=m41_knn_rf_md). Los otros 4 modelos no usan preprocesamiento que aprenda de los datos. |
| V2.2 | Semilla fija | PASA | celda [2] (id=a16e5791): `RANDOM_STATE = 42`; celda [12] (id=a37aa1ce): `cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)` | Toda operación aleatoria (`StratifiedKFold` externo e interno, `DecisionTreeClassifier`, `RandomForestClassifier`) recibe `random_state=RANDOM_STATE` (grep de `random_state` en el archivo no muestra ninguna instancia sin él). Cada función crea su propio objeto `StratifiedKFold`; no hay un `RandomState` global compartido que avance entre llamadas. |
| V2.3 | Estratificación | PASA | celda [12] (id=a37aa1ce): `StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)`; celda [15] (id=m41_knn_rf_code): `cv_interna = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)` | Es clasificación (multiclase). El notebook no usa `train_test_split` en ningún punto (sin coincidencias al buscar `train_test_split`); toda partición, externa e interna (CV anidada de KNN), usa `StratifiedKFold`. |
| V2.4 | Misma partición para los modelos comparados | PASA | celda [13] (id=baf5d90f): `evaluar_con_cv(LogisticRegression(...), X, y, ...)` / celda [15] (id=m41_knn_rf_code): `evaluar_con_cv(construir_knn_con_seleccion_de_k(), X, y, ...)` | Los 5 modelos (regresión logística, árbol, Naive Bayes, KNN, Random Forest) se evalúan con la misma función `evaluar_con_cv` (celda [12]), los mismos `X`, `y` (celda [4]) y el mismo esquema `StratifiedKFold(n_splits=10, shuffle=True, random_state=RANDOM_STATE)`, que al recrearse con los mismos parámetros produce particiones idénticas en cada llamada. |
| V3.1 | Nada se ajusta con datos de prueba | PASA | celda [15] (id=m41_knn_rf_code): `GridSearchCV(flujo, {'knn__n_neighbors': VALORES_K}, cv=cv_interna, scoring='accuracy')` pasado sin ajustar a `evaluar_con_cv` | No existe un conjunto de prueba separado en el notebook (toda evaluación es por CV). El único hiperparámetro realmente elegido por CV es `k` de KNN, y se elige con `GridSearchCV` (CV interna de 5) anidado dentro de cada partición externa de 10, cumpliendo el requisito de CV anidada. La profundidad del árbol (`max_depth=3`) no se elige mirando una métrica de evaluación: está fijada explícitamente por el enunciado, según la celda [18] (id=04ee62ba): `"En la sección 3 entrenaste el árbol con max_depth=3 porque así te lo pedí."` La exploración posterior de profundidades (celda [19]) es diagnóstica y no alimenta el número finalmente reportado en la tabla comparativa (celda [25]), que proviene de la celda [13]. |
| V3.2 | Ninguna columna posterior a la predicción | PASA | celda [4] (id=4abcd0e9): `X = iris.data.values` | Las 4 predictoras son las medidas físicas originales del dataset (`sepal length`, `sepal width`, `petal length`, `petal width`), no derivadas de `target`/`especie`. La columna `especie` sí se deriva de `target` (celda [4]) pero no se usa como predictora — `X` se construye solo de `iris.data.values`. No hay señal de alarma real de fuga (los máximos de 1.000 en algunas particiones son esperables en Iris, un dataset clásicamente muy separable, sobre todo por `setosa`). |
| V4.1 | Métrica por subgrupo | NO SE PUEDE DETERMINAR | — | El argumento de subgrupos se entregó como "ninguna" y el dataset Iris (medidas florales de 150 flores) no contiene ninguna columna de atributo protegido ni proxy razonable (columnas disponibles, según celda [4]: `sepal length`, `sepal width`, `petal length`, `petal width`, `target`, `especie`). No aplica esta verificación. |
| V4.2 | Disparidad dentro del umbral | NO SE PUEDE DETERMINAR | — | Depende de V4.1, que no es PASA (no hay variables de subgrupo definidas ni aplicables en este proyecto). |
| V5.1 | Sin `inf`/`NaN` al entrenar | PASA | celda [4] (id=4abcd0e9): `iris = load_iris(as_frame=True)` / `df = iris.frame.copy()` | Los datos provienen directamente de `load_iris` de `scikit-learn` (dataset empaquetado, sin valores faltantes). No existe en el notebook ninguna división entre columnas, `errors="coerce"`, ni unión de tablas que pudiera generar `inf`/`NaN` (sin coincidencias al revisar las celdas de construcción de `X`, `y`). |
| V6.1 | Sin identificadores ni atributos prohibidos | PASA | celda [4] (id=4abcd0e9): `X = iris.data.values` | Las 4 predictoras finales son medidas continuas (`sepal length`, `sepal width`, `petal length`, `petal width`); ninguna es un identificador único ni un atributo declarado prohibido. Ni el notebook ni `README.md` declaran variables prohibidas. |

## Acciones recomendadas

1. **[V1.2]** Agregar una matriz de confusión (agregada entre particiones, o al menos de una partición de ejemplo) con `confusion_matrix`, para poder verificar que el accuracy reportado es consistente con los aciertos/errores reales. (prioridad: media)
2. **[V1.3]** Si en el futuro se quiere reportar desempeño por especie (por ejemplo, para saber si el modelo confunde más *versicolor* con *virginica*), agregar `classification_report` o `precision_recall_fscore_support` con las etiquetas 0/1/2 explícitas. (prioridad: media)
3. **[V1.4]** Mostrar explícitamente la distribución de clases (p. ej. `df['especie'].value_counts()`) en una celda con salida guardada, para que la razón de desbalance quede verificable como evidencia del propio proyecto y no como conocimiento externo sobre el dataset Iris. (prioridad: media)
4. **[V1.5]** Documentar explícitamente (en una celda de texto o en `README.md`) que este es un ejercicio de aula sin una clase de interés ni costos de error diferenciados, para dejar constancia de que la ausencia de esa declaración es intencional y no un olvido. (prioridad: media)
5. **[V4.1]** Si se quisiera auditar disparidad de desempeño entre subgrupos en un proyecto futuro con este mismo flujo, sería necesario partir de un dataset con atributos protegidos o proxies razonables; Iris (medidas florales) no los tiene, así que registrar esa limitación explícitamente si se reutiliza este notebook como plantilla. (prioridad: media)
6. **[V4.2]** Misma acción que V4.1: sin variables de subgrupo aplicables, no hay disparidad que calcular. (prioridad: media)

## Limitaciones de esta auditoría

- El notebook no guarda ninguna matriz de confusión ni reporte por clase, solo accuracy global (`cross_val_score` / `.score()`); por eso V1.2 y V1.3 quedan sin evidencia sobre la que pronunciarse.
- La distribución de clases de `target`/`especie` no aparece en ninguna salida guardada del notebook; aunque el dataset Iris de `scikit-learn` es públicamente conocido como balanceado (50/50/50), esa cifra no se tomó de una salida ni de código de este proyecto, así que V1.4 queda como no determinable según las reglas de esta auditoría (no inventar números).
- El accuracy de entrenamiento por profundidad del árbol (sección 6) solo se grafica (celda [19], id=534deae5); no aparece como texto en una salida guardada, así que esa evidencia específica es visual y no se pudo citar como cifra textual.
- El dataset Iris no contiene atributos protegidos ni proxies razonables, y el usuario indicó explícitamente "ninguna" variable de subgrupo, por lo que V4.1 y V4.2 no se pudieron evaluar como PASA/FALLA.
