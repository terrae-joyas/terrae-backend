# ADR-009-01 — Ajuste de cantidad de inventario como operación atómica basada en delta

## Estado
Aceptado — Etapa 9

## Contexto

`InventarioModel.cantidad` (Etapa 5) representa las existencias de una
joya en su sucursal. Dos diseños posibles para modificarla:

1. **Sobrescritura directa**: `PUT /inventario/{id}` con
   `cantidad: 5` — el cliente envía el valor final.
2. **Ajuste por delta**: `PATCH /inventario/{id}/ajustar` con
   `delta: -1` (o `+3`) y un `motivo` — el cliente envía el cambio, no
   el valor final.

La sobrescritura directa es más simple pero pierde información de
negocio (¿la joya salió por venta, por préstamo, por corrección de
conteo físico?) y es más propensa a condiciones de carrera silenciosas:
dos operadores leyendo `cantidad: 5` y escribiendo `cantidad: 4` cada
uno (por ejemplo, tras vender 1 unidad cada uno) resultarían en
`cantidad: 4` en vez de `3` — el segundo `PUT` pisa al primero sin que
Optimistic Locking por sí solo lo prevenga necesariamente si ambos
leyeron la misma versión antes de que cualquiera escribiera.

## Decisión

Se implementa el ajuste por delta como la única forma de modificar
`cantidad` (no existe un `PUT` que sobrescriba `cantidad` directamente).
El repositorio ejecuta un `UPDATE` condicional atómico:

```sql
UPDATE inventario
SET cantidad = cantidad + :delta, version = version + 1, actualizado_en = now(), actualizado_por = :usuario_id
WHERE id = :id AND version = :version_esperada AND cantidad + :delta >= 0
```

Si `rowcount == 0`, el repositorio distingue la causa (conflicto de
versión vs. resultado negativo) con una lectura adicional solo para
componer un mensaje de error preciso — la garantía de atomicidad real
la da la cláusula `WHERE` de la sentencia anterior, no esa lectura de
diagnóstico.

Cada ajuste se registra como evento de dominio
(`EntidadActualizadaEvent` con `campos_modificados={"delta": ..., "motivo": ...}`)
y como versión (`RegistradorVersion`, Etapa 7.5) — el histórico de
`historial_eventos` para una fila de inventario se convierte, en la
práctica, en un kardex de movimientos consultable.

## Consecuencias

- El DTO de ajuste (`InventarioAjustarCantidadRequest`) exige `delta`
  (puede ser negativo) y `motivo` (obligatorio, a diferencia del
  `motivo` opcional de `Esmeralda` — un movimiento de inventario sin
  motivo es deuda de auditoría inaceptable para esta entidad).
- Mover una joya de sucursal o corregir su `ubicacion_fisica` sigue
  usando `PUT` con Optimistic Locking estándar (no toca `cantidad`).
- Precedente para toda entidad futura con "cantidad"/"saldo"/valores
  acumulativos: usar ajuste por delta, no sobrescritura directa.
