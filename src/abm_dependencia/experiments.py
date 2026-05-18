"""Utilidades para ejecutar experimentos del ABM."""

from __future__ import annotations

from abm_dependencia.model import DependencyABM


def run_experiment(n_agents: int = 1000, n_months: int = 60, seed: int | None = None, params: dict | None = None):
    """Ejecuta un experimento y devuelve sus resultados agregados."""
    model = DependencyABM(n_agents=n_agents, params=params, seed=seed)
    model.run_model(n_months=n_months)
    return model.get_results()
