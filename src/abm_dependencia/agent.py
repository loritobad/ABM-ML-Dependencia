"""Compatibilidad con la ruta antigua del agente."""

from model.agents import DependenciaAgent

ElderlyAgent = DependenciaAgent

__all__ = ["DependenciaAgent", "ElderlyAgent"]
