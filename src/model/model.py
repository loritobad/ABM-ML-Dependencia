"""Clase principal del ABM de dependencia (Mesa) — mapeo operativo v1.5."""

from __future__ import annotations

from typing import Optional

import pandas as pd
from mesa import Model
from mesa.datacollection import DataCollector

from .agents import DependenciaAgent
from .capacity import QUEUE_KEYS, occupancy_ok, queue_for_benefit
from .parameters import BENEFIT_KEYS, normalize_parameters


class DependenciaABM(Model):
    """Modelo mensual del circuito SAAD (v1.5: cupos nacionales de 3 colas)."""

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
        self.ocupados = {key: 0 for key in QUEUE_KEYS}
        self.rechazos_capacidad = 0
        self.datacollector = self._build_datacollector()
        self._create_agents()
        self.datacollector.collect(self)

    def _create_agents(self) -> None:
        for unique_id in range(self.n_agents):
            DependenciaAgent(model=self, unique_id=unique_id)

    def step(self) -> None:
        """FIFO de lista primero; luego ticks de agentes (nuevos PIA)."""
        self._asignar_desde_lista()
        self.agents.shuffle_do("step")
        self.month += 1
        self.datacollector.collect(self)

    def run_model(self, n_months: Optional[int] = None) -> None:
        months = n_months or int(self.params["simulation_months"])
        for _ in range(months):
            self.step()

    def run(self, n_months: Optional[int] = None) -> pd.DataFrame:
        self.run_model(n_months=n_months)
        return self.get_results()

    def get_results(self) -> pd.DataFrame:
        return self.datacollector.get_model_vars_dataframe().reset_index(drop=True)

    def try_occupy(self, agent: DependenciaAgent, *, count_reject: bool = True) -> bool:
        """Intenta ocupar un hueco de la cola del agente y el techo de atendidas."""
        if not agent.tipo_prestacion:
            agent.tipo_prestacion = agent._sortear_prestacion()
        queue = queue_for_benefit(agent.tipo_prestacion)
        agent.cola_recurso = queue
        if not occupancy_ok(self.ocupados, self.params, queue):
            if count_reject:
                self.rechazos_capacidad += 1
            return False
        self.ocupados[queue] += 1
        agent._cambiar_estado(agent.PRESTACION_EFECTIVA)
        return True

    def _asignar_desde_lista(self) -> None:
        waiting = [
            a
            for a in self.agents
            if a.estado_saad == DependenciaAgent.LISTA_ESPERA
        ]
        waiting.sort(key=lambda a: (a.mes_entrada_lista, a.unique_id))
        for agent in waiting:
            self.try_occupy(agent, count_reject=False)

    def _build_datacollector(self) -> DataCollector:
        reporters = {
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
            "vuln_sanitaria": lambda model: sum(
                1 for a in model.agents if a.vulnerabilidad_sanitaria
            ),
            "edad_65_74": lambda model: model._count_age("65_74"),
            "edad_75_84": lambda model: model._count_age("75_84"),
            "edad_85_plus": lambda model: model._count_age("85_plus"),
            "ocupados_residencial": lambda model: model.ocupados["residencial"],
            "ocupados_dia": lambda model: model.ocupados["dia"],
            "ocupados_resto": lambda model: model.ocupados["resto"],
            "cupo_residencial": lambda model: int(model.params["cupo_residencial"]),
            "cupo_dia": lambda model: int(model.params["cupo_dia"]),
            "cupo_resto": lambda model: int(model.params["cupo_resto"]),
            "cupo_atendidas": lambda model: int(model.params["cupo_atendidas"]),
            "rechazos_capacidad": lambda model: model.rechazos_capacidad,
        }
        for key in BENEFIT_KEYS:
            reporters[key] = (
                lambda model, benefit=key: model._count_benefit(benefit)
            )
        return DataCollector(model_reporters=reporters)

    def _count_status(self, status: str) -> int:
        return sum(1 for agent in self.agents if agent.estado_saad == status)

    def _count_grade(self, grade: str) -> int:
        return sum(1 for agent in self.agents if agent.grado_dependencia == grade)

    def _count_benefit(self, benefit_type: str) -> int:
        return sum(1 for agent in self.agents if agent.tipo_prestacion == benefit_type)

    def _count_age(self, age_group: str) -> int:
        return sum(1 for agent in self.agents if agent.grupo_edad == age_group)


DependenceABM = DependenciaABM
