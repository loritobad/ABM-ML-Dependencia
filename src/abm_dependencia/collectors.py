"""Funciones auxiliares para recolectar salidas agregadas del modelo."""


def _iter_agents(model):
    """Devuelve un iterador robusto sobre agentes del modelo."""
    if hasattr(model, "agents"):
        return iter(model.agents)
    if hasattr(model, "schedule") and hasattr(model.schedule, "agents"):
        return iter(model.schedule.agents)
    return iter(())


def count_vulnerables(model) -> int:
    """Cuenta agentes vulnerables."""
    return sum(1 for agent in _iter_agents(model) if getattr(agent, "is_vulnerable", False))


def count_status(model, status: str) -> int:
    """Cuenta agentes en un estado administrativo."""
    return sum(1 for agent in _iter_agents(model) if getattr(agent, "saad_status", None) == status)


def count_grade(model, grade: str) -> int:
    """Cuenta agentes con un grado de dependencia concreto."""
    return sum(1 for agent in _iter_agents(model) if getattr(agent, "dependency_grade", None) == grade)


def count_benefit_type(model, benefit_type: str) -> int:
    """Cuenta agentes con un tipo de prestación concreto."""
    return sum(1 for agent in _iter_agents(model) if getattr(agent, "benefit_type", None) == benefit_type)
