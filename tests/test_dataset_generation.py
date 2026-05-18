"""Pruebas básicas de generación de datasets sintéticos."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from analysis.metrics import calculate_simulation_metrics  # noqa: E402
from datasets.graph_exporter import build_graph_tables  # noqa: E402
from datasets.mlp_exporter import TARGET_COLUMNS, build_mlp_row  # noqa: E402
from datasets.scenario_sampler import sample_scenario  # noqa: E402
from datasets.split_generator import generate_splits  # noqa: E402
from model.model import DependenceABM  # noqa: E402
from model.parameters import get_base_parameters  # noqa: E402


def test_mlp_and_graph_exports_share_simulation_id_and_targets() -> None:
    parameters = sample_scenario(get_base_parameters(), random_seed=7)
    parameters["initial_vulnerable_population"] = 50
    parameters["simulation_months"] = 2

    model = DependenceABM(parameters=parameters, seed=7)
    results = model.run()
    metrics = calculate_simulation_metrics(results)

    mlp_row = build_mlp_row(1, parameters, metrics)
    nodes, edges, graph_targets = build_graph_tables(1, results, metrics)

    assert mlp_row["simulation_id"] == graph_targets["simulation_id"]
    assert all(mlp_row[key] == graph_targets[key] for key in TARGET_COLUMNS)
    assert len(nodes) == 16
    assert len(edges) == 15


def test_splits_are_generated_by_simulation_id() -> None:
    splits = generate_splits(list(range(1, 11)), random_seed=42)

    simulation_ids = [row["simulation_id"] for row in splits]
    split_values = {row["split"] for row in splits}

    assert len(simulation_ids) == len(set(simulation_ids))
    assert split_values.issubset({"train", "validation", "test"})
