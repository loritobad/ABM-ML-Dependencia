"""Ejecuta la puerta de validación ABM ↔ IMCV (paso 1 de la ruta metodológica)."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .analysis.imcv_validation import (
        save_validation_report,
        validate_national_proxy_from_metrics,
    )
    from .analysis.metrics import calculate_simulation_metrics
    from .model.model import DependenciaABM
    from .model.parameters import get_base_parameters
except ImportError:
    from analysis.imcv_validation import (
        save_validation_report,
        validate_national_proxy_from_metrics,
    )
    from analysis.metrics import calculate_simulation_metrics
    from model.model import DependenciaABM
    from model.parameters import get_base_parameters


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "metrics" / "abm_imcv_validation.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validación empírica ABM vs IMCV.")
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--mae-threshold", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    parameters = get_base_parameters()
    model = DependenciaABM(parameters=parameters, seed=args.seed)
    metrics = calculate_simulation_metrics(model.run())
    report = validate_national_proxy_from_metrics(
        metrics,
        year=args.year,
        mae_threshold=args.mae_threshold,
    )
    report["abm_wellbeing_proxy"] = metrics["wellbeing_proxy"]
    report["reference_file"] = "data/raw/imcv_reference.csv"
    path = save_validation_report(report, args.output)

    print(f"Proxy bienestar ABM: {metrics['wellbeing_proxy']:.4f}")
    print(f"MAE: {report['mae']:.4f} (umbral={report['mae_threshold']})")
    print(f"Pearson: {report['pearson']}")
    print(f"Spearman: {report['spearman']}")
    print(f"Decisión de puerta: {report['gate_decision']}")
    print(f"Informe: {path}")
    if report["gate_decision"] == "no_pasa":
        print(
            "ADVERTENCIA: no entrenar surrogates hasta revisar calibración "
            "o documentar reservas metodológicas."
        )


if __name__ == "__main__":
    main()
