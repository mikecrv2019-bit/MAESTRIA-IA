# -*- coding: utf-8 -*-
"""Pruebas automatizadas del pipeline de diagnostico de biopsias (Tarea 3.1)."""
import numpy as np
import pandas as pd
import pytest

import app


@pytest.fixture(scope="module")
def df_features():
    """Dataset ya con la columna derivada, para no repetir la carga en cada prueba."""
    df = app.cargar_datos()
    return app.construir_caracteristicas(df)


def test_construir_caracteristicas_no_produce_infinitos_ni_nulos(df_features):
    columna = df_features['variabilidad_por_biopsia']
    assert not np.isinf(columna).any(), "variabilidad_por_biopsia tiene valores infinitos"
    assert not columna.isna().any(), "variabilidad_por_biopsia tiene valores nulos"


def test_columna_fuga_no_esta_en_columnas_predictoras():
    assert app.COLUMNA_FUGA not in app.COLUMNAS_PREDICTORAS, (
        f"'{app.COLUMNA_FUGA}' es una fuga de informacion (solo se conoce "
        "despues del diagnostico) y no debe usarse como predictor"
    )


def test_predecir_caso_devuelve_benigno_o_maligno(df_features):
    modelo, _, _ = app.entrenar_modelo(df_features)
    caso = {col: df_features[col].iloc[0] for col in app.COLUMNAS_PREDICTORAS}
    resultado = app.predecir_caso(modelo, caso)
    assert resultado in ('benigno', 'maligno')


def test_validar_datos_detiene_ante_datos_invalidos():
    df_malo = pd.DataFrame({'x': [1.0, np.inf, 3.0]})
    with pytest.raises(ValueError):
        app.validar_datos(df_malo, ['x'], detener=True)


def test_validar_datos_no_detiene_si_detener_es_false(capsys):
    df_malo = pd.DataFrame({'x': [1.0, np.nan, 3.0]})
    problemas = app.validar_datos(df_malo, ['x'], detener=False)
    assert problemas  # detecto el problema...
    capsys.readouterr()  # ...pero no lo interrumpio


def test_entrenar_modelo_corre_de_extremo_a_extremo_sin_la_fuga(df_features):
    modelo, acc_train, acc_test = app.entrenar_modelo(df_features)
    assert 0.0 <= acc_train <= 1.0
    assert 0.0 <= acc_test <= 1.0
