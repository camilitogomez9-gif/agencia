# Migración Venttur → GHL — Resumen ejecutivo + tareas del cliente

**Fecha:** 2026-09-07 · **Cutover objetivo:** 15/9/2026.

> **Runbook completo (el "cómo" paso a paso):** `00_migracion_ghl/04_guia_migracion/` (módulos 00-12).
> **Estado de ejecución detallado:** `00_migracion_ghl/05_ejecucion/REGISTRO-EJECUCION.md`.
> Este documento es el **resumen para compartir** + lo que necesitamos del cliente.

---

## Estado en 3 líneas

- **~80-90% de lo que controla la agencia está hecho:** datos + estructura migrados a GHL y validados; el agente (Mauricio) reconstruido y andando en un entorno de prueba.
- **Lo que falta es sobre todo el canal de WhatsApp** (traspaso del WABA + plantillas de Meta) y algunas validaciones que necesitan un número de prueba — más algunos textos/decisiones del cliente.
- El **camino crítico** hacia el 15/9 es la **decisión del WABA**: es lo único que depende de un tercero (Meta/ManyChat).

---

## ✅ Lo que ya está listo

- **Datos:** 2.299 opportunities + 6.316 contactos importados y reconciliados en GHL, con sus dueños reasignados.
- **Estructura:** 56 custom fields + 20 pipelines (incl. el operativo del bot) + tags.
- **Agente:** context builder (lee el estado del lead), sessionKey MX, tools `crear_contacto` y `elevar`, despachador con tope de 2 toques, clasificador de "Cualificado" y barrido de "interrumpida" — todo construido y validado por API, en staging.
- **Decisiones cerradas:** tope-2, derivación a Mauricio, criterio de "Cualificado".

---

## 🔴 Lo que necesitamos de Mauricio y Max

### A) WhatsApp / WABA — todo desde **Meta Business Manager → WhatsApp Manager**
1. **¿Con qué número corre hoy el bot?** (el del canal, **no** el directo de Rodrigo `+52 1 33 1944 2476` que se comparte al agendar).
2. **¿Ese número lo compraron ustedes o se los dio ManyChat?** — define si lo podemos conservar (los de ManyChat son de un solo uso y no se pueden mover).
3. **Captura de WhatsApp Manager** donde se vea la cuenta de WhatsApp Business (WABA `1931874540684022`) y de qué negocio (Business Manager) cuelga.
4. **¿La verificación de negocio está aprobada?** (Configuración del negocio → Centro de seguridad).
5. **Si el número es de Venttur:** desactivar la **verificación en dos pasos (2FA)** de ese número + tener el **nombre para mostrar (display name) aprobado**.
6. ⚠️ **Regla dura:** **NO instalar la app de WhatsApp / WhatsApp Business** en ese número (bloquea la migración).

### B) Contenidos y decisiones
7. **Textos** de confirmación de cita y de recordatorios (los que hoy salen de Clientify).
8. **Textos/assets** de los 3 programas nuevos (Viajes educativos, Educación superior, Cursos de idiomas) + cómo quieren el pipeline de **Viajes educativos**.
9. **Emails** de los usuarios (Mauricio/Max) para asignación + avisos cuando el bot deriva a una persona.
10. **Rodrigo y Andrés:** conectar su **calendario personal** a GHL (cuando lleguemos a la parte de calendarios).

---

## Próximos pasos (nuestro lado)

Terminar el runbook → **testear el agente por Telegram** (se comparte con Mauricio para que lo pruebe) → una vez conformes, **traspaso del WABA** → smoke tests post-traspaso → cierre de la migración. Las fechas están en `04_guia_migracion/00_indice.md §📅 Calendario`.
