# Tarea 3.1 — App de Diagnóstico de Biopsias de Mama

Informe de depuración y corrección del pipeline entregado por el equipo clínico.
Todos los números de este documento vienen de ejecuciones reales (`app.py`,
`test_app.py` y el notebook `Copy_of_App_Diagnostico_Biopsias_Mama.ipynb`,
los tres ejecutados de punta a punta), no de estimaciones.

## 1. El error de funcionamiento (`ValueError: Input X contains infinity...`)

### Reproducción del fallo

Ejecutando el notebook original, en orden, tal como fue entregado, falla en la
celda "6. Ejecutar el pipeline completo" con:

```
ValueError: Input X contains infinity or a value too large for dtype('float64').
```

y como consecuencia, las celdas posteriores (`guardar_modelo`, gráfico de
coeficientes, `predecir_caso`) fallan en cascada con
`NameError: name 'modelo' is not defined`, porque `modelo` nunca llegó a
asignarse.

### Dos hipótesis sobre qué función lo introduce

- **H1 — `cargar_datos()` introduce el valor no finito.** Es la primera
  función que toca los datos, así que es la primera sospechosa razonable.
- **H2 — `construir_caracteristicas()` lo introduce**, al calcular
  `variabilidad_por_biopsia = mean texture / num_biopsias_previas`, cuando
  `num_biopsias_previas` vale 0 (division por cero → `inf`).

### Evidencia

Usando `validar_datos()` (que revisa nulos e infinitos) en cada etapa:

```
H1 (cargar_datos): sin problemas -> DESCARTADA

AVISO: Validacion fallida en 1 columna(s):
  - variabilidad_por_biopsia: 0 nulos, 135 infinitos
H2 (construir_caracteristicas, version original): {'variabilidad_por_biopsia': {'nulos': 0, 'infinitos': 135}}
Filas con num_biopsias_previas == 0: 135 -> coinciden con las filas 'infinitos' de arriba: CONFIRMADA
```

- Los datos recién cargados (`cargar_datos()`) no tienen un solo nulo ni
  infinito → **H1 descartada con evidencia**.
- Después de `construir_caracteristicas()` aparecen exactamente 135 valores
  infinitos, y las 135 filas con `variabilidad_por_biopsia = inf` son
  precisamente las 135 filas donde `num_biopsias_previas == 0` (135/569 =
  23.7% del dataset, no un caso raro) → **H2 confirmada con evidencia**.
- El traceback original también lo respalda: el `ValueError` se dispara
  dentro de `sklearn.utils.validation._assert_all_finite`, que es
  **validación de entrada antes de ajustar el modelo**, no un fallo del
  optimizador de `LogisticRegression`. Es decir, el valor infinito ya venía
  corrupto en `X` antes de llegar a `.fit()`.

### Causa confirmada y corrección aplicada

`construir_caracteristicas()` dividía por `num_biopsias_previas`, un valor
válido y frecuente de 0 (una paciente sin biopsias previas), no un dato
faltante ni un error de captura. La corrección en [`app.py`](app.py):

```python
df['variabilidad_por_biopsia'] = df['mean texture'] / (df['num_biopsias_previas'] + 1)
```

Se usa `+ 1` en el denominador (en vez de, por ejemplo, `.replace(0, 1)`)
porque desplaza la escala de forma consistente para *todas* las filas —
`.replace(0, 1)` hace que 0 y 1 biopsias previas produzcan el mismo
denominador, mezclando dos valores reales distintos.

## 2. La fuga de información

### Columna identificada

`sesiones_tratamiento_programadas` es la columna prohibida dentro de
`COLUMNAS_PREDICTORAS`. Verificación exacta sobre los 569 casos:

```
diagnostico    sesiones_tratamiento_programadas > 0
0 (maligno)    212 de 212 (100%)
1 (benigno)      0 de 357 (100% en 0)
```

Es decir, **el valor de esta columna determina el diagnóstico al 100%**: se
programan sesiones de tratamiento *después* de confirmar que el tumor es
maligno, así que en el momento real de la biopsia —cuando se necesita la
predicción— este dato todavía no existe. Se retiró de `COLUMNAS_PREDICTORAS`
en `app.py`.

### Accuracy antes y después (misma partición train/test, mismo `random_state=42`)

| | accuracy train | accuracy test |
|---|---|---|
| **Con** la fuga | 1.0000 | **1.0000** |
| **Sin** la fuga | 0.7324 | **0.7343** |

**Optimismo introducido por la fuga: +0.2657 (26.6 puntos porcentuales)
de accuracy de prueba.** Un modelo con accuracy de prueba perfecta (1.0000)
sobre un problema médico real es en sí misma una señal de alarma, no un
logro — nadie predice biopsias con 100% de certeza a partir de mediciones
de imagen. El 0.7343 sin fuga es el número honesto: bajo, pero real.

## 3. Efecto del desbalance de clases

`diagnostico` está desbalanceado: 62.7% benigno / 37.3% maligno. Se comparó
`entrenar_modelo(usar_class_weight=False)` contra
`entrenar_modelo(usar_class_weight=True)`, ya sin la fuga, sobre la misma
partición (con `stratify=y`, ver nota en la sección 4):

| | accuracy test |
|---|---|
| `class_weight=None` | 0.7343 |
| `class_weight='balanced'` | 0.7343 |

**El accuracy es idéntico** (0.7343 en ambos casos) — a primera vista
parecería que `class_weight='balanced'` no sirvió de nada. Pero el accuracy
agregado esconde lo que pasa por clase. Matriz de confusión y recall por
clase sobre el mismo set de prueba (143 casos: 53 malignos, 90 benignos):

| | precisión maligno | **recall maligno** | precisión benigno | recall benigno |
|---|---|---|---|---|
| `class_weight=None` | 0.6923 | **0.5094** | 0.7500 | 0.8667 |
| `class_weight='balanced'` | 0.6316 | **0.6792** | 0.8023 | 0.7667 |

Con `class_weight=None`, el modelo **detecta solo el 50.9% de los tumores
malignos reales** (26 de 53 se clasifican como falsos negativos). Con
`class_weight='balanced'`, el recall de malignos sube a 67.9% (solo 17 falsos
negativos), a costa de más falsos positivos en benignos (la precisión de
maligno baja de 0.69 a 0.63).

**Por qué vale la pena usar `class_weight='balanced'` aunque el accuracy no
cambie:** el accuracy trata un falso negativo en maligno y un falso positivo
en benigno como errores equivalentes, porque solo cuenta "aciertos totales" y
la clase mayoritaria (benigno) domina ese conteo. Pero en este contexto
clínico no son equivalentes: un falso positivo en benigno significa que un
especialista revisa un caso de más (costo bajo); un falso negativo en maligno
significa un tumor maligno que el modelo etiquetó como benigno y que podría
no priorizarse para revisión (costo alto). `class_weight='balanced'` mueve la
frontera de decisión para reducir precisamente ese error caro, y esa mejora
es invisible si solo se mira el accuracy — por eso la consigna insiste en
mirar la métrica *antes* de decidir si un cambio "mejoró" el modelo.

## 4. Pruebas automatizadas (`test_app.py`)

Seis pruebas con `pytest`, `assert`, todas con prefijo `test_`, todas
pasando:

```
test_construir_caracteristicas_no_produce_infinitos_ni_nulos   PASSED
test_columna_fuga_no_esta_en_columnas_predictoras               PASSED
test_predecir_caso_devuelve_benigno_o_maligno                   PASSED
test_validar_datos_detiene_ante_datos_invalidos                 PASSED
test_validar_datos_no_detiene_si_detener_es_false                PASSED
test_entrenar_modelo_corre_de_extremo_a_extremo_sin_la_fuga      PASSED
6 passed in 2.12s
```

Las tres mínimas pedidas son las tres primeras; las otras tres cubren el fix
de `validar_datos()` (sección 5) y una prueba de regresión de extremo a
extremo para que el pipeline nunca vuelva a quedar roto en silencio.

## 5. Refactor de `validar_datos()`

**Estado original:** la función estaba definida pero nunca se llamaba desde
el pipeline (`entrenar_modelo()` no la invoca en ningún momento), y además
tenía un `NameError` propio: referenciaba una variable global `detener` que
no existe en ningún lado del notebook. Si alguien la hubiera llamado tal
cual, habría fallado por su cuenta antes de llegar a validar nada.

**Decisión: conectarla, no eliminarla.** Es exactamente el chequeo que
habría atrapado el bug de la sección 1 antes de que llegara a
`LogisticRegression.fit()` — el problema nunca fue que la función estuviera
mal pensada, sino que estaba desconectada. Eliminarla habría dejado el
pipeline sin ninguna barrera de calidad de datos. Los cambios:

1. `detener` pasa a ser un parámetro (`detener=True` por defecto) en vez de
   una variable global inexistente — corrige el `NameError`.
2. `entrenar_modelo()` llama a `validar_datos(df, columnas, detener=True)`
   antes de separar `X`/`y`, así que **cualquier** llamada futura al pipeline
   (desde el notebook, desde un script, desde un test) queda protegida
   automáticamente, sin depender de que alguien se acuerde de llamarla a
   mano.

Las pruebas `test_validar_datos_detiene_ante_datos_invalidos` y
`test_validar_datos_no_detiene_si_detener_es_false` cubren este cambio, y
`test_entrenar_modelo_corre_de_extremo_a_extremo_sin_la_fuga` confirma que
la guardia no rompe el flujo normal cuando los datos están limpios.

## 6. Decisiones adicionales tomadas por cuenta propia

No pedidas explícitamente en la consigna, pero necesarias o directamente
relevantes para lo que sí se pidió — señaladas aquí para que se puedan
revisar y, si no se está de acuerdo, revertir:

- **Se extrajo el pipeline a `app.py` para que `pytest` pudiera probarlo —
  decisión revertida a medias tras una falla real.** El notebook original
  solo definía las funciones dentro de sus propias celdas, lo cual no es
  importable por `pytest`, así que se creó `app.py` como módulo, y en un
  primer momento el notebook lo importaba (`from app import ...`) en vez de
  redefinir las funciones, para no mantener dos copias de la misma lógica.
  Al probarlo en Google Colab (el badge del notebook apunta ahí) esto falló
  con `ModuleNotFoundError: No module named 'app'`: Colab abre el `.ipynb`
  en una máquina virtual nueva que no tiene ningún otro archivo del
  repositorio, así que un `import` a un módulo local nunca puede resolverse.
  Reproducido y confirmado con el traceback real del usuario, se revirtió la
  parte de *importar*: el notebook ahora vuelve a definir las funciones
  directamente en sus celdas (autocontenido, corre en Colab sin archivos
  adjuntos), mientras que `app.py` se mantiene con la misma lógica
  exclusivamente para `test_app.py`. El costo de esta marcha atrás es que
  ahora sí hay dos copias que mantener sincronizadas a mano si el pipeline
  vuelve a cambiar — un trade-off consciente, no un descuido: `pytest`
  necesita un módulo importable y Colab necesita un notebook sin
  dependencias externas, y no hay una sola estructura de archivos que
  satisfaga ambas cosas a la vez.
- **`cargar_datos()` ya no depende de un `np.random.RandomState` global
  compartido.** En la versión original, `rng` se creaba una sola vez a nivel
  de módulo y cada llamada a `cargar_datos()` avanzaba su estado — dos
  llamadas en la misma sesión, con el mismo `RANDOM_STATE=42`, producían
  columnas sintéticas *distintas*. Ahora cada llamada crea su propio
  `RandomState(random_state)`, así que `cargar_datos()` es reproducible por
  sí misma, sin importar cuántas veces se haya llamado antes.
- **Se agregó `stratify=y` al `train_test_split` de `entrenar_modelo()`.**
  Dado que `diagnostico` está desbalanceado (62.7/37.3), estratificar
  asegura que el conjunto de prueba mantenga esa misma proporción, lo cual
  es la práctica estándar para no medir el modelo sobre una partición que
  por azar quedó más o menos desbalanceada que el dataset completo.

## 7. Cómo verificar

```bash
python -m pytest test_app.py -v
python app.py
```

`app.py` corre el pipeline completo (carga, features, entrenamiento con la
fuga ya removida, guardado del modelo) y reproduce las cifras de este
informe.
