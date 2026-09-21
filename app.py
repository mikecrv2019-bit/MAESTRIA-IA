# -*- coding: utf-8 -*-
"""Pipeline de diagnostico asistido de biopsias de mama (Tarea 3.1, Modulo 3).

Extraido del notebook a un modulo importable para poder probarlo con
pytest (ver test_app.py).

Fixes aplicados en esta version (ver INFORME_TAREA_3_1.md para la
evidencia completa):
1. construir_caracteristicas(): dividia por num_biopsias_previas, que
   puede ser 0, produciendo `inf` y tumbando entrenar_modelo() con
   ValueError.
2. entrenar_modelo(): 'sesiones_tratamiento_programadas' se retira de
   COLUMNAS_PREDICTORAS por fuga de informacion (solo se conoce despues
   del diagnostico: se programan sesiones de tratamiento porque ya se
   sabe que el tumor es maligno).
"""
import numpy as np
import pandas as pd
import joblib
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

RANDOM_STATE = 42
rng = np.random.RandomState(RANDOM_STATE)

# Columna identificada como fuga de informacion (ver INFORME_TAREA_3_1.md,
# seccion 2): es 100% determinista respecto a `diagnostico` porque las
# sesiones de tratamiento solo se programan DESPUES de saber que el tumor
# es maligno. Se deja el nombre aqui, fuera de COLUMNAS_PREDICTORAS, para
# que quede explicito por que no aparece como predictor.
COLUMNA_FUGA = 'sesiones_tratamiento_programadas'

COLUMNAS_PREDICTORAS = [
    'mean texture', 'mean smoothness', 'mean symmetry', 'mean fractal dimension',
    'texture error', 'smoothness error', 'symmetry error',
    'variabilidad_por_biopsia', 'num_biopsias_previas',
]


def cargar_datos():
    """Carga el dataset de biopsias y agrega las columnas clinicas complementarias."""
    data = load_breast_cancer(as_frame=True)
    df = data.frame.copy()
    df['diagnostico'] = data.target  # 0 = maligno, 1 = benigno
    n = len(df)

    df['num_biopsias_previas'] = rng.randint(0, 4, size=n)
    df['sesiones_tratamiento_programadas'] = np.where(
        df['diagnostico'] == 0,
        rng.randint(3, 9, size=n),
        0,
    )
    return df


def explorar_datos(df):
    """Imprime un resumen rapido del dataset antes de entrenar nada."""
    print(f"Filas: {len(df)}  |  Columnas: {df.shape[1]}")
    print()
    print("Distribucion de diagnostico (0 = maligno, 1 = benigno):")
    print(df['diagnostico'].value_counts(normalize=True).round(3))
    print()
    print("Valores nulos por columna (solo columnas con al menos 1):")
    nulos = df.isna().sum()
    print(nulos[nulos > 0] if nulos.any() else "Ninguno")


def validar_datos(df, columnas):
    """Revisa que las columnas indicadas no tengan nulos ni valores infinitos."""
    problemas = {}
    for col in columnas:
        n_nulos = df[col].isna().sum()
        n_infinitos = np.isinf(df[col]).sum() if np.issubdtype(df[col].dtype, np.number) else 0
        if n_nulos or n_infinitos:
            problemas[col] = {'nulos': int(n_nulos), 'infinitos': int(n_infinitos)}
    if problemas:
        detalle = "\n".join(
            f"  - {c}: {d['nulos']} nulos, {d['infinitos']} infinitos"
            for c, d in problemas.items()
        )
        mensaje = f"Validacion fallida en {len(problemas)} columna(s):\n{detalle}"
        if detener:
            raise ValueError(mensaje)
        print("AVISO:", mensaje)
    else:
        print(f"Validacion OK: {len(columnas)} columnas sin nulos ni infinitos.")

    return problemas


def construir_caracteristicas(df):
    """Agrega una metrica derivada de variabilidad de textura por biopsia previa.

    CORREGIDO (causa confirmada del ValueError): num_biopsias_previas puede
    ser 0 (~24% de las filas, no un caso raro), asi que se suma 1 al
    denominador para no dividir por cero sin perder la fila ni inventar un
    valor faltante.
    """
    df = df.copy()
    df['variabilidad_por_biopsia'] = df['mean texture'] / (df['num_biopsias_previas'] + 1)
    return df


def entrenar_modelo(df, usar_class_weight=False, columnas_predictoras=None):
    """Entrena un clasificador de regresion logistica y devuelve el modelo y sus metricas.

    columnas_predictoras permite pasar una lista distinta a COLUMNAS_PREDICTORAS
    (por ejemplo, para reproducir el accuracy "con fuga" y compararlo contra
    el corregido, sobre la misma particion; ver INFORME_TAREA_3_1.md).
    """
    columnas = columnas_predictoras if columnas_predictoras is not None else COLUMNAS_PREDICTORAS
    X = df[columnas]
    y = df['diagnostico']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE
    )

    kwargs = {'max_iter': 5000}
    if usar_class_weight:
        kwargs['class_weight'] = 'balanced'

    modelo = LogisticRegression(**kwargs)
    modelo.fit(X_train, y_train)

    acc_train = accuracy_score(y_train, modelo.predict(X_train))
    acc_test = accuracy_score(y_test, modelo.predict(X_test))
    return modelo, acc_train, acc_test


def guardar_modelo(modelo, ruta="modelo_biopsias.joblib"):
    """Serializa el modelo entrenado para que el servicio de inferencia lo cargue."""
    joblib.dump(modelo, ruta)
    print(f"Modelo guardado en: {ruta}")


def predecir_caso(modelo, caso: dict):
    """Predice el diagnostico para una paciente nueva a partir de un diccionario de mediciones."""
    entrada = pd.DataFrame([caso])[COLUMNAS_PREDICTORAS]
    pred = modelo.predict(entrada)[0]
    return 'benigno' if pred == 1 else 'maligno'


if __name__ == "__main__":
    df = cargar_datos()
    df = construir_caracteristicas(df)
    modelo, acc_train, acc_test = entrenar_modelo(df)
    print(f"Accuracy en entrenamiento: {acc_train:.4f}")
    print(f"Accuracy en prueba:        {acc_test:.4f}")
    guardar_modelo(modelo)
