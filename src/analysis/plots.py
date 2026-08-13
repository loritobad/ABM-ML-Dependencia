"""Visualizaciones principales de la simulación base."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _plot_lines(
    df: pd.DataFrame,
    columns: list[str],
    title: str,
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    for column in columns:
        ax.plot(df["month"], df[column], label=column)

    ax.set_title(title)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Numero de agentes")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_estados_saad(df: pd.DataFrame, output_path: str | Path) -> None:
    """Genera la evolución de los estados administrativos del SAAD."""
    _plot_lines(
        df,
        [
            "no_solicitantes",
            "pendiente_grado",
            "sin_grado",
            "con_derecho",
            "con_pia",
            "prestacion_efectiva",
            "lista_espera",
        ],
        "Evolución mensual de estados administrativos del SAAD",
        output_path,
    )


def plot_grados_dependencia(df: pd.DataFrame, output_path: str | Path) -> None:
    """Genera la evolución de grados I, II y III."""
    _plot_lines(
        df,
        ["grado_I", "grado_II", "grado_III"],
        "Evolución mensual de grados de dependencia reconocidos",
        output_path,
    )


def plot_prestaciones(df: pd.DataFrame, output_path: str | Path) -> None:
    """Genera la evolución de las prestaciones finales consideradas."""
    try:
        from ..model.parameters import BENEFIT_KEYS
    except ImportError:  # pragma: no cover
        from model.parameters import BENEFIT_KEYS

    _plot_lines(
        df,
        list(BENEFIT_KEYS),
        "Evolución mensual de prestaciones asignadas (8 categorías v1)",
        output_path,
    )


def plot_estados_finales(df: pd.DataFrame, output_path: str | Path) -> None:
    """Genera la evolución de estados finales o casi finales del sistema."""
    _plot_lines(
        df,
        [
            "no_solicitantes",
            "sin_grado",
            "prestacion_efectiva",
            "lista_espera",
        ],
        "Evolución mensual de estados finales del sistema",
        output_path,
    )
