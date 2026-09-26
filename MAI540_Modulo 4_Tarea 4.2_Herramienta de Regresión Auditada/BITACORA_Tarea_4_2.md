# Bitácora de desarrollo asistido — Tarea 4.2: Herramienta de Regresión Auditada

MAI 540 — Machine Learning | Módulo 4 | Sesión con Claude Code del 25 de septiembre de 2026

## Forma de trabajo

Fui pegando cada punto de la consigna tal cual, con la misma restricción en todos: *"debes ejecutarla tal como se indica, no debes alucionar si tienes duda me consultas"*. Esa instrucción funcionó igual que en la Tarea 4.1: Claude se detuvo a preguntarme antes de decidir cosas que eran mías (qué columnas prohibir por fuga, cómo tratar los duplicados, el umbral de disparidad para regresión, cómo corregir el hallazgo de la auditoría), en vez de decidirlas por su cuenta y seguir.

## Paso 1 — Definir el problema y elegir los datos

- **Objetivo:** una variable continua, una decisión de negocio, una columna de fuga y una de subgrupos.
- **Instrucción que funcionó:** solo pegar el punto 1. Claude exploró el CSV (`CO2 Emissions_Canada.csv`, 7.385 filas) antes de proponer nada, y verificó con código que las columnas de consumo tienen R² ≥ 0,98 contra el CO₂ dentro de cada tipo de combustible, antes de marcarlas como fuga.
- **Decisiones mías (consultadas con `AskUserQuestion`):** qué columnas de consumo prohibir (elegí solo Comb L/100 km y mpg, dejando City/Hwy), qué variable usar para subgrupos (Fuel Type) y qué decisión de negocio apoya la predicción (estimar antes de homologar).
- **Verifiqué:** que el MD5 del CSV copiado a la carpeta del proyecto coincidiera con el original.

## Paso 2 — Construir la herramienta

- **Objetivo:** partición antes de preprocesar, tres modelos sobre la misma partición.
- **Lo que pedí explícitamente:** "pídele a Claude Code el plan y revísalo" — Claude presentó el plan completo (columnas, partición, pipeline, hiperparámetros) *antes* de escribir código, con cuatro preguntas para mí: qué hacer con City/Hwy (decidí prohibirlas también, porque contradecían la decisión del paso 1), cómo tratar los 1.103 duplicados exactos, qué hacer con la única fila de gas natural, y si excluir Make/Model.
- **Decisiones de Claude (no pedidas):** imputación con mediana/moda dentro del Pipeline (aunque hoy no hay nulos, como protección ante datos nuevos), `OneHotEncoder(handle_unknown="ignore")`, `StandardScaler` en las numéricas, y Random Forest con 300 árboles como segundo modelo, justificado por captar interacciones no lineales.
- **Verifiqué:** que la media aprendida por el escalador coincidiera con la del entrenamiento y no con la del dataset completo (evidencia de que no hay fuga en el preprocesamiento).

## Paso 3 y 4 — Métricas y residuos

- Pedí la tabla de MSE/RMSE/R² de los tres modelos y la interpretación en palabras. Claude generó el texto con las cifras reales del cuaderno, no genéricas: RMSE de 15,37 g/km para Random Forest, con la comparación explícita contra la referencia trivial (reducción del 74,2 %).
- En residuos, Claude fue más allá de lo pedido: buscó, sin usar `Make`/`Model` como predictoras, qué tenían en común los vehículos con mayor error, y encontró que los híbridos y los de tracción integral tienen un sesgo sistemático que las cinco especificaciones permitidas no capturan. Esto no lo pedí; lo verifiqué revisando los nombres de los vehículos con mayor residuo.

## Paso 5 — Auditar con la Skill

- **Instrucción:** ejecutar la Skill de la 4.1 *tal cual* primero, como evidencia de qué tan reutilizable era, antes de extenderla. Corrí `claude -p "/auditoria-modelos ..."` con la v1.4 sin tocar: 6 de 15 subcriterios (los de clasificación: matriz de confusión, accuracy, etc.) quedaron en "NO SE PUEDE DETERMINAR — no aplica a regresión".
- **Decisión mía:** el umbral de disparidad en regresión (razón RMSE subgrupo/global ≤ 1,10, en vez de la diferencia absoluta de 0,10 que usa la Skill en clasificación).
- Claude extendió `SKILL.md` a la v2.0 (criterios de regresión para V1, V2.3 y V4) en un commit aparte, documentando en el README de la Skill qué cambió y por qué.
- **Resultado de la v2.0:** un solo hallazgo, V4.2 FALLA — el subgrupo diésel superaba el umbral (razón 1,2407).
- **Verifiqué:** que las 16 citas de celda del informe (`celda [i] (id=...)`) correspondieran de verdad a esa celda del cuaderno, comparando contra los `id` reales del `.ipynb`. Coincidieron todas.

## Paso 6 — Corregir el hallazgo

- Pedí que la corrección se decidiera *antes* de mirar el conjunto de prueba, y que se probara una sola vez. Claude propuso, y yo aprobé, tres intentos en orden:
  1. **Ponderar por tipo de combustible** (`sample_weight`): no corrigió — la razón del diésel bajó apenas a 1,2238 y empeoró el error global.
  2. **Elegir una alternativa con validación cruzada** sobre el entrenamiento (menos hojas, separar el tipo de transmisión de las marchas): tampoco corrigió en prueba, pero reveló algo importante — en CV, el diésel *no* tenía más error (razón 0,79), así que el problema no era el modelo.
  3. **Corregir la causa real:** revisando los residuos, Claude encontró que los dos mayores errores del diésel eran el mismo vehículo escrito dos veces con distinta capitalización ("Colorado ZR2 4WD" / "COLORADO ZR2 4WD"). Normalizar `Make`/`Model` antes de eliminar duplicados corrigió la disparidad (razón 1,00).
- Esta fue una decisión que Claude señaló con honestidad: encontró la causa mirando la prueba, aunque la corrección en sí (una regla de limpieza aplicada igual a todo el dataset, antes de dividir) no es el tipo de ajuste que la Skill prohíbe. Lo dejó explícito en el informe, sin ocultarlo.
- **Verifiqué:** que la segunda auditoría (v2.0 sobre el modelo corregido) diera los 15 subcriterios PASA, y volví a comprobar las citas de celda contra los `id` del cuaderno.

## Paso 7 — Limitaciones

Pedí el rango de entrenamiento, los subgrupos con más error, qué variables cambian con el tiempo y cuándo no usar la herramienta. Claude calculó todo en código (no de memoria) y encontró un ejemplo concreto de extrapolación que no había pedido: el único vehículo de 16 cilindros del dataset (un Bugatti Chiron) quedó en prueba, fuera del rango de entrenamiento, con un error de +114,5 g/km — la evidencia más clara de por qué no extrapolar.

## Qué queda pendiente o sin resolver

- Los dos intentos de corrección que no funcionaron (ponderación y la alternativa de CV) quedan documentados en el cuaderno como evidencia, pero no se aplican al modelo final.
- El umbral relativo de disparidad (razón ≤ 1,10) es una adaptación mía del 0,10 absoluto de Telco; no viene de una fuente externa, y queda declarado como decisión propia en `context.md`.
