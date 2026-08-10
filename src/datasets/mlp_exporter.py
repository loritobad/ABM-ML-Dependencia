"""Exportación tabular de simulaciones ABM para surrogates (MLP y familias).

Unidad experimental: escenario (simulation_id / scenario_id), no agente-mes.
Target principal: wellbeing_proxy (alineable con IMCV).
Targets secundarios: cobertura y saturación / lista de espera.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


TARGET_COLUMNS = [
    "target_wellbeing_proxy",
    "target_rate_prestacion_efectiva",
    "target_rate_lista_espera",
    "target_rate_sin_grado",
    "target_final_prestacion_efectiva",
    "target_final_lista_espera",
    "target_final_sin_grado",
    "target_month_prestacion_effectiva_exceeds_no_solicitantes",
]

VARIANCE_COLUMNS = [
    "std_wellbeing_proxy",
    "std_rate_prestacion_efectiva",
    "std_rate_lista_espera",
]


def build_targets(metrics: dict) -> dict:
    """Extrae los targets comunes para surrogates tabulares y grafo."""
    return {
        "target_wellbeing_proxy": metrics["wellbeing_proxy"],
        "target_rate_prestacion_efectiva": metrics["rate_prestacion_efectiva"],
        "target_rate_lista_espera": metrics["rate_lista_espera"],
        "target_rate_sin_grado": metrics["rate_sin_grado"],
        "target_final_prestacion_efectiva": metrics["final_prestacion_efectiva"],
        "target_final_lista_espera": metrics["final_lista_espera"],
        "target_final_sin_grado": metrics["final_sin_grado"],
        "target_month_prestacion_effectiva_exceeds_no_solicitantes": metrics[
            "month_prestacion_effectiva_exceeds_no_solicitantes"
        ],
    }


def build_mlp_row(
    simulation_id: int,
    parameters: dict,
    metrics: dict,
    *,
    regime: str = "interpolation",
    n_replicas: int = 1,
    std_metrics: dict | None = None,
) -> dict:
    """Genera una fila plana de parámetros de entrada y targets."""
    grados = parameters["distribucion_grados"]
    prestaciones = parameters["distribucion_prestaciones"]
    row = {
        "simulation_id": simulation_id,
        "scenario_id": simulation_id,
        "regime": regime,
        "n_replicas": n_replicas,
        "initial_vulnerable_population": parameters["initial_vulnerable_population"],
        "simulation_months": parameters["simulation_months"],
        "prob_solicitud_mensual": parameters["prob_solicitud_mensual"],
        "prob_reconocimiento_grado": parameters["prob_reconocimiento_grado"],
        "prob_con_derecho": parameters["prob_con_derecho"],
        "prob_pia": parameters["prob_pia"],
        "prob_prestacion_efectiva": parameters["prob_prestacion_efectiva"],
        "prob_lista_espera": parameters["prob_lista_espera"],
        "prob_grado_I": grados["I"],
        "prob_grado_II": grados["II"],
        "prob_grado_III": grados["III"],
        "prob_teleasistencia": prestaciones["teleasistencia"],
        "prob_ayuda_domicilio": prestaciones["ayuda_domicilio"],
        "prob_atencion_residencial": prestaciones["atencion_residencial"],
        "prob_cuidados_familiares": prestaciones["cuidados_familiares"],
    }
    row.update(build_targets(metrics))
    if std_metrics:
        row.update(std_metrics)
    else:
        row.update({column: 0.0 for column in VARIANCE_COLUMNS})
    return row


def save_mlp_dataset(rows: list[dict], output_path: str | Path) -> None:
    """Guarda el dataset tabular de surrogates en CSV."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)
