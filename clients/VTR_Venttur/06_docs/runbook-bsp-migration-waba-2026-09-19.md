# Runbook operativo — BSP migration WABA `1931874540684022` → GHL

**Fecha:** 2026-09-19 · **Cutover VTR:** 26-27/9/2026 · **Ventana de ejecución sugerida:** sábado 20 o lunes 22/9, hora de bajo tráfico (madrugada Mx).

> **Contexto y decisión previa.** El diagnóstico completo del canal está en `portabilidad-numero-whatsapp-2026-08-18.md` (Escenario A confirmado: el número lo compró Venttur, es portable). El listado de gates y precondiciones del cutover general está en `00_migracion_ghl/04_guia_migracion/12_cutover.md`. Este runbook es **solo el paso a paso operativo del traspaso del WABA en sí** — no cubre plantillas ni datos.
>
> **Fuentes oficiales:** [GHL — Redesigned WhatsApp Onboarding](https://help.gohighlevel.com/support/solutions/articles/155000008043) · [GHL — Setup WhatsApp for a Sub-Account (Method 3 = BSP migration)](https://help.gohighlevel.com/support/solutions/articles/155000001980) · [Meta — WhatsApp Business Platform migration](https://developers.facebook.com/docs/whatsapp/embedded-signup/migrate).
>
> **Regla dura que ordena todo:** el proceso usa **Meta Embedded Signup** dentro de la UI de GHL. Es un OAuth atómico. No se piden tokens ni WABA ID a mano — GHL los captura vía popup de Facebook. Consecuencia: quien ejecuta necesita estar logueado como **admin del Business Portfolio en Meta** al momento de arrancar.

---

## 0. Antes de empezar — quiénes y qué

**Quien ejecuta:** Mauricio (o quien tenga rol de admin del Business Portfolio de Venttur en Meta). Necesita:
- Sesión activa en `business.facebook.com` con esa cuenta.
- Sesión activa en `app.gohighlevel.com` en la sub-account de VTR (id `7aXb4JCKsWV5nUyBXeSF`).
- Acceso al número `1931874540684022` para recibir un **código OTP por SMS o llamada** (paso 6).
- la agencia disponible en paralelo por chat/llamada por si aparece un error de los documentados (§8).

**Duración estimada del acto en sí:** 15-30 minutos (los 8 clicks del proceso). Downtime perceptible: **segundos a pocos minutos**, solo en el switchover del webhook. Post-proceso: quality rating queda en `UNKNOWN` las primeras 24 h; Meta recalibra después con tráfico real.

---

## 1. Precondiciones — verificar TODAS antes de arrancar

Si cualquiera de estas 4 no está OK, el proceso se traba a mitad. Verificar en este orden y **no pasar al paso 2 hasta que las 4 estén ✅**.

### 1.1 · 2FA (two-step verification) desactivada en el número
- Meta BM → **WhatsApp Manager** → **Phone Numbers** → click en el número `1931874540684022` → **Two-step verification** → **Turn off**.
- **Es la causa #1 documentada de migraciones trabadas.** Aunque parezca "off", si el número la había activado alguna vez conviene apagar y volver a apagar.

### 1.2 · Display name aprobado
- Meta BM → WhatsApp Manager → Phone Numbers → click en el número → **Name and about** → confirmar estado **Approved**.
- Si está `Pending` o `Rejected`, la migración termina con **error #131037** (`display name approval required`) y el canal queda inutilizable hasta que Meta apruebe.

### 1.3 · Verificación de negocio (business verification) del BM
- Meta BM → **Business Settings** → **Security Center** → confirmar **Business Verification: Verified**.
- Si el BM no está verificado, ni siquiera arranca el flow.

### 1.4 · Admin del Business Portfolio
- Meta BM → **Business Settings** → **People** → confirmar que la cuenta que va a ejecutar tiene rol **Admin** (no Employee) sobre el Portfolio que contiene la WABA.

**⚠️ Si falla cualquier check, RESOLVER PRIMERO. No hay atajos — todos los errores comunes se rastrean a estos 4 ítems.**

---

## 2. Regla dura — qué NO hacer nunca

> 🚨 **NO instalar la app de WhatsApp ni WhatsApp Business en el número `1931874540684022`.**
>
> Cloud API (que es lo que usa GHL/Meta) y la app son **excluyentes**. Instalar la app rompe el registro Cloud API y bloquea el número — mismo escenario que arrastramos con Collazo en junio, imposible de destrabar por soporte de Meta (ver `portabilidad §6`).
>
> Esta regla aplica **antes, durante y después** del traspaso. Si alguien del equipo o del cliente pregunta "¿puedo verificar el número desde mi celular?", la respuesta es **no**.

---

## 3. El proceso — 8 clicks en GHL

**Ubicación:** GHL → sub-account de VTR → **Settings → WhatsApp → "Migrating from an existing BSP (Business Solution Provider)"**.

| # | Paso GHL | Qué pasa | Verificación intermedia |
|---|---|---|---|
| 1 | Click **"Migrating from an existing BSP"** | Se abre la wizard | Deberías ver un banner que dice "Migrate your existing WhatsApp Business Account" |
| 2 | Click **Continue** | Arranca | — |
| 3 | **Select Business Assets** | Se abre el **popup de Facebook (Embedded Signup)**. Login con la cuenta admin del Portfolio. Elegir: Business Portfolio de Venttur → WABA `1931874540684022` → número | Al terminar el popup, GHL muestra "Business assets linked" |
| 4 | **Enter Business Details** — completar razón social + dirección + país | Click **Next** | GHL guarda |
| 5 | **Add Your Phone Number** — ingresar `+52 1 33 …` (el mismo número) | Click **Next** | — |
| 6 | **Verify Your Phone Number** — elegir método (SMS o Voz) → click **Send code** | Meta envía OTP al número | El **teléfono físico o cualquier receptor del SMS** recibe un código de 6 dígitos en 30-60 seg |
| 7 | **Enter the OTP** | Meta valida | Si el código expira o rebota: reintentar (Meta permite 2-3 reintentos antes de bloquear 15 min) |
| 8 | **Review and Confirm** — chequear que el WABA ID, número y display name son los correctos → **Confirm** | Meta ejecuta el switchover: número pasa a WABA-de-LeadConnector como partner registrado, webhook cambia | ⏱ **Segundos a minutos.** GHL muestra "WhatsApp account connected" |

**Al terminar los 8 clicks, la WABA ya vive en GHL.** Meta preserva automáticamente: número, display name, calidad, límites de mensajería, OBA (Official Business Account) status, y **plantillas APPROVED con calidad GREEN** (tope 250 por WABA).

Lo que **NO se preserva**: plantillas en amarillo/rechazadas, historial de conversaciones (los mensajes viejos de ManyChat quedan en ManyChat).

---

## 4. Verificaciones post-migración — hacer YA, no esperar

Estas 4 pruebas se hacen los primeros 15-30 minutos post-traspaso. Si alguna falla, ver §8 (troubleshooting).

### 4.1 · Templates duplicadas
- GHL → **Settings → WhatsApp → Templates**
- Confirmar que aparecen las **10 plantillas** que ya están APPROVED en el WABA de Venttur (ver `submit-templates-log.json` y `plantillas-meta-live-1931874540684022-2026-09-17.md`).
- Estado esperado: `Approved`. Quality rating puede aparecer `UNKNOWN` — es normal las primeras 24h.
- Si falta alguna: seguramente era `PENDING` o quality `YELLOW`/`RED` — Meta las descartó en el traspaso. Se re-submitean.

### 4.2 · Número, display name, WABA ID
- GHL → Settings → WhatsApp → **Channel** (o similar) → confirmar que muestra el número correcto, display name correcto, y WABA ID `1931874540684022`.

### 4.3 · Test de envío (template)
- Enviar una plantilla approved a un contacto de prueba (Mauricio, Max, la agencia — cualquiera con el número agendado como contact en GHL).
- Confirmar que **llega** y que el status queda `delivered` en GHL Conversations.

### 4.4 · Test de recepción (webhook)
- El contacto de prueba responde el mensaje.
- Confirmar que la respuesta **aparece en GHL Conversations en tiempo real** (segundos). Esto valida que el webhook de Meta ya apunta a GHL, no a ManyChat.

---

## 5. Ventana de indisponibilidad efectiva

- **Segundos a pocos minutos** para el switchover del webhook (paso 8).
- Durante esa ventana, mensajes entrantes **podrían no ver un webhook activo** (ni ManyChat ni GHL) — Meta los encola y los reintenta hasta 5 minutos, así que en la práctica no se pierden.
- **Recomendación:** ejecutar sábado o lunes en franja de bajo tráfico Mx (madrugada Mx UTC-6). Evitar mediodía-tarde de un día hábil.

---

## 6. Qué pasa con ManyChat después

- **Automatic:** apenas Meta reasigna la WABA, el webhook que ManyChat tenía queda **desconectado**. ManyChat empieza a mostrar el canal como offline.
- **No hay que hacer nada** — no borrar, no desconectar, no cancelar el plan de ManyChat *el mismo día*. Dejar todo intacto por si necesitamos volver (ver §7).
- **Después del cutover del 26-27/9, y solo si todo está OK**, se puede cancelar ManyChat.

---

## 7. Plan B — rollback

**El proceso BSP migration es reversible: siempre podés volver a otra BSP** repitiendo el proceso desde la otra plataforma. Pero rollback tiene 2 sabores:

### 7.1 · Rollback rápido (mismo día, si el test §4 falla)
- Volver a ManyChat: en la UI de ManyChat, iniciar el Embedded Signup con la misma WABA + número.
- Meta re-asigna el webhook a ManyChat en el mismo timeframe (segundos).
- **Requisito:** que la cuenta ManyChat siga activa (no cancelada).

### 7.2 · Rollback diferido (post-cutover, si algo aparece mal en producción)
- Igual que 7.1, pero implica coordinar con Mauricio/Max porque parte de los leads ya empezaron a llegar via GHL.
- Puede haber mensajes en tránsito que se pierden.
- **No es la opción preferida** — es el paracaídas.

### 7.3 · Si la migración se queda "in transit" (Meta no completa)
- Documentado en foros pero no oficialmente por Meta: puede pasar que el paso 8 no responda por >30 min.
- **NO reintentar el proceso** — puede duplicar la request y trabar más.
- **Sí abrir ticket** en soporte de Meta desde el BM (Help → Contact Support → WhatsApp) referenciando el número y el error.
- Contactar soporte de GHL en paralelo (chat en la UI).

---

## 8. Errores comunes (documentados) — qué hacer

| Error | Causa | Fix |
|---|---|---|
| **`131037` — Display name approval required** | Display name en `Pending`/`Rejected` en Meta | Volver a Meta BM → WhatsApp Manager → Phone → Name and about → aprobar/re-submit. Sin esto no hay canal. |
| **"2FA required" o "Two-step verification"** aunque se apagó | La desactivación no propagó, o hay 2FA a nivel Business (no Phone) | Meta BM → Business Settings → Security → confirmar 2FA de la cuenta admin. Reintentar en 15 min. |
| **"Payment method already exists"** durante onboarding | GHL detecta que el BM ya tiene un método de pago (por otro BSP) | Bug conocido de GHL. Contactar soporte GHL con screenshot; workaround: continuar el proceso, el error suele ser cosmético. |
| **OTP no llega** | Número mal escrito, o Meta tuvo rate limit | Reintentar con método distinto (SMS ↔ Voice). Si persiste, esperar 15 min y reintentar. |
| **"Business assets not found"** en paso 3 | La cuenta que hizo login no es admin del Portfolio | Cerrar popup, verificar rol en Meta BM → Business Settings → People, volver a intentar. |

---

## 9. Después del traspaso — checklist para cerrar

Al terminar los pasos 1-4, actualizar:

- [ ] `ESTADO_MIGRACION.md` → sección B-05: cambiar de "escenario A confirmado, sin iniciar" a **"BSP migration ejecutada YYYY-MM-DD HH:MM"**.
- [ ] `submit-templates-log.json` → si las 10 templates preserved siguen APPROVED, agregar campo `preserved_after_bsp_migration: true` con timestamp.
- [ ] `12_cutover.md` gate "WABA resuelto" → marcar ✅.
- [ ] Avisar a Mauricio/Max por WhatsApp: "WABA conectada a GHL, canal operativo desde HH:MM Mx, sin incidentes. Test de send/receive OK."
- [ ] **NO cancelar** ManyChat hasta después del 27/9 (post-cutover, cuando todo esté verde en producción).

---

## 10. Preguntas frecuentes que puede tener Mauricio

**¿Se pierden los leads existentes?**
No. Los leads son contactos en GHL Contacts (ya importados desde Clientify + Airtable). El WABA solo mueve el canal — el CRM no se toca en este paso.

**¿Hay que avisarle a los suscriptores/leads que cambia algo?**
No. El número, display name y "cómo se ve" en WhatsApp del lado del contacto **no cambia en absoluto**. Es transparente.

**¿Y si algo sale mal el día del cutover (26-27/9)?**
El rollback rápido (§7.1) toma minutos. Y si el problema no es del canal, se puede seguir trabajando en n8n con el canal viejo hasta resolver.

**¿Cuánto tarda que las plantillas vuelvan a estar calificadas?**
Meta reevalúa con tráfico real de las primeras 24-48 h. Es normal ver `UNKNOWN` al principio.

**¿ManyChat se puede cancelar ya?**
Después del 27/9, cuando todo esté verde en producción. Antes no.

---

## Referencias

- Diagnóstico WABA VTR: [`portabilidad-numero-whatsapp-2026-08-18.md`](./portabilidad-numero-whatsapp-2026-08-18.md)
- Cutover general: [`00_migracion_ghl/04_guia_migracion/12_cutover.md`](../00_migracion_ghl/04_guia_migracion/12_cutover.md)
- Plantillas Meta live en WABA `1931874540684022`: [`plantillas-meta-live-1931874540684022-2026-09-17.md`](./plantillas-meta-live-1931874540684022-2026-09-17.md)
- Templates log: [`submit-templates-log.json`](./submit-templates-log.json)
- GHL BSP migration (fuente oficial): https://help.gohighlevel.com/support/solutions/articles/155000008043-redesigned-whatsapp-onboarding-experience-in-highlevel
- Método 3 (setup) fuente oficial: https://help.gohighlevel.com/support/solutions/articles/155000001980-how-to-set-up-whatsapp-for-a-sub-account
- Error `#131037` (display name): https://help.gohighlevel.com/support/solutions/articles/155000007730
- Precedente Collazo (regla "no instalar app"): `clients/CLZ_Collazo/06_docs/migracion-whatsapp-manychat-2026-06-30.md`
