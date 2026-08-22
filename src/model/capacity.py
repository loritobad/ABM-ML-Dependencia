"""Cupos SAAD v1.5: 3 colas nacionales + techo de atendidas.

Escala: stock_IMSERSO * N / solicitudes (31/12/2024).
No usa el 8,70 % de limbo ni el 91,30 % de cobertura como input.
"""

from __future__ import annotations

from typing import Mapping

# IMSERSO, informe mensual 31/12/2024 (estsisaad_evolucion_20241231.pdf)
SOLICITUDES_SAAD_2024 = 2_165_648
CON_DERECHO_SAAD_2024 = 1_636_757
PIA_SAAD_2024 = 1_518_424
PRESTACION_EFECTIVA_SAAD_2024 = 1_494_311

PRESTACIONES_SAAD_2024 = {
    "prevencion": 78_342,
    "teleasistencia": 524_561,
    "ayuda_domicilio": 357_497,
    "centro_dia_noche": 110_349,
    "atencion_residencial": 184_545,
    "pev": 222_787,
    "cuidados_familiares": 636_030,
    "asistencia_personal": 11_034,
}

QUEUE_RESIDENCIAL = "residencial"
QUEUE_DIA = "dia"
QUEUE_RESTO = "resto"
QUEUE_KEYS = (QUEUE_RESIDENCIAL, QUEUE_DIA, QUEUE_RESTO)

BENEFIT_TO_QUEUE = {
    "atencion_residencial": QUEUE_RESIDENCIAL,
    "centro_dia_noche": QUEUE_DIA,
    "prevencion": QUEUE_RESTO,
    "teleasistencia": QUEUE_RESTO,
    "ayuda_domicilio": QUEUE_RESTO,
    "pev": QUEUE_RESTO,
    "cuidados_familiares": QUEUE_RESTO,
    "asistencia_personal": QUEUE_RESTO,
}

STOCK_RESIDENCIAL = PRESTACIONES_SAAD_2024["atencion_residencial"]
STOCK_DIA = PRESTACIONES_SAAD_2024["centro_dia_noche"]
STOCK_RESTO = sum(PRESTACIONES_SAAD_2024.values()) - STOCK_RESIDENCIAL - STOCK_DIA


def scale_stock(stock: int, n_agents: int, denominator: int = SOLICITUDES_SAAD_2024) -> int:
    """Entero no negativo; redondeo al más cercano."""
    if denominator <= 0 or n_agents <= 0:
        return 0
    return max(0, int(round(stock * n_agents / denominator)))


def cupos_from_n(n_agents: int) -> dict[str, int]:
    """Cupos simulados para una población N (misma regla de escala)."""
    n = int(n_agents)
    return {
        "cupo_residencial": scale_stock(STOCK_RESIDENCIAL, n),
        "cupo_dia": scale_stock(STOCK_DIA, n),
        "cupo_resto": scale_stock(STOCK_RESTO, n),
        "cupo_atendidas": scale_stock(PRESTACION_EFECTIVA_SAAD_2024, n),
    }


def queue_for_benefit(benefit: str) -> str:
    try:
        return BENEFIT_TO_QUEUE[benefit]
    except KeyError as exc:
        raise KeyError(f"Prestación desconocida para cola: {benefit}") from exc


def occupancy_ok(ocupados: Mapping[str, int], cupos: Mapping[str, int], queue: str) -> bool:
    """Hueco en la cola y en el techo nacional de atendidas."""
    if ocupados.get(queue, 0) >= cupos[f"cupo_{queue}"]:
        return False
    atendidas = sum(int(ocupados.get(k, 0)) for k in QUEUE_KEYS)
    if atendidas >= cupos["cupo_atendidas"]:
        return False
    return True
