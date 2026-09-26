import sys
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Evita caracteres corruptos en la consola de Windows
sys.stdout.reconfigure(encoding="utf-8")

DATA = Path(__file__).parent / "data" / "datos.csv"

df = pd.read_csv(DATA)

# --- Preparación de variables ---
# timestamp viene como texto: se convierte a fecha y se extrae el día de la semana
df["dia_semana"] = pd.to_datetime(df["timestamp"]).dt.day_name()
# follow_up_required es booleana: se trata como categórica
df["follow_up_required"] = df["follow_up_required"].astype(str)

# Objetivo: 1 = Insatisfecho (customer_satisfaction <= 2). No se usa como predictor.
y = (df["customer_satisfaction"] <= 2).astype(int)

num_cols = ["response_time_min", "interaction_cost_usd", "customer_sentiment"]
cat_cols = ["handled_by", "query_type", "resolution_status",
            "follow_up_required", "device_type", "region", "dia_semana"]
features_antes = num_cols
features_despues = num_cols + cat_cols  # exactamente las 10 del README

# Mismo split para ANTES y DESPUÉS (mismas filas en train y test)
X_train, X_test, y_train, y_test = train_test_split(
    df[features_despues], y, test_size=0.25, random_state=42, stratify=y
)

# --- ANTES: modelo original (3 variables numéricas) ---
antes = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", LogisticRegression(max_iter=1000, random_state=42)),
])
antes.fit(X_train[features_antes], y_train)
pred_antes = antes.predict(X_test[features_antes])

# --- DESPUÉS: 10 variables + ColumnTransformer + class_weight balanced ---
preprocesamiento = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]), num_cols),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]), cat_cols),
])
despues = Pipeline([
    ("prep", preprocesamiento),
    ("model", LogisticRegression(max_iter=1000, random_state=42,
                                 class_weight="balanced")),
])
# El preprocesamiento se ajusta únicamente con los datos de entrenamiento
despues.fit(X_train, y_train)
pred_despues = despues.predict(X_test)


def metricas(pred):
    return [accuracy_score(y_test, pred),
            precision_score(y_test, pred, zero_division=0),
            recall_score(y_test, pred, zero_division=0),
            f1_score(y_test, pred, zero_division=0)]


print("=== CUSTOMER SERVICE AI CHATBOT: ANTES vs DESPUÉS ===")
print(f"Filas: {len(df):,} | Train: {len(X_train):,} | Test: {len(X_test):,} "
      "(test_size=0.25, random_state=42)")
print(f"Insatisfechos en test: {int(y_test.sum())} de {len(y_test)}")
print(f"Variables ANTES: {len(features_antes)} | DESPUÉS: {len(features_despues)}")

print("\n--- Matriz de confusión ANTES (filas=real, columnas=predicho; 0=No, 1=Yes) ---")
print(confusion_matrix(y_test, pred_antes))
print("\n--- Matriz de confusión DESPUÉS ---")
print(confusion_matrix(y_test, pred_despues))

print("\n--- Comparación (clase positiva: Insatisfecho = Yes) ---")
print(f"{'Métrica':<12}{'ANTES':>8}{'DESPUÉS':>10}{'Cambio':>9}")
for nombre, a, d in zip(["Accuracy", "Precision", "Recall", "F1"],
                        metricas(pred_antes), metricas(pred_despues)):
    print(f"{nombre:<12}{a:>8.4f}{d:>10.4f}{d - a:>+9.4f}")
