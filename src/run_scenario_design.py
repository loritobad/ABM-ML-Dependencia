"""Exporta el diseño LHS v1.5 (4.7) sin ejecutar el ABM.

100 escenarios de interpolación + 15 de extrapolación (seed=42).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from .datasets.scenario_sampler import flatten_parameters, sample_lhs_scenarios
except ImportError:
    from datasets.scenario_sampler import flatten_parameters, sample_lhs_scenarios

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "outputs" / "datasets" / "lhs_scenario_design.csv"

N_INTERPOLATION = 100
N_EXTRAPOLATION = 15
SEED = 42
GRADE_III_HIGH = 0.30
FACTOR_HISTORICO = (0.95, 1.05)


def classify_row(row: dict) -> dict:
    factor = float(row["factor_capacidad"])
    grade_iii = float(row["prob_grado_III"])
    regime = row["regime"]
    if factor < 0.90:
        capacidad = "recorte"
    elif factor > 1.10:
        capacidad = "expansion"
    else:
        capacidad = "entorno_2024"
    historico = regime == "interpolation" and (
        FACTOR_HISTORICO[0] <= factor <= FACTOR_HISTORICO[1]
    )
    return {
        "estrato_capacidad": capacidad,
        "estrato_grado_III": "alto" if grade_iii > GRADE_III_HIGH else "base",
        "escenario_historico": historico,
        "escenario_contrafactual": (not historico) or regime == "extrapolation",
    }


def build_design() -> pd.DataFrame:
    rows = []
    interpolation = sample_lhs_scenarios(
        N_INTERPOLATION, seed=SEED, regime="interpolation"
    )
    extrapolation = sample_lhs_scenarios(
        N_EXTRAPOLATION, seed=SEED + 10_000, regime="extrapolation"
    )
    for block in (interpolation, extrapolation):
        for item in block:
            sid = int(item["scenario_id"])
            if item["regime"] == "extrapolation":
                sid = N_INTERPOLATION + sid
            row = flatten_parameters(sid, item["parameters"])
            row["scenario_id"] = sid
            row["regime"] = item["regime"]
            row["seed_escenario"] = item["seed"]
            row.update(classify_row(row))
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    df = build_design()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"Diseño: {OUTPUT} ({len(df)} escenarios)")
    print(df.groupby("regime").size().to_string())
    print(df.groupby("estrato_capacidad").size().to_string())
    print(
        "históricos:",
        int(df["escenario_historico"].sum()),
        "contrafactuales:",
        int(df["escenario_contrafactual"].sum()),
    )


if __name__ == "__main__":
    main()
