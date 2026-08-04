# Manual del Desarrollador — Terrae

## Filosofía de trabajo

Este proyecto se desarrolla **etapa por etapa**, siguiendo el Prompt Maestro
del Ecosistema Digital Terrae. Reglas clave para cualquier persona (o IA)
que contribuya al código:

1. **Nunca romper el simulador existente** (`frontend/simulator/index.html`).
   Es la fuente de verdad visual y funcional del proyecto.
2. **No rediseñar** — solo convertir progresivamente el simulador en
   componentes reales, manteniendo la identidad visual exacta.
3. **Una etapa a la vez.** No avanzar a la siguiente etapa sin que la
   actual esté completa, documentada y validada.
4. **Código de nivel producción.** Nunca pseudocódigo ni funciones
   incompletas (`TODO` sin implementar en código que se declara "terminado").
5. **Clean Architecture / SOLID / DDD** en backend; **Repository Pattern**
   para toda persistencia; **DTOs** para la API.
6. **Documentar cada cambio estructural** en `CHANGELOG.md` y actualizar
   `docs/ARQUITECTURA.md` cuando corresponda.

## Convenciones de commits (Conventional Commits)

```
<tipo>(<alcance opcional>): <descripción breve>

[cuerpo opcional]
```

Tipos usados en este proyecto: `feat`, `fix`, `docs`, `chore`, `refactor`,
`test`, `style`, `build`, `ci`.

Ejemplos para la Etapa 1:
```
chore(repo): estructura inicial del monorepo Terrae
docs(readme): documentar arquitectura y manuales de la Etapa 1
chore(brand): incorporar activos de identidad visual Terrae
```

## Convención de ramas (a partir de la Etapa 2)

```
main                  → producción
develop                → integración
feature/<nombre-etapa>  → una rama por etapa, ej. feature/etapa-02-entorno
fix/<descripcion>        → correcciones puntuales
```

## Estructura de carpetas — reglas de contribución

| Carpeta | Quién trabaja aquí | Regla |
|---|---|---|
| `frontend/simulator/` | Nadie (solo lectura) | Es la referencia; no se edita salvo corrección explícita autorizada. |
| `frontend/src/` | Frontend/Full Stack | Componentes reales, deben replicar el diseño del simulador. |
| `backend/app/` | Backend | Clean Architecture: `domain/`, `application/`, `infrastructure/`, `api/`. |
| `database/` | Ingeniería de datos | Migraciones versionadas, nunca editar una migración ya aplicada. |
| `blockchain/` | Blockchain | Contratos con tests antes de cualquier despliegue, ni siquiera en testnet. |
| `ai/` | IA | Modelos y datasets no se versionan en Git (ver `.gitignore`); usar almacenamiento externo. |
| `docs/` | Todo el equipo | Toda etapa debe dejar su documentación aquí. |

## Checklist antes de cerrar cualquier etapa

- [ ] Código fuente completo (sin pseudocódigo).
- [ ] `README.md` de la etapa/módulo actualizado.
- [ ] Documentación técnica y arquitectura actualizadas.
- [ ] Árbol de archivos actualizado.
- [ ] Commits recomendados definidos.
- [ ] Checklist de validación ejecutado.
- [ ] Pruebas realizadas documentadas.
- [ ] Próxima etapa propuesta.

## Variables de entorno

Ver `.env.example` en la raíz. Nunca hardcodear secretos ni URLs de
producción en el código fuente.

## Identidad visual — referencia obligatoria para frontend

Ver `docs/IDENTIDAD_VISUAL.md`. Cualquier componente nuevo debe usar
exactamente la paleta, tipografías y tokens ya definidos ahí — no se
introducen colores, fuentes o espaciados nuevos sin justificación explícita.
