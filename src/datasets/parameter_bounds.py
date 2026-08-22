"""Rangos paramétricos LHS alineados al mapeo operativo v1.5 (Tablas 6–13).

Los valores centrales coinciden con DEFAULT_PARAMETERS. La palanca de oferta
es ``factor_capacidad`` (multiplica los cupos IMSERSO), no el dado 98,41 %.
"""

from __future__ import annotations

from copy import deepcopy

try:
    from ..model.parameters import BENEFIT_KEYS, GRADE_KEYS, get_base_parameters
except ImportError:  # pragma: no cover
    from model.parameters import BENEFIT_KEYS, GRADE_KEYS, get_base_parameters

# Reexport for samplers
__all__ = [
    "LHS_PARAMETER_BOUNDS",
    "LHS_EXTRAPOLATION_BOUNDS",
    "CAPACITY_KEYS",
    "BENEFIT_KEYS",
    "GRADE_KEYS",
    "base_with_bounds",
]

CAPACITY_KEYS = frozenset({"factor_capacidad"})

# Variables continuas muestreables por LHS (núcleo SAAD v1.5)
LHS_PARAMETER_BOUNDS: dict[str, tuple[float, float]] = {
    "prob_solicitud_mensual": (0.020, 0.050),
    "prob_solicitud_si_vulnerable": (0.035, 0.080),
    "prob_resolucion_grado_mensual": (0.200, 0.500),
    "prob_con_derecho": (0.7935, 0.8060),
    "prob_pia_mensual": (0.250, 0.550),
    "factor_capacidad": (0.80, 1.20),
    "meses_min_pendiente_grado": (5.0, 12.0),
    "meses_min_tramite_prestacion": (1.0, 6.0),
}

LHS_EXTRAPOLATION_BOUNDS: dict[str, tuple[float, float]] = {
    "prob_solicitud_mensual": (0.015, 0.060),
    "prob_solicitud_si_vulnerable": (0.025, 0.100),
    "prob_resolucion_grado_mensual": (0.150, 0.600),
    "prob_con_derecho": (0.750, 0.850),
    "prob_pia_mensual": (0.150, 0.650),
    "factor_capacidad": (0.55, 1.45),
    "meses_min_pendiente_grado": (3.0, 14.0),
    "meses_min_tramite_prestacion": (0.0, 8.0),
}


def base_with_bounds() -> dict:
    """Devuelve parámetros base junto con metadatos de rangos LHS."""
    return {
        "base": get_base_parameters(),
        "interpolation_bounds": deepcopy(LHS_PARAMETER_BOUNDS),
        "extrapolation_bounds": deepcopy(LHS_EXTRAPOLATION_BOUNDS),
    }
