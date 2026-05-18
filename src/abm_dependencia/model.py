"""Modelo ABM de dependencia construido con Mesa."""

from __future__ import annotations

from copy import deepcopy
from typing import Optional

import pandas as pd
from mesa import Model
from mesa.datacollection import DataCollector

from abm_dependencia.agent import ElderlyAgent
from abm_dependencia.collectors import count_benefit_type, count_grade, count_status, count_vulnerables
from abm_dependencia.parameters import BASE_PARAMETERS


class DependencyABM(Model):
    """Modelo mensual mínimo del circuito administrativo de dependencia."""

    def __init__(self, n_agents: int = 1000, params: Optional[dict] = None, seed: Optional[int] = None) -> None:
        super().__init__(rng=seed)
        self.n_agents = n_agents
        self.params = deepcopy(BASE_PARAMETERS)
        if params:
            self.params.update(params)
        self.month = 0
        self.datacollector = self._build_datacollector()
        self.create_agents()
        self.datacollector.collect(self)

    def create_agents(self) -> None:
        """Crea la población sintética inicial de personas mayores."""
        for unique_id in range(self.n_agents):
            age_group = self.random.choices(
                ["65_74", "75_84", "85_plus"],
                weights=[0.50, 0.35, 0.15],
                k=1,
            )[0]
            territory_type = self.random.choices(
                ["rural", "intermedio", "urbano"],
                weights=[0.25, 0.35, 0.40],
                k=1,
            )[0]
            ElderlyAgent(
                model=self,
                age_group=age_group,
                territory_type=territory_type,
                unique_id=unique_id,
            )

    def step(self) -> None:
        """Ejecuta un tick mensual del modelo y recolecta salidas agregadas."""
        self.agents.shuffle_do("step")
        self.month += 1
        self.datacollector.collect(self)

    def run_model(self, n_months: int = 60) -> None:
        """Ejecuta la simulación durante n meses."""
        for _ in range(n_months):
            self.step()

    def get_results(self) -> pd.DataFrame:
        """Devuelve las salidas agregadas recolectadas por mes."""
        return self.datacollector.get_model_vars_dataframe().reset_index(drop=True)

    @staticmethod
    def _build_datacollector() -> DataCollector:
        return DataCollector(
            model_reporters={
                "month": lambda model: model.month,
                "vulnerables": count_vulnerables,
                "no_solicitantes": lambda model: count_status(model, "no_solicitante"),
                "pendiente_grado": lambda model: count_status(model, "pendiente_grado"),
                "sin_grado": lambda model: count_status(model, "sin_grado"),
                "con_derecho": lambda model: count_status(model, "con_derecho"),
                "con_pia": lambda model: count_status(model, "con_pia"),
                "prestacion_efectiva": lambda model: count_status(model, "prestacion_efectiva"),
                "lista_espera": lambda model: count_status(model, "lista_espera"),
                "grado_I": lambda model: count_grade(model, "I"),
                "grado_II": lambda model: count_grade(model, "II"),
                "grado_III": lambda model: count_grade(model, "III"),
                "teleasistencia": lambda model: count_benefit_type(model, "teleasistencia"),
                "ayuda_domicilio": lambda model: count_benefit_type(model, "ayuda_domicilio"),
                "atencion_residencial": lambda model: count_benefit_type(model, "atencion_residencial"),
                "cuidados_familiares": lambda model: count_benefit_type(model, "cuidados_familiares"),
            }
        )
