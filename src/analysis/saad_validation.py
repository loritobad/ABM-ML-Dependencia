"""Validación empírica externa del ABM frente a tasas de gestión del SAAD.

Pregunta: ¿son plausibles la cobertura y el limbo simulados frente al IMSERSO
(Tabla 11 / estsisaad, 31/12/2024)?

 El wellbeing_proxy sigue siendo target de surrogates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

DEFAULT_MAE_THRESHOLD_PP = 5.0
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REFERENCE = PROJECT_ROOT / "data" / "raw" / "saad_reference.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "metrics" / "abm_saad_validation.json"
GATE_INDICATORS = ("cobertura", "limbo")


def load_saad_reference(path: str | Path | None = None) -> pd.DataFrame:
    reference_path = Path(path) if path else DEFAULT_REFERENCE
    if not reference_path.exists():
        raise FileNotFoundError(f"No se encontró la referencia SAAD en {reference_path}.")
    df = pd.read_csv(reference_path)
    required = {"indicator", "year", "value_pp", "denominator"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en la referencia SAAD: {sorted(missing)}")
    return df


def rates_from_metrics(metrics: Mapping[str, float]) -> dict[str, Any]:
    attended = float(metrics["final_prestacion_efectiva"])
    waiting = float(metrics["final_lista_espera"])
    with_right = float(metrics["final_con_derecho"])
    with_pia = float(metrics["final_con_pia"])
    pending_grade = float(metrics["final_pendiente_grado"])
    no_request = float(metrics["final_no_solicitantes"])
    n_pop = float(metrics["final_vulnerable_population"])

    right_stock = attended + waiting + with_right + with_pia
    applicants = n_pop - no_request
    limbo_stock = waiting + with_right + with_pia
    cobertura_pp = 100.0 * attended / right_stock if right_stock else 0.0
    limbo_pp = 100.0 * limbo_stock / right_stock if right_stock else 0.0
    pending_pp = 100.0 * pending_grade / applicants if applicants else 0.0
    return {
        "right_stock": right_stock,
        "limbo_stock": limbo_stock,
        "attended": attended,
        "applicants": applicants,
        "cobertura_pp": cobertura_pp,
        "limbo_pp": limbo_pp,
        "pendiente_grado_pp": pending_pp,
    }


def decide_gate(mae_pp: float, threshold_pp: float = DEFAULT_MAE_THRESHOLD_PP) -> str:
    if mae_pp <= threshold_pp:
        return "pasa"
    if mae_pp <= threshold_pp * 1.5:
        return "pasa_con_reservas"
    return "no_pasa"


def validate_abm_against_saad(
    metrics: Mapping[str, float],
    reference: pd.DataFrame | None = None,
    *,
    year: int = 2024,
    mae_threshold_pp: float = DEFAULT_MAE_THRESHOLD_PP,
) -> dict[str, Any]:
    ref = reference if reference is not None else load_saad_reference()
    ref_year = ref.loc[ref["year"] == year].copy()
    if ref_year.empty:
        raise ValueError(f"No hay filas SAAD para el año {year}.")
    rates = rates_from_metrics(metrics)
    per_indicator = []
    errors = []
    for name in GATE_INDICATORS:
        row = ref_year.loc[ref_year["indicator"] == name]
        if row.empty:
            raise ValueError(f"Falta el indicador '{name}' en la referencia SAAD.")
        observed = float(row.iloc[0]["value_pp"])
        simulated = float(rates[f"{name}_pp"])
        abs_err = abs(simulated - observed)
        errors.append(abs_err)
        per_indicator.append(
            {
                "indicator": name,
                "denominator": str(row.iloc[0]["denominator"]),
                "observed_pp": observed,
                "abm_pp": simulated,
                "abs_error_pp": abs_err,
                "source": str(row.iloc[0].get("source", "")),
            }
        )
    mae_pp = float(sum(errors) / len(errors))
    optional = ref_year.loc[ref_year["indicator"] == "pendiente_grado"]
    optional_check = None
    if not optional.empty:
        obs = float(optional.iloc[0]["value_pp"])
        optional_check = {
            "indicator": "pendiente_grado",
            "denominator": "solicitudes",
            "observed_pp": obs,
            "abm_pp": rates["pendiente_grado_pp"],
            "abs_error_pp": abs(rates["pendiente_grado_pp"] - obs),
            "in_gate_mae": False,
        }
    return {
        "year": year,
        "n_indicators": len(GATE_INDICATORS),
        "mae_pp": mae_pp,
        "mae_threshold_pp": mae_threshold_pp,
        "gate_decision": decide_gate(mae_pp, mae_threshold_pp),
        "abm_rates": rates,
        "per_indicator": per_indicator,
        "optional_check": optional_check,
        "mapeo_version": metrics.get("mapeo_version", "v1.5"),
        "note": (
            "Puerta SAAD (IMSERSO). Cupos v1.5 escalados por solicitudes; "
            "el limbo no se usa como tamaño de cupo. El IMCV queda archivado."
        ),
        "metrics_source": "outputs/metrics/base_simulation_metrics.json",
        "reference_file": "data/raw/saad_reference.csv",
    }


def save_validation_report(report: dict[str, Any], path: str | Path | None = None) -> Path:
    output = Path(path) if path else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return output
