"""Rangos paramétricos defendibles para el muestreo LHS (Tablas 6–14 del TFM).

Los valores centrales coinciden con DEFAULT_PARAMETERS. Los mínimos/máximos
representan rangos plausibles derivados de la parametrización empírica del
capítulo 4; pueden ajustarse sin cambiar la API del sampler.
"""

from __future__ import annotations

from copy import deepcopy

from ..model.parameters import get_base_parameters

# (min, max) para variables continuas muestreables por LHS
LHS_PARAMETER_BOUNDS: dict[str, tuple[float, float]] = {
    "prob_solicitud_mensual": (0.020, 0.055),
    "prob_reconocimiento_grado": (0.100, 0.280),
    "prob_con_derecho": (0.650, 0.900),
    "prob_pia": (0.120, 0.350),
    "prob_prestacion_efectiva": (0.450, 0.850),
}

# Extremos usados para el hold-out de extrapolación (fuera o en el borde)
LHS_EXTRAPOLATION_BOUNDS: dict[str, tuple[float, float]] = {
    "prob_solicitud_mensual": (0.015, 0.065),
    "prob_reconocimiento_grado": (0.080, 0.320),
    "prob_con_derecho": (0.550, 0.950),
    "prob_pia": (0.080, 0.420),
    "prob_prestacion_efectiva": (0.350, 0.920),
}

GRADE_KEYS = ("I", "II", "III")
BENEFIT_KEYS = (
    "teleasistencia",
    "ayuda_domicilio",
    "atencion_residencial",
    "cuidados_familiares",
)


def base_with_bounds() -> dict:
    """Devuelve parámetros base junto con metadatos de rangos LHS."""
    return {
        "base": get_base_parameters(),
        "interpolation_bounds": deepcopy(LHS_PARAMETER_BOUNDS),
        "extrapolation_bounds": deepcopy(LHS_EXTRAPOLATION_BOUNDS),
    }
