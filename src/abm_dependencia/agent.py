"""Agentes del modelo de dependencia."""

from __future__ import annotations

from typing import Optional

from mesa import Agent


class ElderlyAgent(Agent):
    """Persona mayor de 65 años que transita por estados del sistema SAAD."""

    STATUS_NO_SOLICITANTE = "no_solicitante"
    STATUS_PENDIENTE_GRADO = "pendiente_grado"
    STATUS_SIN_GRADO = "sin_grado"
    STATUS_CON_DERECHO = "con_derecho"
    STATUS_CON_PIA = "con_pia"
    STATUS_PRESTACION_EFECTIVA = "prestacion_efectiva"
    STATUS_LISTA_ESPERA = "lista_espera"

    def __init__(
        self,
        model,
        age_group: str,
        territory_type: str,
        unique_id: Optional[int] = None,
    ) -> None:
        super().__init__(model)
        self.unique_id = unique_id if unique_id is not None else getattr(self, "unique_id", None)
        self.age_group = age_group
        self.territory_type = territory_type
        self.is_vulnerable = self._initialize_vulnerability()
        self.saad_status = self.STATUS_NO_SOLICITANTE
        self.dependency_grade: Optional[str] = None
        self.benefit_type: Optional[str] = None
        self.waiting_time = 0

    def step(self) -> None:
        """Avanza un mes la trayectoria administrativa del agente."""
        if self.saad_status == self.STATUS_NO_SOLICITANTE:
            self._maybe_request_assessment()
        elif self.saad_status == self.STATUS_PENDIENTE_GRADO:
            self._process_grade_resolution()
        elif self.saad_status == self.STATUS_CON_DERECHO:
            self._process_benefit_resolution()
        elif self.saad_status == self.STATUS_CON_PIA:
            self._process_effective_benefit()
        elif self.saad_status == self.STATUS_PRESTACION_EFECTIVA:
            self._assign_benefit_if_needed()
        elif self.saad_status == self.STATUS_LISTA_ESPERA:
            self.waiting_time += 1

    def _initialize_vulnerability(self) -> bool:
        probabilities = {
            "65_74": self.model.params["p_vulnerable_65_74"],
            "75_84": self.model.params["p_vulnerable_75_84"],
            "85_plus": self.model.params["p_vulnerable_85_plus"],
        }
        return self.random.random() < probabilities[self.age_group]

    def _maybe_request_assessment(self) -> None:
        if self.is_vulnerable and self.random.random() < self.model.params["p_request_if_vulnerable"]:
            self.saad_status = self.STATUS_PENDIENTE_GRADO
            self.waiting_time = 0

    def _process_grade_resolution(self) -> None:
        self.waiting_time += 1
        if self.waiting_time < self.model.params["months_to_grade_resolution"]:
            return

        if self.random.random() >= self.model.params["p_grade_resolution"]:
            return

        if self.random.random() < self.model.params["p_no_grade"]:
            self.saad_status = self.STATUS_SIN_GRADO
            self.waiting_time = 0
            return

        self.dependency_grade = self._draw_dependency_grade()
        self.saad_status = self.STATUS_CON_DERECHO
        self.waiting_time = 0

    def _draw_dependency_grade(self) -> str:
        draw = self.random.random()
        p_grade_i = self.model.params["p_grade_I"]
        p_grade_ii = self.model.params["p_grade_II"]

        if draw < p_grade_i:
            return "I"
        if draw < p_grade_i + p_grade_ii:
            return "II"
        return "III"

    def _process_benefit_resolution(self) -> None:
        self.waiting_time += 1
        if self.waiting_time < self.model.params["months_to_benefit_resolution"]:
            return

        if self.random.random() < self.model.params["p_pia"]:
            self.saad_status = self.STATUS_CON_PIA
        else:
            self.saad_status = self.STATUS_LISTA_ESPERA
        self.waiting_time = 0

    def _process_effective_benefit(self) -> None:
        if self.random.random() < self.model.params["p_effective_benefit"]:
            self.saad_status = self.STATUS_PRESTACION_EFECTIVA
            self._assign_benefit_if_needed()
        else:
            self.saad_status = self.STATUS_LISTA_ESPERA
        self.waiting_time = 0

    def _assign_benefit_if_needed(self) -> None:
        if self.benefit_type is not None:
            return
        distribution = self.model.params["benefit_distribution"]
        self.benefit_type = self.random.choices(
            list(distribution.keys()),
            weights=list(distribution.values()),
            k=1,
        )[0]
