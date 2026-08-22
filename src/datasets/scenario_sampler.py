"""Muestreo reproducible de escenarios paramétricos para el ABM.

Fuente de verdad metodológica: Latin Hypercube Sampling (LHS) sobre rangos
plausibles (Tablas 6–14). La perturbación ±10% se mantiene como modo legacy.
"""

from __future__ import annotations

from copy import deepcopy
import random
from typing import Literal

import numpy as np

try:
    from ..model.capacity import cupos_from_n
    from ..model.parameters import get_base_parameters
    from .parameter_bounds import (
        BENEFIT_KEYS,
        CAPACITY_KEYS,
        GRADE_KEYS,
        LHS_EXTRAPOLATION_BOUNDS,
        LHS_PARAMETER_BOUNDS,
    )
except ImportError:
    from model.capacity import cupos_from_n
    from model.parameters import get_base_parameters
    from datasets.parameter_bounds import (
        BENEFIT_KEYS,
        CAPACITY_KEYS,
        GRADE_KEYS,
        LHS_EXTRAPOLATION_BOUNDS,
        LHS_PARAMETER_BOUNDS,
    )


Regime = Literal["interpolation", "extrapolation"]


def clip_probability(value: float) -> float:
    """Limita una probabilidad al intervalo [0, 1]."""
    return min(max(float(value), 0.0), 1.0)


def normalize_distribution(distribution: dict[str, float]) -> dict[str, float]:
    """Normaliza una distribución para que sus valores sumen 1."""
    clipped = {key: max(float(value), 0.0) for key, value in distribution.items()}
    total = sum(clipped.values())
    if total == 0:
        uniform_value = 1.0 / len(clipped)
        return {key: uniform_value for key in clipped}
    return {key: value / total for key, value in clipped.items()}


def perturb_probability(
    value: float, scale: float = 0.10, rng: random.Random | None = None
) -> float:
    """Perturba una probabilidad de forma suave y reproducible (legacy)."""
    rng = rng or random.Random()
    factor = rng.uniform(1.0 - scale, 1.0 + scale)
    return clip_probability(value * factor)


def perturb_distribution(
    distribution: dict[str, float],
    scale: float = 0.10,
    rng: random.Random | None = None,
) -> dict[str, float]:
    """Perturba y normaliza una distribución categórica (legacy)."""
    rng = rng or random.Random()
    varied = {
        key: value * rng.uniform(1.0 - scale, 1.0 + scale)
        for key, value in distribution.items()
    }
    return normalize_distribution(varied)


def sample_scenario(
    base_parameters: dict,
    random_seed: int | None = None,
) -> dict:
    """Modo legacy: copia de parámetros base con variaciones ±10%."""
    rng = random.Random(random_seed)
    parameters = deepcopy(base_parameters)

    for key in [
        "prob_solicitud_mensual",
        "prob_solicitud_si_vulnerable",
        "prob_resolucion_grado_mensual",
        "prob_con_derecho",
        "prob_pia_mensual",
        "prob_prestacion_efectiva",
    ]:
        if key in parameters:
            parameters[key] = perturb_probability(parameters[key], rng=rng)

    parameters["prob_lista_espera"] = clip_probability(
        1.0 - parameters["prob_prestacion_efectiva"]
    )
    # Alias legacy
    parameters["prob_reconocimiento_grado"] = parameters["prob_resolucion_grado_mensual"]
    parameters["prob_pia"] = parameters["prob_pia_mensual"]
    parameters["distribucion_grados"] = perturb_distribution(
        parameters["distribucion_grados"], rng=rng
    )
    parameters["distribucion_prestaciones"] = perturb_distribution(
        parameters["distribucion_prestaciones"], rng=rng
    )
    return parameters


def latin_hypercube(
    n_samples: int,
    n_dimensions: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """LHS unitario en [0, 1]^d (una muestra por estrato y dimensión)."""
    cut = np.linspace(0.0, 1.0, n_samples + 1)
    u = rng.uniform(size=(n_samples, n_dimensions))
    points = np.empty((n_samples, n_dimensions), dtype=float)
    for dim in range(n_dimensions):
        points[:, dim] = cut[:-1] + u[:, dim] * (cut[1:] - cut[:-1])
        rng.shuffle(points[:, dim])
    return points


def apply_capacity_factor(parameters: dict, factor: float | None = None) -> dict:
    """Escala los cupos IMSERSO por factor_capacidad (enteros ≥ 1)."""
    n = int(parameters["initial_vulnerable_population"])
    scale = float(parameters["factor_capacidad"] if factor is None else factor)
    parameters["factor_capacidad"] = scale
    for key, stock in cupos_from_n(n).items():
        parameters[key] = max(1, int(round(stock * scale)))
    return parameters


def _map_unit_to_bounds(unit_value: float, low: float, high: float) -> float:
    return float(low + unit_value * (high - low))


def _sample_simplex(keys: tuple[str, ...], rng: np.random.Generator) -> dict[str, float]:
    raw = rng.random(len(keys))
    raw = raw / raw.sum()
    return {key: float(value) for key, value in zip(keys, raw)}


def build_parameters_from_lhs_row(
    unit_row: np.ndarray,
    *,
    regime: Regime = "interpolation",
    base_parameters: dict | None = None,
    rng: np.random.Generator | None = None,
) -> dict:
    """Construye un dict de parámetros ABM a partir de una fila LHS unitaria."""
    bounds = (
        LHS_PARAMETER_BOUNDS
        if regime == "interpolation"
        else LHS_EXTRAPOLATION_BOUNDS
    )
    keys = list(bounds.keys())
    if len(unit_row) != len(keys):
        raise ValueError(
            f"La fila LHS tiene {len(unit_row)} dimensiones; se esperaban {len(keys)}."
        )

    parameters = deepcopy(base_parameters or get_base_parameters())
    month_keys = {"meses_min_pendiente_grado", "meses_min_tramite_prestacion"}
    for index, key in enumerate(keys):
        low, high = bounds[key]
        raw = _map_unit_to_bounds(unit_row[index], low, high)
        if key in month_keys:
            parameters[key] = int(round(raw))
        elif key in CAPACITY_KEYS:
            parameters[key] = float(raw)
        else:
            parameters[key] = clip_probability(raw)

    apply_capacity_factor(parameters)
    parameters["prob_lista_espera"] = clip_probability(
        1.0 - parameters.get("prob_prestacion_efectiva", 0.9841)
    )
    parameters["prob_reconocimiento_grado"] = parameters["prob_resolucion_grado_mensual"]
    parameters["prob_pia"] = parameters["prob_pia_mensual"]

    local_rng = rng or np.random.default_rng(0)
    # Distribuciones categóricas: Dirichlet suave centrada en la base
    base_grades = parameters["distribucion_grados"]
    grade_center = np.array([base_grades[k] for k in GRADE_KEYS], dtype=float)
    grade_draw = local_rng.dirichlet(grade_center * 20.0 + 1e-6)
    parameters["distribucion_grados"] = {
        key: float(value) for key, value in zip(GRADE_KEYS, grade_draw)
    }

    base_benefits = parameters["distribucion_prestaciones"]
    benefit_center = np.array([base_benefits[k] for k in BENEFIT_KEYS], dtype=float)
    benefit_draw = local_rng.dirichlet(benefit_center * 20.0 + 1e-6)
    parameters["distribucion_prestaciones"] = {
        key: float(value) for key, value in zip(BENEFIT_KEYS, benefit_draw)
    }
    return parameters


def sample_lhs_scenarios(
    n_scenarios: int,
    *,
    seed: int = 42,
    regime: Regime = "interpolation",
    initial_agents: int | None = None,
) -> list[dict]:
    """Genera escenarios LHS con identificadores reproducibles."""
    base_parameters = get_base_parameters()
    if initial_agents is not None:
        base_parameters["initial_vulnerable_population"] = initial_agents

    bounds = (
        LHS_PARAMETER_BOUNDS
        if regime == "interpolation"
        else LHS_EXTRAPOLATION_BOUNDS
    )
    n_dim = len(bounds)
    rng = np.random.default_rng(seed)
    unit_samples = latin_hypercube(n_scenarios, n_dim, rng)

    scenarios = []
    for scenario_id, unit_row in enumerate(unit_samples, start=1):
        scenario_rng = np.random.default_rng(seed + scenario_id * 17)
        parameters = build_parameters_from_lhs_row(
            unit_row,
            regime=regime,
            base_parameters=base_parameters,
            rng=scenario_rng,
        )
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "simulation_id": scenario_id,
                "seed": int(seed + scenario_id),
                "regime": regime,
                "parameters": parameters,
            }
        )
    return scenarios


def sample_scenarios(
    n_simulations: int,
    seed: int = 42,
    initial_agents: int | None = None,
    *,
    method: Literal["lhs", "legacy"] = "lhs",
    regime: Regime = "interpolation",
) -> list[dict]:
    """API unificada de muestreo de escenarios."""
    if method == "legacy":
        base_parameters = get_base_parameters()
        if initial_agents is not None:
            base_parameters["initial_vulnerable_population"] = initial_agents
        scenarios = []
        for simulation_id in range(1, n_simulations + 1):
            scenario_seed = seed + simulation_id
            scenarios.append(
                {
                    "scenario_id": simulation_id,
                    "simulation_id": simulation_id,
                    "seed": scenario_seed,
                    "regime": "legacy",
                    "parameters": sample_scenario(base_parameters, scenario_seed),
                }
            )
        return scenarios

    return sample_lhs_scenarios(
        n_simulations,
        seed=seed,
        regime=regime,
        initial_agents=initial_agents,
    )


def flatten_parameters(simulation_id: int, parameters: dict) -> dict:
    """Convierte parámetros anidados en una fila para CSV."""
    grados = parameters["distribucion_grados"]
    prestaciones = parameters["distribucion_prestaciones"]
    row = {
        "simulation_id": simulation_id,
        "initial_vulnerable_population": parameters["initial_vulnerable_population"],
        "simulation_months": parameters["simulation_months"],
        "prob_solicitud_mensual": parameters["prob_solicitud_mensual"],
        "prob_solicitud_si_vulnerable": parameters.get(
            "prob_solicitud_si_vulnerable", parameters["prob_solicitud_mensual"]
        ),
        "prob_resolucion_grado_mensual": parameters.get(
            "prob_resolucion_grado_mensual",
            parameters.get("prob_reconocimiento_grado"),
        ),
        "prob_reconocimiento_grado": parameters.get(
            "prob_reconocimiento_grado",
            parameters.get("prob_resolucion_grado_mensual"),
        ),
        "prob_con_derecho": parameters["prob_con_derecho"],
        "prob_pia_mensual": parameters.get("prob_pia_mensual", parameters.get("prob_pia")),
        "prob_pia": parameters.get("prob_pia", parameters.get("prob_pia_mensual")),
        "prob_prestacion_efectiva": parameters.get("prob_prestacion_efectiva", 0.9841),
        "prob_lista_espera": parameters.get("prob_lista_espera"),
        "factor_capacidad": parameters.get("factor_capacidad", 1.0),
        "cupo_residencial": parameters.get("cupo_residencial"),
        "cupo_dia": parameters.get("cupo_dia"),
        "cupo_resto": parameters.get("cupo_resto"),
        "cupo_atendidas": parameters.get("cupo_atendidas"),
        "meses_min_pendiente_grado": parameters.get("meses_min_pendiente_grado"),
        "meses_min_tramite_prestacion": parameters.get("meses_min_tramite_prestacion"),
        "prob_grado_I": grados["I"],
        "prob_grado_II": grados["II"],
        "prob_grado_III": grados["III"],
        "pension_media_nacional": parameters.get("pension_media_nacional"),
        "prop_nacional_65": parameters.get("prop_nacional_65"),
    }
    for key in BENEFIT_KEYS:
        row[f"prob_{key}"] = prestaciones[key]
    return row
