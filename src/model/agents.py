"""Agentes del modelo de dependencia — mapeo operativo v1."""

from __future__ import annotations

from typing import Optional

from mesa import Agent


class DependenciaAgent(Agent):
    """Agente que transita por el circuito SAAD con salud inicial y delays."""

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
        self.meses_tramite_prestacion = 0
        self.cola_recurso: Optional[str] = None
        self.mes_entrada_lista = 10**9

        # Contexto Tabla 7 (v1)
        self.grupo_edad = self._sortear_grupo_edad()
        self.vulnerabilidad_sanitaria = self._sortear_vulnerabilidad()
        self.salud_autopercibida = self._sortear_salud()

    def step(self) -> None:
        """Avanza un mes la situación administrativa del agente."""
        self.meses_en_estado += 1
        if self.estado_saad in (self.CON_DERECHO, self.CON_PIA):
            self.meses_tramite_prestacion += 1

        if self.estado_saad == self.NO_SOLICITANTE:
            self._solicitar_si_corresponde()
        elif self.estado_saad == self.PENDIENTE_GRADO:
            self._resolver_grado_si_corresponde()
        elif self.estado_saad == self.CON_DERECHO:
            self._tramitar_pia_si_corresponde()
        elif self.estado_saad == self.CON_PIA:
            self._resolver_prestacion_si_corresponde()

    def _cambiar_estado(self, nuevo_estado: str) -> None:
        self.estado_saad = nuevo_estado
        self.meses_en_estado = 0

    def _sortear_grupo_edad(self) -> str:
        dist = self.model.params["distribucion_grupos_edad"]
        return self.random.choices(list(dist.keys()), weights=list(dist.values()), k=1)[
            0
        ]

    def _sortear_vulnerabilidad(self) -> bool:
        p = self.model.params["prob_vulnerabilidad_por_edad"][self.grupo_edad]
        return self.random.random() < p

    def _sortear_salud(self) -> str:
        dist = self.model.params["distribucion_salud_autopercibida"]
        return self.random.choices(list(dist.keys()), weights=list(dist.values()), k=1)[
            0
        ]

    def _prob_solicitud(self) -> float:
        if self.vulnerabilidad_sanitaria:
            return float(self.model.params["prob_solicitud_si_vulnerable"])
        return float(self.model.params["prob_solicitud_mensual"])

    def _solicitar_si_corresponde(self) -> None:
        if self.random.random() < self._prob_solicitud():
            self._cambiar_estado(self.PENDIENTE_GRADO)

    def _resolver_grado_si_corresponde(self) -> None:
        min_meses = int(self.model.params["meses_min_pendiente_grado"])
        if self.meses_en_estado < min_meses:
            return
        if self.random.random() >= self.model.params["prob_resolucion_grado_mensual"]:
            return

        if self.random.random() < self.model.params["prob_con_derecho"]:
            self.grado_dependencia = self._sortear_grado()
            self.meses_tramite_prestacion = 0
            self._cambiar_estado(self.CON_DERECHO)
        else:
            self._cambiar_estado(self.SIN_GRADO)

    def _tramitar_pia_si_corresponde(self) -> None:
        if self.random.random() < self.model.params["prob_pia_mensual"]:
            self._cambiar_estado(self.CON_PIA)

    def _resolver_prestacion_si_corresponde(self) -> None:
        min_tramite = int(self.model.params["meses_min_tramite_prestacion"])
        if self.meses_tramite_prestacion < min_tramite:
            return
        if self.tipo_prestacion is None:
            self.tipo_prestacion = self._sortear_prestacion()
        if self.model.try_occupy(self):
            return
        self.mes_entrada_lista = self.model.month
        self._cambiar_estado(self.LISTA_ESPERA)

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
