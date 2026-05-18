"""Parámetros centralizados de la simulación base del SAAD."""

from __future__ import annotations

from copy import deepcopy


DEFAULT_PARAMETERS = {
    "initial_vulnerable_population": 6387,
    "simulation_months": 60,
    "prob_solicitud_mensual": 0.035,
    "prob_reconocimiento_grado": 0.18,
    "prob_con_derecho": 0.8032,
    "prob_pia": 0.22,
    "prob_prestacion_efectiva": 0.70,
    "prob_lista_espera": 0.30,
    "distribucion_grados": {
        "I": 0.3615,
        "II": 0.3744,
        "III": 0.2641,
    },
    "distribucion_prestaciones": {
        "teleasistencia": 0.308,
        "ayuda_domicilio": 0.210,
        "atencion_residencial": 0.108,
        "cuidados_familiares": 0.374,
    },
}

BASE_PARAMETERS = DEFAULT_PARAMETERS

PARAMETER_ALIASES = {
    "initial_vulnerable_agents": "initial_vulnerable_population",
    "monthly_request_probability": "prob_solicitud_mensual",
    "grade_recognition_probability": "prob_reconocimiento_grado",
    "right_recognition_probability": "prob_con_derecho",
    "pia_probability": "prob_pia",
    "effective_benefit_probability": "prob_prestacion_efectiva",
    "waiting_list_probability": "prob_lista_espera",
    "dependency_grade_distribution": "distribucion_grados",
    "benefit_distribution": "distribucion_prestaciones",
}


def get_base_parameters() -> dict:
    """Devuelve una copia independiente de los parámetros base."""
    return deepcopy(DEFAULT_PARAMETERS)


def normalize_parameters(parameters: dict | None = None) -> dict:
    """Combina parámetros base con posibles claves antiguas o nuevas."""
    normalized = get_base_parameters()
    if not parameters:
        return normalized

    for key, value in parameters.items():
        normalized_key = PARAMETER_ALIASES.get(key, key)
        normalized[normalized_key] = deepcopy(value)
    return normalized
