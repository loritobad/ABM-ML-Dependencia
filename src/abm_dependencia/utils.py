"""Funciones comunes para scripts y experimentos."""

from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """Devuelve la raíz del repositorio."""
    return Path(__file__).resolve().parents[2]


def ensure_directory(path: Path) -> Path:
    """Crea un directorio si no existe y devuelve su ruta."""
    path.mkdir(parents=True, exist_ok=True)
    return path
