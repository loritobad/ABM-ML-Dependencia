"""Parámetros base del modelo ABM de dependencia."""

BASE_PARAMETERS = {
    "p_vulnerable_65_74": 0.576,
    "p_vulnerable_75_84": 0.680,
    "p_vulnerable_85_plus": 0.754,
    "p_request_if_vulnerable": 0.35,
    "p_grade_resolution": 0.9410,
    "p_no_grade": 0.1968,
    "p_right_recognition": 0.8032,
    "p_grade_I": 0.3615,
    "p_grade_II": 0.3744,
    "p_grade_III": 0.2641,
    "p_pia": 0.9277,
    "p_effective_benefit": 0.9841,
    "months_to_grade_resolution": 8,
    "months_to_benefit_resolution": 3,
    "benefit_distribution": {
        "prevencion_promocion": 0.0369,
        "teleasistencia": 0.2468,
        "ayuda_domicilio": 0.1682,
        "centro_dia_noche": 0.0519,
        "atencion_residencial": 0.0868,
        "pev_servicio": 0.1048,
        "cuidados_familiares": 0.2993,
        "asistencia_personal": 0.0052,
    },
}
