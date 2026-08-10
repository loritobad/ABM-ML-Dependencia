"""Generación reproducible de particiones por scenario/simulation_id.

Incluye hold-out de extrapolación, tocado una sola vez al final de la
evaluación de surrogates (ruta metodológica, paso 4).
"""

from __future__ import annotations

import random

import pandas as pd


def generate_splits(
    simulation_ids: list[int],
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42,
    extrapolation_ids: list[int] | None = None,
) -> list[dict]:
    """Asigna train/validation/test sin dividir un escenario entre particiones.

    Los `extrapolation_ids` se etiquetan como `extrapolation` y no entran en
    train/validation/test de interpolación.
    """
    if round(train_ratio + val_ratio + test_ratio, 10) != 1.0:
        raise ValueError("train_ratio + val_ratio + test_ratio debe ser igual a 1.")

    extrapolation_set = set(extrapolation_ids or [])
    in_sample_ids = [sid for sid in simulation_ids if sid not in extrapolation_set]

    shuffled_ids = list(in_sample_ids)
    random.Random(random_seed).shuffle(shuffled_ids)

    n_simulations = len(shuffled_ids)
    n_train = int(n_simulations * train_ratio)
    n_val = int(n_simulations * val_ratio)

    train_ids = set(shuffled_ids[:n_train])
    val_ids = set(shuffled_ids[n_train : n_train + n_val])

    rows = []
    for simulation_id in sorted(set(simulation_ids) | extrapolation_set):
        if simulation_id in extrapolation_set:
            split = "extrapolation"
        elif simulation_id in train_ids:
            split = "train"
        elif simulation_id in val_ids:
            split = "validation"
        else:
            split = "test"
        rows.append({"simulation_id": simulation_id, "scenario_id": simulation_id, "split": split})

    return sorted(rows, key=lambda row: row["simulation_id"])


def generate_dataset_splits(
    simulation_ids: list[int],
    seed: int = 42,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    extrapolation_ids: list[int] | None = None,
) -> pd.DataFrame:
    """Compatibilidad con la API previa del proyecto."""
    rows = generate_splits(
        simulation_ids=simulation_ids,
        train_ratio=train_ratio,
        val_ratio=validation_ratio,
        test_ratio=1.0 - train_ratio - validation_ratio,
        random_seed=seed,
        extrapolation_ids=extrapolation_ids,
    )
    return pd.DataFrame(rows)
