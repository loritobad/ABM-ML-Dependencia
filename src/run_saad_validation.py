"""Ejecuta la puerta de validación ABM ↔ tasas SAAD (IMSERSO/Observatorio)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .analysis.saad_validation import save_validation_report, validate_abm_against_saad
except ImportError:
    from analysis.saad_validation import save_validation_report, validate_abm_against_saad

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METRICS = PROJECT_ROOT / "outputs" / "metrics" / "base_simulation_metrics.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "metrics" / "abm_saad_validation.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validación empírica ABM vs SAAD.")
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--from-metrics", dest="from_metrics", default=str(DEFAULT_METRICS))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    metrics_path = Path(args.from_metrics)
    if not metrics_path.exists():
        raise SystemExit(f"No existe {metrics_path}. Ejecute python -m src.run_simulation")
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    report = validate_abm_against_saad(metrics, year=args.year)
    out = save_validation_report(report, args.output)
    try:
        from .analysis.plots import plot_puerta_saad
    except ImportError:
        from analysis.plots import plot_puerta_saad

    figure_path = PROJECT_ROOT / "outputs" / "figures" / "puerta_saad_cobertura_limbo.png"
    plot_puerta_saad(
        report,
        ocupados={
            "residencial": int(metrics.get("ocupados_residencial", 0)),
            "dia": int(metrics.get("ocupados_dia", 0)),
            "resto": int(metrics.get("ocupados_resto", 0)),
        },
        cupos={
            "cupo_residencial": int(metrics.get("cupo_residencial", 0)),
            "cupo_dia": int(metrics.get("cupo_dia", 0)),
            "cupo_resto": int(metrics.get("cupo_resto", 0)),
            "cupo_atendidas": int(metrics.get("cupo_atendidas", 0)),
        },
        output_path=figure_path,
    )
    print(f"Figura: {figure_path}")
    print(f"Informe: {out}")
    print(f"MAE: {report['mae_pp']:.2f} pp")
    print(f"Decisión de puerta: {report['gate_decision']}")
    for row in report["per_indicator"]:
        print(
            f"  {row['indicator']}: ABM {row['abm_pp']:.2f} vs obs {row['observed_pp']:.2f} "
            f"(|e|={row['abs_error_pp']:.2f} pp)"
        )


if __name__ == "__main__":
    main()
