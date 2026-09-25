# auditoria-modelos

Skill de Claude Code que audita un proyecto de machine learning supervisado (notebook `.ipynb` o script `.py`) y escribe un informe `AUDIT_REPORT.md`. **Solo audita: no modifica ni ejecuta el código auditado.**

MAI 540 — Machine Learning | Tarea 4.1

## Qué audita

15 subcriterios agrupados en 6 verificaciones. Cada uno se resuelve como `PASA`, `FALLA` o `NO SE PUEDE DETERMINAR`, y siempre con evidencia citada (celda o línea).

| Verificación | Subcriterios |
|---|---|
| V1 Métricas reportadas | V1.1 rango válido · V1.2 consistencia con la matriz de confusión · V1.3 clase positiva correcta · V1.4 no solo accuracy con desbalance · V1.5 métrica acorde al costo del error |
| V2 Partición de datos | V2.1 dividir antes de preprocesar · V2.2 semilla fija · V2.3 estratificación · V2.4 misma partición para los modelos comparados |
| V3 Fuga de información | V3.1 nada se ajusta con datos de prueba · V3.2 ninguna columna posterior a la predicción |
| V4 Disparidad entre subgrupos | V4.1 métrica por subgrupo · V4.2 diferencia con la métrica global ≤ 0.10 (mínimo 20 positivos por subgrupo) |
| V5 Validez de datos de entrada | V5.1 sin `inf`/`NaN` al entrenar |
| V6 Variables no admisibles | V6.1 sin identificadores ni atributos prohibidos |

Los criterios exactos (qué hace PASA, FALLA o NO SE PUEDE DETERMINAR cada uno) están en `SKILL.md`.

## Cómo se invoca

Desde la raíz de este repositorio (donde está `.claude/skills/`), en Claude Code:

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

- **Solo clasificación.** Los criterios de V1 suponen matriz de confusión, precisión, exhaustividad y F1. No sabe auditar regresión (MSE, RMSE, R², residuos) sin extenderla.
- **Depende de las salidas guardadas.** No ejecuta el proyecto, así que lo que dependa de un número que el notebook no imprimió queda en `NO SE PUEDE DETERMINAR`. Por ejemplo, en Iris V1.4 queda así porque el notebook nunca imprime la distribución de clases.
- **No detecta errores que solo aparecen al ejecutar.** Por ejemplo, celdas ejecutadas fuera de orden. En la prueba con biopsias lo anotó en Limitaciones, pero no lo convirtió en veredicto.
- **Solo revisa lo que cubren V1–V6.** En el notebook original de biopsias, `guardar_modelo(modelo)` y `predecir_caso(modelo, …)` usan un modelo que nunca se entrenó, y el caso de ejemplo para predecir incluye la columna con fuga. Ningún subcriterio cubre la etapa de guardado e inferencia.
- **La restricción de solo lectura no es absoluta.** `disallowed-tools: Edit NotebookEdit` se levanta con el siguiente mensaje del usuario, y la Skill no bloquea `Bash` por sí misma. Para garantizar que no modifique nada, invócala con `--allowedTools` restringido, como en el ejemplo.
- **El formato de evidencia supone `id` de celda.** Los notebooks en formato anterior a nbformat 4.5 no tienen `id`.
- **Los veredictos los emite un modelo de lenguaje.** La estabilidad se probó repitiendo auditorías sobre el mismo proyecto. Aun así, verifica la evidencia citada antes de actuar.

## Historial de versiones

| Versión | Cambio | Motivo |
|---|---|---|
| 1.0 | Versión inicial | — |
| 1.1 | Prohíbe reutilizar informes `AUDIT_REPORT*.md` anteriores y escribe la versión en el cuerpo del `SKILL.md` | Una segunda ejecución sobre biopsias leyó el informe anterior y repitió sus veredictos sin auditar. Además, un informe salió sin número de versión, porque el encabezado YAML no siempre es visible para el modelo. |
| 1.2 | V2.4: "mismos datos" = la misma variable `X`, sin transformar fuera del estimador | Con un defecto inyectado (KNN evaluado con `X_escalado`, los demás modelos con `X`), la v1.1 dio PASA porque "las filas son las mismas". |
| 1.3 | V1.4 se juzga por el código, no por las salidas | Dos ejecuciones de la v1.1 sobre el mismo notebook de biopsias dieron FALLA y NO SE PUEDE DETERMINAR en V1.4. |
