"""Muestreo reproducible de escenarios paramétricos para el ABM."""

from __future__ import annotations

from copy import deepcopy
import random

try:
    from ..model.parameters import get_base_parameters
except ImportError:
    from model.parameters import get_base_parameters


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
    """Perturba una probabilidad de forma suave y reproducible."""
    rng = rng or random.Random()
    factor = rng.uniform(1.0 - scale, 1.0 + scale)
    return clip_probability(value * factor)


def perturb_distribution(
    distribution: dict[str, float],
    scale: float = 0.10,
    rng: random.Random | None = None,
) -> dict[str, float]:
    """Perturba y normaliza una distribución categórica."""
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
    """Devuelve una copia de parámetros base con variaciones controladas."""
    rng = random.Random(random_seed)
    parameters = deepcopy(base_parameters)

    for key in [
        "prob_solicitud_mensual",
        "prob_reconocimiento_grado",
        "prob_con_derecho",
        "prob_pia",
        "prob_prestacion_efectiva",
    ]:
        parameters[key] = perturb_probability(parameters[key], rng=rng)

    parameters["prob_lista_espera"] = clip_probability(
        1.0 - parameters["prob_prestacion_efectiva"]
    )
    parameters["distribucion_grados"] = perturb_distribution(
        parameters["distribucion_grados"], rng=rng
    )
    parameters["distribucion_prestaciones"] = perturb_distribution(
        parameters["distribucion_prestaciones"], rng=rng
    )

    return parameters


def sample_scenarios(
    n_simulations: int,
    seed: int = 42,
    initial_agents: int | None = None,
) -> list[dict]:
    """Genera múltiples escenarios con identificadores reproducibles."""
    base_parameters = get_base_parameters()
    if initial_agents is not None:
        base_parameters["initial_vulnerable_population"] = initial_agents

    scenarios = []
    for simulation_id in range(1, n_simulations + 1):
        scenario_seed = seed + simulation_id
        scenarios.append(
            {
                "simulation_id": simulation_id,
                "seed": scenario_seed,
                "parameters": sample_scenario(base_parameters, scenario_seed),
            }
        )
    return scenarios


def flatten_parameters(simulation_id: int, parameters: dict) -> dict:
    """Convierte parámetros anidados en una fila para CSV."""
    grados = parameters["distribucion_grados"]
    prestaciones = parameters["distribucion_prestaciones"]
    return {
        "simulation_id": simulation_id,
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
