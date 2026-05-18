"""Genera gráficos descriptivos a partir de la simulación base."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "outputs" / "runs" / "base_simulation.csv"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"


def plot_lines(data: pd.DataFrame, columns: list[str], title: str, output_path: Path) -> None:
    """Genera un gráfico de líneas para un conjunto de columnas."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for column in columns:
        ax.plot(data["month"], data[column], label=column)
    ax.set_title(title)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Numero de agentes")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main() -> None:
    """Lee el CSV base y guarda los gráficos principales."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"No existe {INPUT_PATH}. Ejecuta primero: python scripts/run_base_simulation.py"
        )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(INPUT_PATH)

    plot_lines(
        data,
        ["pendiente_grado", "con_derecho", "con_pia", "prestacion_efectiva", "lista_espera"],
        "Evolucion de estados SAAD",
        FIGURES_DIR / "evolucion_estados_saad.png",
    )
    plot_lines(
        data,
        ["grado_I", "grado_II", "grado_III"],
        "Evolucion de grados de dependencia",
        FIGURES_DIR / "evolucion_grados_dependencia.png",
    )
    plot_lines(
        data,
        ["teleasistencia", "ayuda_domicilio", "atencion_residencial", "cuidados_familiares"],
        "Evolucion de prestaciones",
        FIGURES_DIR / "evolucion_prestaciones.png",
    )

    print(f"Graficos generados en: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
