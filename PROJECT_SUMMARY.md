# Resumen de continuidad del proyecto

## Fuente de verdad metodológica

Ruta del TFM: `ruta_metodologica/ruta-desarrollo-capitulo-04.md` (workspace) + `docs/metodologia.md` (este repo).

## Estado (2026-08-20)

- ABM Mesa **v1.5**: circuito SAAD + 3 colas nacionales + techo de atendidas (6387 × 60, seed=42).
- Post-PIA por hueco (no dado 98,41 %). Lista FIFO. Stock concurrente.
- `wellbeing_proxy` = target de surrogates (no puerta).
- Puerta SAAD: **`pasa`** (MAE 3,09 pp). Informe `outputs/metrics/abm_saad_validation.json`.
- IMCV archivado como puerta.
- `run_experiments` LHS ejecutado: 115 filas, 1.150 corridas Mesa, SHA256 en `dataset_manifest.json`.
- `src/surrogates/` scaffold con bloqueo por `abm_saad_validation.json`.

## Comandos

```powershell
python -m src.run_simulation
python -m src.run_saad_validation --year 2024
python -m src.run_experiments --method lhs --n-replicas 10
python -m src.surrogates.train
python -m pytest
```

## Próximos pasos

1. Entrenar surrogates sobre el dataset 4.8 y versionar métricas (4.9–4.10).
2. Implementar entrenamiento/evaluación de Dummy, Ridge, CART, RF/GBM, MLP.
3. Tabla de veredicto (fidelidad, aceleración, extrapolación) + tests estadísticos.
4. Prototipo web con el surrogate ganador.
