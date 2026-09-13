# Tarea 2.2 — Preprocesamiento del Proyecto Telco Churn

MAI 540 · Módulo 2. Herramienta de preprocesamiento gobernada por [`context.md`](context.md) (Tarea 2.1), aplicada al dataset *Telco Customer Churn* (4,500 clientes, 21 columnas).

## Cómo ejecutar esto sin preguntarme nada

1. Abre [`Tarea_2.2_Preprocesamiento_Telco_Churn.ipynb`](Tarea_2.2_Preprocesamiento_Telco_Churn.ipynb) en Google Colab (botón "Open in Colab" de GitHub, o `File > Open notebook > GitHub` pegando esta URL de repo).
2. Ejecuta las celdas en orden. La celda de "Paso 0" te va a pedir el archivo CSV por el diálogo de carga de Colab — súbelo desde tu equipo.
3. **El CSV no está en este repositorio a propósito** (ver "Por qué no hay datos aquí" abajo). Si no tienes el archivo, pide `datos Proyecto - Telco_Churn.csv` al profesor o consíguelo del dataset público *IBM Telco Customer Churn* en Kaggle — las columnas deben coincidir exactamente con las que usa el notebook (ver diccionario en `context.md`).
4. No hace falta instalar nada: Colab ya trae `pandas`, `numpy` y `scikit-learn`. Si lo corres localmente, usa `requirements.txt`.

Al terminar, el notebook deja en memoria `train_full`, `test_full`, `y_train`, `y_test`: el conjunto de datos procesado, listo para entrenar un modelo.

## Por qué no hay datos aquí

`context.md` (sección "Restricciones de Seguridad" → "Datos personales") prohíbe subir el CSV a repositorios públicos. Este repositorio es público, así que el notebook carga el archivo en tiempo de ejecución (`files.upload()` de Colab) en vez de traerlo versionado. `.gitignore` bloquea además cualquier `.csv` que se intente subir por error.

## Qué hace el pipeline, y en qué orden (y por qué ese orden evita fuga de información)

| # | Paso | Se calcula con | Por qué en ese punto |
|---|---|---|---|
| 1 | Eliminar `TotalCharges`, `customerID`, `gender` | Regla fija de `context.md`, no depende de los datos | Debe pasar antes que nada: si se deja `TotalCharges` un paso más y luego se particiona, ya "contaminó" cualquier estadístico que se calcule después. |
| 2 | Recodificar `"No internet/phone service"` → `"No"` | Regla fija (R2/R3 de `context.md`) | Es una sustitución de texto determinista, no aprende nada de la distribución de los datos — segura antes de particionar. |
| 3 | Diagnóstico de nulos, duplicados y atípicos | Todo el dataset (solo lectura) | Es un reporte descriptivo: cuenta cosas, no ajusta (`fit`) ningún parámetro que el pipeline vaya a reutilizar. Por eso es seguro hacerlo antes de particionar, a diferencia de los pasos 5-7. |
| 4 | **Partición train/test (75/25, estratificada, `random_state=42`)** | — | **Punto de no retorno.** Todo lo que sigue debe aprenderse solo del lado de entrenamiento. |
| 5 | Imputación (comparación mediana/media) | `X_train` únicamente | Si el imputador se ajustara con el dataset completo, la mediana/media ya incluiría información del conjunto de prueba — el modelo terminaría evaluándose con un test set que ayudó a calibrar su propio preprocesamiento. |
| 6 | One-hot de nominales + escalado de numéricas | `X_train` únicamente | Mismo motivo: las categorías que el `OneHotEncoder` "conoce" y la media/desviación del `StandardScaler` deben venir solo de entrenamiento. `test` se transforma con esos parámetros ya fijos, nunca se reajustan. |
| 7 | Selección de características por correlación | `X_train` únicamente | Elegir qué variables entran al modelo mirando su correlación con el target en el conjunto de prueba sería, en la práctica, dejar que el test set opine sobre el diseño del modelo — una forma sutil de fuga que no deja rastro en las métricas hasta que el modelo se usa con datos nuevos de verdad. |

La regla resumen (tomada de `context.md`, sección "Partición y orden de ejecución"): **todo lo que se ajusta con los datos, se ajusta después de particionar, y solo con el lado de entrenamiento.** Lo único que se hace antes son reglas fijas (no dependen de los datos) o reportes de solo lectura (no se reutilizan).

## Decisiones con evidencia (resumen — detalle completo en el notebook)

- **Faltantes:** fuera de `TotalCharges` (ya excluida), 0 valores faltantes en las 17 columnas restantes. Se mantiene un imputador defensivo (mediana, por robustez a atípicos futuros) aunque hoy no tenga nada que imputar.
- **Duplicados:** 42 filas (20 grupos) coinciden exactamente en las columnas que ve el modelo; 34 de esas 42 tienen `tenure = 1` (catálogo de combinaciones de plan pequeño para clientes nuevos: 316 combinaciones distintas entre 388 clientes de un mes). Cada fila tiene un `customerID` original único y no son filas adyacentes en el archivo. **Se conservan todas.**
- **Atípicos:** 0 detectados por IQR en `tenure` y `MonthlyCharges`. No se aplica ningún recorte.
- **Codificación:** binarias → 0/1 directo; `InternetService`/`PaymentMethod` (nominal) → one-hot `drop="first"`; `Contract` → one-hot en vez de ordinal, pese a tener orden natural, porque el salto en la tasa de churn entre categorías no es lineal (42.8 % → 11.0 % → 3.1 %, según `context.md`).
- **Selección de características:** se conservan las 21 columnas procesadas. Ningún par de variables supera 0.80 de correlación entre sí; las de correlación débil con `Churn` se revisaron individualmente (no se descartó ninguna por umbral automático).
- **Variables condicionadas** (`SeniorCitizen`, `Partner`, `Dependents`): incluidas en el conjunto procesado, pero `context.md` exige una auditoría de sesgo por subgrupos antes de declarar válido cualquier modelo que las use. Esa auditoría pertenece a la fase de modelado (fuera del alcance de esta tarea de preprocesamiento) y queda pendiente, documentada aquí.

## Estructura de este directorio

```
MAI540_Modulo2_Tarea_2.2_Proyecto_Telco_Churn/
├── README.md                                          <- este archivo
├── context.md                                          <- reglas del proyecto (Tarea 2.1)
├── Tarea_2.2_Preprocesamiento_Telco_Churn.ipynb        <- notebook, ejecutable en Colab
├── requirements.txt                                    <- dependencias para correrlo localmente
└── .gitignore                                          <- bloquea CSVs y datos locales
```

## Dependencias

`pandas`, `numpy`, `scikit-learn` (ver `requirements.txt`). Todas vienen preinstaladas en Google Colab.
