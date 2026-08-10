"""Batch de escenarios LHS × réplicas (punto de entrada de scripts/)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from run_experiments import run_experiments  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ejecuta el diseño de escenarios LHS y genera el dataset sintético."
    )
    parser.add_argument("--n-simulations", type=int, default=100)
    parser.add_argument("--n-extrapolation", type=int, default=15)
    parser.add_argument("--n-replicas", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--initial-agents", type=int, default=None)
    parser.add_argument("--method", choices=["lhs", "legacy"], default="lhs")
    parser.add_argument("--no-graphs", action="store_true")
    args = parser.parse_args()

    run_experiments(
        n_simulations=args.n_simulations,
        n_extrapolation=args.n_extrapolation,
        n_replicas=args.n_replicas,
        random_seed=args.seed,
        initial_agents=args.initial_agents,
        method=args.method,
        build_graphs=not args.no_graphs,
    )


if __name__ == "__main__":
    main()
