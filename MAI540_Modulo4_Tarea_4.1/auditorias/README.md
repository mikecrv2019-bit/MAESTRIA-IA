# Informes de auditoría — Tarea 4.1

Los tres informes finales los generó la Skill `.claude/skills/auditoria-modelos` y **no fueron editados**; solo se les cambió el nombre para que queden como `AUDIT_REPORT_<proyecto>.md`. Todas las auditorías se ejecutaron sin interfaz (`claude -p "/auditoria-modelos …"`), dando permiso solo a `Skill(auditoria-modelos)`, `Read`, `Glob`, `Grep` y `Write`.

| Informe | Proyecto auditado | Versión de la Skill | Archivo original generado |
|---|---|---|---|
| `AUDIT_REPORT_biopsias_original.md` | (a) `App_Diagnostico_Biopsias_Mama.ipynb`, versión original con defectos (Tarea 3.1) | 1.3 | `AUDIT_REPORT_biopsias_original_5.md` |
| `AUDIT_REPORT_iris.md` | (b) `App_Comparacion_Clasificadores_Iris.ipynb`, con los cinco clasificadores | 1.3 | `AUDIT_REPORT_iris_4.md` |
| `AUDIT_REPORT_housing.md` | (c) `housing.csv` (California Housing, solo datos, sin notebook) | 1.4 | `AUDIT_REPORT_housing.md` |

## Resumen de veredictos

| Verificación | Biopsias original | Iris | Housing |
|---|---|---|---|
| V1 Métricas reportadas | FALLA | NO SE PUEDE DETERMINAR | NO SE PUEDE DETERMINAR |
| V2 Partición de datos | FALLA | PASA | NO SE PUEDE DETERMINAR |
| V3 Fuga de información | FALLA | PASA | NO SE PUEDE DETERMINAR |
| V4 Disparidad entre subgrupos | NO SE PUEDE DETERMINAR | NO SE PUEDE DETERMINAR | NO SE PUEDE DETERMINAR |
| V5 Validez de datos de entrada | FALLA | PASA | NO SE PUEDE DETERMINAR |
| V6 Variables no admisibles | PASA | PASA | NO SE PUEDE DETERMINAR |

## `evidencia_punto5/` (estabilidad y refinamiento)

- `biopsias_original/`: cinco ejecuciones sobre el mismo notebook. La 1 es de la v1.0; la 2 y la 3, de la v1.1 (difieren en V1.4); la 4 y la 5, de la v1.3 (iguales en los 15 subcriterios). Una sexta ejecución, con la v1.0, no produjo informe: reutilizó el anterior.
- `iris/`: cuatro ejecuciones, tres con la v1.0 y una con la v1.3. Los 15 veredictos son iguales en las cuatro.
- `defecto_inyectado/`: una copia de Iris con un escalado ajustado sobre todo `X` antes de la validación cruzada (celda 15, id `m41_knn_rf_code`). El informe sin sufijo es de la v1.1: V2.1 y V3.1 dan FALLA, pero V2.4 da PASA (omisión). El informe `_2` es de la v1.2, donde V2.4 ya da FALLA.
