"""Parámetros centralizados del ABM SAAD — contrato mapeo operativo v1.

Fuente de verdad: tema/mapeo-operativo-4.4.md (Tablas 6–14 del TFM).
"""

from __future__ import annotations

from copy import deepcopy

from .capacity import cupos_from_n


# Claves canónicas de prestaciones (Tabla 12, ocho categorías)
BENEFIT_KEYS = (
    "prevencion",
    "teleasistencia",
    "ayuda_domicilio",
    "centro_dia_noche",
    "atencion_residencial",
    "pev",
    "cuidados_familiares",
    "asistencia_personal",
)

GRADE_KEYS = ("I", "II", "III")
AGE_GROUP_KEYS = ("65_74", "75_84", "85_plus")
HEALTH_KEYS = ("favorable", "intermedia", "desfavorable")


DEFAULT_PARAMETERS = {
    # --- Dimensionamiento / contexto (Tablas 6, 10) ---
    "initial_vulnerable_population": 6387,
    "simulation_months": 60,
    "prop_nacional_65": 0.2015,
    "pension_media_nacional": 1439.11,
    # --- Cohortes y salud inicial (Tabla 7) ---
    "distribucion_grupos_edad": {
        "65_74": 0.48,
        "75_84": 0.35,
        "85_plus": 0.17,
    },
    "prob_vulnerabilidad_por_edad": {
        "65_74": 0.576,
        "75_84": 0.680,
        "85_plus": 0.754,
    },
    "distribucion_salud_autopercibida": {
        "favorable": 0.449,
        "intermedia": 0.388,
        "desfavorable": 0.162,
    },
    # --- Circuito SAAD: probs mensuales + delays (Tablas 11, 13) ---
    "prob_solicitud_mensual": 0.035,
    "prob_solicitud_si_vulnerable": 0.055,
    # Tras meses_min_pendiente_grado (≈236 días ≈ 8 meses)
    "meses_min_pendiente_grado": 8,
    "prob_resolucion_grado_mensual": 0.35,
    "prob_con_derecho": 0.8032,
    # Trámite derecho→prestación (≈101 días ≈ 3 meses)
    "meses_min_tramite_prestacion": 3,
    "prob_pia_mensual": 0.40,
    # Post-PIA v1.5: la prestación ya no se sortea con 98,41 %.
    # Las claves se conservan por compatibilidad LHS; Mesa usa cupos.
    "prob_prestacion_efectiva": 0.9841,
    "prob_lista_espera": 0.0159,
    "factor_capacidad": 1.0,
    "mapeo_version": "v1.5",
    "distribucion_grados": {
        "I": 0.3615,
        "II": 0.3744,
        "III": 0.2641,
    },
    # Tabla 12 — taxonomía completa
    "distribucion_prestaciones": {
        "prevencion": 0.0369,
        "teleasistencia": 0.2468,
        "ayuda_domicilio": 0.1682,
        "centro_dia_noche": 0.0519,
        "atencion_residencial": 0.0868,
        "pev": 0.1048,
        "cuidados_familiares": 0.2993,
        "asistencia_personal": 0.0053,
    },
}

BASE_PARAMETERS = DEFAULT_PARAMETERS

PARAMETER_ALIASES = {
    "initial_vulnerable_agents": "initial_vulnerable_population",
    "monthly_request_probability": "prob_solicitud_mensual",
    "grade_recognition_probability": "prob_resolucion_grado_mensual",
    "prob_reconocimiento_grado": "prob_resolucion_grado_mensual",
    "right_recognition_probability": "prob_con_derecho",
    "pia_probability": "prob_pia_mensual",
    "prob_pia": "prob_pia_mensual",
    "effective_benefit_probability": "prob_prestacion_efectiva",
    "waiting_list_probability": "prob_lista_espera",
    "dependency_grade_distribution": "distribucion_grados",
    "benefit_distribution": "distribucion_prestaciones",
}


def get_base_parameters() -> dict:
    """Devuelve una copia independiente de los parámetros base v1."""
    return deepcopy(DEFAULT_PARAMETERS)


def normalize_parameters(parameters: dict | None = None) -> dict:
    """Combina parámetros base con posibles claves antiguas o nuevas."""
    normalized = get_base_parameters()
    if not parameters:
        return _ensure_complements(normalized)

    for key, value in parameters.items():
        normalized_key = PARAMETER_ALIASES.get(key, key)
        normalized[normalized_key] = deepcopy(value)

    return _ensure_complements(normalized)


def _ensure_complements(params: dict) -> dict:
    """Deriva lista de espera como complemento si solo viene prestación efectiva."""
    pe = float(params.get("prob_prestacion_efectiva", 0.9841))
    if "prob_lista_espera" not in params or params.get("prob_lista_espera") is None:
        params["prob_lista_espera"] = max(0.0, min(1.0, 1.0 - pe))
    # Compat: exponer alias legacy usado en datasets antiguos
    params.setdefault(
        "prob_reconocimiento_grado", params["prob_resolucion_grado_mensual"]
    )
    params.setdefault("prob_pia", params["prob_pia_mensual"])
    n = int(params["initial_vulnerable_population"])
    for key, value in cupos_from_n(n).items():
        params.setdefault(key, value)
    return params
