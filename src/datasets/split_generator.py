"""Generación reproducible de particiones por simulation_id."""

from __future__ import annotations

import random

import pandas as pd


def generate_splits(
    simulation_ids: list[int],
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42,
) -> list[dict]:
    """Asigna train/validation/test sin dividir una simulación entre particiones."""
    if round(train_ratio + val_ratio + test_ratio, 10) != 1.0:
        raise ValueError("train_ratio + val_ratio + test_ratio debe ser igual a 1.")

    shuffled_ids = list(simulation_ids)
    random.Random(random_seed).shuffle(shuffled_ids)

    n_simulations = len(shuffled_ids)
    n_train = int(n_simulations * train_ratio)
    n_val = int(n_simulations * val_ratio)

    train_ids = set(shuffled_ids[:n_train])
    val_ids = set(shuffled_ids[n_train : n_train + n_val])

    rows = []
    for simulation_id in shuffled_ids:
        if simulation_id in train_ids:
            split = "train"
        elif simulation_id in val_ids:
            split = "validation"
        else:
            split = "test"
        rows.append({"simulation_id": simulation_id, "split": split})

    return sorted(rows, key=lambda row: row["simulation_id"])


def generate_dataset_splits(
    simulation_ids: list[int],
    seed: int = 42,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
) -> pd.DataFrame:
    """Compatibilidad con la API previa del proyecto."""
    rows = generate_splits(
        simulation_ids=simulation_ids,
        train_ratio=train_ratio,
        val_ratio=validation_ratio,
        test_ratio=1.0 - train_ratio - validation_ratio,
        random_seed=seed,
    )
    return pd.DataFrame(rows)
