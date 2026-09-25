# Bitácora de desarrollo asistido — Tarea 4.1: Skill de auditoría de modelos

MAI 540 — Machine Learning | Módulo 4 | Sesiones con Claude Code del 23 y 24 de septiembre de 2026

## Forma de trabajo

En cada punto pegué la consigna textual y agregué la misma restricción: *"haz exactamente lo que están solicitando por favor no alucines"*. El 24-sep pedí además *"cualquier duda me consultas"*. Esa instrucción funcionó: Claude se detuvo a preguntar en cuatro decisiones que eran mías (qué hacer con housing, qué hacer con los archivos que yo había borrado en GitHub, el formato de esta bitácora y cómo resolver que la Skill rechazara housing) en lugar de decidirlas por su cuenta.

## Paso 1 — Cerrar la evaluación de clasificación

- **Objetivo:** matriz de confusión y precisión, exhaustividad y F1 de "maligno" en biopsias; KNN y Random Forest en Iris.
- **Decisiones de Claude:**
  - Usó `pos_label=0`, porque en el dataset `0 = maligno`, y recalculó las métricas a mano desde la matriz con `assert`.
  - En KNN puso el `StandardScaler` dentro de un `Pipeline` y eligió k entre 1 y 30 con un `GridSearchCV` de 5 particiones anidado en la validación cruzada de 10 particiones.
  - En Random Forest usó 100 árboles con `random_state=42`.
- **Verificación:** el 24-sep volví a ejecutar el código de ambos notebooks sobre una copia. Los resultados coincidieron con los guardados:
  - Biopsias: VP = 27, FN = 26, FP = 12, precisión 0.6923, exhaustividad 0.5094, F1 0.5870.
  - Iris: KNN 0.9600 y Random Forest 0.9533.

## Paso 2 — Lista de verificaciones

- **Objetivo:** criterios que puedan pasar o fallar, cada uno ligado a un error de los Módulos 1 a 3.
- **Decisiones de Claude (no pedidas):**
  - Dividió las 4 verificaciones mínimas en 13 subcriterios y agregó V5 (datos no finitos) y V6 (identificadores o atributos prohibidos), con lo que suman 15.
  - Definió "desbalance" como una razón ≥ 1.5 y exigió al menos 20 positivos por subgrupo.
  - El umbral de 0.10 para la disparidad no lo inventó: viene de mi `context.md` del Módulo 2.
- **Verificación:** comprobé cada cifra citada contra el archivo de origen: 0.8000 y `[[763 63] [162 137]]` en la Tarea 1.2; 73,47 %, r = 0,9996 y "≤ 0,10" en `context.md`; 135 `inf` y 212/212 en `INFORME_TAREA_3_1.md`.

## Paso 3 — Redactar la Skill

- **Instrucción:** la consigna del punto 3 más *"no alucines"*.
- **Decisiones de Claude:**
  - En el encabezado: `argument-hint`, `arguments`, `disallowed-tools: Edit NotebookEdit` y `metadata.version`.
  - Evidencia con el formato `celda [i] (id=…)`, sin ejecutar nunca el código auditado y sin inventar números.
  - Si el informe ya existe, se crea con sufijo `_2` en vez de sobrescribirlo.
  - Una sección de "Limitaciones" en el informe y una autorrevisión que cuenta 15 filas.
- **Verificación:** confirmé en la documentación oficial (code.claude.com/docs/en/skills) que existen todos los campos del encabezado, y comprobé que los notebooks tienen `id` de celda.

## Paso 4 — Ejecutar sobre tres proyectos

- **Instrucciones que no funcionaron:**
  - `claude -p "/auditoria-modelos …" --allowedTools "Skill" … --permission-mode dontAsk`: la herramienta Skill fue rechazada.
  - La primera ejecución sobre `housing.csv` terminó sin informe y la Skill pidió el notebook.
- **Instrucción que funcionó:** `--allowedTools "Skill(auditoria-modelos)" "Read" "Glob" "Grep" "Write"`, sin `Bash`, para que la auditoría no pudiera ejecutar código. Estas ejecuciones usaron el modelo predeterminado del CLI (Sonnet 5).
- **Decisiones:**
  - La consigna pide el notebook de Iris "ya con los cinco clasificadores". El archivo que yo adjunté era la plantilla sin resolver, así que se auditó la versión de `iris-clasificadores-repo`.
  - Para housing elegí auditar solo el CSV. Claude propuso `ocean_proximity` como variable de subgrupo.
- **Verificación:**
  - Anoté las respuestas correctas de biopsias **antes** de leer el informe.
  - Guardé el hash MD5 de cada notebook antes y después de auditar: ninguno cambió.
  - Validé con un script que el `id` de cada cita corresponda a esa celda.
  - Comprobé la línea 292 y los 207 nulos de `total_bedrooms` en `housing.csv`.

## Paso 5 — Estabilidad y refinamiento

- **Objetivo:** ejecutar dos veces sobre el mismo proyecto e introducir un defecto a propósito.
- **Qué encontré:**
  - **v1.0:** la segunda ejecución leyó el informe anterior y lo dio por bueno; un informe salió sin versión.
  - **v1.1:** V1.4 cambió de FALLA a NO SE PUEDE DETERMINAR entre dos ejecuciones.
  - **Defecto inyectado:** escalado de todo `X` antes de la validación cruzada, dejando comentarios engañosos. La v1.1 detectó la fuga (V2.1 y V3.1 FALLA), no se dejó engañar por los comentarios, pero dio PASA en V2.4.
- **Qué cambié:** la v1.1 prohíbe reutilizar informes y pone la versión en el cuerpo del archivo; la v1.2 precisa qué significa "mismos datos" en V2.4; la v1.3 dice que V1.4 se juzga por el código.
- **Verificación:**
  - Con la v1.3, las dos ejecuciones sobre biopsias coinciden en los 15 subcriterios.
  - Con la v1.2, V2.4 da FALLA en la copia con el defecto.
  - En Iris, 4 de 4 ejecuciones coinciden.

## Paso 6 — Versionado

- **Commits:**
  - Uno por versión (1.0 → 1.4), con qué cambió y por qué. Como el SKILL.md de trabajo ya estaba modificado, Claude reconstruyó la historia a partir de copias de cada versión que había guardado antes de cada cambio.
  - Otro commit para el README de la Skill y otro para los informes.
- **GitHub:**
  - Yo había borrado desde la web el notebook corregido de la 3.1 y su informe. Por instrucción mía se integraron esos commits y se restauraron los tres archivos.
  - También se subió el notebook de Iris con los cinco clasificadores, con el mismo nombre de archivo.

## Lo que queda pendiente o sin resolver

- Algunas citas tienen el índice de celda corrido en una posición, aunque el `id` es correcto. Está documentado en el README; no está corregido.
- El informe final de biopsias no menciona que `guardar_modelo` y `predecir_caso` usan un modelo nunca entrenado. Ningún criterio cubre la etapa de guardado e inferencia.
