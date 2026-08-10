"""Entrenamiento de surrogates (scaffold).

No ejecutar la comparativa completa hasta que la puerta IMCV esté documentada.
Este módulo fija la interfaz y el control de variables experimentales.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .catalog import SURROGATE_FAMILIES, list_families

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GATE_REPORT = PROJECT_ROOT / "outputs" / "metrics" / "abm_imcv_validation.json"
MANIFEST = PROJECT_ROOT / "outputs" / "datasets" / "dataset_manifest.json"


def gate_allows_training(report_path: Path = GATE_REPORT) -> tuple[bool, str]:
    """Comprueba la decisión de puerta ABM↔IMCV."""
    if not report_path.exists():
        return False, (
            f"No existe {report_path}. Ejecute primero: python -m src.run_imcv_validation"
        )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    decision = report.get("gate_decision")
    if decision in {"pasa", "pasa_con_reservas"}:
        return True, decision
    return False, f"Puerta en estado '{decision}'. No entrenar surrogates."


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold de entrenamiento de surrogates.")
    parser.add_argument(
        "--family",
        choices=list_families(),
        default=None,
        help="Familia concreta; si se omite, lista el catálogo.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Permite continuar aunque la puerta no esté en pasa/pasa_con_reservas.",
    )
    args = parser.parse_args()

    allowed, detail = gate_allows_training()
    print(f"Puerta IMCV: {detail}")
    if not allowed and not args.force:
        raise SystemExit(1)

    if not MANIFEST.exists():
        raise SystemExit(
            f"Falta {MANIFEST}. Genere el dataset con: python -m src.run_experiments"
        )

    if args.family is None:
        print("Familias disponibles:")
        for key, meta in SURROGATE_FAMILIES.items():
            print(f"  - {key}: {meta['label']} [{meta['role']}]")
        print(
            "Entrenamiento completo (CV anidada, multi-semilla, Friedman) "
            "pendiente de implementación en evaluate_surrogates."
        )
        return

    print(
        f"Scaffold OK para '{args.family}'. "
        "Implementar fit/predict en el siguiente incremento del TFM."
    )


if __name__ == "__main__":
    main()
