"""Figuras y resumen estadístico del dataset 4.8 (LHS × réplicas, v1.5).

No inventa métricas: lee mlp_dataset.csv, dataset_splits.csv y el diseño 4.7.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "outputs" / "datasets"
FIG = Path(r"C:\Users\kike_\Desktop\TFM\tema\figuras")
OUT_JSON = DATA / "dataset_48_summary.json"

TEAL = "#2F6F6B"
STEEL = "#5B7C99"
SAND = "#C4A574"
CHARCOAL = "#2C3338"
GRID = "#D5DDE3"

SPLIT_COLORS = {
    "train": TEAL,
    "validation": STEEL,
    "test": SAND,
    "extrapolation": "#8C5A3C",
}
ESTRATO_COLORS = {
    "recorte": SAND,
    "entorno_2024": TEAL,
    "expansion": STEEL,
}


def load_joined() -> pd.DataFrame:
    mlp = pd.read_csv(DATA / "mlp_dataset.csv")
    splits = pd.read_csv(DATA / "dataset_splits.csv")
    design = pd.read_csv(DATA / "lhs_scenario_design.csv")
    df = mlp.merge(splits[["scenario_id", "split"]], on="scenario_id", how="left")
    labels = design[
        [
            "scenario_id",
            "estrato_capacidad",
            "estrato_grado_III",
            "escenario_historico",
            "escenario_contrafactual",
        ]
    ]
    df = df.merge(labels, on="scenario_id", how="left")
    if df["split"].isna().any():
        raise ValueError("Faltan splits para algún scenario_id.")
    return df


def summarize(df: pd.DataFrame) -> dict:
    y = df["target_wellbeing_proxy"]
    std_y = df["std_wellbeing_proxy"]
    split_counts = df["split"].value_counts().to_dict()
    regime_counts = df["regime"].value_counts().to_dict()
    summary = {
        "n_rows": int(len(df)),
        "n_replicas": int(df["n_replicas"].iloc[0]),
        "n_abm_runs": int(len(df) * df["n_replicas"].iloc[0]),
        "wellbeing_min": float(y.min()),
        "wellbeing_max": float(y.max()),
        "wellbeing_mean": float(y.mean()),
        "wellbeing_std_between": float(y.std(ddof=1)),
        "std_intra_mean": float(std_y.mean()),
        "std_intra_max": float(std_y.max()),
        "std_intra_min": float(std_y.min()),
        "coverage_n_mean": float(df["target_rate_prestacion_efectiva"].mean()),
        "wait_n_mean": float(df["target_rate_lista_espera"].mean()),
        "sin_grado_n_mean": float(df["target_rate_sin_grado"].mean()),
        "prestacion_stock_mean": float(df["target_final_prestacion_efectiva"].mean()),
        "lista_stock_mean": float(df["target_final_lista_espera"].mean()),
        "factor_min": float(df["factor_capacidad"].min()),
        "factor_max": float(df["factor_capacidad"].max()),
        "split_counts": {k: int(v) for k, v in split_counts.items()},
        "regime_counts": {k: int(v) for k, v in regime_counts.items()},
        "corr_factor_wellbeing": float(
            df["factor_capacidad"].corr(df["target_wellbeing_proxy"])
        ),
        "corr_factor_lista": float(
            df["factor_capacidad"].corr(df["target_final_lista_espera"])
        ),
    }
    by_split = (
        df.groupby("split")["target_wellbeing_proxy"]
        .agg(["count", "mean", "min", "max"])
        .round(3)
    )
    summary["by_split"] = {
        idx: {
            "n": int(row["count"]),
            "mean": float(row["mean"]),
            "min": float(row["min"]),
            "max": float(row["max"]),
        }
        for idx, row in by_split.iterrows()
    }
    if "estrato_capacidad" in df.columns:
        by_cap = (
            df.groupby("estrato_capacidad")["target_wellbeing_proxy"]
            .agg(["count", "mean"])
            .round(3)
        )
        summary["by_capacidad"] = {
            idx: {"n": int(row["count"]), "mean": float(row["mean"])}
            for idx, row in by_cap.iterrows()
        }
    return summary


def _style(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=CHARCOAL)
    ax.xaxis.label.set_color(CHARCOAL)
    ax.yaxis.label.set_color(CHARCOAL)
    ax.title.set_color(CHARCOAL)
    ax.grid(True, axis="y", color=GRID, linewidth=0.8, alpha=0.9)


def fig_hist_and_splits(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.4))
    ax = axes[0]
    bins = 12
    for split, color in SPLIT_COLORS.items():
        subset = df.loc[df["split"] == split, "target_wellbeing_proxy"]
        if subset.empty:
            continue
        ax.hist(
            subset,
            bins=bins,
            range=(df["target_wellbeing_proxy"].min(), df["target_wellbeing_proxy"].max()),
            color=color,
            alpha=0.72,
            label=split,
            edgecolor="white",
            linewidth=0.6,
        )
    ax.set_title("Distribución del target (media de 10 réplicas)")
    ax.set_xlabel("wellbeing_proxy (0–10)")
    ax.set_ylabel("Número de escenarios")
    ax.legend(frameon=False, fontsize=8)
    _style(ax)

    ax = axes[1]
    order = ["train", "validation", "test", "extrapolation"]
    counts = [int((df["split"] == s).sum()) for s in order]
    colors = [SPLIT_COLORS[s] for s in order]
    bars = ax.bar(order, counts, color=colors, width=0.72, edgecolor="white")
    ax.set_title("Partición por scenario_id (sin fuga)")
    ax.set_ylabel("Número de escenarios")
    ax.set_ylim(0, max(counts) * 1.18)
    for bar, n in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.2,
            str(n),
            ha="center",
            va="bottom",
            color=CHARCOAL,
            fontsize=10,
        )
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(["Train", "Validación", "Test", "Extrapolación"])
    _style(ax)
    fig.tight_layout()
    out = FIG / "grafico24-dataset-target-particiones.png"
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", out)


def fig_factor_vs_target(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.4))
    ax = axes[0]
    interp = df[df["regime"] == "interpolation"]
    extra = df[df["regime"] == "extrapolation"]
    ax.scatter(
        interp["factor_capacidad"],
        interp["target_wellbeing_proxy"],
        c=TEAL,
        s=32,
        alpha=0.85,
        label="Interpolación (n=100)",
        zorder=3,
    )
    ax.scatter(
        extra["factor_capacidad"],
        extra["target_wellbeing_proxy"],
        c=SAND,
        s=48,
        marker="D",
        alpha=0.9,
        label="Extrapolación (n=15)",
        zorder=4,
    )
    ax.axvline(1.0, color=CHARCOAL, linestyle="--", linewidth=1, alpha=0.7)
    ax.set_title("Factor de capacidad y proxy de bienestar")
    ax.set_xlabel("factor_capacidad")
    ax.set_ylabel("target_wellbeing_proxy")
    ax.legend(frameon=False, fontsize=8)
    _style(ax)

    ax = axes[1]
    ax.scatter(
        interp["factor_capacidad"],
        interp["target_final_lista_espera"],
        c=TEAL,
        s=32,
        alpha=0.85,
        label="Interpolación",
        zorder=3,
    )
    ax.scatter(
        extra["factor_capacidad"],
        extra["target_final_lista_espera"],
        c=SAND,
        s=48,
        marker="D",
        alpha=0.9,
        label="Extrapolación",
        zorder=4,
    )
    ax.axvline(1.0, color=CHARCOAL, linestyle="--", linewidth=1, alpha=0.7)
    ax.set_title("Factor de capacidad y stock en lista de espera")
    ax.set_xlabel("factor_capacidad")
    ax.set_ylabel("Agentes en lista (media de réplicas)")
    ax.legend(frameon=False, fontsize=8)
    _style(ax)
    fig.tight_layout()
    out = FIG / "grafico25-factor-capacidad-salidas.png"
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", out)


def fig_suelo_error(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.4))
    ax = axes[0]
    ax.hist(
        df["std_wellbeing_proxy"],
        bins=14,
        color=STEEL,
        edgecolor="white",
        linewidth=0.7,
    )
    ax.axvline(
        df["std_wellbeing_proxy"].mean(),
        color=SAND,
        linestyle="--",
        linewidth=1.4,
        label=f"Media intra-escenario = {df['std_wellbeing_proxy'].mean():.3f}",
    )
    ax.set_title("Suelo de error (desv. intra-escenario del proxy)")
    ax.set_xlabel("std_wellbeing_proxy")
    ax.set_ylabel("Número de escenarios")
    ax.legend(frameon=False, fontsize=8)
    _style(ax)

    ax = axes[1]
    order = ["recorte", "entorno_2024", "expansion"]
    present = [e for e in order if e in set(df["estrato_capacidad"].dropna())]
    means = [
        df.loc[df["estrato_capacidad"] == e, "target_wellbeing_proxy"].mean()
        for e in present
    ]
    colors = [ESTRATO_COLORS[e] for e in present]
    labels = {
        "recorte": "Recorte",
        "entorno_2024": "Entorno 2024",
        "expansion": "Expansión",
    }
    bars = ax.bar(
        [labels[e] for e in present],
        means,
        color=colors,
        width=0.62,
        edgecolor="white",
    )
    ax.set_title("Proxy medio según estrato de oferta (4.7)")
    ax.set_ylabel("target_wellbeing_proxy (media)")
    ymin = min(means) - 0.15
    ymax = max(means) + 0.15
    ax.set_ylim(ymin, ymax)
    for bar, val in zip(bars, means):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{val:.2f}",
            ha="center",
            va="bottom",
            color=CHARCOAL,
            fontsize=10,
        )
    _style(ax)
    fig.tight_layout()
    out = FIG / "grafico26-suelo-error-estratos.png"
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", out)


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    df = load_joined()
    summary = summarize(df)
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    fig_hist_and_splits(df)
    fig_factor_vs_target(df)
    fig_suelo_error(df)
    print("rows", len(df), "wrote", OUT_JSON)


if __name__ == "__main__":
    main()
