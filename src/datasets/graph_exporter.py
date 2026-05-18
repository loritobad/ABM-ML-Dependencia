"""Exportación relacional de simulaciones ABM para una GNN posterior."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .mlp_exporter import build_targets


NODE_TYPES = {
    "sistema": "system",
    "vulnerables": "population",
    "no_solicitantes": "administrative_state",
    "pendiente_grado": "administrative_state",
    "sin_grado": "administrative_state",
    "con_derecho": "administrative_state",
    "con_pia": "administrative_state",
    "prestacion_efectiva": "administrative_state",
    "lista_espera": "administrative_state",
    "grado_I": "degree",
    "grado_II": "degree",
    "grado_III": "degree",
    "teleasistencia": "benefit",
    "ayuda_domicilio": "benefit",
    "atencion_residencial": "benefit",
    "cuidados_familiares": "benefit",
}

DEGREE_NODES = ["grado_I", "grado_II", "grado_III"]
BENEFIT_NODES = [
    "teleasistencia",
    "ayuda_domicilio",
    "atencion_residencial",
    "cuidados_familiares",
]

EDGE_SPECS = [
    ("sistema", "vulnerables", "hierarchy"),
    ("vulnerables", "no_solicitantes", "hierarchy"),
    ("no_solicitantes", "pendiente_grado", "administrative_transition"),
    ("pendiente_grado", "sin_grado", "administrative_transition"),
    ("pendiente_grado", "con_derecho", "administrative_transition"),
    ("con_derecho", "con_pia", "administrative_transition"),
    ("con_pia", "prestacion_efectiva", "administrative_transition"),
    ("con_pia", "lista_espera", "administrative_transition"),
    ("con_derecho", "grado_I", "degree_assignment"),
    ("con_derecho", "grado_II", "degree_assignment"),
    ("con_derecho", "grado_III", "degree_assignment"),
    ("prestacion_efectiva", "teleasistencia", "benefit_assignment"),
    ("prestacion_efectiva", "ayuda_domicilio", "benefit_assignment"),
    ("prestacion_efectiva", "atencion_residencial", "benefit_assignment"),
    ("prestacion_efectiva", "cuidados_familiares", "benefit_assignment"),
]


def build_graph_tables(
    simulation_id: int,
    df: pd.DataFrame,
    metrics: dict,
) -> tuple[list[dict], list[dict], dict]:
    """Construye tablas de nodos, aristas y targets de grafo."""
    initial_population = metrics["initial_vulnerable_population"]
    total_grados = sum(metrics[f"final_{node}"] for node in DEGREE_NODES)
    total_prestaciones = sum(metrics[f"final_{node}"] for node in BENEFIT_NODES)

    nodes = [
        _build_node(
            simulation_id=simulation_id,
            node_id=node_id,
            df=df,
            initial_population=initial_population,
            total_grados=total_grados,
            total_prestaciones=total_prestaciones,
            metrics=metrics,
        )
        for node_id in NODE_TYPES
    ]

    final_values = {node["node_id"]: node["value_final"] for node in nodes}
    edges = [
        {
            "simulation_id": simulation_id,
            "source": source,
            "target": target,
            "relation_type": relation_type,
            "weight": final_values[target],
        }
        for source, target, relation_type in EDGE_SPECS
    ]

    graph_target = {"simulation_id": simulation_id}
    graph_target.update(build_targets(metrics))
    return nodes, edges, graph_target


def save_graph_dataset(
    nodes: list[dict],
    edges: list[dict],
    graph_targets: list[dict],
    output_dir: str | Path,
) -> None:
    """Guarda nodos, aristas y targets de grafo en CSV."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(nodes).to_csv(output_dir / "nodes.csv", index=False)
    pd.DataFrame(edges).to_csv(output_dir / "edges.csv", index=False)
    pd.DataFrame(graph_targets).to_csv(output_dir / "graph_targets.csv", index=False)


def _build_node(
    simulation_id: int,
    node_id: str,
    df: pd.DataFrame,
    initial_population: int,
    total_grados: int,
    total_prestaciones: int,
    metrics: dict,
) -> dict:
    if node_id == "sistema":
        value_initial = metrics["initial_vulnerable_population"]
        value_final = metrics["final_vulnerable_population"]
        value_max = value_final
        value_min = value_initial
        value_mean = value_final
        rate_final = 1.0
    else:
        series = df[node_id]
        value_initial = float(series.iloc[0])
        value_final = float(series.iloc[-1])
        value_max = float(series.max())
        value_min = float(series.min())
        value_mean = float(series.mean())
        rate_final = _node_rate(node_id, value_final, initial_population, total_grados, total_prestaciones)

    return {
        "simulation_id": simulation_id,
        "node_id": node_id,
        "node_type": NODE_TYPES[node_id],
        "value_initial": value_initial,
        "value_final": value_final,
        "value_max": value_max,
        "value_min": value_min,
        "value_mean": value_mean,
        "rate_final": rate_final,
    }


def _node_rate(
    node_id: str,
    value_final: float,
    initial_population: int,
    total_grados: int,
    total_prestaciones: int,
) -> float:
    if node_id in DEGREE_NODES:
        return _safe_rate(value_final, total_grados)
    if node_id in BENEFIT_NODES:
        return _safe_rate(value_final, total_prestaciones)
    return _safe_rate(value_final, initial_population)


def _safe_rate(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)
