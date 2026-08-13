"""Rangos paramétricos LHS alineados al mapeo operativo v1 (Tablas 6–13).

Los valores centrales coinciden con DEFAULT_PARAMETERS del contrato v1.
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
    "BENEFIT_KEYS",
    "GRADE_KEYS",
    "base_with_bounds",
]

# Variables continuas muestreables por LHS (núcleo SAAD v1)
LHS_PARAMETER_BOUNDS: dict[str, tuple[float, float]] = {
    "prob_solicitud_mensual": (0.020, 0.050),
    "prob_solicitud_si_vulnerable": (0.035, 0.080),
    "prob_resolucion_grado_mensual": (0.200, 0.500),
    "prob_con_derecho": (0.7935, 0.8060),
    "prob_pia_mensual": (0.250, 0.550),
    "prob_prestacion_efectiva": (0.850, 0.990),
    "meses_min_pendiente_grado": (5.0, 12.0),
    "meses_min_tramite_prestacion": (1.0, 6.0),
}

LHS_EXTRAPOLATION_BOUNDS: dict[str, tuple[float, float]] = {
    "prob_solicitud_mensual": (0.015, 0.060),
    "prob_solicitud_si_vulnerable": (0.025, 0.100),
    "prob_resolucion_grado_mensual": (0.150, 0.600),
    "prob_con_derecho": (0.750, 0.850),
    "prob_pia_mensual": (0.150, 0.650),
    "prob_prestacion_efectiva": (0.700, 0.995),
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
