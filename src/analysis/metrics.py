"""Métricas descriptivas internas de la simulación base."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .wellbeing import estimate_wellbeing_proxy


def _safe_rate(numerator: float, denominator: float) -> float:
    """Calcula una tasa evitando divisiones por cero."""
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def _to_builtin(value: Any) -> Any:
    """Convierte valores de pandas/numpy a tipos nativos serializables."""
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def calculate_simulation_metrics(df: pd.DataFrame) -> dict:
    """Calcula métricas internas y descriptivas de la simulación base."""
    try:
        from ..model.parameters import BENEFIT_KEYS
    except ImportError:  # pragma: no cover
        from model.parameters import BENEFIT_KEYS

    if df.empty:
        raise ValueError("El DataFrame de simulación no puede estar vacío.")

    ordered_df = df.sort_values("month").reset_index(drop=True)
    initial_row = ordered_df.iloc[0]
    final_row = ordered_df.iloc[-1]
    initial_vulnerable_population = float(initial_row["vulnerables"])

    total_grados = float(
        final_row["grado_I"] + final_row["grado_II"] + final_row["grado_III"]
    )
    total_prestaciones = float(sum(float(final_row[k]) for k in BENEFIT_KEYS))

    exceeds_mask = (
        ordered_df["prestacion_efectiva"] > ordered_df["no_solicitantes"]
    )
    month_exceeds = (
        int(ordered_df.loc[exceeds_mask, "month"].iloc[0])
        if exceeds_mask.any()
        else None
    )

    numeric_columns = ordered_df.select_dtypes(include="number").columns.drop(
        "month", errors="ignore"
    )
    prestacion_diff = ordered_df["prestacion_efectiva"].diff().dropna()
    lista_espera_diff = ordered_df["lista_espera"].diff().dropna()

    metrics = {
        "simulation_months": int(final_row["month"] - initial_row["month"]),
        "initial_vulnerable_population": int(initial_row["vulnerables"]),
        "final_vulnerable_population": int(final_row["vulnerables"]),
        "final_no_solicitantes": int(final_row["no_solicitantes"]),
        "final_pendiente_grado": int(final_row["pendiente_grado"]),
        "final_sin_grado": int(final_row["sin_grado"]),
        "final_con_derecho": int(final_row["con_derecho"]),
        "final_con_pia": int(final_row["con_pia"]),
        "final_prestacion_efectiva": int(final_row["prestacion_efectiva"]),
        "final_lista_espera": int(final_row["lista_espera"]),
        "rate_no_solicitantes": _safe_rate(
            final_row["no_solicitantes"], initial_vulnerable_population
        ),
        "rate_pendiente_grado": _safe_rate(
            final_row["pendiente_grado"], initial_vulnerable_population
        ),
        "rate_sin_grado": _safe_rate(
            final_row["sin_grado"], initial_vulnerable_population
        ),
        "rate_prestacion_efectiva": _safe_rate(
            final_row["prestacion_efectiva"], initial_vulnerable_population
        ),
        "rate_lista_espera": _safe_rate(
            final_row["lista_espera"], initial_vulnerable_population
        ),
        "final_grado_I": int(final_row["grado_I"]),
        "final_grado_II": int(final_row["grado_II"]),
        "final_grado_III": int(final_row["grado_III"]),
        "rate_grado_I": _safe_rate(final_row["grado_I"], total_grados),
        "rate_grado_II": _safe_rate(final_row["grado_II"], total_grados),
        "rate_grado_III": _safe_rate(final_row["grado_III"], total_grados),
        "final_vuln_sanitaria": int(final_row.get("vuln_sanitaria", 0)),
        "month_prestacion_effectiva_exceeds_no_solicitantes": month_exceeds,
        "mean_monthly_increase_prestacion_efectiva": float(prestacion_diff.mean()),
        "mean_monthly_increase_lista_espera": float(lista_espera_diff.mean()),
        "max_monthly_increase_prestacion_efectiva": int(prestacion_diff.max())
        if len(prestacion_diff)
        else 0,
        "max_monthly_increase_lista_espera": int(lista_espera_diff.max())
        if len(lista_espera_diff)
        else 0,
        "has_negative_values": bool((ordered_df[numeric_columns] < 0).any().any()),
        "vulnerable_population_constant": bool(ordered_df["vulnerables"].nunique() == 1),
        "no_solicitantes_monotonic_decreasing": bool(
            ordered_df["no_solicitantes"].is_monotonic_decreasing
        ),
        "prestacion_efectiva_monotonic_increasing": bool(
            ordered_df["prestacion_efectiva"].is_monotonic_increasing
        ),
        "lista_espera_monotonic_increasing": bool(
            ordered_df["lista_espera"].is_monotonic_increasing
        ),
        "mapeo_version": "v1.5",
    }
    for key in BENEFIT_KEYS:
        metrics[f"final_{key}"] = int(final_row[key])
        metrics[f"rate_{key}"] = _safe_rate(final_row[key], total_prestaciones)

    metrics["wellbeing_proxy"] = estimate_wellbeing_proxy(metrics)
    return {key: _to_builtin(value) for key, value in metrics.items()}


def save_metrics(metrics: dict, output_path: str | Path) -> None:
    """Guarda las métricas en formato JSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2, ensure_ascii=False)


def metrics_to_dataframe(metrics: dict) -> pd.DataFrame:
    """Convierte un diccionario de métricas en una tabla larga."""
    return pd.DataFrame(
        [{"metric": metric, "value": value} for metric, value in metrics.items()]
    )
