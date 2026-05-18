"""Genera datasets sintéticos para modelos sustitutos MLP y GNN."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    from .analysis.metrics import calculate_simulation_metrics
    from .datasets.graph_exporter import build_graph_tables, save_graph_dataset
    from .datasets.mlp_exporter import TARGET_COLUMNS, build_mlp_row, save_mlp_dataset
    from .datasets.scenario_sampler import flatten_parameters, sample_scenario
    from .datasets.split_generator import generate_splits
    from .model.model import DependenceABM
    from .model.parameters import get_base_parameters
except ImportError:
    from analysis.metrics import calculate_simulation_metrics
    from datasets.graph_exporter import build_graph_tables, save_graph_dataset
    from datasets.mlp_exporter import TARGET_COLUMNS, build_mlp_row, save_mlp_dataset
    from datasets.scenario_sampler import flatten_parameters, sample_scenario
    from datasets.split_generator import generate_splits
    from model.model import DependenceABM
    from model.parameters import get_base_parameters


N_SIMULATIONS = 100
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = PROJECT_ROOT / "outputs" / "datasets"
GRAPHS_DIR = DATASETS_DIR / "graphs"


def run_experiments(
    n_simulations: int = N_SIMULATIONS,
    random_seed: int = 42,
    initial_agents: int | None = None,
) -> None:
    """Ejecuta escenarios ABM y exporta representaciones tabular y relacional."""
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)

    base_parameters = get_base_parameters()
    if initial_agents is not None:
        base_parameters["initial_vulnerable_population"] = initial_agents

    parameter_rows = []
    mlp_rows = []
    node_rows = []
    edge_rows = []
    graph_target_rows = []
    simulation_ids = list(range(1, n_simulations + 1))

    for simulation_id in simulation_ids:
        scenario_seed = random_seed + simulation_id
        parameters = sample_scenario(base_parameters, random_seed=scenario_seed)

        model = DependenceABM(parameters=parameters, seed=scenario_seed)
        df = model.run()
        metrics = calculate_simulation_metrics(df)

        parameter_rows.append(flatten_parameters(simulation_id, parameters))
        mlp_rows.append(build_mlp_row(simulation_id, parameters, metrics))

        nodes, edges, graph_target = build_graph_tables(simulation_id, df, metrics)
        node_rows.extend(nodes)
        edge_rows.extend(edges)
        graph_target_rows.append(graph_target)

        print(f"Simulacion completada: {simulation_id}/{n_simulations}")

    simulation_parameters = pd.DataFrame(parameter_rows)
    mlp_dataset = pd.DataFrame(mlp_rows)
    nodes = pd.DataFrame(node_rows)
    edges = pd.DataFrame(edge_rows)
    graph_targets = pd.DataFrame(graph_target_rows)
    splits = pd.DataFrame(generate_splits(simulation_ids, random_seed=random_seed))

    _validate_outputs(
        n_simulations=n_simulations,
        mlp_dataset=mlp_dataset,
        nodes=nodes,
        edges=edges,
        graph_targets=graph_targets,
        splits=splits,
    )

    simulation_parameters.to_csv(DATASETS_DIR / "simulation_parameters.csv", index=False)
    save_mlp_dataset(mlp_rows, DATASETS_DIR / "mlp_dataset.csv")
    save_graph_dataset(node_rows, edge_rows, graph_target_rows, GRAPHS_DIR)
    splits.to_csv(DATASETS_DIR / "dataset_splits.csv", index=False)

    print("\nResumen de generación de datasets")
    print(f"Simulaciones ejecutadas: {n_simulations}")
    print(f"Dataset MLP: {DATASETS_DIR / 'mlp_dataset.csv'}")
    print(f"Filas MLP: {len(mlp_dataset)}")
    print(f"Nodos generados: {len(nodes)}")
    print(f"Aristas generadas: {len(edges)}")
    print(f"Graph targets: {GRAPHS_DIR / 'graph_targets.csv'}")
    print(f"Splits: {DATASETS_DIR / 'dataset_splits.csv'}")


def _validate_outputs(
    n_simulations: int,
    mlp_dataset: pd.DataFrame,
    nodes: pd.DataFrame,
    edges: pd.DataFrame,
    graph_targets: pd.DataFrame,
    splits: pd.DataFrame,
) -> None:
    """Valida consistencia básica entre datasets MLP y GNN."""
    if len(mlp_dataset) != n_simulations:
        raise ValueError("mlp_dataset.csv debe tener N_SIMULATIONS filas.")
    if len(graph_targets) != n_simulations:
        raise ValueError("graph_targets.csv debe tener N_SIMULATIONS filas.")

    mlp_ids = set(mlp_dataset["simulation_id"])
    target_ids = set(graph_targets["simulation_id"])
    node_ids = set(nodes["simulation_id"])
    edge_ids = set(edges["simulation_id"])
    split_ids = set(splits["simulation_id"])

    if mlp_ids != target_ids:
        raise ValueError("Los simulation_id de MLP y graph_targets no coinciden.")
    if not node_ids.issubset(target_ids):
        raise ValueError("nodes.csv contiene simulation_id ausentes en graph_targets.")
    if not edge_ids.issubset(target_ids):
        raise ValueError("edges.csv contiene simulation_id ausentes en graph_targets.")
    if split_ids != target_ids:
        raise ValueError("dataset_splits.csv no contiene todos los simulation_id.")

    mlp_targets = mlp_dataset[["simulation_id", *TARGET_COLUMNS]].sort_values(
        "simulation_id"
    )
    graph_target_values = graph_targets[
        ["simulation_id", *TARGET_COLUMNS]
    ].sort_values("simulation_id")
    if not mlp_targets.reset_index(drop=True).equals(
        graph_target_values.reset_index(drop=True)
    ):
        raise ValueError("Los targets de MLP y GNN no coinciden por simulation_id.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera datasets sintéticos ABM para MLP y GNN."
    )
    parser.add_argument("--n-simulations", type=int, default=N_SIMULATIONS)
    parser.add_argument("--random-seed", "--seed", dest="random_seed", type=int, default=42)
    parser.add_argument("--initial-agents", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_experiments(
        n_simulations=args.n_simulations,
        random_seed=args.random_seed,
        initial_agents=args.initial_agents,
    )


if __name__ == "__main__":
    main()
