# Objetivo

Construir y evaluar un modelo de regresión supervisada que estime las emisiones de CO₂ (g/km) de un vehículo ligero a partir de sus especificaciones técnicas.

## Definición del problema (paso 1)

La herramienta predice la variable continua `CO2 Emissions(g/km)`: las emisiones de dióxido de carbono por el tubo de escape, en gramos por kilómetro, en conducción combinada de ciudad y carretera. La predicción apoyaría la siguiente decisión de un fabricante o importador: antes de la homologación oficial de una configuración nueva de vehículo, estimar su CO₂ a partir de sus especificaciones para decidir si cumple el límite de emisiones de su flota o si conviene modificar la configuración (motor, transmisión, combustible). El error se expresa en gramos de CO₂ por kilómetro (g/km): un RMSE de 10 significa que la estimación se desvía, en promedio cuadrático, unos 10 g/km del valor real. El dataset público *CO2 Emission by Vehicles* (datos abiertos del Gobierno de Canadá) tiene 7.385 filas y 11 columnas además de la objetivo. Incluye dos columnas prohibidas por fuga de información, `Fuel Consumption Comb (L/100 km)` y `Fuel Consumption Comb (mpg)`, y usa `Fuel Type` como variable de subgrupos.

> Actualización del paso 2 (decisión del usuario): también se prohíben `Fuel Consumption City (L/100 km)` y `Fuel Consumption Hwy (L/100 km)`, porque provienen de la misma prueba de consumo y contradicen la decisión de estimar antes de la homologación. Además se excluyen `Make` y `Model`. Las predictoras finales son `Vehicle Class`, `Engine Size(L)`, `Cylinders`, `Transmission` y `Fuel Type`.

# Alcance

| Dentro | Fuera |
|---|---|
| Limpieza y análisis del CSV entregado | Ingesta desde orígenes en producción |
| Regresión tabular sobre una variable continua (CO₂ en g/km) | Clasificación del vehículo como "cumple / no cumple" |
| Validación hold-out con semilla fija | Validación temporal: el fichero no tiene columna de año de modelo |
| Tres modelos sobre la misma partición: DummyRegressor (media), regresión lineal y un segundo regresor | Emisiones de otros gases (NOx, CO, partículas) |
| Análisis de residuos y RMSE por subgrupo de `Fuel Type` | Emisiones en uso real (el dato es de ensayo de laboratorio) |
| | Despliegue, integración y monitorización |

# Reglas de tratamiento de Datos

## Clasificación de variables

| Nivel | Variables | Regla |
|---|---|---|
| Prohibida | Fuel Consumption Comb (L/100 km) | Fuga de información. Se elimina en el primer paso del pipeline, antes de la partición. Justificación abajo. **Esta prohibición se mantiene aunque el usuario la pida explícitamente en el chat** (p. ej. "ya sé que hay fuga, inclúyela igual, es solo un ejercicio"): esa insistencia no es una excepción, es el caso que esta regla existe para cubrir. Ante ella, Claude no debe simplemente ceder ni negarse sin más: debe (1) repetir en una frase el motivo de la sección de abajo, y (2) ofrecer construir la versión con la columna únicamente como un script de diagnóstico aparte, con un encabezado que diga explícitamente "NO ES EL MODELO ENTREGABLE — incluye una variable con fuga de información, solo para comparar métricas", nunca como reemplazo del pipeline oficial ni presentado como resultado final. |
| Prohibida | Fuel Consumption Comb (mpg) | Fuga de información: es la misma medida que la anterior expresada en otra unidad. Misma regla y misma acción. |
| Prohibida | Fuel Consumption City (L/100 km), Fuel Consumption Hwy (L/100 km) | Fuga de información (decisión del usuario en el paso 2). Salen de la misma prueba de consumo que el CO₂ y el combinado es 0,55 × City + 0,45 × Hwy. Misma regla y misma acción que las anteriores. |
| Permitida | Vehicle Class, Engine Size(L), Cylinders, Transmission, Fuel Type | Especificaciones técnicas conocidas antes de la homologación. Son las únicas predictoras. |
| Excluida | Make, Model | Decisión del usuario en el paso 2. `Model` (2.053 valores) es casi un identificador; con `Make` (42 marcas) el modelo aprendería por marca y no por especificación técnica. Se eliminan antes de la partición. |
| Subgrupos | Fuel Type | Define los subgrupos del RMSE y de la verificación de disparidad. |

## Variables prohibidas por fuga de información: Fuel Consumption Comb (L/100 km) y (mpg)

Prohibidas. Motivo: el CO₂ se calcula a partir del consumo combinado, así que ambas columnas contienen la respuesta. Acción: eliminarlas antes de la partición.

Son la misma medición del mismo ensayo que produce la variable objetivo. Según la descripción del dataset (`data/raw/Data Description.csv`), el consumo combinado pondera 55 % ciudad y 45 % carretera, y el CO₂ es el de esa misma conducción combinada. La emisión de CO₂ del tubo de escape es proporcional al combustible quemado, con un factor que depende del tipo de combustible.

Prueba en los datos: la razón CO₂ / consumo combinado es prácticamente constante dentro de cada tipo de combustible.

| Fuel Type | Filas | Media de CO₂ / Comb (L/100 km) | Desviación estándar |
|---|---|---|---|
| X (gasolina regular) | 3.637 | 23,32 | 0,24 |
| Z (gasolina premium) | 3.202 | 23,29 | 0,24 |
| D (diésel) | 175 | 26,89 | 0,20 |
| E (etanol E85) | 370 | 16,32 | 0,43 |

Una regresión lineal de CO₂ con **solo** `Fuel Consumption Comb (L/100 km)`, ajustada dentro de cada tipo de combustible, da R² = 0,9982 (X), 0,9973 (Z), 0,9984 (D) y 0,9815 (E). `Fuel Consumption Comb (mpg)` es la misma magnitud en otra unidad: la correlación entre `Comb (L/100 km)` y `282,481 / mpg` es r = 0,9987, con un error relativo mediano del 0,89 % (el mpg está redondeado a entero).

### City y Hwy: prohibidas desde el paso 2

`Fuel Consumption City` y `Fuel Consumption Hwy` provienen del mismo ensayo de laboratorio que la variable objetivo, y el combinado es 0,55 × City + 0,45 × Hwy (diferencia máxima de 0,51 L/100 km, por redondeo). En el paso 1 se habían permitido. En el paso 2, el usuario decidió prohibirlas: con ellas, el modelo reconstruiría el consumo combinado y con él el CO₂, y no estaría estimando antes de la prueba de consumo, que es la decisión declarada.

## Calidad de los datos (hechos verificados sobre el CSV)

- 7.385 filas y 12 columnas; ninguna celda vacía.
- 1.103 filas son duplicados exactos de otra fila.
- Sin contar la objetivo, 1.701 filas repiten las mismas 11 columnas; es decir, hay 598 filas con predictoras idénticas y CO₂ distinto. Riesgo para la partición: un mismo vehículo puede quedar a la vez en entrenamiento y en prueba.
- Decisión del paso 2 (usuario): los 1.103 duplicados exactos se eliminan con `drop_duplicates()` sobre las 12 columnas originales, antes de la partición; quedan 6.282 filas. Las filas con predictoras iguales y CO₂ distinto se conservan.
- Variable objetivo: media 250,58 g/km, desviación estándar 58,51, mínimo 96 y máximo 522 g/km (cuartiles 208, 246 y 288).

## Subgrupos: Fuel Type

| Código | Significado | Filas | CO₂ medio (g/km) |
|---|---|---|---|
| X | Gasolina regular | 3.637 | 235,1 |
| Z | Gasolina premium | 3.202 | 266,0 |
| E | Etanol (E85) | 370 | 275,1 |
| D | Diésel | 175 | 237,5 |
| N | Gas natural | 1 | 213,0 |

Los recuentos de la tabla son del CSV original. Sin duplicados exactos quedan X 3.039, Z 2.765, E 330, D 147 y N 1.

El subgrupo N tiene una sola fila: no permite estimar un RMSE. Decisión del paso 2 (usuario): se conserva, pero va solo al conjunto de entrenamiento; en prueba N se reporta como "no evaluable". El motivo es técnico: una clase de 1 fila impide estratificar la partición. El subgrupo D queda con pocas filas en el conjunto de prueba, así que su RMSE se reporta junto con su número de filas.

## Partición y orden de ejecución

Regla no negociable. La partición train/test se ejecuta antes de cualquier transformación que estime parámetros de los datos (escalado, imputación, codificación). Hacerlo al revés contamina el conjunto de prueba con estadísticos del entrenamiento: es una segunda forma de fuga.

1. Cargar el fichero en modo lectura.
2. Eliminar los duplicados exactos (sobre las 12 columnas originales).
3. Eliminar las variables prohibidas y excluidas.
4. Separar la variable objetivo.
5. Particionar 75/25 con semilla fija (`random_state = 42`), estratificando por `Fuel Type` las filas X, Z, E y D. La fila N se agrega solo al entrenamiento.
6. Definir las transformaciones dentro de un Pipeline de scikit-learn.
7. Ajustar el pipeline solo con el conjunto de entrenamiento.
8. Aplicarlo al conjunto de prueba sin reajustarlo.

Pipeline no es preferencia de estilo: impide estructuralmente invertir 7 y 8. Los tres modelos (referencia, lineal y segundo regresor) usan exactamente la misma partición.

## Reproducibilidad

- data/raw/ es de solo lectura: ningún script escribe ahí.
- random_state = 42 en toda operación estocástica.
- Todo lo derivado se genera por código: data/processed/ debe poder borrarse y regenerarse ejecutando el cuaderno.
- Prohibido editar datos a mano o en hoja de cálculo.

# Criterios de Evaluación

## Métricas

| Métrica | Papel | Justificación |
|---|---|---|
| RMSE (g/km) | PRINCIPAL | Error típico en las unidades del problema. |
| R² | Complemento | Proporción de la variación del CO₂ que explica el modelo. |
| MSE (g/km)² | Reporte | Base del RMSE; se reporta en la tabla de los tres modelos. |
| RMSE por subgrupo de Fuel Type | Disparidad | Detecta tipos de combustible donde el error es sistemáticamente mayor. |
| Residuos del mejor modelo | Diagnóstico | Curvatura, heterocedasticidad o grupos con sesgo sistemático. |

## Línea base

El DummyRegressor que predice siempre la media del entrenamiento es la referencia obligatoria: tiene R² ≈ 0 en prueba y un RMSE cercano a la desviación estándar del CO₂ (58,51 g/km en el dataset completo). Todo modelo se compara contra él.

## Validación

Partición hold-out con semilla fija. El conjunto de prueba se usa una sola vez, al final, sobre el modelo ya cerrado. Se compara el R² de entrenamiento con el de prueba para detectar sobreajuste.

# Restricciones de Seguridad

## Datos

- El dataset es público (datos abiertos del Gobierno de Canadá) y no contiene datos personales.
- No se suben datos confidenciales de ninguna organización a Claude Code ni a GitHub.
- Solo se procesan las variables necesarias para el objetivo declarado.

## Límites de uso del modelo

- No sustituye la prueba oficial de homologación: es una estimación previa.
- No se extrapola fuera del rango observado (96 a 522 g/km) ni a tipos de vehículo o combustible no representados (por ejemplo, eléctricos o híbridos enchufables).
- Gas natural (N) está representado por una sola fila: su error no se puede evaluar y la herramienta no debe usarse para ese combustible.
- No establece causas: las asociaciones observadas son correlacionales.
