# Resumen de continuidad del proyecto

## Fuente de verdad metodológica

Ruta del TFM: `ruta_metodologica/ruta-desarrollo-capitulo-04.md` (workspace) + `docs/metodologia.md` (este repo).

## Estado (2026-08-10)

- ABM Mesa del circuito SAAD operativo (6387 × 60, salida mensual agregada).
- `wellbeing_proxy` integrado en métricas y targets.
- Validación IMCV implementada (`src/run_imcv_validation.py`); referencia en `data/raw/imcv_reference.csv` (**plantilla**).
- `run_experiments` usa LHS por defecto, réplicas, hold-out de extrapolación y SHA256.
- `src/surrogates/` catálogo + scaffold con bloqueo por puerta IMCV.
- Entrenamiento comparativo (CV anidada, Friedman, etc.) **pendiente**.

## Comandos

```powershell
python -m src.run_simulation
python -m src.run_imcv_validation
python -m src.run_experiments --method lhs --n-replicas 10
python -m src.surrogates.train
python -m pytest
```

## Próximos pasos

1. Sustituir plantilla IMCV por valores oficiales INE y cerrar decisión de puerta.
2. Regenerar dataset LHS×réplicas y versionar manifest.
3. Implementar entrenamiento/evaluación de Dummy, Ridge, CART, RF/GBM, MLP.
4. Tabla de veredicto (fidelidad, aceleración, extrapolación) + tests estadísticos.
5. Prototipo web con el surrogate ganador.
