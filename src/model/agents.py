"""Agentes del modelo de dependencia."""

from __future__ import annotations

from typing import Optional

from mesa import Agent


class DependenciaAgent(Agent):
    """Agente individual que transita por el circuito administrativo SAAD."""

    NO_SOLICITANTE = "no_solicitante"
    PENDIENTE_GRADO = "pendiente_grado"
    SIN_GRADO = "sin_grado"
    CON_DERECHO = "con_derecho"
    CON_PIA = "con_pia"
    PRESTACION_EFECTIVA = "prestacion_efectiva"
    LISTA_ESPERA = "lista_espera"

    def __init__(self, model, unique_id: Optional[int] = None) -> None:
        super().__init__(model)
        if unique_id is not None:
            self.unique_id = unique_id

        self.estado_saad = self.NO_SOLICITANTE
        self.grado_dependencia: Optional[str] = None
        self.tipo_prestacion: Optional[str] = None
        self.meses_en_estado = 0

    def step(self) -> None:
        """Avanza un mes la situación administrativa del agente."""
        self.meses_en_estado += 1

        if self.estado_saad == self.NO_SOLICITANTE:
            self._solicitar_si_corresponde()
        elif self.estado_saad == self.PENDIENTE_GRADO:
            self._resolver_grado_si_corresponde()
        elif self.estado_saad == self.CON_DERECHO:
            self._tramitar_pia_si_corresponde()
        elif self.estado_saad == self.CON_PIA:
            self._resolver_prestacion()

    def _cambiar_estado(self, nuevo_estado: str) -> None:
        self.estado_saad = nuevo_estado
        self.meses_en_estado = 0

    def _solicitar_si_corresponde(self) -> None:
        if self.random.random() < self.model.params["prob_solicitud_mensual"]:
            self._cambiar_estado(self.PENDIENTE_GRADO)

    def _resolver_grado_si_corresponde(self) -> None:
        if self.random.random() >= self.model.params["prob_reconocimiento_grado"]:
            return

        if self.random.random() < self.model.params["prob_con_derecho"]:
            self.grado_dependencia = self._sortear_grado()
            self._cambiar_estado(self.CON_DERECHO)
        else:
            self._cambiar_estado(self.SIN_GRADO)

    def _tramitar_pia_si_corresponde(self) -> None:
        if self.random.random() < self.model.params["prob_pia"]:
            self._cambiar_estado(self.CON_PIA)

    def _resolver_prestacion(self) -> None:
        weights = [
            self.model.params["prob_prestacion_efectiva"],
            self.model.params["prob_lista_espera"],
        ]
        nuevo_estado = self.random.choices(
            [self.PRESTACION_EFECTIVA, self.LISTA_ESPERA],
            weights=weights,
            k=1,
        )[0]
        if nuevo_estado == self.PRESTACION_EFECTIVA:
            self.tipo_prestacion = self._sortear_prestacion()
        self._cambiar_estado(nuevo_estado)

    def _sortear_grado(self) -> str:
        distribution = self.model.params["distribucion_grados"]
        return self.random.choices(
            list(distribution.keys()),
            weights=list(distribution.values()),
            k=1,
        )[0]

    def _sortear_prestacion(self) -> str:
        distribution = self.model.params["distribucion_prestaciones"]
        return self.random.choices(
            list(distribution.keys()),
            weights=list(distribution.values()),
            k=1,
        )[0]
