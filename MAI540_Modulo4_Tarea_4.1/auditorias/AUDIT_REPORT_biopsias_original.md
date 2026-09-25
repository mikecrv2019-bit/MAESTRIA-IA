# Informe de auditoría — App_Diagnostico_Biopsias_Mama

- **Archivos auditados:** `C:\Users\jaimelopez\Documents\ATLANTIS UNIVERSITY 2026 - 2027\MAI540 - SEP 01 2026 - OCT 08 2026\MODULO 3\App_Diagnostico_Biopsias_Mama.ipynb`
- **Archivos de apoyo leídos:** ninguno (no hay `README.md`, `context.md`, `DESCRIPCION.md` ni informes `.md` del autor en la carpeta del proyecto; los archivos `AUDIT_REPORT*.md` existentes no se leen por regla 7)
- **Columna objetivo:** `diagnostico` — codificación: 0 = maligno, 1 = benigno (evidencia: celda [4] (id=bbb980c2): `df['diagnostico'] = data.target  # 0 = maligno, 1 = benigno`)
- **Tipo de problema:** clasificación binaria (evidencia: celda [16] (id=881f59c8): `modelo = LogisticRegression(**kwargs)`; `diagnostico` toma solo los valores 0/1, celda [4])
- **Subgrupos:** ninguno (origen: argumento entregado "ninguna"; no se encontraron columnas de sexo/género, edad, estado civil o situación familiar ni proxies entre los predictores — celda [16] (id=881f59c8), lista `COLUMNAS_PREDICTORAS`)
- **Skill:** auditoria-modelos v1.3 — fecha: 2026-09-24
- **Modificaciones al proyecto:** ninguna (auditoría de solo lectura)

## Resumen

| Verificación | Resultado |
|---|---|
| V1 Métricas reportadas | FALLA |
| V2 Partición de datos | FALLA |
| V3 Fuga de información | FALLA |
| V4 Disparidad entre subgrupos | NO SE PUEDE DETERMINAR |
| V5 Validez de datos de entrada | FALLA |
| V6 Variables no admisibles | PASA |

## Tabla de verificación

| ID | Verificación | Resultado | Evidencia | Observación |
|---|---|---|---|---|
| V1.1 | Rango válido | NO SE PUEDE DETERMINAR | celda [18] (id=93d6fc8f), salida: `ValueError: Input X contains infinity or a value too large for dtype('float64').` | La celda que imprime `acc_train`/`acc_test` (celda [18]) lanza una excepción antes de llegar al `print`; no queda ninguna métrica numérica en las salidas guardadas del notebook. |
| V1.2 | Consistencia con la matriz | NO SE PUEDE DETERMINAR | (ninguna salida con matriz de confusión) | El notebook nunca importa ni llama `confusion_matrix` ni `classification_report`; no hay matriz de confusión en ninguna salida guardada. |
| V1.3 | Clase positiva correcta | NO SE PUEDE DETERMINAR | celda [16] (id=881f59c8): `acc_train = accuracy_score(y_train, modelo.predict(X_train))` | La única métrica que el código calcula es `accuracy_score`, que no depende de `pos_label`; no se calcula ninguna métrica por clase (precisión, exhaustividad, F1) a la que aplicar este criterio. |
| V1.4 | No solo accuracy con desbalance | FALLA | celda [6] (id=cba9b56a), salida: `1    0.627` / `0    0.373`; razón = 0.627/0.373 = 1.6810 ≥ 1.5 (desbalance). celda [2] (id=b7d1693a): `from sklearn.metrics import accuracy_score` (único import de métricas). celda [16] (id=881f59c8): `acc_train = accuracy_score(...)` / `acc_test = accuracy_score(...)` | Hay desbalance (razón 1.6810) y el único cálculo de métrica en todo el código del notebook es `accuracy_score`; no se calcula exhaustividad, precisión, F1 ni matriz de confusión en ninguna función. Se juzga el código, no depende de que la celda haya corrido. |
| V1.5 | Métrica acorde al costo | FALLA | celda [0] (id=4769b499): `estima ... si un tumor es maligno o benigno. La idea es que el modelo ayude a priorizar qué casos revisa primero un especialista` | El proyecto identifica una clase de interés (maligno, el desenlace que importa detectar en un contexto de priorización clínica) pero no declara en ningún lado (código, celdas de texto, archivos de apoyo) cuál error cuesta más (FN o FP); la única métrica calculada es accuracy, que no prioriza la exhaustividad de la clase maligna. |
| V2.1 | División antes del preprocesamiento que aprende | PASA | celda [16] (id=881f59c8): `X_train, X_test, y_train, y_test = train_test_split(...)` seguido de `modelo.fit(X_train, y_train)` | El único `fit` de todo el notebook es el del modelo, sobre `X_train`/`y_train`. `construir_caracteristicas` (celda [12], id=b397da6d) es una transformación determinística (una división aritmética) que no aprende de los datos; no hay `StandardScaler`, imputador, codificador ni selector en ningún lugar del notebook. |
| V2.2 | Semilla fija | FALLA | celda [2] (id=b7d1693a): `rng = np.random.RandomState(RANDOM_STATE)` (generador global, creado una sola vez fuera de cualquier función); usado dentro de `cargar_datos()` en celda [4] (id=bbb980c2): `rng.randint(0, 4, size=n)` y `rng.randint(3, 9, size=n)` | `cargar_datos()` no crea su propio generador; reutiliza el `RandomState` global `rng`, que avanza cada vez que se llama la función. `cargar_datos()` se invoca tres veces en el notebook (celda [4], celda [10] `df_crudo = cargar_datos()`, y celda [18] `df = cargar_datos()`), así que `num_biopsias_previas` y `sesiones_tratamiento_programadas` reciben valores distintos en cada llamada pese a fijar `RANDOM_STATE = 42`. |
| V2.3 | Estratificación | FALLA | celda [16] (id=881f59c8): `train_test_split(X, y, test_size=0.25, random_state=RANDOM_STATE)` | Es clasificación binaria (`diagnostico`) y la única partición del notebook no usa `stratify=y`. |
| V2.4 | Misma partición para los modelos comparados | NO SE PUEDE DETERMINAR | celda [16] (id=881f59c8): `def entrenar_modelo(df, usar_class_weight=False): ...`; celda [18] (id=93d6fc8f): `modelo, acc_train, acc_test = entrenar_modelo(df)` | `entrenar_modelo` acepta un parámetro `usar_class_weight`, pero en todo el notebook se llama una sola vez y con el valor por defecto (`False`); no hay comparación entre modelos. |
| V3.1 | Nada se ajusta con datos de prueba | PASA | celda [16] (id=881f59c8): `modelo.fit(X_train, y_train)` | El único ajuste (`fit`) del notebook usa exclusivamente `X_train`/`y_train`; no hay selección de variables, hiperparámetros ni umbral que dependa de `X_test`/`y_test`. |
| V3.2 | Ninguna columna posterior a la predicción | FALLA | celda [4] (id=bbb980c2): `df['sesiones_tratamiento_programadas'] = np.where(df['diagnostico'] == 0, rng.randint(3, 9, size=n), 0,)` | `sesiones_tratamiento_programadas` —incluida entre los predictores en celda [16] (id=881f59c8), lista `COLUMNAS_PREDICTORAS`— se construye directamente a partir de la variable objetivo `diagnostico`. Cuántas sesiones de tratamiento tiene programadas una paciente solo se conoce **después** de conocer el diagnóstico, no en el momento de predecir. |
| V4.1 | Métrica por subgrupo | NO SE PUEDE DETERMINAR | celda [16] (id=881f59c8), lista `COLUMNAS_PREDICTORAS`; carga de datos en celda [4] (id=bbb980c2) | No se entregó ninguna variable de subgrupo (argumento "ninguna") y no se encontró en el proyecto ninguna columna de sexo/género, edad, estado civil o situación familiar ni proxy evidente entre las columnas del dataset (mediciones de imagen de biopsia más `num_biopsias_previas` y `sesiones_tratamiento_programadas`). |
| V4.2 | Disparidad dentro del umbral | NO SE PUEDE DETERMINAR | (depende de V4.1) | V4.1 no es PASA. |
| V5.1 | Sin `inf`/`NaN` al entrenar | FALLA | celda [12] (id=b397da6d): `df['variabilidad_por_biopsia'] = df['mean texture'] / df['num_biopsias_previas']`; celda [12] salida: fila con `num_biopsias_previas = 0` → `variabilidad_por_biopsia = inf`; celda [18] (id=93d6fc8f) salida: `ValueError: Input X contains infinity or a value too large for dtype('float64').` | La división no protege el caso `num_biopsias_previas == 0` (que ocurre, `rng.randint(0, 4, ...)` genera ceros). Existe una función de validación (`validar_datos`, celda [10], id=fbef5102) que detecta el problema (`'variabilidad_por_biopsia': {'nulos': 0, 'infinitos': 140}`), pero solo se usa en una celda de diagnóstico exploratorio; nunca se llama dentro del flujo real de entrenamiento (celda [18], "Ejecutar el pipeline completo"), que por eso falla con `ValueError` al llegar al `fit`. |
| V6.1 | Sin identificadores ni atributos prohibidos | PASA | celda [16] (id=881f59c8): `COLUMNAS_PREDICTORAS = ['mean texture', 'mean smoothness', 'mean symmetry', 'mean fractal dimension', 'texture error', 'smoothness error', 'symmetry error', 'variabilidad_por_biopsia', 'num_biopsias_previas', 'sesiones_tratamiento_programadas']` | Ninguna de las columnas predictoras es un identificador único (el dataset `load_breast_cancer` no trae columna de ID) ni un atributo que el proyecto declare prohibido. |

## Acciones recomendadas

1. **[V1.1]** Corregir primero la causa raíz (ver V5.1) para que la celda [18] termine de ejecutarse sin excepción y las métricas de accuracy queden impresas en una salida guardada; luego verificar que estén en [0, 1]. (prioridad: media)
2. **[V1.2]** Agregar el cálculo y la impresión de una matriz de confusión (`confusion_matrix`) sobre el conjunto de prueba, para poder verificar la consistencia de las métricas reportadas. (prioridad: media)
3. **[V1.3]** Agregar métricas por clase (p. ej. `classification_report` o `precision_recall_fscore_support` con `pos_label` explícito) para poder auditar si la clase positiva se calcula con la etiqueta correcta. (prioridad: media)
4. **[V1.4]** Dado el desbalance (razón 1.6810), agregar al código el cálculo de exhaustividad y precisión (o F1) de la clase maligna, además de accuracy, por ejemplo con `classification_report(y_test, y_pred)` o `recall_score`/`precision_score` con `pos_label=0`. (prioridad: alta)
5. **[V1.5]** Declarar explícitamente en una celda de texto o en un archivo de apoyo cuál error es más costoso (falso negativo en maligno vs. falso positivo), y ajustar la métrica prioritaria reportada para que penalice ese error. (prioridad: alta)
6. **[V2.2]** Crear el generador aleatorio dentro de `cargar_datos()` (p. ej. `rng = np.random.RandomState(RANDOM_STATE)` como primera línea de la función) en lugar de reutilizar un `RandomState` global, para que cada llamada produzca los mismos valores de `num_biopsias_previas` y `sesiones_tratamiento_programadas`. (prioridad: alta)
7. **[V2.3]** Agregar `stratify=y` a la llamada de `train_test_split` en `entrenar_modelo` (celda [16]), dado que es un problema de clasificación con desbalance. (prioridad: alta)
8. **[V2.4]** Si se desea comparar modelos (p. ej. con y sin `class_weight='balanced'`), llamar `entrenar_modelo` más de una vez con parámetros distintos sobre la misma partición, y documentar la comparación; si solo se usará un modelo, no se requiere acción. (prioridad: media)
9. **[V3.2]** Excluir `sesiones_tratamiento_programadas` de `COLUMNAS_PREDICTORAS`, o reconstruir la columna con una fuente de datos que no dependa de `diagnostico`, porque en producción esa información no existe antes de emitir la predicción. (prioridad: alta)
10. **[V4.1]** Si en el futuro se agregan columnas demográficas o de subgrupo al dataset, calcular la métrica prioritaria por separado para cada subgrupo antes de desplegar el modelo. (prioridad: media)
11. **[V4.2]** Ver acción V4.1; sin variables de subgrupo no hay disparidad que medir. (prioridad: media)
12. **[V5.1]** Proteger la división en `construir_caracteristicas` (celda [12]) contra `num_biopsias_previas == 0` (p. ej. sumar 1 al denominador, o imputar/enmascarar esos casos) y, adicionalmente, llamar `validar_datos` dentro del flujo real de `cargar_datos`/`construir_caracteristicas`/`entrenar_modelo` en lugar de solo en la celda de diagnóstico exploratorio. (prioridad: alta)

## Limitaciones de esta auditoría

- El notebook no tiene salidas guardadas de las métricas de accuracy, matriz de confusión ni métricas por clase, porque la celda que las produce (celda [18]) termina en una excepción antes de imprimirlas; V1.1, V1.2 y V1.3 quedan sin poder verificarse por esta razón.
- No se ejecutó el notebook ni su código (regla 1 de la Skill); todos los hallazgos provienen de la lectura del código y de las salidas ya guardadas en el archivo `.ipynb`.
- No se entregaron variables de subgrupo y no se encontró ninguna en el proyecto, por lo que V4 queda íntegramente en NO SE PUEDE DETERMINAR.
