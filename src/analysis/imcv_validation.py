"""Validación empírica externa del ABM frente al IMCV (puerta metodológica).

Pregunta: ¿es el ABM suficientemente plausible respecto a indicadores observados?
NO mide fidelidad de surrogates. Los surrogates solo se entrenan si esta puerta
se supera (o se documenta explícitamente como 'pasa con reservas').

Entrada esperada: CSV de referencia con columnas mínimas:
  territory, year, imcv_value
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .wellbeing import estimate_wellbeing_proxy

DEFAULT_MAE_THRESHOLD = 0.5
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REFERENCE = PROJECT_ROOT / "data" / "raw" / "imcv_reference.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "metrics" / "abm_imcv_validation.json"


def load_imcv_reference(path: str | Path | None = None) -> pd.DataFrame:
    """Carga la serie de referencia IMCV."""
    reference_path = Path(path) if path else DEFAULT_REFERENCE
    if not reference_path.exists():
        raise FileNotFoundError(
            f"No se encontró la referencia IMCV en {reference_path}. "
            "Complete data/raw/imcv_reference.csv (plantilla en el repo)."
        )
    df = pd.read_csv(reference_path)
    required = {"territory", "year", "imcv_value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en la referencia IMCV: {sorted(missing)}")
    return df


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return float("nan")
    rx = pd.Series(x).rank(method="average").to_numpy()
    ry = pd.Series(y).rank(method="average").to_numpy()
    return _pearson(rx, ry)


def _ks_statistic(x: np.ndarray, y: np.ndarray) -> float:
    """Estadístico KS de dos muestras sin dependencia de SciPy."""
    x_sorted = np.sort(x)
    y_sorted = np.sort(y)
    data = np.concatenate([x_sorted, y_sorted])
    cdf_x = np.searchsorted(x_sorted, data, side="right") / len(x_sorted)
    cdf_y = np.searchsorted(y_sorted, data, side="right") / len(y_sorted)
    return float(np.max(np.abs(cdf_x - cdf_y)))


def validate_abm_against_imcv(
    abm_wellbeing_by_territory: dict[str, float] | pd.Series,
    reference: pd.DataFrame | None = None,
    *,
    year: int | None = None,
    mae_threshold: float = DEFAULT_MAE_THRESHOLD,
) -> dict[str, Any]:
    """Compara el proxy de bienestar del ABM con el IMCV de referencia.

    Parameters
    ----------
    abm_wellbeing_by_territory:
        Mapa territory -> wellbeing_proxy del ABM (agregado).
    reference:
        DataFrame IMCV. Si es None, se carga desde data/raw/imcv_reference.csv.
    year:
        Filtra la referencia a un año concreto. Si None, usa el año más reciente.
    mae_threshold:
        Umbral de aceptación (ejemplo metodológico: 0.5 puntos IMCV).
    """
    ref = reference if reference is not None else load_imcv_reference()
    if year is None:
        year = int(ref["year"].max())
    ref_year = ref.loc[ref["year"] == year].copy()
    if ref_year.empty:
        raise ValueError(f"No hay filas IMCV para el año {year}.")

    abm_series = pd.Series(abm_wellbeing_by_territory, dtype=float)
    merged = ref_year.merge(
        abm_series.rename("abm_wellbeing").rename_axis("territory").reset_index(),
        on="territory",
        how="inner",
    )
    if merged.empty:
        raise ValueError(
            "No hay territorios en común entre el ABM y la referencia IMCV."
        )

    observed = merged["imcv_value"].to_numpy(dtype=float)
    predicted = merged["abm_wellbeing"].to_numpy(dtype=float)
    abs_err = np.abs(predicted - observed)
    mae = float(np.mean(abs_err))
    rmse = float(np.sqrt(np.mean((predicted - observed) ** 2)))
    pearson = _pearson(predicted, observed)
    spearman = _spearman(predicted, observed)
    ks = _ks_statistic(predicted, observed)

    if mae <= mae_threshold:
        gate = "pasa"
    elif mae <= mae_threshold * 1.5:
        gate = "pasa_con_reservas"
    else:
        gate = "no_pasa"

    per_territory = [
        {
            "territory": row.territory,
            "imcv_value": float(row.imcv_value),
            "abm_wellbeing": float(row.abm_wellbeing),
            "abs_error": float(abs(row.abm_wellbeing - row.imcv_value)),
        }
        for row in merged.itertuples(index=False)
    ]

    return {
        "year": year,
        "n_territories": int(len(merged)),
        "mae": mae,
        "rmse": rmse,
        "pearson": pearson,
        "spearman": spearman,
        "ks_statistic": ks,
        "mae_threshold": mae_threshold,
        "gate_decision": gate,
        "per_territory": per_territory,
        "note": (
            "El surrogate mide fidelidad al ABM, no exactitud sobre la realidad. "
            "Esta puerta valida el eslabón ABM → realidad (IMCV)."
        ),
    }


def validate_national_proxy_from_metrics(
    metrics: dict[str, float],
    reference: pd.DataFrame | None = None,
    *,
    territory: str = "España",
    year: int | None = None,
    mae_threshold: float = DEFAULT_MAE_THRESHOLD,
) -> dict[str, Any]:
    """Atajo: valida un único proxy nacional derivado de métricas ABM."""
    proxy = estimate_wellbeing_proxy(metrics)
    return validate_abm_against_imcv(
        {territory: proxy},
        reference=reference,
        year=year,
        mae_threshold=mae_threshold,
    )


def save_validation_report(report: dict[str, Any], path: str | Path | None = None) -> Path:
    """Guarda el informe de puerta IMCV en JSON."""
    output = Path(path) if path else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    return output
