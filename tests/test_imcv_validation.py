"""Pruebas de la puerta de validación IMCV."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from analysis.imcv_validation import validate_abm_against_imcv  # noqa: E402


def test_imcv_gate_computes_mae_and_decision() -> None:
    reference = pd.DataFrame(
        {
            "territory": ["España", "Madrid"],
            "year": [2024, 2024],
            "imcv_value": [7.3, 7.5],
        }
    )
    report = validate_abm_against_imcv(
        {"España": 7.2, "Madrid": 7.4},
        reference=reference,
        year=2024,
        mae_threshold=0.5,
    )
    assert report["n_territories"] == 2
    assert report["mae"] < 0.5
    assert report["gate_decision"] == "pasa"
    assert "pearson" in report
