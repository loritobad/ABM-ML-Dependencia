"""Paquete de modelos sustitutos (surrogates) del ABM.

Orden metodológico obligatorio:
1. Validar ABM vs tasas SAAD (`python -m src.run_saad_validation`)
2. Generar dataset LHS × réplicas (`python -m src.run_experiments`)
3. Entrenar/evaluar familias aquí

Familias previstas: DummyRegressor, Ridge, CART, RandomForest, GradientBoosting/XGBoost, MLP.
"""

from .catalog import SURROGATE_FAMILIES, list_families

__all__ = ["SURROGATE_FAMILIES", "list_families"]
