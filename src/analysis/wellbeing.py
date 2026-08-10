"""Proxy agregado de bienestar alineable con el IMCV.

El ABM no dispone de microdatos de bienestar subjetivo. Este módulo define un
indicador sintético a escala 0-10 a partir de salidas agregadas del SAAD, para:

1. Validación empírica externa frente al IMCV (puerta metodológica).
2. Target principal de los modelos sustitutos (fidelidad al ABM).

La fórmula es deliberadamente simple, documentada y revisable. No sustituye al
IMCV observado; solo produce un proxy comparable en magnitud.
"""

from __future__ import annotations

from typing import Mapping


DEFAULT_BASELINE = 7.0
DEFAULT_WEIGHT_COVERAGE = 1.5
DEFAULT_WEIGHT_WAIT = 2.0
DEFAULT_WEIGHT_NO_GRADE = 0.8
DEFAULT_WEIGHT_GRADE_III = 0.5


def estimate_wellbeing_proxy(
    metrics: Mapping[str, float],
    *,
    baseline: float = DEFAULT_BASELINE,
    weight_coverage: float = DEFAULT_WEIGHT_COVERAGE,
    weight_wait: float = DEFAULT_WEIGHT_WAIT,
    weight_no_grade: float = DEFAULT_WEIGHT_NO_GRADE,
    weight_grade_iii: float = DEFAULT_WEIGHT_GRADE_III,
) -> float:
    """Estima un proxy de bienestar agregado en escala aproximada 0-10.

    Componentes:
    - cobertura efectiva (prestación efectiva) → efecto positivo
    - lista de espera → efecto negativo
    - resoluciones sin grado → efecto negativo moderado
    - peso del grado III entre reconocidos → presión asistencial negativa
    """
    coverage = float(metrics.get("rate_prestacion_efectiva", 0.0))
    wait = float(metrics.get("rate_lista_espera", 0.0))
    no_grade = float(metrics.get("rate_sin_grado", 0.0))
    grade_iii = float(metrics.get("rate_grado_III", 0.0))

    proxy = (
        baseline
        + weight_coverage * coverage
        - weight_wait * wait
        - weight_no_grade * no_grade
        - weight_grade_iii * grade_iii
    )
    return float(max(0.0, min(10.0, proxy)))


def wellbeing_components(metrics: Mapping[str, float]) -> dict[str, float]:
    """Devuelve el proxy y sus componentes para auditoría/trazabilidad."""
    return {
        "rate_prestacion_efectiva": float(metrics.get("rate_prestacion_efectiva", 0.0)),
        "rate_lista_espera": float(metrics.get("rate_lista_espera", 0.0)),
        "rate_sin_grado": float(metrics.get("rate_sin_grado", 0.0)),
        "rate_grado_III": float(metrics.get("rate_grado_III", 0.0)),
        "wellbeing_proxy": estimate_wellbeing_proxy(metrics),
    }
