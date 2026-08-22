"""Pruebas de cupos SAAD v1.5 y de la puerta cobertura/limbo."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from analysis.saad_validation import decide_gate, rates_from_metrics, validate_abm_against_saad  # noqa: E402
from model.capacity import cupos_from_n, occupancy_ok, queue_for_benefit, scale_stock  # noqa: E402
from model.model import DependenciaABM  # noqa: E402
from model.parameters import normalize_parameters  # noqa: E402


def test_scale_n6387_matches_reference() -> None:
    cupos = cupos_from_n(6387)
    assert cupos["cupo_residencial"] == 544
    assert cupos["cupo_dia"] == 325
    assert cupos["cupo_resto"] == 5398
    assert cupos["cupo_atendidas"] == 4407


def test_benefit_to_queue() -> None:
    assert queue_for_benefit("atencion_residencial") == "residencial"
    assert queue_for_benefit("centro_dia_noche") == "dia"
    assert queue_for_benefit("pev") == "resto"
    assert queue_for_benefit("cuidados_familiares") == "resto"


def test_occupancy_never_exceeds_cupo() -> None:
    cupos = {"cupo_residencial": 2, "cupo_dia": 2, "cupo_resto": 10, "cupo_atendidas": 3}
    ocupados = {"residencial": 2, "dia": 0, "resto": 0}
    assert occupancy_ok(ocupados, cupos, "residencial") is False
    ocupados = {"residencial": 1, "dia": 0, "resto": 2}
    assert occupancy_ok(ocupados, cupos, "resto") is False  # techo atendidas = 3


def test_tiny_run_respects_cupos() -> None:
    model = DependenciaABM(
        parameters={
            "initial_vulnerable_population": 40,
            "simulation_months": 16,
            "cupo_residencial": 2,
            "cupo_dia": 1,
            "cupo_resto": 8,
            "cupo_atendidas": 10,
        },
        seed=3,
    )
    model.run_model(n_months=16)
    assert model.ocupados["residencial"] <= 2
    assert model.ocupados["dia"] <= 1
    assert model.ocupados["resto"] <= 8
    assert sum(model.ocupados.values()) <= 10
    assert model.ocupados["residencial"] + model.ocupados["dia"] + model.ocupados["resto"] == model._count_status(
        "prestacion_efectiva"
    )


def test_fifo_oldest_waiter_first() -> None:
    model = DependenciaABM(
        parameters={
            "initial_vulnerable_population": 6,
            "simulation_months": 1,
            "cupo_residencial": 0,
            "cupo_dia": 0,
            "cupo_resto": 1,
            "cupo_atendidas": 1,
        },
        seed=1,
    )
    agents = list(model.agents)
    for i, agent in enumerate(agents[:3]):
        agent.estado_saad = agent.LISTA_ESPERA
        agent.tipo_prestacion = "teleasistencia"
        agent.cola_recurso = "resto"
        agent.mes_entrada_lista = i
        agent.unique_id = i
    model._asignar_desde_lista()
    assigned = [a for a in agents[:3] if a.estado_saad == "prestacion_efectiva"]
    assert len(assigned) == 1
    assert assigned[0].mes_entrada_lista == 0


def test_gate_thresholds() -> None:
    assert decide_gate(4.9) == "pasa"
    assert decide_gate(5.2) == "pasa_con_reservas"
    assert decide_gate(8.0) == "no_pasa"


def test_validate_against_saad_reference() -> None:
    metrics = {
        "final_prestacion_efectiva": 4392,
        "final_lista_espera": 72,
        "final_con_derecho": 47,
        "final_con_pia": 39,
        "final_pendiente_grado": 225,
        "final_no_solicitantes": 387,
        "final_vulnerable_population": 6387,
        "mapeo_version": "v1.5",
    }
    rates = rates_from_metrics(metrics)
    assert abs(rates["cobertura_pp"] - 96.52747252747253) < 1e-6
    report = validate_abm_against_saad(metrics, year=2024)
    assert report["gate_decision"] in {"pasa", "pasa_con_reservas", "no_pasa"}
    assert report["n_indicators"] == 2


def test_base_parameters_include_cupos() -> None:
    from model.parameters import normalize_parameters

    p2 = normalize_parameters(None)
    assert p2["cupo_residencial"] == 544
    assert scale_stock(184545, 6387) == 544
