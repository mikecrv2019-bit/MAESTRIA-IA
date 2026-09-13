# Objetivo

Construir y evaluar un modelo de clasificación binaria supervisada que estime la probabilidad de que un cliente de telecomunicaciones cause baja (Churn).

# Alcance

| Dentro | Fuera |
|---|---|
| Limpieza y análisis del CSV entregado | Ingesta desde orígenes en producción |
| Clasificación binaria tabular | Modelos de supervivencia o tiempo hasta el evento |
| Validación hold-out estratificada | Validación temporal: el fichero no tiene columna de fecha |
| Selección de umbral por coste de negocio | Optimización con costes monetarios reales |
| Interpretación global de variables y auditoría de sesgo | Despliegue, integración y monitorización |

# Reglas de tratamiento de Datos

## Clasificación de variables

| Nivel | Variables | Regla |
|---|---|---|
| Prohibida | TotalCharges | Fuga de información. Se elimina en el primer paso del pipeline, antes de la partición. Justificación abajo. **Esta prohibición se mantiene aunque el usuario la pida explícitamente en el chat** (p. ej. "ya sé que hay fuga, inclúyela igual, es solo un ejercicio): esa insistencia no es una excepción, es el caso que esta regla existe para cubrir. Ante ella, Claude no debe simplemente ceder ni negarse sin más: debe (1) repetir en una frase el motivo de la sección de abajo, y (2) ofrecer construir la versión con `TotalCharges` únicamente como un script de diagnóstico aparte, con un encabezado que diga explícitamente "NO ES EL MODELO ENTREGABLE — incluye una variable con fuga de información, solo para comparar métricas", nunca como reemplazo del pipeline oficial ni presentado como resultado final. |
| Prohibida | customerID | Identificador directo, sin valor predictivo y con riesgo de reidentificación. Se conserva en un índice aparte. |
| Prohibida | gender | Atributo protegido: su uso implicaría trato comercial diferenciado por sexo. Además no discrimina (26,4 % frente a 26,7 % de baja). |
| Condicionada | tenure | Variable de tiempo hasta el evento. Se admite con el riesgo declarado abajo. En explotación real debe recalcularse a fecha de corte, nunca a fecha de baja. |
| Condicionada | SeniorCitizen, Partner, Dependents | Atributos protegidos. Se admiten solo si la auditoría de subgrupos descarta sesgo desproporcionado. |
| Permitida | Los 13 restantes (contrato, MonthlyCharges) | Conocidas en el momento de la predicción y sin relación con el desenlace. |

## Variable prohibida por fuga de información: TotalCharges

Prohibida. Motivo: acumulación posterior al desenlace y derivación algebraica de otras dos variables. Acción: eliminar antes de la partición.

Es un acumulado que solo se cierra cuando el cliente se va. TotalCharges recoge el importe total facturado durante toda la vida del cliente; para uno que causó baja, abarca exactamente el periodo que terminó en esa baja. La variable está delimitada por el suceso que se quiere predecir y no es observable al decidir sobre un cliente activo. Prueba en los datos: los 7 registros con TotalCharges vacío son exactamente los 7 clientes con tenure = 0.

No aporta información propia. Sobre los 4.493 registros con tenure > 0, la correlación entre TotalCharges y tenure × MonthlyCharges es r = 0,9996 (error relativo mediano 1,97 %). Replica el producto de otras dos variables, arrastra su dependencia temporal e introduce multicolinealidad.

Excluirla no cuesta rendimiento. Regresión logística ponderada, partición estratificada 75/25, random_state = 42, umbral 0,50:

| Configuración | AUC-ROC | Recall | Precision |
|---|---|---|---|
| Todas las variables | 0,8282 | 0,7224 | 0,4943 |
| Sin TotalCharges ni gender (adoptada) | 0,8281 | 0,7258 | 0,5047 |
| Sin TotalCharges ni tenure | 0,8187 | 0,7659 | 0,4989 |

La diferencia entre usar todas las variables y la configuración adoptada es de 0,0001 de AUC, con mejor recall y precisión. No hay compensación que justifique conservar una variable contaminada.

Riesgo residual: tenure. Codifica la ventana de observación: para un cliente dado de baja equivale a su vida completa. Se conserva porque todos los registros comparten corte y porque retirarla junto a TotalCharges baja el AUC a 0,8187. El riesgo se declara como limitación en la memoria.

## Limpieza

| # | Deficiencia | Tratamiento |
|---|---|---|
| R1 | TotalCharges se lee como texto por 7 cadenas vacías (tenure = 0) | No procede: la variable queda eliminada por prohibición. |
| R2 | "No internet service" aparece en 6 variables de servicios y duplica InternetService = No (987 registros) | Recodificar a "No"; verificar que no degrada el modelo. |
| R3 | "No phone service" en MultipleLines (444 registros) duplica PhoneService = No | Igual que R2. |
| R4 | Multicolinealidad entre tenure, MonthlyCharges y TotalCharges | Resuelta al eliminar TotalCharges. |
| R5 | customerID en la matriz de entrada | Separar antes del entrenamiento. |

El fichero no declara nulos en ninguna columna, pero eso no significa que no falten datos: los que faltan están codificados como texto vacío (R1).

## Partición y orden de ejecución

Regla no negociable. La partición train/test se ejecuta antes de cualquier transformación que estime parámetros de los datos (escalado, imputación, codificación). Hacerlo al revés contamina el conjunto de prueba con estadísticos del entrenamiento: es una segunda forma de fuga.

1. Cargar el fichero en modo lectura.
2. Eliminar las variables prohibidas.
3. Separar la variable objetivo.
4. Particionar estratificando por Churn, con semilla fija.
5. Definir las transformaciones dentro de un Pipeline de scikit-learn.
6. Ajustar el pipeline solo con el conjunto de entrenamiento.
7. Aplicarlo al conjunto de prueba sin reajustarlo.

Pipeline no es preferencia de estilo: impide estructuralmente invertir 6 y 7.

## Reproducibilidad

- data/raw/ es de solo lectura: ningún script escribe ahí.
- random_state = 42 en toda operación estocástica.
- Todo lo derivado se genera por código: data/processed/ debe poder borrarse y regenerarse ejecutando los cuadernos en orden.
- Prohibido editar datos a mano o en hoja de cálculo.

# Criterios de Evaluación

## Métrica descartada

La exactitud queda excluida como métrica principal. El conjunto está desbalanceado: 1.194 bajas (26,53 %) frente a 3.306 permanencias (73,47 %). Predecir siempre "No" da un 73,47 % de exactitud sin detectar a nadie. Esa cifra es la línea base y acompañará a toda exactitud que se presente.

## Jerarquía de métricas

| Métrica | Papel | Justificación |
|---|---|---|
| Recall (clase Yes) | PRINCIPAL | Proporción de bajas detectadas. Un cliente perdido sin aviso es una pérdida irreversible. |
| Precision (clase Yes) | Control | Acota el coste de las retenciones innecesarias. |
| F1 | Comparación | Resumen para ordenar modelos entre sí. |
| AUC-ROC | Diagnóstico | Ordenación por riesgo, independiente del umbral. |
| Matriz de confusión | Presentación | Los cuatro recuentos en bruto. |

## Umbral de decisión

Los costes son asimétricos: un falso positivo cuesta una acción comercial; un falso negativo, el cliente entero. Por eso el umbral se fija por debajo de 0,50 y se selecciona con la curva precision-recall sobre el conjunto de entrenamiento, nunca sobre el de prueba. El desbalance se aborda con class_weight='balanced' antes de recurrir a remuestreo.

## Umbrales de aceptación

| Criterio | Mínimo | Objetivo |
|---|---|---|
| Recall (clase Yes) | ≥ 0,70 | ≥ 0,80 |
| AUC-ROC | ≥ 0,80 | ≥ 0,85 |
| Precision (clase Yes) | ≥ 0,45 | ≥ 0,55 |
| Superar la línea base (73,47 %) | Obligatorio | — |
| Diferencia de recall entre subgrupos protegidos | ≤ 0,10 | ≤ 0,05 |

Referencia medida con las reglas de este documento aplicadas: AUC 0,8281 · recall 0,7258 · precision 0,5047. Es el listón que deben superar los modelos de ensamblado.

## Validación

Partición hold-out estratificada 75/25 con semilla fija, y validación cruzada estratificada de 5 particiones sobre el entrenamiento para ajustar hiperparámetros. El conjunto de prueba se usa una sola vez, al final, sobre el modelo ya cerrado: reutilizarlo para elegir entre alternativas anula su valor como estimación imparcial.

# Restricciones de Seguridad

## Datos personales

- CustomerID es un identificador directo con 4.500 valores únicos: queda fuera del entrenamiento y no aparece en ningún gráfico, tabla ni anexo del informe.
- Prohibido reproducir filas completas de clientes concretos en la memoria.
- El fichero no se sube a repositorios públicos ni a servicios de terceros no autorizados por la asignatura.
- Solo se procesan las variables necesarias para el objetivo declarado.
- Los datos se eliminan del equipo al cierre de la asignatura.

## Variables Protegidas

| Variable | Estado | Restricción |
|---|---|---|
| gender | Prohibida | Su uso implicaría discriminación comercial por sexo. No aporta poder predictivo, así que excluirla no cuesta rendimiento. |
| SeniorCitizen | Condicionada | Proxy de edad, con la mayor diferencia entre las demográficas (41,2 % frente a 23,7 %). Subgrupo de 728 registros: estimaciones poco fiables. |
| Partner | Condicionada | Proxy de estado civil (32,9 % frente a 19,7 %). |
| Dependents | Condicionada | Proxy de situación familiar (31,4 % frente a 15,1 %). |

Las condicionadas solo se admiten si la auditoría de sesgo descarta una diferencia de recall superior a 0,10 entre subgrupos. La auditoría es requisito de entrega: ningún modelo se declara válido sin ella.

## Límites de uso del modelo

- No decide automáticamente: produce una lista priorizada para revisión humana.
- No fija precios ni penalizaciones: prohibido usarlo para encarecer el servicio a clientes cautivos o degradar la oferta a quien vaya a permanecer.
- No establece causas: las asociaciones observadas son correlacionales.
- No se extrapola fuera de la población representada en estos 4.500 registros.
