# Metodología del ABM

## Representación del modelo

Este repositorio contiene una primera versión experimental de un modelo basado en agentes para representar el circuito de dependencia en España. El modelo avanza en pasos mensuales y describe transiciones administrativas simplificadas desde la no solicitud hasta la prestación efectiva o la lista de espera.

## Agentes

Cada agente representa una persona mayor de 65 años. Los agentes se caracterizan por grupo de edad, tipo de territorio, situación de vulnerabilidad, estado administrativo en el SAAD, grado de dependencia, tipo de prestación y tiempo de espera acumulado.

## Estados administrativos

Los estados incluidos son:

- `no_solicitante`: persona que no ha iniciado solicitud.
- `pendiente_grado`: solicitud iniciada y pendiente de resolución de grado.
- `sin_grado`: resolución sin reconocimiento de grado.
- `con_derecho`: reconocimiento de grado y derecho a prestación.
- `con_pia`: Programa Individual de Atención reconocido.
- `prestacion_efectiva`: prestación asignada y efectiva.
- `lista_espera`: persona con derecho o trámite pendiente sin prestación efectiva.

## Datos agregados generados

La simulación genera un CSV mensual con conteos agregados de personas vulnerables, estados administrativos, grados de dependencia y prestaciones seleccionadas. Estas salidas están pensadas como base para análisis descriptivo, comparación de escenarios y futura generación de datos sintéticos para modelos sustitutos de Machine Learning.

## Limitaciones

Esta versión no está calibrada con microdatos individuales ni reproduce diferencias territoriales reales por comunidad autónoma. Las probabilidades se aplican de forma homogénea y las transiciones son una simplificación del procedimiento administrativo. Tampoco incorpora mortalidad, entrada de nuevas cohortes, costes, bienestar subjetivo ni modelos predictivos avanzados. Su objetivo es ofrecer una base mínima, reproducible y defendible para ampliar el TFM.
