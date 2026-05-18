"""Clase principal del ABM de dependencia construido con Mesa."""

from __future__ import annotations

from typing import Optional

import pandas as pd
from mesa import Model
from mesa.datacollection import DataCollector

from .agents import DependenciaAgent
from .parameters import normalize_parameters


class DependenciaABM(Model):
    """Modelo mensual mínimo del flujo administrativo simplificado del SAAD."""

    def __init__(
        self,
        params: Optional[dict] = None,
        parameters: Optional[dict] = None,
        seed: Optional[int] = 42,
    ) -> None:
        super().__init__(rng=seed)
        self.params = normalize_parameters(parameters)
        if params:
            self.params = normalize_parameters({**self.params, **params})

        self.month = 0
        self.n_agents = int(self.params["initial_vulnerable_population"])
        self.datacollector = self._build_datacollector()
        self._create_agents()
        self.datacollector.collect(self)

    def _create_agents(self) -> None:
        for unique_id in range(self.n_agents):
            DependenciaAgent(model=self, unique_id=unique_id)

    def step(self) -> None:
        """Ejecuta un tick mensual y guarda indicadores agregados."""
        self.agents.shuffle_do("step")
        self.month += 1
        self.datacollector.collect(self)

    def run_model(self, n_months: Optional[int] = None) -> None:
        """Ejecuta la simulación durante el número de meses indicado."""
        months = n_months or int(self.params["simulation_months"])
        for _ in range(months):
            self.step()

    def run(self, n_months: Optional[int] = None) -> pd.DataFrame:
        """Ejecuta la simulación y devuelve directamente sus resultados."""
        self.run_model(n_months=n_months)
        return self.get_results()

    def get_results(self) -> pd.DataFrame:
        """Devuelve un DataFrame mensual con las salidas agregadas."""
        return self.datacollector.get_model_vars_dataframe().reset_index(drop=True)

    @staticmethod
    def _build_datacollector() -> DataCollector:
        return DataCollector(
            model_reporters={
                "month": lambda model: model.month,
                "vulnerables": lambda model: model.n_agents,
                "no_solicitantes": lambda model: model._count_status("no_solicitante"),
                "pendiente_grado": lambda model: model._count_status("pendiente_grado"),
                "sin_grado": lambda model: model._count_status("sin_grado"),
                "con_derecho": lambda model: model._count_status("con_derecho"),
                "con_pia": lambda model: model._count_status("con_pia"),
                "prestacion_efectiva": lambda model: model._count_status(
                    "prestacion_efectiva"
                ),
                "lista_espera": lambda model: model._count_status("lista_espera"),
                "grado_I": lambda model: model._count_grade("I"),
                "grado_II": lambda model: model._count_grade("II"),
                "grado_III": lambda model: model._count_grade("III"),
                "teleasistencia": lambda model: model._count_benefit("teleasistencia"),
                "ayuda_domicilio": lambda model: model._count_benefit(
                    "ayuda_domicilio"
                ),
                "atencion_residencial": lambda model: model._count_benefit(
                    "atencion_residencial"
                ),
                "cuidados_familiares": lambda model: model._count_benefit(
                    "cuidados_familiares"
                ),
            }
        )

    def _count_status(self, status: str) -> int:
        return sum(1 for agent in self.agents if agent.estado_saad == status)

    def _count_grade(self, grade: str) -> int:
        return sum(1 for agent in self.agents if agent.grado_dependencia == grade)

    def _count_benefit(self, benefit_type: str) -> int:
        return sum(1 for agent in self.agents if agent.tipo_prestacion == benefit_type)


DependenceABM = DependenciaABM
