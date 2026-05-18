"""Compatibilidad con la ruta antigua del modelo."""

from __future__ import annotations

from model.model import DependenciaABM


class DependencyABM(DependenciaABM):
    """Alias compatible con la primera versión del proyecto."""

    def __init__(self, n_agents: int | None = None, params: dict | None = None, seed=None):
        params = dict(params or {})
        if n_agents is not None:
            params["initial_vulnerable_agents"] = n_agents
        super().__init__(params=params, seed=seed)


__all__ = ["DependenciaABM", "DependencyABM"]
