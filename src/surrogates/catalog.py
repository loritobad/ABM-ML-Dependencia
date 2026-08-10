"""Catálogo de familias de surrogate alineado con la comparativa académica."""

from __future__ import annotations

SURROGATE_FAMILIES = {
    "dummy": {
        "label": "DummyRegressor (media)",
        "role": "baseline",
        "library": "sklearn.dummy.DummyRegressor",
    },
    "ridge": {
        "label": "Ridge (lineal regularizado)",
        "role": "baseline",
        "library": "sklearn.linear_model.Ridge",
    },
    "cart": {
        "label": "CART (árbol individual)",
        "role": "family",
        "library": "sklearn.tree.DecisionTreeRegressor",
    },
    "random_forest": {
        "label": "Random Forest",
        "role": "family",
        "library": "sklearn.ensemble.RandomForestRegressor",
    },
    "gradient_boosting": {
        "label": "Gradient Boosting / XGBoost",
        "role": "family",
        "library": "sklearn.ensemble.GradientBoostingRegressor | xgboost",
    },
    "mlp": {
        "label": "MLP (perceptrón multicapa)",
        "role": "family",
        "library": "sklearn.neural_network.MLPRegressor | torch",
    },
}


def list_families() -> list[str]:
    """Devuelve los identificadores de familia/baseline."""
    return list(SURROGATE_FAMILIES.keys())
