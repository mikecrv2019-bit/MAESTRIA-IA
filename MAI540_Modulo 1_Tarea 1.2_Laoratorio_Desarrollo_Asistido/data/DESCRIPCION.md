# Customer Service AI Chatbot — Descripción de datos

Fuente original: dataset público de Kaggle "Customer Service Interaction Dataset" (Customer Service Interactions for AI Chatbot Evaluation): https://www.kaggle.com/datasets/zadafiyabhrami/customer-service-ineraction-dataset

- Filas: 4,500 interacciones
- Variable objetivo: `Insatisfecho` = `Yes` cuando `customer_satisfaction` ≤ 2; `No` en caso contrario
- Clases: desbalanceadas (~20% `Yes`, ~80% `No`)

## Columnas

| Columna | Tipo | Descripción |
|---|---|---|
| interaction_id | identificador | Único por interacción. No debe usarse como predictor. |
| timestamp | texto (debe convertirse) | Fecha de la interacción (enero a junio de 2024) |
| query_type | categórica | Tipo de consulta (facturación, soporte técnico, envío, contraseña, cuenta, producto) |
| handled_by | categórica | Quién atendió el caso: `AI Chatbot` o `Human Agent` |
| response_time_min | numérica | Tiempo de respuesta en minutos |
| resolution_status | categórica | Resultado del caso: `Resolved`, `Escalated` o `Pending` |
| customer_sentiment | numérica | Sentimiento del cliente durante la interacción (0 a 1) |
| customer_satisfaction | numérica (1 a 5) | Calificación de satisfacción. Se usa solo para construir el objetivo. |
| interaction_cost_usd | numérica | Costo de la interacción en dólares |
| customer_id | identificador | Único por cliente. No debe usarse como predictor. |
| region | categórica | Estado de EE. UU. del cliente (50 valores) |
| device_type | categórica | Dispositivo: `Mobile`, `Desktop` o `Tablet` |
| follow_up_required | booleana | Si el caso requiere seguimiento (`True`/`False`) |

## Nota sobre `timestamp`
La fecha se lee como texto (`object`), no como fecha. Para usarla en el modelo debe convertirse con `pd.to_datetime` y extraerse el día de la semana (`dia_semana`), que se trata como variable categórica.

## Nota sobre el origen de los datos
Es un dataset sintético creado para evaluar chatbots de servicio al cliente; las empresas no suelen publicar sus interacciones reales por motivos de privacidad.

## Nota sobre esta versión académica
El archivo `datos.csv` fue ajustado únicamente en cantidad de registros (muestra estratificada de 4,500 de las 10,000 filas originales) para mantener una carga de trabajo comparable entre las variantes de la tarea. Las variables y el alcance indicado en `README.md` se mantienen sin cambios.
