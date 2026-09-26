# Customer Service AI Chatbot — Tarea 1.2 (versión equilibrada)

## Objetivo y nivel de dificultad
Este proyecto es un problema de **clasificación binaria** cuyo objetivo es predecir si un cliente quedará **insatisfecho** con la atención recibida (**Insatisfecho = Yes** cuando `customer_satisfaction` ≤ 2; clase positiva).

Los datos provienen de un centro de servicio al cliente donde cada caso fue atendido por un **chatbot de IA** o por un **agente humano**. El modelo permitiría anticipar qué clientes necesitan seguimiento antes de que respondan la encuesta.

Esta versión fue ajustada para que tenga una carga de trabajo comparable con las demás variantes de la Tarea 1.2. El alcance del modelo final está limitado a **10 predictores**, un único algoritmo y un mismo patrón de preprocesamiento y evaluación.

## Punto de partida
`main.py` contiene un modelo funcional pero deliberadamente limitado que usa solo unas pocas variables numéricas. Debes ejecutarlo sin modificar nada y conservar su salida como evidencia del **ANTES**.

## Predictores obligatorios del modelo final
Usa **exactamente estas 10 variables**; no es necesario buscar ni añadir otras:

- `response_time_min`
- `interaction_cost_usd`
- `customer_sentiment`
- `handled_by`
- `query_type`
- `resolution_status`
- `follow_up_required`
- `device_type`
- `region`
- `dia_semana` (se obtiene a partir de `timestamp`; ver consideraciones)

Para el preprocesamiento, considera:
- **Numéricas:** `response_time_min`, `interaction_cost_usd`, `customer_sentiment`.
- **Categóricas:** `handled_by`, `query_type`, `resolution_status`, `follow_up_required`, `device_type`, `region`, `dia_semana`.

## Mejora solicitada
Completa el proyecto para que:
1. mantenga un `train_test_split` con `test_size=0.25` y `random_state=42` (usa `stratify=y` solo en clasificación);
2. construya un `ColumnTransformer` con dos ramas:
   - numérica: `SimpleImputer(strategy="median")` + `StandardScaler()`;
   - categórica: `SimpleImputer(strategy="most_frequent")` + `OneHotEncoder(handle_unknown="ignore")`;
3. mantenga el conjunto de prueba separado y ajuste todo el preprocesamiento únicamente con los datos de entrenamiento;
4. use como algoritmo final `LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")`; **no es necesario probar otros algoritmos ni hacer tuning de hiperparámetros**;
   - `class_weight="balanced"` permite trabajar de forma uniforme con la clase positiva/minoritaria sin añadir búsqueda de hiperparámetros;
5. reporte accuracy, precision, recall y F1 para la clase `Insatisfecho=Yes`;
6. presente una comparación clara entre **ANTES** y **DESPUÉS** usando el mismo `random_state` y el mismo tamaño de prueba;
7. explique con sus propias palabras qué cambió y por qué.

## Consideraciones específicas del dataset
- `timestamp` viene como texto. Conviértelo con `pd.to_datetime` y crea la columna `dia_semana` (nombre del día). No uses `timestamp` directamente como predictor.
- `follow_up_required` es booleana (`True`/`False`): trátala como categórica en el modelo final.
- **No uses `customer_satisfaction` como predictor**: de ella se construye la variable objetivo, y usarla sería fuga de información.
- No uses `interaction_id` ni `customer_id`, porque son identificadores únicos.

## Flujo obligatorio
1. Pide a Claude Code que lea el proyecto y lo explique **sin modificar archivos**.
2. Ejecuta `python main.py` y conserva la salida como evidencia del **ANTES**.
3. Pide un plan que respete exactamente el alcance de este README. Revísalo antes de autorizar cambios.
4. Autoriza la implementación.
5. Ejecuta nuevamente el proyecto y conserva evidencia del **DESPUÉS**.
6. Completa `BITACORA.md` con tus propias palabras.

## Entrega
- Proyecto completado.
- Evidencia de ejecución antes y después.
- Bitácora de desarrollo asistido.
- Explicación propia del pipeline, los tipos de variables y las métricas.

## Límite de alcance
Para mantener una dificultad equivalente entre estudiantes, **no se requiere** selección automática de variables, validación cruzada, búsqueda de hiperparámetros, ingeniería avanzada de características ni comparación de múltiples algoritmos.
