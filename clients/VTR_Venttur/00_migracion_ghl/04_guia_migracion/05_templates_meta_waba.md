# 05 · WhatsApp WABA + Message Templates de Meta

> ### 🔄 Estado a 2026-09-07 — 🔴 EL GATE CRÍTICO (depende del cliente)
> **[CLIENTE] — 4 datos del WABA** (Meta Business Manager → WhatsApp Manager): (1) con qué **número** corre el bot (no el directo de Rodrigo `+52 1 33 1944 2476`; candidato `+52 1 33 2627 4502`); (2) si lo **compró Venttur** (portable) o lo **dio ManyChat** (no portable → chip); (3) **captura** de WhatsApp Manager con la WABA `1931874540684022` y de qué Business Manager cuelga; (4) **verificación de negocio** aprobada.
> **[CLIENTE] — prereqs escenario A (portar):** desactivar **2FA** del número + **display name** aprobado. **Regla dura:** NO instalar la app de WhatsApp en ese número.
> **[LA AGENCIA + Meta] — plantillas:** exportar las APPROVED+GREEN, crear/re-aprobar las faltantes (las 3 `seg_dia_3/5/7_bs`), **aprobación 24-72h → arrancar apenas se decida el WABA**.
> **Deadline propio 1/9 VENCIDO.** Decisión pre-tomada del cliente: si hay riesgo de downtime → chip nuevo. Ver `06_docs/portabilidad-numero-whatsapp-2026-08-18.md`.

> **🔴 Crítico + gate vencido.** El canal de WhatsApp: la **portabilidad de la WABA** (prioridad #1 del cliente, **deadline propio 1/9 YA VENCIDO** al 3/9) y las **Message Templates** de re-enganche (aprobación Meta 24-72h). La topología del canal no cambia con esto (`06`); lo que cambia es **número migrado vs chip nuevo** y **cuántas plantillas se re-aprueban**.
>
> **Para quién:** la agencia + cliente (Mauricio/Max proveen accesos a Meta BM). **Prerequisito:** nada de código; sí la desambiguación del WABA. **Referencia:** `06_canal_whatsapp_y_agente.md §7`, `09_nurturing_rescate_reengagement.md §7`, `06_docs/portabilidad-numero-whatsapp-2026-08-18.md`.
>
> **Estimado:** 3-5 hs de trabajo + **espera de terceros** (Meta 24-72h, respuesta de ManyChat/cliente). **Corroborado contra el snapshot** (16 flows reales) + la revisión de portabilidad.

---

## 5.0 ⏰ Por qué esto va PRIMERO

Es la única pieza que depende de **terceros** (ManyChat + Meta). El deadline propio de portabilidad era el **1/9** y **ya pasó** (hoy 3/9, T-12). La decisión ya está pre-tomada por el cliente:

> *"Si la portabilidad no es viable o implica riesgo de downtime, preferimos número nuevo."* → **no hace falta re-consultar**, alcanza con avisar y avanzar.

**Acción inmediata (día 1 de la ejecución):** conseguir del cliente la desambiguación del WABA (§5.1). Sin eso no se sabe si el número migra o hay que comprar chip — y si es chip, hay **24-72h** de re-aprobación de plantillas que hay que arrancar YA para llegar al 15/9.

---

## 5.1 La pregunta que define todo

> ### ¿El número del bot lo compró Venttur, o se lo dio ManyChat?

| Respuesta | Escenario | Consecuencia |
|---|---|---|
| **Lo trajo Venttur** (número propio, WABA en el BM de Venttur) | **A** | ✅ migra por BSP conservando número, display name, calidad, límites, OBA y **plantillas aprobadas** |
| **Lo dio ManyChat** | **B** | ❌ **no portable** (números de ManyChat son de un solo uso) → chip nuevo, todo se re-crea |

**Datos recibidos (18/8):** número del bot `+52 1 33 2627 4502` (Guadalajara, chip de Venttur — coherente con el quirk MX), WABA ID `1931874540684022`. **Falta el último paso (2 min):** en `business.facebook.com` de Venttur → Configuración → Cuentas → Cuentas de WhatsApp, ver si el WABA `1931874540684022` cuelga del **Business Manager de Venttur** (→ A) o no (→ B, escenario Collazo).

⚠️ **No confundir con el `+52 1 33 1944 2476`** (aparece 21 veces): ese es el **directo de Rodrigo** que el flow "Agenda" comparte al agendar — dato de negocio a preservar (`04`/`06 §7`), NO el canal. La inconsistencia interna de `ronda-2` (llama a `1944 2476` "número vigente" pero B1 da `2627 4502` como el del bot) **se desambigua acá**.

**Los 4 datos a pedir al cliente** (todos salen de Meta BM → WhatsApp Manager): (1) con qué número corre el bot; (2) quién lo proveyó; (3) captura de WhatsApp Manager mostrando de qué BM cuelga la WABA; (4) si la verificación de negocio está aprobada. Texto listo para mandar en `portabilidad-numero-whatsapp-2026-08-18.md` §Anexo.

---

## 5.2 Escenario A — migración BSP (viable)

GHL tiene el camino nativo **"Migrating from an existing BSP"** — mueve la WABA existente a LeadConnector **sin recrear la WABA**.

**Qué preserva Meta** (número · display name · calidad · límites de mensajería · OBA · **plantillas APPROVED + calidad GREEN**, tope 250). Matices: las amarillas/rechazadas **no viajan**; la calidad queda `UNKNOWN` 24h y Meta recalifica.

**Prerequisitos (los 3 del lado de Venttur):**
1. ⚠️ **Desactivar 2FA** del número (causa #1 de migraciones trabadas).
2. **Verificación de negocio** confirmada en Meta BM.
3. **Display name aprobado.**

**Pasos:**
1. En GHL sub-cuenta → `Settings → WhatsApp` → **"Migrate from existing BSP"**.
2. Seguir el flujo de Meta (verificación del número).
3. ⚠️ **Ventana de downtime = solo el paso final de registro**, hasta que termina la duplicación de plantillas. **Planificar en franja de bajo tráfico.**
4. ✅ Verificar que las plantillas APPROVED aparecen en GHL post-migración.

**Downtime:** prácticamente nulo (minutos).

---

## 5.3 Escenario B — chip nuevo (no portable)

No hay workaround. Lo que arrastra:

| Se pierde | Impacto |
|---|---|
| Límite de mensajería | arranca en **250 conversaciones iniciadas / 24h** hasta que escala |
| Plantillas aprobadas | se **re-crean y re-aprueban desde cero** (Meta 24-72h) |
| Historial / hilo con contactos del número viejo | no viaja |

⚠️ **El límite de 250/24h estrangula el outreach tri-toque** en las primeras semanas post-cutover (medido en Collazo: 426 avisos obligaron a partir el envío 213+213). Planificar el ramp-up.

> **El segundo número (Clientify, recordatorios) NO entra acá:** decisión cerrada (`portabilidad §8`) — **muere y no se avisa**. No hay broadcast ni ventana de 250/24h por ese lado.

**Regla dura heredada de Collazo:** nunca instalar la app de WhatsApp/WhatsApp Business en un número que va a Cloud API (son excluyentes → repite el bloqueo).

---

## 5.4 Inventario de templates (flows ManyChat → GHL Message Templates)

Los **16 flows reales** (snapshot) se clasifican: **template de re-enganche** (este módulo), **canal/handoff/inbound** (`06`/`07`), o **utility/interno**.

| Flow (ns) | Nombre | Carpeta | Destino | MKT/UTIL |
|---|---|---|---|---|
| `content20260612151152_969589` | **[LA AGENCIA] Outreach Boarding Form Meta** (Touch 1) | Seguimientos | **Template GHL** (`boarding_form_followup`) | MARKETING |
| `content20260616231914_193459` | **[LA AGENCIA] Outreach Boarding Touch 2** | Seguimientos | **Template GHL** | MARKETING |
| `content20260616231947_185709` | **[LA AGENCIA] Outreach Boarding Touch 3** | Seguimientos | **Template GHL** | MARKETING |
| `content20250718115245_638127` | Boarding School (nurturing drip) | Seguimientos | **Templates GHL** (4 toques) | MARKETING |
| `content20250718121921_967738` | Pathway (nurturing drip) | Seguimientos | **Templates GHL** (4 toques) | MARKETING |
| `content20250718122822_491460` | Gap year (nurturing drip) | Seguimientos | **Templates GHL** (4 toques) | MARKETING |
| `content20250718123255_243860` | Año Académico (nurturing drip) | Seguimientos | **Templates GHL** (4 toques) | MARKETING |
| `content20250718123847_652764` | Summer Camp (nurturing drip) | Seguimientos | **Templates GHL** (4 toques) | MARKETING |
| `content20250718124216_992343` | Lead General (nurturing drip) | Seguimientos | **Templates GHL** | MARKETING |
| `content20250617172539_850988` | Enviar mensajes (rescate + send) | Agente IA Principal | ⚠️ **doble uso** — ver flag | MKT (rescate) / free-form (agente) |
| `content20250718124614_140983` | **Agenda** ⚠️ | Seguimientos | confirmación/agenda (`04`/`07`) — comparte nº Rodrigo | — |
| `content20250721163426_851504` | **Seguimiento agenda** ⚠️ | Agendamiento | **se consolida en el rescate** (`09`) | — |
| `content20250716130059_365663` | Elevar (handoff) | Agente IA Principal | **Assign+notify GHL** (`06 §5`/`07`) | — |
| `content20250617171957_654158` | Recibir mensajes (inbound debounce) | Agente IA Principal | **Contact Reply → n8n** (`06 §1`/`07`) | — |
| `content20250918181220_518318` | Asignar número (Tag-triggered) | (sin carpeta) | interno — se rehace con la lógica de canal (`07`) | — |
| `content20260210212250_552933` | Borrar contactos | Manejo de contactos | utility — no migra | — |

> ⚠️ **Bloqueante de verificación (ESTADO próximos-pasos #7):** los nombres de **`Agenda` (`...140983`)** y **`Seguimiento agenda` (`...851504`)** **podrían estar cruzados**. **No se toca ni se mapea ninguno de los dos `flow_ns` hasta abrirlos en ManyChat y confirmar cuál es cuál.** El de confirmación de cita va a `04`/`07`; el de seguimiento-post-link se consolida en el rescate (`09`).
>
> ⚠️ **`Enviar mensajes` (`...850988`) es de doble uso:** hoy es el caño de envío del agente (parte1/2/3, free-form) **y** el diseño (`09 §7`) lo lista como origen del rescate Fase 1/2. Al reconstruir: el **reply del agente** va free-form (`06 §4`, sandbox B2) y el **rescate** va por template (§abajo). **Separar los dos usos** al construir — no son la misma cosa en destino.

### Colapso ~17 → ~10 templates

Los **rescate** (Fase 1/2 × 6 programas = 12 mensajes) viven verbatim en `06_docs/rescue-flow-message-templates.md` y en `template-texts-canonical.md`. Los **outreach** (3 toques) en `template-texts-canonical.md`. El **nurturing drip** (5 programas × 4 toques + Lead General) colapsa por programa. GHL las agrupa como Message Templates parametrizadas → los ~17 flows quedan en **~10 templates** (varios son la misma estructura por programa, con merge fields).

### 3 plantillas faltantes ⚠️

`seg_dia_3_bs` / `seg_dia_5_bs` / `seg_dia_7_bs` (34 fallos de entrega en el Reporte la agencia 1): **no están en el repo**, viven en Meta/ManyChat. **Exportar de Meta antes del cutover.** Si la WABA no migra (escenario B), se re-crean y re-aprueban como todas.

---

## 5.5 Aprobación de Meta (timing pre-cutover)

- **Toda plantilla ausente de la WABA migrada** (escenario A parcial) **o todas** (escenario B) se **re-crean y re-aprueban**: Meta tarda **24-72h**.
- ⚠️ **Categoría:** el outreach es **MARKETING** (Meta rechazó utility — requiere opt-in). Redactar como MARKETING desde el inicio (lección Collazo: Meta recategoriza por contenido, no por nombre; imperativos/exclamaciones/CTA empujan a MARKETING). Si alguna califica como **UTILITY** (atada a una acción previa del cliente, ej. confirmación/recordatorio de cita), abarata el envío — probar por contenido.
- **Agendar las aprobaciones YA** (a T-12): re-aprobar sobre la fecha es el riesgo. Los recordatorios de cita (`04`) también necesitan su template.
- **Merge params por programa:** cada template lleva merge fields (`{{contact.first_name}}`, link de calendario del programa, etc.). Ver `06 §2` (Merge Fields GHL vs `{{first_name}}` de ManyChat).

---

## 5.6 Banderas y checkpoints

| Bandera | Estado |
|---|---|
| WABA portable sí/no | **desambiguar YA** (deadline 1/9 vencido) — decisión pre-tomada: chip nuevo si riesgo |
| Cruce de nombres `Agenda`/`Seguimiento agenda` | ⚠️ **verificar en ManyChat antes de tocar sus `flow_ns`** |
| `Enviar mensajes` doble uso | separar reply free-form (agente) de rescate (template) |
| Send de template por API + merge params | **sandbox B3** — fallback: Workflow Send Action |
| 3 plantillas faltantes `seg_dia_*_bs` | exportar de Meta antes del cutover |
| Secretos: Bearer ManyChat, tokens Meta pixel | **rotar** (`00 §secretos`) |

✅ **Checkpoints de cierre:**
- [ ] Desambiguación del WABA resuelta (A o B) → plan de número confirmado.
- [ ] (A) migración BSP hecha con 2FA off + verificación de negocio + display name; plantillas APPROVED verificadas en GHL. **(B)** chip nuevo activado + ramp-up de 250/24h planificado.
- [ ] `Agenda` vs `Seguimiento agenda` desambiguados en ManyChat.
- [ ] Las ~10 templates de re-enganche creadas en GHL con merge fields por programa.
- [ ] Las 3 `seg_dia_*_bs` exportadas/recreadas.
- [ ] Todas las plantillas **APPROVED** por Meta **antes** del cutover (arrancar 24-72h antes).

---

*Corroborado contra el snapshot 2026-07-24 (16 flows reales con `ns` + carpetas) y `portabilidad-numero-whatsapp-2026-08-18.md`. Deadline de portabilidad (1/9) vencido al 2026-09-03. 2026-09-03.*
