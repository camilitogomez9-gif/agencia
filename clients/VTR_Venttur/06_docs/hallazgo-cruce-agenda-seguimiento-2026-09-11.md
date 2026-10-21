# Hallazgo: los flows "Agenda" y "Seguimiento agenda" están CRUZADOS

**Fecha:** 2026-09-11 · Verificado en vivo en ManyChat (cuenta Venttur). Cierra el `#9` de pendientes y la bandera de `05_templates_meta_waba.md §5.4` / `manychat-flows-content-2026-07-20.md`.

## El hallazgo

Los dos flows tienen los **nombres cambiados respecto a su contenido**. **Mapear por CONTENIDO, nunca por nombre.**

| Flow (nombre en ManyChat) | `flow_ns` | Carpeta | Estado | Contenido REAL | Destino en GHL |
|---|---|---|---|---|---|
| **"Agenda"** | `content20250718124614_140983` | Seguimientos | STOPPED | **SEGUIMIENTO post-link**: *"Hola [Nombre] 👋 Hace unos días te compartí el enlace... pero vi que aún no la agendaste. ¿Tuviste algún problema con el link?..."* + tag `seguimiento_agenda` | Rescate / seguimiento (`09`) |
| **"Seguimiento agenda"** | `content20250721163426_851504` | Agendamiento | STOPPED | **CONFIRMACIÓN de cita**: condicional por `programa_interes` → *"Rodrigo se comunicará contigo por WhatsApp directamente desde el número +52 1 33 1944 2476..."* + *"Siéntete con la libertad de compartirlo con algún familiar... Nos vemos pronto!"* | Confirmación de cita (`04` / `07`) |

## Corrección a la documentación previa

- El doc `manychat-flows-content-2026-07-20.md` tenía la asociación **al revés** (describía "Agenda" como la confirmación de Rodrigo). La verificación en vivo del 2026-09-11 muestra lo contrario. **Vale la verificación en vivo.**
- Ambos flows están **STOPPED** hoy (no activos).

## Implicancia para la migración

- La plantilla / workflow de **confirmación de cita** en GHL se arma con el contenido del flow llamado **"Seguimiento agenda"** (`...851504`) — el de Rodrigo.
- El **seguimiento post-link** (rescate) usa el contenido del flow llamado **"Agenda"** (`...140983`) — que ya está cubierto por el rescate n8n / las plantillas `rescate_*`.
- El número directo de Rodrigo **+52 1 33 1944 2476** es dato de negocio a preservar en la confirmación (NO es el número del bot).
