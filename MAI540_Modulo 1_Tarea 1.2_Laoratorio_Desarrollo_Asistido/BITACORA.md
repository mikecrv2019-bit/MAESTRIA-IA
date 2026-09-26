# Bitácora de desarrollo asistido – Tarea 1.2

## 1. Comprensión inicial
- Problema: predecir si un cliente quedará insatisfecho (customer_satisfaction ≤ 2) tras ser atendido por un chatbot de IA o un agente humano, para dar seguimiento antes de la encuesta. Es una clasificación binaria; la clase positiva es Insatisfecho = Yes.
- Datos: data/datos.csv, 4.500 interacciones y 13 columnas (dataset sintético de Kaggle), sin valores nulos. Cerca del 20 % de los casos son insatisfechos (clases desbalanceadas).
- Modelo inicial: LogisticRegression con imputación por mediana y solo 3 variables numéricas (response_time_min, interaction_cost_usd, customer_sentiment).
- Faltaba: las variables categóricas (incluido dia_semana derivado de timestamp), ColumnTransformer con escalado y one-hot, class_weight='balanced', métricas de la clase positiva y la comparación ANTES/DESPUÉS.
- Observación de datos: customer_sentiment va de −0,72 a 1,00, aunque DESCRIPCION.md dice «0 a 1».

## 2. Ejecución inicial (ANTES)
- Comando: python main.py (sin modificar el archivo). Terminó sin errores (código 0).
- Salida: Filas 4.500; 3 variables; Accuracy 0,8009; matriz de confusión [[901, 0], [224, 0]].
- Limitación: el modelo predice «No» en los 1.125 casos de prueba. El accuracy coincide con la proporción de la clase mayoritaria, y precision, recall y F1 de la clase Yes son 0: no detecta a ningún insatisfecho. Solo se observó un problema de codificación de caracteres en la consola de Windows.

## 3. Interacción con Claude Code
- Paso 1 – Objetivo: entender el proyecto sin tocarlo. Instrucción: leer y explicar el proyecto sin modificar archivos. Resultado: funcionó; Claude leyó main.py, README, DESCRIPCION y los datos, y no cambió nada.
- Paso 2 – Objetivo: obtener la línea base. Instrucción: ejecutar tal como está. Funcionó; se guardó ANTES_salida.txt.
- Paso 3 – Objetivo: obtener un plan antes de programar. Claude propuso un plan de 9 puntos ajustado al README (10 variables, ColumnTransformer, class_weight='balanced', 4 métricas, comparación). Lo revisé y lo aprobé antes de autorizar el código.
- Instrucción que no funcionó del todo: al principio indiqué «no subas nada aún al repositorio» y luego «vas a subir la tarea al repositorio»; como no se indicó cuál repositorio, Claude no pudo subirlo y dejó la carpeta local lista.
- Decisiones que Claude tomó por su cuenta: (a) revisar nulos, rango de sentimiento y proporción de clases; (b) conservar el modelo ANTES dentro del mismo main.py para comparar con el mismo split; (c) guardar el original como main_original.py; (d) reconfigurar la salida a UTF-8 para evitar caracteres corruptos; (e) usar zero_division=0 en precision/recall/F1 para el modelo ANTES.

## 4. Verificación
- Ejecuté python main.py y guardé DESPUES_salida.txt (código de salida 0, sin errores ni advertencias).
- El bloque ANTES del nuevo main.py reproduce exactamente la salida original (matriz [[901, 0], [224, 0]], accuracy 0,8009), lo que confirma que la comparación usa el mismo split (test_size=0.25, random_state=42, stratify=y).
- Inspeccioné en el código que se usan exactamente las 10 variables, que no entran customer_satisfaction, interaction_id, customer_id ni timestamp, y que el preprocesamiento se ajusta solo con entrenamiento porque va dentro del Pipeline. Confirmé que las matrices suman 1.125 casos de prueba con 224 insatisfechos reales.

## 5. Resultado (DESPUÉS)
- Matriz de confusión DESPUÉS: [[764, 137], [65, 159]].
- Comparación (clase Insatisfecho = Yes): ver tabla.
- Qué mejoró: el modelo pasó de no detectar ningún insatisfecho a detectar 159 de 224 (recall 0,71). El accuracy sube poco (+0,02), pero precision, recall y F1 pasan de 0 a 0,54 / 0,71 / 0,61. El coste es que aparecen 137 falsos positivos. Mejoró porque class_weight='balanced' da más peso a la clase minoritaria y porque las variables categóricas aportan información nueva.

| Métrica | ANTES | DESPUÉS | Cambio |
|---|---|---|---|
| Accuracy | 0,8009 | 0,8204 | +0,0196 |
| Precision | 0,0000 | 0,5372 | +0,5372 |
| Recall | 0,0000 | 0,7098 | +0,7098 |
| F1 | 0,0000 | 0,6115 | +0,6115 |

## 6. Explicación propia
_(A redactar por el estudiante con sus propias palabras; ver preguntas guía en el informe .docx.)_
