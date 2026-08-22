"""Genera datasets sintéticos para surrogates según la ruta metodológica.

Pipeline:
1. Muestreo LHS (interpolación) + hold-out de extrapolación
2. ≥R réplicas por escenario; media y desviación de targets
3. Export tabular (+ grafo opcional)
4. Splits por scenario_id (train/val/test/extrapolation)
5. Hash SHA256 del dataset principal
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean, pstdev

import pandas as pd

try:
    from .analysis.metrics import calculate_simulation_metrics
    from .datasets.graph_exporter import build_graph_tables, save_graph_dataset
    from .datasets.mlp_exporter import (
        TARGET_COLUMNS,
        VARIANCE_COLUMNS,
        build_mlp_row,
        save_mlp_dataset,
    )
    from .datasets.scenario_sampler import (
        flatten_parameters,
        sample_lhs_scenarios,
        sample_scenarios,
    )
    from .datasets.split_generator import generate_splits
    from .model.model import DependenceABM
    from .model.parameters import get_base_parameters
except ImportError:
    from analysis.metrics import calculate_simulation_metrics
    from datasets.graph_exporter import build_graph_tables, save_graph_dataset
    from datasets.mlp_exporter import (
        TARGET_COLUMNS,
        VARIANCE_COLUMNS,
        build_mlp_row,
        save_mlp_dataset,
    )
    from datasets.scenario_sampler import (
        flatten_parameters,
        sample_lhs_scenarios,
        sample_scenarios,
    )
    from datasets.split_generator import generate_splits
    from model.model import DependenceABM
    from model.parameters import get_base_parameters


N_SIMULATIONS = 100
N_EXTRAPOLATION = 15
N_REPLICAS = 10
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = PROJECT_ROOT / "outputs" / "datasets"
GRAPHS_DIR = DATASETS_DIR / "graphs"
MANIFEST_PATH = DATASETS_DIR / "dataset_manifest.json"


def _average_metrics(metrics_list: list[dict]) -> tuple[dict, dict]:
    """Promedia métricas numéricas y calcula desviaciones clave."""
    keys = metrics_list[0].keys()
    averaged: dict = {}
    for key in keys:
        values = [m[key] for m in metrics_list]
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
            averaged[key] = float(mean(values))
        else:
            averaged[key] = values[0]

    std_metrics = {
        "std_wellbeing_proxy": float(
            pstdev([m["wellbeing_proxy"] for m in metrics_list])
            if len(metrics_list) > 1
            else 0.0
        ),
        "std_rate_prestacion_efectiva": float(
            pstdev([m["rate_prestacion_efectiva"] for m in metrics_list])
            if len(metrics_list) > 1
            else 0.0
        ),
        "std_rate_lista_espera": float(
            pstdev([m["rate_lista_espera"] for m in metrics_list])
            if len(metrics_list) > 1
            else 0.0
        ),
    }
    return averaged, std_metrics


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_experiments(
    n_simulations: int = N_SIMULATIONS,
    n_extrapolation: int = N_EXTRAPOLATION,
    n_replicas: int = N_REPLICAS,
    random_seed: int = 42,
    initial_agents: int | None = None,
    method: str = "lhs",
    build_graphs: bool = True,
) -> dict:
    """Ejecuta escenarios ABM y exporta representaciones para surrogates."""
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)

    if method == "lhs":
        interpolation = sample_lhs_scenarios(
            n_simulations,
            seed=random_seed,
            regime="interpolation",
            initial_agents=initial_agents,
        )
        extrapolation = sample_lhs_scenarios(
            n_extrapolation,
            seed=random_seed + 10_000,
            regime="extrapolation",
            initial_agents=initial_agents,
        )
        # Reasignar IDs globales: interpolación 1..N, extrapolación N+1..
        for offset, scenario in enumerate(extrapolation, start=1):
            new_id = n_simulations + offset
            scenario["scenario_id"] = new_id
            scenario["simulation_id"] = new_id
        scenarios = interpolation + extrapolation
    else:
        scenarios = sample_scenarios(
            n_simulations,
            seed=random_seed,
            initial_agents=initial_agents,
            method="legacy",
        )
        for scenario in scenarios:
            scenario["regime"] = "legacy"

    parameter_rows = []
    mlp_rows = []
    node_rows = []
    edge_rows = []
    graph_target_rows = []
    simulation_ids = []
    extrapolation_ids = []

    for scenario in scenarios:
        simulation_id = int(scenario["simulation_id"])
        parameters = scenario["parameters"]
        regime = scenario.get("regime", "interpolation")
        base_seed = int(scenario["seed"])

        replica_metrics = []
        last_df = None
        for replica in range(n_replicas):
            replica_seed = base_seed * 1000 + replica
            model = DependenceABM(parameters=parameters, seed=replica_seed)
            df = model.run()
            last_df = df
            replica_metrics.append(calculate_simulation_metrics(df))

        metrics, std_metrics = _average_metrics(replica_metrics)
        parameter_rows.append(flatten_parameters(simulation_id, parameters))
        mlp_rows.append(
            build_mlp_row(
                simulation_id,
                parameters,
                metrics,
                regime=regime,
                n_replicas=n_replicas,
                std_metrics=std_metrics,
            )
        )

        if build_graphs and last_df is not None:
            nodes, edges, graph_target = build_graph_tables(simulation_id, last_df, metrics)
            node_rows.extend(nodes)
            edge_rows.extend(edges)
            graph_target_rows.append(graph_target)

        simulation_ids.append(simulation_id)
        if regime == "extrapolation":
            extrapolation_ids.append(simulation_id)

        print(
            f"Escenario {simulation_id}/{len(scenarios)} "
            f"[{regime}] replicas={n_replicas} "
            f"wellbeing={metrics['wellbeing_proxy']:.3f}"
        )

    splits = pd.DataFrame(
        generate_splits(
            simulation_ids,
            random_seed=random_seed,
            extrapolation_ids=extrapolation_ids,
        )
    )

    simulation_parameters = pd.DataFrame(parameter_rows)
    mlp_dataset = pd.DataFrame(mlp_rows)

    _validate_outputs(
        n_expected=len(scenarios),
        mlp_dataset=mlp_dataset,
        graph_targets=pd.DataFrame(graph_target_rows) if graph_target_rows else None,
        splits=splits,
        build_graphs=build_graphs,
    )

    simulation_parameters.to_csv(DATASETS_DIR / "simulation_parameters.csv", index=False)
    mlp_path = DATASETS_DIR / "mlp_dataset.csv"
    save_mlp_dataset(mlp_rows, mlp_path)
    splits.to_csv(DATASETS_DIR / "dataset_splits.csv", index=False)

    if build_graphs:
        save_graph_dataset(node_rows, edge_rows, graph_target_rows, GRAPHS_DIR)

    dataset_hash = _sha256_file(mlp_path)
    manifest = {
        "method": method,
        "n_interpolation_scenarios": n_simulations if method == "lhs" else len(scenarios),
        "n_extrapolation_scenarios": n_extrapolation if method == "lhs" else 0,
        "n_replicas": n_replicas,
        "random_seed": random_seed,
        "target_columns": TARGET_COLUMNS,
        "variance_columns": VARIANCE_COLUMNS,
        "mlp_dataset": str(mlp_path.relative_to(PROJECT_ROOT)),
        "sha256_mlp_dataset": dataset_hash,
        "splits": str((DATASETS_DIR / "dataset_splits.csv").relative_to(PROJECT_ROOT)),
        "note": (
            "Diseño experimental, no muestra poblacional. "
            "Una fila = un escenario (vector de parámetros) con targets "
            "igual a la media de n_replicas ejecuciones Mesa. "
            "1150 corridas no generan 1150 filas. "
            "std_* estima el suelo de error irreducible intra-escenario. "
            "Palanca de oferta: factor_capacidad (cupos v1.5), no el dado 98,41 %."
        ),
        "mapeo_version": "v1.5",
        "unit": "scenario",
        "n_abm_runs": n_replicas * len(scenarios),
    }
    with MANIFEST_PATH.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)

    print("\nResumen de generación de datasets")
    print(f"Escenarios: {len(scenarios)}")
    print(f"Réplicas por escenario: {n_replicas}")
    print(f"Dataset: {mlp_path}")
    print(f"SHA256: {dataset_hash}")
    print(f"Manifest: {MANIFEST_PATH}")
    return manifest


def _validate_outputs(
    n_expected: int,
    mlp_dataset: pd.DataFrame,
    graph_targets: pd.DataFrame | None,
    splits: pd.DataFrame,
    build_graphs: bool,
) -> None:
    if len(mlp_dataset) != n_expected:
        raise ValueError("mlp_dataset.csv debe tener una fila por escenario.")
    if "target_wellbeing_proxy" not in mlp_dataset.columns:
        raise ValueError("Falta target_wellbeing_proxy en el dataset.")

    mlp_ids = set(mlp_dataset["simulation_id"])
    split_ids = set(splits["simulation_id"])
    if split_ids != mlp_ids:
        raise ValueError("dataset_splits.csv no contiene todos los simulation_id.")

    if build_graphs and graph_targets is not None and not graph_targets.empty:
        target_ids = set(graph_targets["simulation_id"])
        if mlp_ids != target_ids:
            raise ValueError("Los simulation_id de MLP y graph_targets no coinciden.")
        shared = ["simulation_id", *TARGET_COLUMNS]
        mlp_targets = mlp_dataset[shared].sort_values("simulation_id")
        graph_target_values = graph_targets[shared].sort_values("simulation_id")
        if not mlp_targets.reset_index(drop=True).equals(
            graph_target_values.reset_index(drop=True)
        ):
            raise ValueError("Los targets de MLP y GNN no coinciden por simulation_id.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera datasets sintéticos ABM (LHS × réplicas) para surrogates."
    )
    parser.add_argument("--n-simulations", type=int, default=N_SIMULATIONS)
    parser.add_argument("--n-extrapolation", type=int, default=N_EXTRAPOLATION)
    parser.add_argument("--n-replicas", type=int, default=N_REPLICAS)
    parser.add_argument("--random-seed", "--seed", dest="random_seed", type=int, default=42)
    parser.add_argument("--initial-agents", type=int, default=None)
    parser.add_argument(
        "--method",
        choices=["lhs", "legacy"],
        default="lhs",
        help="lhs = ruta metodológica; legacy = perturbación ±10%.",
    )
    parser.add_argument("--no-graphs", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_experiments(
        n_simulations=args.n_simulations,
        n_extrapolation=args.n_extrapolation,
        n_replicas=args.n_replicas,
        random_seed=args.random_seed,
        initial_agents=args.initial_agents,
        method=args.method,
        build_graphs=not args.no_graphs,
    )


if __name__ == "__main__":
    main()
