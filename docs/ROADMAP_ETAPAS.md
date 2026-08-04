# Roadmap de Etapas — Ecosistema Digital Terrae

Plan de desarrollo dividido en etapas independientes, funcionales y
subibles a GitHub una por una, siguiendo el Prompt Maestro Terrae.

> **Desde la Etapa 8**, todas las etapas se rigen adicionalmente por el
> Prompt Maestro Permanente V2.0 (JJ GROUP SAS), consolidado en
> `CONSTITUCION_INGENIERIA_TERRAE.md`: exige Revisión de Consistencia
> Global antes de cada etapa, ADR de decisiones importantes
> (`docs/adr/`), y el régimen obligatorio de auditoría/versionado/Domain
> Events/logging/Optimistic Locking para toda entidad nueva.

| # | Etapa | Estado |
|---|---|---|
| 1 | Arquitectura y estructura del repositorio | ✅ Completada |
| 2 | Configuración del entorno y herramientas (Docker, linters, scripts) | ✅ Completada |
| 3 | Migración del simulador a componentes reales (React/Next.js) | ✅ Completada |
| 4 | Sistema de autenticación y roles (JWT) | ✅ Completada |
| 5 | Base de datos inicial (modelo completo PostgreSQL) | ✅ Completada |
| 6 | API REST base (FastAPI, versionada, documentada) | ✅ Completada |
| 7 | Gestión de joyas | ✅ Completada |
| 7.5 | Arquitectura Empresarial Transversal (auditoría, eventos, logging, concurrencia) | ✅ Completada |
| 8 | Gestión de esmeraldas | ✅ Completada |
| 9 | Inventario | ✅ Completada |
| 10 | Certificados digitales (+ activos multimedia trazables) | ✅ Completada |
| 11 | QR y trazabilidad | ⏳ Pendiente |
| 12 | Blockchain (EmeraldChain, smart contracts, wallet) | ⏳ Pendiente |
| 13 | IA para clasificación gemológica (SIEGEM Lab) | ⏳ Pendiente |
| 14 | Gestión de imágenes y multimedia | ⏳ Pendiente |
| 15 | Dashboard ejecutivo | ⏳ Pendiente |
| 16 | Centro de operaciones (backoffice completo) | ⏳ Pendiente |
| 17 | Auditoría y registros (logs, trazabilidad de acciones) | ⏳ Pendiente |
| 18 | Seguridad y respaldos | ⏳ Pendiente |
| 19 | Ventas, clientes y garantías | ⏳ Pendiente |
| 20 | NFT y tokens | ⏳ Pendiente |
| 21 | Optimización y pruebas (QA integral) | ⏳ Pendiente |
| 22 | Preparación para producción y despliegue | ⏳ Pendiente |

## Formato obligatorio de entrega por etapa

Cada etapa, al entregarse, debe incluir:

1. Objetivos y alcance.
2. Arquitectura (actualización de `docs/ARQUITECTURA.md` si aplica).
3. Código fuente completo.
4. Árbol de archivos actualizado.
5. Explicación técnica.
6. Instrucciones de instalación y configuración.
7. Checklist de validación.
8. Pruebas realizadas.
9. Commits recomendados (Conventional Commits).
10. Próxima etapa recomendada.

## Regla de avance

No se inicia una etapa nueva sin autorización explícita al cierre de la
etapa anterior, mediante la pregunta:

> "Etapa finalizada correctamente. ¿Desea continuar con la siguiente etapa?"
