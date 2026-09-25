---
name: auditoria-modelos
description: Audita un proyecto de machine learning supervisado (notebook .ipynb o script .py) y emite un informe AUDIT_REPORT.md con veredictos PASA / FALLA / NO SE PUEDE DETERMINAR, cada uno con evidencia (celda o línea). Revisa métricas reportadas, partición de datos, fuga de información, disparidad entre subgrupos, validez de los datos de entrada y variables no admisibles. Usar cuando se pida auditar, revisar o validar un modelo, un pipeline de entrenamiento o su evaluación. Solo audita, no modifica el código.
argument-hint: <ruta-del-proyecto> <columna-objetivo> <columna(s)-subgrupo|ninguna> [nombre-del-informe]
arguments: [ruta, objetivo, subgrupos, informe]
disallowed-tools: Edit NotebookEdit
metadata:
  version: "1.2"
---

**Versión de esta Skill: 1.2** (este número es el que se escribe en el campo `Skill` del informe).

# Propósito

Verificar, con evidencia citada y sin modificar nada, si un proyecto de machine learning supervisado evalúa, divide y alimenta su modelo de forma válida, y dejar el resultado en un informe `AUDIT_REPORT.md`.

# Entradas esperadas

| Entrada | Argumento | Qué es | Si no se entrega |
|---|---|---|---|
| Proyecto | `$ruta` | Ruta a un `.ipynb` o `.py`, o a una carpeta. En una carpeta se auditan todos los `.ipynb` y `.py` que entrenan o evalúan un modelo, más los archivos que estos importan. | No se audita. Se pide la ruta y se detiene la Skill. |
| Columna objetivo | `$objetivo` | Nombre de la variable que el modelo predice (p. ej. `diagnostico`, `Churn`, `target`). | Se busca en el código la asignación de `y` (p. ej. `y = df['...']`) y se cita esa línea como evidencia. Si hay más de un candidato o ninguno, las verificaciones que dependen de ella quedan en NO SE PUEDE DETERMINAR. |
| Subgrupos | `$subgrupos` | Columna o columnas (separadas por coma) que definen los subgrupos para V4, o `ninguna`. | Se buscan en las columnas del proyecto atributos protegidos o sus proxies (sexo o género, edad o `SeniorCitizen`, estado civil o `Partner`, situación familiar o `Dependents`). Se usan los que aparezcan, citando dónde. |
| Nombre del informe | `$informe` | Nombre del archivo de salida (p. ej. `AUDIT_REPORT_biopsias_original.md`). | `AUDIT_REPORT.md`. |

Archivos de apoyo que se leen si existen en la carpeta del proyecto: `README.md`, `context.md`, `DESCRIPCION.md` e informes `.md` escritos por el autor del proyecto. Sirven como evidencia de lo que el proyecto **declara** (costo de los errores, variables prohibidas, cuándo se conoce cada columna). **Nunca son archivos de apoyo** los informes de auditorías anteriores (`AUDIT_REPORT*.md`): no se leen ni se citan (ver regla 7).

# Reglas obligatorias

1. **Audita, no modifica.** Está prohibido editar, reescribir, formatear o ejecutar los archivos auditados. Por eso `Edit` y `NotebookEdit` están deshabilitados en esta Skill. La única escritura permitida es crear el archivo del informe. Tampoco se ejecutan el notebook ni los scripts del proyecto, porque pueden escribir archivos (modelos `.joblib`, salidas) o cambiar las salidas guardadas. Si se usa Bash, es solo para leer (`grep`, `cat`, listar) o para aritmética sobre números copiados del proyecto, nunca para importar o correr su código.
2. **Todo veredicto cita evidencia.** Formatos:
   - notebook: `celda [i] (id=<id>)`, donde `i` es la posición en el arreglo `cells` del `.ipynb` contando desde 0 (incluye celdas de texto);
   - script: `archivo.py:línea`;
   - salida guardada: `celda [i] (id=<id>), salida`.

   La evidencia incluye el fragmento literal (código o salida) entre comillas invertidas, de máximo 2 líneas.
3. **Solo tres veredictos:** `PASA`, `FALLA`, `NO SE PUEDE DETERMINAR`. No se usan "parcial", "no aplica" ni "probablemente". Lo que no aplica (p. ej. no hay subgrupos, o hay un solo modelo) se registra como `NO SE PUEDE DETERMINAR` y el motivo va en la columna de observación.
4. **Sin evidencia no hay PASA.** Si no se encuentra la celda, la línea o la salida que demuestre el criterio, el veredicto es `NO SE PUEDE DETERMINAR`. Nunca se asume que algo está bien porque no se vio que estuviera mal.
5. **No inventar números.** Toda cifra del informe es una de dos cosas: (a) una salida guardada en el proyecto, citada, o (b) aritmética sobre esas salidas, con la operación escrita (p. ej. `27/(27+12) = 0.6923`). Si el notebook no tiene salidas guardadas, lo que depende de ellas queda en `NO SE PUEDE DETERMINAR`.
6. **Evaluar todos los subcriterios, siempre, en el orden fijo** V1.1 → V6.1. No se omite ninguno, aunque el resultado parezca obvio.
7. **Cada ejecución es una auditoría completa e independiente.** Aunque ya exista un `AUDIT_REPORT*.md` en la carpeta, no se lee, no se reutiliza, no se compara y no se declara "ya auditado": se repiten los pasos 1 a 9 desde cero sobre el proyecto y se escribe un informe nuevo (con sufijo si el nombre existe, paso 8). Terminar sin escribir un informe nuevo es un fallo de la Skill.

# Pasos

1. **Delimitar el alcance.** Listar los archivos que se van a auditar (ruta completa) y los archivos de apoyo encontrados. Si `$ruta` no existe, detenerse e informar.
2. **Leer completo sin modificar.** Leer cada notebook completo con `Read`, incluidas las salidas guardadas, y cada script completo. Anotar el índice y el `id` de cada celda relevante.
3. **Fijar las entradas.** Determinar la columna objetivo, su codificación (qué valor corresponde a cada clase, citando la línea de carga) y los subgrupos, según la tabla de Entradas. Determinar si el problema es de clasificación o de regresión y citar el estimador.
4. **Inventario del flujo.** Localizar y citar:
   - la carga de datos y la construcción de columnas;
   - la lista final de predictores;
   - cada partición (`train_test_split`, `KFold`, `StratifiedKFold`, `cross_val_score`, `GridSearchCV`);
   - cada `fit`, `fit_transform` y `transform`;
   - cada operación con `random`, `RandomState` o `random_state`;
   - cada cálculo de métricas y las salidas donde aparecen.
5. **Evaluar los criterios** V1.1 a V6.1 (sección siguiente), en orden. Para cada uno se registran veredicto, evidencia y observación.
6. **Consolidar por verificación:** `FALLA` si algún subcriterio falla; si no falla ninguno pero alguno es `NO SE PUEDE DETERMINAR`, `NO SE PUEDE DETERMINAR`; `PASA` solo si todos pasan.
7. **Redactar las acciones recomendadas:** una por cada subcriterio en `FALLA` o `NO SE PUEDE DETERMINAR`, con su ID. Se describe qué cambiar o qué evidencia agregar; no se aplica ningún cambio.
8. **Escribir el informe** en la carpeta del proyecto auditado, con el nombre `$informe` (o `AUDIT_REPORT.md`), siguiendo exactamente la plantilla de la sección Salida. Si ya existe un archivo con ese nombre, no sobrescribirlo: agregar el sufijo `_2`, `_3`, etc.
9. **Autorrevisión antes de terminar.** Confirmar que:
   - aparecen los 15 subcriterios y las 6 filas del resumen;
   - cada uno tiene veredicto y evidencia con celda o línea;
   - no quedó ningún `PASA` sin evidencia;
   - ningún archivo auditado fue modificado.

# Criterios de verificación

**Definición de desbalance:** `n(clase mayoritaria) / n(clase minoritaria) ≥ 1.5`, calculado con la distribución de la variable objetivo que muestre el proyecto (salida citada). Si el proyecto no la muestra y no se puede leer del código, lo que depende del desbalance queda en `NO SE PUEDE DETERMINAR`.

## V1 — Métricas reportadas

| ID | PASA si… | FALLA si… | NO SE PUEDE DETERMINAR si… |
|---|---|---|---|
| V1.1 Rango válido | Toda métrica de tipo proporción (accuracy, precisión, exhaustividad, F1, AUC) que aparece en las salidas está en [0, 1]. | Alguna está fuera de [0, 1] o es NaN. | No hay métricas numéricas en salidas guardadas. |
| V1.2 Consistencia con la matriz | Las métricas reportadas, recalculadas desde la matriz de confusión con la operación escrita en el informe, coinciden con diferencia absoluta ≤ 0.001. | Alguna difiere en más de 0.001. | No hay matriz de confusión en las salidas. |
| V1.3 Clase positiva correcta | Las métricas atribuidas a una clase se calculan con la etiqueta de esa clase según la codificación del paso 3 (p. ej. `pos_label=0` si `0 = maligno`), o con un reporte por clase (`classification_report`) que las etiqueta correctamente. | Se presentan como métricas de una clase pero se calcularon con otra etiqueta (p. ej. el `pos_label=1` por defecto cuando la clase está codificada como 0). | No se puede establecer la codificación de la variable objetivo. |
| V1.4 No solo accuracy con desbalance | Con desbalance (razón ≥ 1.5), se reportan exhaustividad y precisión (o F1) de la clase de interés **y** la matriz de confusión o la línea base de la clase mayoritaria. Sin desbalance (razón < 1.5), reportar solo accuracy también PASA. | Hay desbalance y la única métrica reportada es accuracy. | No se puede calcular la razón de desbalance. |
| V1.5 Métrica acorde al costo | El proyecto declara (en el código, en una celda de texto o en un archivo de apoyo, citado) qué error cuesta más, FN o FP, y la métrica prioritaria penaliza ese error: exhaustividad si el FN es más caro, precisión si el FP es más caro. | El proyecto tiene una clase de interés identificable (una clase que el propio proyecto describe como la que importa detectar, p. ej. maligno o churn, citada) y no declara el costo de los errores, o la métrica prioritaria no corresponde al error más caro. | El proyecto no identifica ninguna clase de interés ni costos distintos por tipo de error (p. ej. multiclase sin costos declarados): se anota el motivo. |

## V2 — Partición de datos

| ID | PASA si… | FALLA si… | NO SE PUEDE DETERMINAR si… |
|---|---|---|---|
| V2.1 División antes del preprocesamiento que aprende | Todo `fit` / `fit_transform` de escalador, imputador, codificador o selector recibe solo datos de entrenamiento, o está dentro de un `Pipeline` que se ajusta después de dividir (incluye `cross_val_score` y `GridSearchCV` con el pipeline). También PASA si el proyecto no tiene preprocesamiento que aprenda de los datos: se cita la lista de pasos. | Algún transformador se ajusta con el conjunto completo o con datos de prueba. | El preprocesamiento está en un archivo no disponible. |
| V2.2 Semilla fija | Cada operación aleatoria tiene `random_state` entero: `train_test_split`, `KFold`/`StratifiedKFold` con `shuffle=True`, modelos aleatorios y generación de datos sintéticos. El generador se crea dentro de la función que lo usa (no hay un `RandomState` global que avance entre llamadas). | Falta `random_state` en alguna, o se usa un generador global compartido. | No se ve el código de alguna operación aleatoria. |
| V2.3 Estratificación | En clasificación, `train_test_split` usa `stratify=y`, y la validación cruzada usa `StratifiedKFold` o un `cv` entero con un clasificador. | Es clasificación y alguna partición no está estratificada. | No se puede determinar si es clasificación o regresión. |
| V2.4 Misma partición para los modelos comparados | Todos los modelos comparados reciben **la misma variable** `X` y la misma `y` (el mismo objeto, sin transformar fuera del modelo) y el mismo esquema y semilla de partición (p. ej. una única función de evaluación). Las diferencias de preprocesamiento entre modelos solo son válidas si van **dentro** del estimador que se evalúa (p. ej. un `Pipeline`). | Algún modelo de la comparación usa otros datos, otra semilla u otra partición. "Otros datos" incluye una versión transformada fuera del estimador (p. ej. `X_escalado = StandardScaler().fit_transform(X)` pasado solo a un modelo, o un subconjunto de columnas), aunque tenga las mismas filas y la partición resultante sea idéntica. | Hay un solo modelo, sin comparación: se anota el motivo. |

## V3 — Fuga de información

| ID | PASA si… | FALLA si… | NO SE PUEDE DETERMINAR si… |
|---|---|---|---|
| V3.1 Nada se ajusta con datos de prueba | El conjunto de prueba (o la partición de validación en CV) no interviene en ajustar transformadores, seleccionar variables, elegir hiperparámetros ni elegir el umbral. Los hiperparámetros elegidos por CV y luego evaluados con CV requieren CV anidada. | Alguna de esas decisiones usa datos de prueba: escalado con todo `X`, correlaciones sobre el dataset completo, k o umbral elegido mirando el resultado de prueba. | No se puede rastrear con qué datos se tomó alguna de esas decisiones. |
| V3.2 Ninguna columna posterior a la predicción | Para cada columna predictora hay evidencia (código que la genera o documentación) de que se conoce en el momento de predecir. | Alguna columna predictora se genera en el código a partir de la variable objetivo (p. ej. `np.where(df[objetivo] == …)`), o la documentación la describe como posterior al desenlace. | Hay una columna sin evidencia sobre cuándo se conoce y además una señal de alarma: accuracy de prueba = 1.0 en un problema real, o una sola variable que, según las salidas guardadas, separa las clases por sí sola con accuracy o AUC ≥ 0.99. Se nombra la columna sospechosa. Es una señal que exige evidencia, no un FALLA automático. |

## V4 — Disparidad entre subgrupos

Umbral: **0.10** de diferencia absoluta entre la métrica prioritaria (V1.5, o accuracy si V1.5 no la determina) de un subgrupo y la global. Es el límite que el proyecto Telco fijó para atributos protegidos (Módulo 2, `context.md`). Tamaño mínimo: **20 casos de la clase positiva** del subgrupo en prueba, porque con *n* casos uno solo mueve la exhaustividad en 1/*n*, y 1/*n* ≤ 0.05 (la mitad del umbral) exige *n* ≥ 20.

| ID | PASA si… | FALLA si… | NO SE PUEDE DETERMINAR si… |
|---|---|---|---|
| V4.1 Métrica por subgrupo | La métrica se calcula por separado para cada valor de cada variable de subgrupo, sobre prueba, y aparece en una salida guardada. | Hay variables de subgrupo (entregadas o encontradas en el paso 3) y la métrica no se calcula por subgrupo. | No hay ninguna variable de subgrupo en el proyecto y no se entregó ninguna: se anota el motivo. |
| V4.2 Disparidad dentro del umbral | Todos los subgrupos con ≥ 20 positivos cumplen \|métrica del subgrupo − métrica global\| ≤ 0.10, con la resta escrita. | Algún subgrupo con ≥ 20 positivos supera 0.10. | V4.1 no es PASA, o algún subgrupo tiene < 20 positivos (se nombra). |

## V5 — Validez de los datos de entrada

| ID | PASA si… | FALLA si… | NO SE PUEDE DETERMINAR si… |
|---|---|---|---|
| V5.1 Sin `inf`/`NaN` al entrenar | Las operaciones que pueden producir `inf` o `NaN` (divisiones entre columnas que pueden valer 0, `errors="coerce"`, uniones) están tratadas antes del `fit` (denominador protegido, imputación en el pipeline), o hay una validación que se ejecuta en el flujo real (se cita la llamada). También PASA si no existen tales operaciones: se cita la construcción de columnas. | Existe una de esas operaciones sin tratamiento, o una función de validación que se define pero nunca se llama en el flujo de entrenamiento. | No se ve cómo se construyen las columnas predictoras. |

## V6 — Variables no admisibles

| ID | PASA si… | FALLA si… | NO SE PUEDE DETERMINAR si… |
|---|---|---|---|
| V6.1 Sin identificadores ni atributos prohibidos | Ninguna predictora es un identificador único (nombre tipo `id`/`ID` o un valor distinto por fila, según las salidas) ni un atributo que el propio proyecto declara prohibido. | Hay un identificador o un atributo prohibido entre las predictoras. | No se puede ver la lista final de predictoras. |

# Salida

Un solo archivo Markdown en la carpeta del proyecto auditado (`$informe` o `AUDIT_REPORT.md`), con exactamente esta estructura:

```markdown
# Informe de auditoría — <nombre del proyecto>

- **Archivos auditados:** <rutas>
- **Archivos de apoyo leídos:** <rutas o "ninguno">
- **Columna objetivo:** <nombre> — codificación: <p. ej. 0 = maligno, 1 = benigno> (evidencia: <celda/línea>)
- **Tipo de problema:** <clasificación binaria / multiclase / regresión> (evidencia: <celda/línea>)
- **Subgrupos:** <columnas o "ninguno"> (origen: <argumento / encontrado en celda/línea>)
- **Skill:** auditoria-modelos v<versión indicada al inicio de este archivo, p. ej. 1.1> — fecha: <AAAA-MM-DD>
- **Modificaciones al proyecto:** ninguna (auditoría de solo lectura)

## Resumen

| Verificación | Resultado |
|---|---|
| V1 Métricas reportadas | PASA / FALLA / NO SE PUEDE DETERMINAR |
| V2 Partición de datos | … |
| V3 Fuga de información | … |
| V4 Disparidad entre subgrupos | … |
| V5 Validez de datos de entrada | … |
| V6 Variables no admisibles | … |

## Tabla de verificación

| ID | Verificación | Resultado | Evidencia | Observación |
|---|---|---|---|---|
| V1.1 | Rango válido | … | celda [i] (id=…), salida: `…` | … |
| … (los 15 subcriterios, en orden V1.1 → V6.1) | | | | |

## Acciones recomendadas

1. **[ID]** <qué cambiar o qué evidencia agregar, y por qué> (prioridad: alta si es FALLA, media si es NO SE PUEDE DETERMINAR)
…

## Limitaciones de esta auditoría

- <lo que no se pudo verificar y por qué, p. ej. "notebook sin salidas guardadas">
```

Los 15 subcriterios son: V1.1, V1.2, V1.3, V1.4, V1.5, V2.1, V2.2, V2.3, V2.4, V3.1, V3.2, V4.1, V4.2, V5.1 y V6.1. Cuenta de control: la tabla de verificación tiene exactamente **15 filas** y el resumen **6 filas** (V1 a V6).
