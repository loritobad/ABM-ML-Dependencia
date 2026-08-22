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


def plot_ocupacion_colas(df: pd.DataFrame, output_path: str | Path) -> None:
    """Ocupación mensual de las tres colas v1.5 frente a su cupo."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    series = (
        ("ocupados_residencial", "Residencial"),
        ("ocupados_dia", "Día/noche"),
        ("ocupados_resto", "Resto"),
    )
    for col, label in series:
        ax.plot(df["month"], df[col], label=label)
    last = df.iloc[-1]
    ax.axhline(int(last["cupo_residencial"]), linestyle="--", alpha=0.6, color="C0")
    ax.axhline(int(last["cupo_dia"]), linestyle="--", alpha=0.6, color="C1")
    ax.axhline(int(last["cupo_resto"]), linestyle="--", alpha=0.6, color="C2")
    ax.axhline(int(last["cupo_atendidas"]), linestyle=":", alpha=0.8, color="black", label="Techo atendidas")
    ax.set_title("Ocupación de colas SAAD (v1.5) frente a cupos")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Agentes ocupando plaza")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_puerta_saad(
    report: dict,
    ocupados: dict[str, int],
    cupos: dict[str, int],
    output_path: str | Path,
) -> None:
    """Barras: cobertura/limbo ABM vs IMSERSO y ocupación final de las 3 colas."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))

    labels = ["Cobertura", "Limbo"]
    observed = [row["observed_pp"] for row in report["per_indicator"]]
    simulated = [row["abm_pp"] for row in report["per_indicator"]]
    x = range(len(labels))
    width = 0.35
    axes[0].bar([i - width / 2 for i in x], observed, width, label="IMSERSO 31/12/2024")
    axes[0].bar([i + width / 2 for i in x], simulated, width, label="ABM mes 60")
    axes[0].set_xticks(list(x))
    axes[0].set_xticklabels(labels)
    axes[0].set_ylabel("Porcentaje sobre personas con derecho")
    axes[0].set_title(f"Puerta SAAD (MAE {report['mae_pp']:.2f} pp; {report['gate_decision']})")
    axes[0].legend()
    axes[0].grid(True, axis="y", alpha=0.3)

    queues = ["residencial", "dia", "resto"]
    names = ["Residencial", "Día/noche", "Resto"]
    occ = [int(ocupados[q]) for q in queues]
    cap = [int(cupos[f"cupo_{q}"]) for q in queues]
    x2 = range(len(queues))
    axes[1].bar([i - width / 2 for i in x2], cap, width, label="Cupo")
    axes[1].bar([i + width / 2 for i in x2], occ, width, label="Ocupados")
    axes[1].axhline(int(cupos["cupo_atendidas"]), linestyle=":", color="black", label="Techo atendidas")
    axes[1].set_xticks(list(x2))
    axes[1].set_xticklabels(names)
    axes[1].set_ylabel("Agentes")
    axes[1].set_title("Ocupación final vs cupo (N = 6.387)")
    axes[1].legend()
    axes[1].grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

