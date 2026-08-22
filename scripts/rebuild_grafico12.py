"""Rebuild grafico12 snapshot table from the v1.5 base CSV."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "simulation_outputs" / "base_simulation.csv"
OUT = Path(r"C:\Users\kike_\Desktop\TFM\tema\figuras\grafico12-tabla-resumen-estados-saad.png")
TEX = Path(r"C:\Users\kike_\Desktop\TFM\tema\figuras\grafico12-tabla-resumen-estados-saad.tex")

COLS = [
    "month",
    "no_solicitantes",
    "pendiente_grado",
    "sin_grado",
    "con_derecho",
    "con_pia",
    "prestacion_efectiva",
    "lista_espera",
]
LABELS = [
    "Mes",
    "No sol.",
    "Pend. grado",
    "Sin grado",
    "Con derecho",
    "Con PIA",
    "Prestación",
    "Lista",
]
PICK = [0, 10, 20, 25, 30, 40, 50, 60]


def main() -> None:
    df = pd.read_csv(CSV)
    sub = df.loc[df["month"].isin(PICK), COLS]
    print(sub.to_string(index=False))
    cell = [[str(int(r[c])) for c in COLS] for _, r in sub.iterrows()]
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.axis("off")
    ax.set_title("Resumen de estados SAAD (v1.5, seed=42, N=6.387)", fontsize=12, pad=8)
    table = ax.table(cellText=cell, colLabels=LABELS, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.15, 1.35)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    plt.close()
    rows = "\n".join(
        "    "
        + " & ".join(str(int(r[c])) for c in COLS)
        + r" \\"
        for _, r in sub.iterrows()
    )
    TEX.write_text(
        "% Tabla resumen estados SAAD (seed=42) — companion LaTeX\n"
        "\\begin{table}[htbp]\n"
        "  \\centering\n"
        "  \\caption{Resumen de estados administrativos del SAAD "
        "(simulación base v1.5, seed = 42, $N=6387$).}\n"
        "  \\label{tab:estados-saad-v15}\n"
        "  \\begin{tabular}{rrrrrrrr}\n"
        "    \\toprule\n"
        "    Mes & No solicit. & Pendiente grado & Sin grado & Con derecho "
        "& Con PIA & Prestación efectiva & Lista espera \\\\\n"
        "    \\midrule\n"
        f"{rows}\n"
        "    \\bottomrule\n"
        "  \\end{tabular}\n"
        "\\end{table}\n",
        encoding="utf-8",
    )
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
