"""Modelo ABM simplificado para el sistema de atención a la dependencia."""

from .model import DependenceABM, DependenciaABM
from .parameters import DEFAULT_PARAMETERS, get_base_parameters

__all__ = ["DEFAULT_PARAMETERS", "DependenceABM", "DependenciaABM", "get_base_parameters"]
