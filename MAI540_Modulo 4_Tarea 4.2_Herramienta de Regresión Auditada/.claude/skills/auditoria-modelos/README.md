# auditoria-modelos

Skill de Claude Code que audita un proyecto de machine learning supervisado (notebook `.ipynb` o script `.py`) y escribe un informe `AUDIT_REPORT.md`. **Solo audita: no modifica ni ejecuta el código auditado.**

MAI 540 — Machine Learning | Tarea 4.1 (versiones 1.x) · Tarea 4.2 (versión 2.0: extensión a regresión)

## Qué audita

15 subcriterios agrupados en 6 verificaciones. Cada uno se resuelve como `PASA`, `FALLA` o `NO SE PUEDE DETERMINAR`, y siempre con evidencia citada (celda o línea).

| Verificación | Subcriterios |
|---|---|
| V1 Métricas reportadas | **Clasificación:** V1.1 rango válido · V1.2 consistencia con la matriz de confusión · V1.3 clase positiva correcta · V1.4 no solo accuracy con desbalance · V1.5 métrica acorde al costo del error. **Regresión (v2.0):** V1.1 MSE/RMSE ≥ 0 y R² ≤ 1 · V1.2 RMSE = √MSE y R² = 1 − MSE/Var · V1.3 referencia trivial (`DummyRegressor`) · V1.4 error en unidades y R², en entrenamiento y prueba · V1.5 análisis de residuos |
| V2 Partición de datos | V2.1 dividir antes de preprocesar · V2.2 semilla fija · V2.3 estratificación (en regresión: la partición conserva los subgrupos) · V2.4 misma partición para los modelos comparados |
| V3 Fuga de información | V3.1 nada se ajusta con datos de prueba · V3.2 ninguna columna posterior a la predicción |
| V4 Disparidad entre subgrupos | **Clasificación:** V4.1 métrica por subgrupo · V4.2 diferencia con la métrica global ≤ 0.10 (mínimo 20 positivos por subgrupo). **Regresión (v2.0):** V4.1 RMSE por subgrupo · V4.2 RMSE del subgrupo / RMSE global ≤ 1.10 (mínimo 20 filas en prueba) |
| V5 Validez de datos de entrada | V5.1 sin `inf`/`NaN` al entrenar |
| V6 Variables no admisibles | V6.1 sin identificadores ni atributos prohibidos |

Los criterios exactos (qué hace PASA, FALLA o NO SE PUEDE DETERMINAR cada uno) están en `SKILL.md`.

## Cómo se invoca

Abre Claude Code en la carpeta que contiene `.claude/skills/` (la v2.0 está en `MAI540_Modulo 4_Tarea 4.2_Herramienta de Regresión Auditada`; la v1.4 sigue en `MAI540_Modulo4_Tarea_4.1`) y escribe:

```
/auditoria-modelos <ruta-del-proyecto> <columna-objetivo> <columna(s)-subgrupo|ninguna> [nombre-del-informe]
```

Ejemplo:

```
/auditoria-modelos "ruta/App_Diagnostico_Biopsias_Mama.ipynb" diagnostico ninguna AUDIT_REPORT_biopsias_original.md
```

Sin interfaz (así se ejecutaron las pruebas de la Tarea 4.1). Si el proyecto está fuera del repositorio, hay que darle acceso a esa carpeta con `--add-dir`:

```
claude -p "/auditoria-modelos <ruta> <objetivo> <subgrupos> <informe>" --add-dir "<carpeta del proyecto>" --allowedTools "Skill(auditoria-modelos)" "Read" "Glob" "Grep" "Write" --permission-mode dontAsk
```

Con `--permission-mode dontAsk`, el permiso tiene que ser `Skill(auditoria-modelos)`: en las pruebas, pasar solo `Skill` hizo que la invocación fuera rechazada. No se autoriza `Bash`, para que la auditoría no pueda ejecutar el código del proyecto.

El informe se guarda en la carpeta del proyecto auditado. Si ya existe un informe con ese nombre, se crea `_2`, `_3`, etc.; nunca se sobrescribe.

## Cómo interpretar el informe

- **Resumen (6 filas):** una verificación da `FALLA` si alguno de sus subcriterios falla. Si ninguno falla pero alguno no se puede determinar, da `NO SE PUEDE DETERMINAR`. Solo da `PASA` si todos pasan.
- **Tabla de verificación (15 filas):** cada fila lleva la evidencia en formato `celda [i] (id=…)` o `archivo.py:línea`, con el fragmento literal. `i` es la posición de la celda en el `.ipynb` contando desde 0, incluidas las celdas de texto. Antes de actuar sobre un veredicto, abre esa celda.
- **`NO SE PUEDE DETERMINAR` no es un PASA.** Significa que el proyecto no muestra evidencia suficiente (por ejemplo, no hay salidas guardadas o no hay subgrupos). La columna de observación dice qué falta.
- **Acciones recomendadas:** hay una por cada subcriterio en `FALLA` (prioridad alta) o `NO SE PUEDE DETERMINAR` (prioridad media). Describen qué cambiar; la Skill no aplica ninguna.
- **Limitaciones:** lo que la auditoría no pudo verificar en ese proyecto concreto.

## Limitaciones conocidas

- **Clasificación y regresión desde la v2.0.** Hasta la v1.4, los criterios de V1 suponían matriz de confusión, precisión, exhaustividad y F1, y no sabían auditar regresión. La v2.0 agrega criterios de regresión para V1, V2.3 y V4. No cubre otros tipos de problema (series de tiempo, clustering, ranking).
- **Los argumentos con espacios no se reciben bien.** En la Tarea 4.2 se invocó con `"CO2 Emissions(g/km)" "Fuel Type" AUDIT_REPORT_v1.4_sin_extension.md`. La v1.4 escribió `AUDIT_REPORT.md` (el nombre por defecto) e informó que no se entregó el subgrupo, aunque lo encontró en el código. Si la objetivo o el subgrupo tienen espacios, verifica en el encabezado del informe qué valores usó, y renombra el informe después si hace falta. Este fallo no está corregido.
- **En regresión, el umbral de V4.2 es relativo (razón ≤ 1.10).** Solo penaliza a los subgrupos con más error que el global. Si un proyecto necesita un umbral absoluto en sus unidades, debe declararlo en un archivo de apoyo.
- **Depende de las salidas guardadas.** No ejecuta el proyecto, así que lo que dependa de un número que el notebook no imprimió queda en `NO SE PUEDE DETERMINAR`. Por ejemplo, en Iris V1.4 queda así porque el notebook nunca imprime la distribución de clases.
- **No detecta errores que solo aparecen al ejecutar.** Por ejemplo, celdas ejecutadas fuera de orden. En la prueba con biopsias lo anotó en Limitaciones, pero no lo convirtió en veredicto.
- **Solo revisa lo que cubren V1–V6.** En el notebook original de biopsias, `guardar_modelo(modelo)` y `predecir_caso(modelo, …)` usan un modelo que nunca se entrenó, y el caso de ejemplo para predecir incluye la columna con fuga. Ningún subcriterio cubre la etapa de guardado e inferencia.
- **La restricción de solo lectura no es absoluta.** `disallowed-tools: Edit NotebookEdit` se levanta con el siguiente mensaje del usuario, y la Skill no bloquea `Bash` por sí misma. Para garantizar que no modifique nada, invócala con `--allowedTools` restringido, como en el ejemplo.
- **El formato de evidencia supone `id` de celda.** Los notebooks en formato anterior a nbformat 4.5 no tienen `id`.
- **El índice de celda puede salir corrido en uno; el `id` es la referencia confiable.** Al contrastar las citas con los notebooks, aparecieron desfases de una posición en las últimas celdas de los notebooks de Iris. Por ejemplo, `celda [24] (id=f7eff5a0)` es en realidad la celda 25. Para ubicar la evidencia, busca siempre por `id`. Este fallo no está corregido.
- **Con un archivo de datos sin código (p. ej. solo `.csv`)**, la auditoría solo puede describir los datos: los 15 subcriterios quedan en `NO SE PUEDE DETERMINAR`.
- **Los veredictos los emite un modelo de lenguaje.** La estabilidad se probó repitiendo auditorías sobre el mismo proyecto. Aun así, verifica la evidencia citada antes de actuar.

## Historial de versiones

| Versión | Cambio | Motivo |
|---|---|---|
| 1.0 | Versión inicial | — |
| 1.1 | Prohíbe reutilizar informes `AUDIT_REPORT*.md` anteriores y escribe la versión en el cuerpo del `SKILL.md` | Una segunda ejecución sobre biopsias leyó el informe anterior y repitió sus veredictos sin auditar. Además, un informe salió sin número de versión, porque el encabezado YAML no siempre es visible para el modelo. |
| 1.2 | V2.4: "mismos datos" = la misma variable `X`, sin transformar fuera del estimador | Con un defecto inyectado (KNN evaluado con `X_escalado`, los demás modelos con `X`), la v1.1 dio PASA porque "las filas son las mismas". |
| 1.3 | V1.4 se juzga por el código, no por las salidas | Dos ejecuciones de la v1.1 sobre el mismo notebook de biopsias dieron FALLA y NO SE PUEDE DETERMINAR en V1.4. |
| 1.4 | Si la ruta no tiene código de modelo, igual se escribe el informe (15 subcriterios en NO SE PUEDE DETERMINAR) | Sobre `housing.csv` (solo datos), la v1.3 terminó sin informe y pidió el notebook, contradiciendo la regla 7. |
| 2.0 | Criterios de regresión para V1.1–V1.5 (rango, √MSE = RMSE y R² = 1 − MSE/Var, referencia trivial, error en unidades y R² en entrenamiento y prueba, residuos), V2.3 (la partición conserva los subgrupos) y V4 (RMSE por subgrupo, razón ≤ 1.10, mínimo 20 filas). Los criterios de clasificación no cambian. | Sobre la herramienta de regresión de CO₂ (Tarea 4.2), la v1.4 dejó 6 de 15 subcriterios (V1.1–V1.5 y V2.3) en NO SE PUEDE DETERMINAR por "no aplica". En V4.2 tuvo que improvisar: su umbral de 0.10 es para proporciones, así que aplicó el que declaraba `context.md`, cosa que su regla no le permitía. Informe: `auditorias/AUDIT_REPORT_v1.4_sin_extension.md`. |
