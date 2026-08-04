# ADR-008-03 — Consumidor real de referencia: logging de auditoría de eventos

## Estado
Aceptado — Etapa 8

## Contexto

ADR-008-01 exige que todo evento publicado tenga al menos un
consumidor real en la misma etapa. `Esmeralda` es la primera entidad
que publica Domain Events (`EntidadCreadaEvent`,
`EntidadActualizadaEvent`, `EntidadDesactivadaEvent`). Se necesita un
consumidor mínimo, reutilizable por cualquier entidad futura, que no
sea un placeholder vacío.

## Decisión

Se implementa `suscribir_logging_auditoria(event_bus)` en
`app/infrastructure/events/consumers.py`: un consumidor que se suscribe
a `DomainEvent` (la clase base, capturando así cualquier subtipo
presente y futuro) y registra una línea de log estructurado por cada
evento recibido, vía `get_logger("domain_events")`.

Este consumidor:
- Es genérico (no conoce nada específico de `Esmeralda`), por lo que
  cualquier entidad futura que publique eventos lo obtiene gratis sin
  registrar nada nuevo.
- Se registra una única vez, en el arranque de la aplicación
  (`app/main.py`, función `configurar_event_bus()`).
- Cumple un propósito real de negocio: auditoría de qué cambió, cuándo
  y quién lo hizo, quedando en los logs estructurados (Etapa 7.5)
  disponibles para cualquier herramienta de observabilidad externa.

## Consecuencias

- `EventBus` dejó de estar "vacío" (Etapa 7.5) y pasa a tener su primer
  consumidor real, cumpliendo el mandato de ADR-008-01 sin publicar
  eventos huérfanos.
- Cualquier entidad futura que publique Domain Events los verá también
  auditados en el log sin trabajo adicional.
- Si en una etapa futura se requiere un consumidor más especializado
  (ej. invalidación de caché, notificación a un sistema externo), se
  agrega como un suscriptor adicional del mismo `EventBus`, sin tocar
  este consumidor de auditoría.
