# Guía ejecutable VTR · recta final WABA → GHL

**Única guía vigente.** Revisión completa del 23/9 contra el estado vivo de n8n, GHL, DNS y Meta. **Cambio de
plan del 23/9: el traspaso de WhatsApp ya no espera al DNS.** La copia de `clients/VTR_Venttur/06_docs/` quedó
como puntero a esta.

| | Cuándo |
|---|---|
| **Hoy** | miércoles 23/9 · **H = hoy**: Max tiene el teléfono del número y el traspaso se hace ahora |
| **PREP** | hasta que la agencia fije **H** |
| **Traspaso de WhatsApp (H)** | **la hora que elegimos nosotros**, con quien tenga el chip del número disponible para el código de Meta (A7). Recomendado: horario laboral CDMX de poco tráfico, con la agencia o Camilo conectados ~1 h. No depende de la agencia |
| **DNS de `promo` (T)** | la hora que confirme la agencia para cambiar el destino del CNAME. Puede ir antes o después de H. Dura ~15 min + un paso suelto a T + 4 h |
| **Apagado de Clientify** | **sábado 26/9 · 21:00 CDMX**, sólo si pasan los gates de la Fase D, que incluyen el DNS (B5). Si el DNS se atrasa, el apagado se corre con él |

**Por qué WhatsApp y DNS van separados:** el traspaso de WhatsApp (BSP) no depende del DNS. El único cruce era
que el agente nuevo manda links a `promo.venttur.com`, que sirve Clientify hasta T: el lead agendaría en
Clientify y GHL no lo vería (sin confirmación W6, un rescate que le escribe "no agendaste", un agente que no ve la
cita). Se resuelve en B2: **hasta T el agente manda las mismas rutas en `vtr.[TU-DOMINIO]`**, que ya sirve las
50 landings de GHL (verificado 23/9: las 6 rutas del agente dan 200 o redirigen a su landing). En B5 se vuelve a
`promo` con un comando. Mientras tanto, lo que sigue llegando a Clientify es lo que entra por links fuera del
agente (anuncios, links de aventureras, links viejos de ManyChat).

`[ ]` pendiente · `[x]` hecho · 👤 lo hace una persona en una UI · 🤖 lo corre un script (o Claude) · 🔴 bloquea el paso siguiente.

Scripts: `S=clients/VTR_Venttur/00_migracion_ghl/05_ejecucion/scripts` (todos leen `.env` solos; ninguno
pide `source`). PIT GHL en `clients/VTR_Venttur/06_docs/ghl-credentials.md` (gitignored).

---

## Checklist maestro

**Fase A · PREP**
- [x] A1 👤 Mensaje a la agencia enviado (bajar TTL de `promo` + cambiar destino con día y hora avisados). **Al 23/9 el TTL sigue en 4 h**: ya no bloquea WhatsApp, sólo el DNS (B5)
- [x] A2 🤖 Crear las landings en GHL · **hecho 22/9 por Claude**: funnel único `LP · Calendarios`, 56 steps en `vtr.[TU-DOMINIO]` (50 + `preparate` + 5 de referenciadoras del 23/9), verificadas 56/56 · español de México (tuteo)
- [x] A3 👤 Verificar las landings en `vtr.[TU-DOMINIO]` · hecho 23/9
- [x] A3b 🤖 Ensayar el cambio de dominio del funnel · **hecho 22/9 con `vtr2.[TU-DOMINIO]`**: conectar + enlazar el funnel deja las páginas sirviendo al instante. **Corregido 23/9:** sólo sirve el dominio principal; en B5 se suma el puente `vtr` → `promo`
- [x] A4 🤖 Las 8 páginas internas de Clientify rehechas o redirigidas en GHL (23/9) · aventureras sigue activo (Max, 23/9); quedan 4 puntos con Mauricio (ver A4)
- [x] A5 👤🔴 Revisar los 5 workflows GHL publicados · WF-01, WF-02 y WEBHOOK ya en Borrador (23/9)
- [x] A6 👤🔴 Confirmar qué key tiene la credencial n8n `OpenAI | Venttur`
- [x] A7 👤🔴 Quién tiene el chip del número **a la hora H** · **Max, confirmado 23/9** (H = hoy)
- [ ] A8 👤 Avisar a los asesores (mensaje en A8, con H)
- [ ] A9 👤 Venttur: confirmar las cuentas bancarias, conectar Mercado Pago y decir qué presupuestos siguen sin cobrar (bloquea D2, no el cutover)
- [x] A10 🤖 Ensayo en seco de los scripts del cutover · hecho 23/9: `--verify` 6 viejos ON / 9 nuevos OFF · `--solo-on` 8 · `--landings-on` 3 · `dominio-links-agente.py --a vtr` 19 links
- [x] A11 🤖 Revisión nodo por nodo del stack nuevo contra el payload real de GHL · **hecho 23/9 tarde**: el main no respondía ningún mensaje; 7 workflows parcheados (ver A11)
- [x] A12 🤖🔴 Prueba E2E del main con un payload de GHL · **hecha 23/9 noche** con el main prendido: aparecieron 5 fallas más, corregidas (ver A12)

**Fase B · WhatsApp (hora H, la elegimos nosotros)** — en este orden:
- [ ] B0 🤖 Snapshot · H − 20 min
- [x] B1 🤖 Prender el stack nuevo (`--solo-on`) · hecho 23/9 noche (la agencia, desde la UI)
- [x] B2 🤖 Links del agente a `vtr.[TU-DOMINIO]` + landings y rescate ON (`--landings-on`) · hecho 23/9 noche (19 links en `vtr`, rescate ya estaba)
- [x] B3 👤🔴 BSP: WABA → GHL · **hecho 23/9 ~22:00 UTC**: cuenta de WhatsApp Business NUEVA "Venttur Education and Travel" (la vieja `1931874540684022` quedó con el número "Transferido"), número verificado por SMS, GHL lo muestra Conectado · calidad Verde. **Pendiente: anotar el ID de la cuenta nueva y confirmar las 11 plantillas en GHL**
- [x] B4 👤🔴 Smoke real por WhatsApp · 23/9: mensaje → GHL → main en 6 s → 3 respuestas *delivered*. `elevar` falló 2 veces y quedó corregido (schema de inputs + avisos: mail a administracion@ por D3, Telegram al chat 6390727286, respuesta limpia al agente)
- [x] B6 🤖 Apagar el stack viejo del agente (`--solo-off`) · hecho 23/9
- [ ] B7 👤 Anuncio · H + 35 min

**B5 · DNS (hora T, la de la agencia; antes o después de H)**
- [ ] ⏸ La agencia cambia el destino del CNAME de `promo` y avisa
- [ ] B5 👤🔴 `promo.venttur.com` → GHL + redirects + links del agente de vuelta a `promo` · T → T + 15 min
- [ ] B5.8 🤖 Apagar los webhooks viejos de landings (`--landings-off`) · T + 4 h

**Fase C · POST (desde H)**
- [x] C1 👤 Publicar los 23 flujos de Rodrigo · publicados 22/9 (ver nota en C1 sobre 2 que no iban)
- [ ] C2 🤖🔴 Despachador: mirar el dry-run y habilitar el envío (con B2 hecho)
- [ ] C3 👤 Testing E2E (8 casos)
- [ ] C4 🤖 Delta de folios CAPI (después de B5.8)
- [ ] C5 👤 Watch mode
- [ ] C6 🤖 Limpieza de restos

**Fase D · Gates para apagar Clientify (viernes 25 – sábado 26 mediodía)**
- [ ] D1 🤖🔴 Delta de datos Clientify → GHL · **1.ª pasada hecha 23/9** (136 contactos, 99 deals nuevos, 82 movidos). Pendiente: **2.ª pasada el viernes 25/9 después del freeze de A8** (`--export --plan --check-ghl` + los 3 `--stage … --apply`) y los 12 deals con etapas sin equivalente (decide Rodrigo)
- [ ] D2 👤🔴 Presupuestos funcionando en GHL (configuración, plantillas, cobro, flujos, reemisión de los abiertos y prueba; ver D2)
- [ ] D3 🤖🔴 Cero dependencias de Clientify en n8n
- [ ] D4 👤🔴 B5 hecho: `promo.venttur.com` sirve GHL y `--landings-off` corrido

**Fase E · CIERRE (sábado 26/9)**
- [ ] E1 GO / NO-GO · E2 Apagar Clientify · E3 Snapshot final · E4 Handoff Mauricio · E5 Postmortem

**Fase F · Semana del 28/9 (no bloquea)** — ver lista al final, y **Canales nuevos** (Instagram, TikTok) después.
Instagram como bandeja para humanos se puede conectar desde H (ver Canales nuevos).

---

## Camino de hormiga

```
PREP · hasta H ─────────────────────────────────────────────────────────────────────────────────────────
 Listo        A2 · A3 · A3b · A5 · A6 · A10 ✅   C1 flujos de Rodrigo ✅
 Falta        A8 asesores (antes de H) · A4 internas (no bloquea) · A9 cuentas + Mercado Pago + pendientes (sólo D2)
                   ▼
WHATSAPP · hora H (la elegimos nosotros) ─────────────────────────────────────────────────────────────────
 B0 ─► B1 ─► B2 (links → vtr + landings/rescate ON) ─► B3 BSP ─► B4 smoke ─► B6 ─► B7
                   ▼
POST · desde H ────────────────────────────────────────────────────────────────────────────────────────
 C2 despachador · C3 E2E · C5 watch · C6 limpieza · Instagram como bandeja (opcional)

DNS · hora T (la de la agencia; en paralelo, antes o después de H) ─────────────────────────────────────
 A1 TTL 300 visible ─► +4 h ─► agencia cambia el CNAME ─► B5 (dominio + redirects + links → promo) ─► +4 h B5.8 ─► C4
                   ▼
CIERRE · sábado 26/9 ────────────────────────────────────────────────────────────────────────────────────
 D1 delta · D2 presupuestos · D3 cero Clientify · D4 B5 hecho ─► E1 GO/NO-GO ─► E2 apagar Clientify ─► E3-E5
                   ▼
DESPUÉS · semana del 28/9 ───────────────────────────────────────────────────────────────────────────────
 Fase F · Canales nuevos (agente en Instagram → TikTok cuando exista para México)
```

---

## Qué ya está hecho (no repetir)

- **GHL:** sub-cuenta `7aXb4JCKsWV5nUyBXeSF`, 8 calendarios de producción con conflictCheck (OAuth Rodrigo +
  Andrés ✅), custom field `atribuida_a`, pipelines + etapas, 18 tags, email template de idiomas, **26 productos
  MXN** cargados (`cargar-products-ghl.py`), import de 6.316 contactos + 2.299 opps (**desde exports del 10/7 y
  24/7 — ver D1**).
- **GHL Workflows (estado 23/9, por API):** 26 publicados y 3 en borrador. Publicados: los 2 de Camilo
  (`Inbound bot → main-venttur-ghl`, que filtra sólo WhatsApp, y `Confirmación de cita → W6`) + los 23 de
  Rodrigo + `Fallback · atribuida_a…` y `Handoff · Notificación al equipo` (ver C1). En borrador: WF-01, WF-02 y
  WEBHOOK.
- **Calendarios (23/9):** los 10 de las landings con nombre legible, **45 min** con horarios cada 45 min, y el
  widget en **español** (ajuste de la cuenta).
- **Meta:** 11/11 plantillas APPROVED · nombre visible aprobado · negocio verificado · la agencia admin del
  Portafolio · 2SV del número desactivado · Mauricio confirmó que no hay app de WhatsApp en el número.
- **n8n (todo OFF salvo el staging):** main nuevo `1eS1Z5k898c3ATnf` **a paridad con el staging probado**
  (prompt v2.2 + `cerrar_conversacion`, `crear_contacto` → GHL, `elevar` con contacto y asesor
  determinísticos, `[ESTADO DEL LEAD]` leído de GHL con `Cita: AGENDADA`), W4 · W6 · W9 · W10 · W11 · W14 ·
  rescate · barrido · clasificador · despachador (con política de recontacto aplicada, envío deshabilitado) ·
  CAPI folio Supabase · 3.725 folios migrados · OpenAI rotada en `Transcribir audio/s`.
- **Landings:** las 50 en GHL (funnel `LP · Calendarios`, sirviendo en `vtr.[TU-DOMINIO]`), con íconos y logo
  propios de GHL (23/9) + **199 redirects** ensayados en `vtr` (eran 205; 6 pasaron a ser landings: `preparate` y las 5 de referenciadoras) + página `Programas` como 404 del dominio.
- **Snapshots de rollback:** `03_workflows/ghl-live-2026-09-22-post-paridad/` (20 workflows: stack nuevo + los
  6 viejos, sha256 en el README).

---

# FASE A · PREP (hasta H)

## A1 · Pedido a la agencia de Venttur · mensaje enviado

`venttur.com` está en la cuenta de Hostinger **de la agencia que les hizo la web**; Mauricio y Max no pueden
editar el DNS y cada cambio se pide por mensaje (tardan 1-2 días, audios de Mauricio del 22/9).

**Decisión (22/9):** se reutiliza `promo.venttur.com`, no se crea un subdominio nuevo. Todas las salidas
(plantillas Meta aprobadas, rescate, agente, links de aventureras, campañas) ya apuntan ahí; un dominio nuevo
obligaría a cambiarlas todas y a re-aprobar plantillas (24-72 h).

**Por qué 2 cambios y no uno (verificado 22/9):**
- GHL recién deja conectar el dominio cuando **su** verificador ve el CNAME nuevo (probado: responde *"No se ha
  podido encontrar un registro CNAME/A que apunte promo a sites.ludicrous.cloud"*). Ese verificador también
  consulta DNS con caché: con el TTL actual (14.400 s = 4 h) podría tardar hasta 4 h en ver el cambio, y en ese
  lapso `promo` queda roto. Con TTL 300 el lapso baja a unos 5 minutos.
- Clientify manda **HSTS de 1 año** en `promo`: mientras GHL no tenga certificado, quien ya visitó la página ve
  un error de seguridad sin opción de continuar. Por eso el cambio de destino tiene que caer en un momento en
  que estemos conectados para completar B5 en el acto.

**Qué se verificó y está bien:** el registro que pide GHL es exactamente `CNAME · promo · sites.ludicrous.cloud`
(leído de la pantalla de conexión de GHL); `promo` no tiene otros registros que choquen; `venttur.com` no tiene
CAA (el certificado de GHL lo emite Google Trust Services) ni DNSSEC; GHL no marcó el dominio como usado en otra
cuenta.

Mensaje para que Mauricio le reenvíe a la agencia:

> Hola, necesitamos dos cambios en el DNS del dominio venttur.com (Hostinger), en el registro CNAME con nombre **promo** (hoy apunta a clientify.dony.clearalias.com). No hay que tocar ningún otro registro.
>
> 1. Lo antes posible: bajar el TTL de ese registro a 300. Solo eso, sin cambiar el destino.
> 2. En un segundo momento: cambiar el destino a **sites.ludicrous.cloud** (TTL 300). Si no deja editarlo, borrar el registro y crear uno nuevo con esos datos.
>
> Para el cambio 2 necesitamos que nos avisen antes el día y la hora en que lo van a hacer, en horario laboral y a partir del jueves 24/9 a las 9:00 (hora de CDMX), porque de nuestro lado hay que activar el dominio en ese mismo momento.
>
> Y por favor avísenle a Mauricio apenas quede hecho cada uno. Gracias!

**La hora que confirme la agencia para el cambio 2 es T, la hora de B5** (dominio + redirects), no la del
traspaso de WhatsApp (desde el 23/9 van separados, ver el encabezado). Antes de darla por buena, Mauricio la
confirma con la agencia o Camilo, que tienen que estar conectados ~15 min para completar B5 en el acto: entre el cambio
y el final de B5, `promo` muestra un error a quien ya resuelva al dominio nuevo.

**Control del cambio 1:** `dig promo.venttur.com CNAME +noall +answer @ns1.dns-parking.com` tiene que mostrar
`300`. **Al 23/9 12:00 ART seguía en `14400`: el cambio 1 todavía no está hecho.** El cambio 2 recién puede ir
**4 h después** de que se vea (el caché viejo tiene que vencer). Mientras no se haga, no se atrasa WhatsApp: se
atrasa B5 y, con él, el apagado de Clientify (gate D4).

## A2 · Landings en GHL ✅ hecho 22/9

Las 50 landings viven en GHL (centralización), en **un solo funnel `LP · Calendarios`** publicado en
**`vtr.[TU-DOMINIO]`** (ya conectado a GHL) para probarlas; en B5 (hora T) el funnel entero pasa a
`promo.venttur.com` (B5). Verificado: 50/50 responden con el cargador, los 50 steps coinciden con `MANIFEST.md`,
y en el navegador se probó formulario, calendario, aventurera, Programas, la de video y un redirect.

**Cómo están armadas (no hay código pegado página por página):**
- Cada landing es un step **plantilla**: una sección con un Custom Code que la oculta. Los steps se crean con
  **Clonar paso** + renombrar (pestaña **Publicación** del step: nombre y URL del paso).
- El contenido lo dibuja el **cargador** del funnel (Configuración → *Código de seguimiento del cuerpo*): lee la
  ruta, busca la landing en un JSON publicado en la biblioteca de medios de GHL y la pinta. Ruta desconocida →
  Programas.
- El JSON sale de los fragmentos de `landings-ghl/_ghl/` y se verifica byte a byte contra ellos antes de subirlo.

**Cambiar el texto o el calendario de una landing** (no se toca el editor de GHL):

```bash
python3 $S/generar-landings-aventureras-calendarios.py   # si cambia una de calendario o aventurera
python3 $S/generar-landings-ghl.py                      # si cambia una de formulario
python3 $S/preparar-landings-ghl.py
python3 $S/generar-renderer-ghl.py --publicar           # sube el JSON nuevo y reescribe cargador.html
```

Después pegar `landings-ghl/_ghl/cargador.html` en Configuración del funnel → *Código de seguimiento del cuerpo*
→ Guardar (cambia la URL del JSON; las 50 páginas lo toman solas, sin republicar). Controlar con
`python3 $S/verificar-landings-ghl.py`.

**Agregar una landing nueva** (p. ej. una aventurera): cargarla en `landings-ghl/_data/aventureras.json`, correr
lo de arriba y crear su step clonando cualquier step del funnel (todos son plantilla) con el nombre y la ruta
de `MANIFEST.md`.

**Reglas que quedaron fijadas:**
- **Español de México con tuteo** en todo texto visible (títulos, botones, errores del formulario). Se corrige en
  los generadores, nunca en el HTML de salida.
- GHL **no acepta `_` en la ruta de un step**. `EstudiaryTrabajar_Agendar` y `PW_Alemania_Agendar` viven como
  `/estudiarytrabajar-agendar` y `/pw-alemania-agendar`, y la URL original sigue funcionando por un redirect
  (incluido en `redirects.json`). No puede morir: la usan el agente, el rescate, el clasificador y plantillas
  de WhatsApp aprobadas por Meta.
- Los 4 funnels viejos de prueba ya no existen en la cuenta (verificado por API: queda uno solo).
- El título SEO que sirve el servidor es **"Venttur"** en 45 steps (lo pone el cargador al abrir, pero las vistas
  previas de links de WhatsApp leen el del servidor). Tienen título propio: Internados, Campamentos,
  CursosIdiomas, EducacionSuperior y GapYear. Cargar el resto es opcional (Fase F).

**Ajustes del 22/9 (feedback de la agencia sobre las landings):**
- **Íconos sociales rotos → arreglado.** Los PNG venían de `cdn.tools.unlayer.com` (el editor de Clientify), que
  empezó a dar 403. Ahora son SVG embebidos (`scripts/_marca_landings.py`) y el logo está copiado en la
  biblioteca de GHL, para que nada dependa de Clientify cuando se apague.
- **Nombres de los calendarios → renombrados por API** (el widget los muestra como título). Las landings
  originales de Clientify mostraban el nombre del programa ("AÑO CON FAMILIA") y debajo "Reunión con
  [asesor]", así que se siguió ese criterio: `cal-internados` → **Internados**, `cal-intercambio` →
  **Intercambio académico con familias**, `cal-campamentos` → **Campamentos de verano**, `cal-pathway-alemania`
  → **Pathway Alemania**, `cal-gap-year` → **Gap Year / Estudia y Trabaja**, `cal-cursos-idiomas` → **Cursos de
  idiomas en el extranjero**, `cal-educacion-superior` → **Educación superior**, `cal-viajes-educativos` →
  **Viajes educativos**, y los personales de Juan José y Niza → **Asesoría con Juan José Alfaro** / **Asesoría
  con Niza Valeriano**. Los slugs no cambian (el embed usa el ID). Rollback en
  `05_ejecucion/snapshots/calendarios-nombres-2026-09-22.json`. **Confirmar los nombres con Mauricio después
  del cutover (no bloquea)** — ver Fase F.
- **Widget en inglés** (días, meses, "Choose Time Slot") → **arreglado el 23/9.** No era por calendario: es
  un ajuste de la cuenta, en Configuración → Calendarios → Preferencias → *Preferencias de cuenta* →
  *Preferencias de widgets* → Idioma: English → **Spanish** (no está en la API). Aplica a los 14 calendarios.
  Verificado en el widget de Intercambio y en el de Juan José: "Seleccione la Fecha & Hora", "Septiembre",
  "Dom. Lun. Mar.…".
- **Duración 30 → 45 min (23/9)**, como la "Reunión con [asesor] · 45 min" de Clientify: `slotDuration` y
  `slotInterval` en 45 por API (serial) en los 10 calendarios de las landings (los 8 de programa + Juan José y
  Niza; no se tocaron los de prueba ni el de Diego). Horarios cada 45 min, asesor asignado intacto. Rollback en
  `05_ejecucion/snapshots/calendarios-duracion-2026-09-23.json`.
- **Cargador nuevo guardado el 23/9** en el funnel (JSON `db18c080-….json`, íconos SVG + logo en GHL):
  verificador 50/50 en `vtr` (el "50/50 en `vtr2`" que se anotó fue un falso positivo, ver A3b); íconos y logo
  revisados en pantalla.

## A3 · Verificar las landings en `vtr.[TU-DOMINIO]` ✅ hecho 23/9

- [x] `/agendar-ema` (formulario): marca, validación de teléfono, el calendario aparece recién al enviar.
  Enviar da error silencioso (W4 está OFF hasta B1): esperado, el calendario igual se revela.
- [x] `/Internados-Calendario?atribuida_a=prueba_a3`: carga el calendario de Internados. Agendar una cita de
  prueba → en GHL el contacto tiene `attributionSource.url` con `atribuida_a=prueba_a3` → cancelar la cita. -> 🔴 no guardó atribuida_a
  - **Revisado 23/9 (Claude): la atribución sí se guardó.** Cita `MAysiFAmUkc0CMlnPomy`, contacto
    `YIv9OmbKw2vtXHdX9OOO`: `lastAttributionSource.url` =
    `https://vtr.[TU-DOMINIO]/Internados-Calendario?atribuida_a=prueba_a3`. Queda en `lastAttributionSource` y
    no en `attributionSource` porque el contacto ya existía (lo creó el import del 3/9): `attributionSource` es
    el primer contacto y `lastAttributionSource` el último. Para un lead nuevo cae en `attributionSource`.
  - **El campo `atribuida_a` del contacto queda vacío en las landings de calendario, y eso es a propósito.** Sólo lo
    completa W4, el de las landings de formulario. Para las de calendario, la fuente es la URL:
    `reporte-aventureras.py --full` lee `lastAttributionSource.url` y, si ahí no está, `attributionSource.url`
    (es lo que reemplazó al workflow deprecado `Fallback · atribuida_a desde attributionSource`). Si hace falta
    que el asesor vea `atribuida_a` en la ficha del contacto, hay que sumarlo a W6: **pedido por la agencia, quedó como
    pendiente después del cutover en la Fase F**, con la especificación armada.
  - Cita de prueba cancelada por la agencia (23/9).
- [x] `/PathwayAlemania-Calendario` y `/ViajesEducativos-Calendario`: **son los 2 embeds que armé yo** (no
  vinieron de tu lista). Confirmar que carga el calendario correcto.
- [x] `/agendar-AlinaBuendia`: 5 botones. Apuntan a `promo.venttur.com/...` (hoy Clientify, 404 ahí): es
  esperado hasta B5.
- [x] En celular: nada desbordado; la página de GHL no agrega márgenes raros alrededor.
- [x] Un link viejo de Clientify ya redirige en el dominio de pruebas (los 205 redirects están ensayados ahí):
  `vtr.[TU-DOMINIO]/agendar-abuendia-afamilia` → Intercambio con `atribuida_a=AlinaBuendia`, y
  `vtr.[TU-DOMINIO]/PW_Alemania_Agendar` → el formulario de Pathway.

Lo automático ya está corrido y en verde (22/9): `verificar-landings-ghl.py` → 50/50, y
`verificar-landings-ghl.py --redirects` → los 205 redirects del dominio de pruebas.

## A3b · Ensayo del cambio de dominio ✅ hecho 22/9

El paso más delicado del día T es que las 50 páginas empiecen a servir en `promo.venttur.com`. Como con `promo`
no se puede probar antes de T, se ensayó el trámite completo con un subdominio nuestro (`vtr2.[TU-DOMINIO]`,
CNAME → `sites.ludicrous.cloud` en Hostinger). Lo que se aprendió, y que ya está volcado en B5:

- **Conectar y enlazar el dominio basta:** las páginas pasaron a servir en `vtr2` **en ~1 minuto** (certificado
  incluido), sin publicar página por página.
- ⚠️ **Corrección 23/9: NO es aditivo.** El funnel sirve sólo en su **dominio principal**; en los otros dominios
  enlazados cada ruta responde 301 a `https://<principal>/programas`. El "50/50 en los dos" del 22/9 fue un falso
  positivo: el verificador seguía el redirect y `/programas` tiene el cargador (corregido: ahora no sigue
  redirects). Consecuencia para B5: cuando `promo` pase a principal, `vtr.[TU-DOMINIO]` deja de servir las
  landings. Por eso B5 suma el **puente** (paso 9): redirects en `vtr` de cada landing a la misma ruta en `promo`.
  Un redirect en un dominio no principal sí funciona y conserva el query (probado 23/9 en `vtr2`).
- **El funnel tiene un dominio "principal"** (Configuración → Dominio) y **el último dominio enlazado pasa a
  serlo**. Importa por una sola razón: la página 404 redirige a `https://<principal>/programas`. Con `vtr2`
  como principal, una ruta inventada en `vtr` mandaba a `vtr2`. Por eso en B5 hay que confirmar que el
  principal quedó en `promo.venttur.com`.
- **Cambiar el principal a mano** (Configuración → Dominio → Guardar) pide dos confirmaciones: aviso de que se
  borran variaciones de pruebas A/B (no hay ninguna) y escribir `CHANGE`. El desplegable a veces necesita dos
  clics para tomar la opción.
- Estado final del ensayo: principal de vuelta en `vtr.[TU-DOMINIO]` (sirve las 51), 404 →
  `vtr.[TU-DOMINIO]/programas`; `vtr2` responde 301 a `vtr.[TU-DOMINIO]/programas` en todas las rutas. `vtr2` quedó conectado (no molesta; sirve para otro ensayo). Se puede
  desconectar en GHL y borrar el CNAME cuando se quiera.

## A4 · 8 páginas internas de Clientify ✅ resueltas 23/9 (queda confirmar con Mauricio)

Antes redirigían a `venttur.com`, que era un comodín y no una decisión. Revisadas el 23/9 contra el backup
(`backup-clientify-2026-09/04-landings/html/`) y la configuración pública de los calendarios de Clientify. **Ya no
queda ninguna "interna sin equivalente"** (`INTERNAS` de `preparar-landings-ghl.py` está vacío). Ensayado en `vtr`:
**56 landings y 199 redirects OK**.

| Página | Qué es | Cómo quedó en GHL |
|---|---|---|
| `formularioref` | Google Form embebido | Redirect directo al Google Form (`DIRECTAS`) |
| `ChatHistoria` | App externa en Railway | Redirect directo a la app (`DIRECTAS`) |
| `preparate` | "Prepárate para la llamada", para familias antes de la asesoría | Landing del funnel, con el mismo texto y video |
| `PMR` | Página de venta del programa de referenciadoras ("mamás afiliadas") | Landing del funnel, mismo contenido y orden. PayPal tal cual (`paypal.com/ncp/payment/M3VWZ9E8BC2BG`). El superform de Clientify pasó a un **formulario nativo de GHL** `form-referenciadoras-pmr` (`OOti4mdEUsW79AOIob6r`): nombre, apellidos, teléfono (WhatsApp), email, país y ciudad, botón "Platicar con un asesor" y mensaje de gracias en español |
| `graciasafil` | Gracias del alta de referenciadoras | Landing del funnel (texto) |
| `agendarPMR` | Calendario Clientify `PRA`: "Sesión 1 Referencias Venttur" | Calendario GHL **Plática sobre el programa de referencias** (`POT8dw9E68OnaCRSgplA`), 60 min |
| `CapacitacionRef` | Calendario Clientify `capacitacion1`: "Capacitación inicial Nueva Aventurera" | Calendario GHL **Capacitación inicial para nuevas aventureras** (`W1o9YsO8QdwzG4IBucOF`), 120 min |
| `seguimientoref` | Calendario Clientify `seguimiento`: "Sesión 1 a 1 con Mauricio" | Calendario GHL **Sesión 1 a 1 con Mauricio** (`muGHmcmYz1pPqX5DGkJU`), 45 min |

**Los 3 calendarios** (creados por API en serie; registro y rollback en
`05_ejecucion/snapshots/calendarios-referenciadoras-2026-09-23.json`, config original de Clientify en
`backup-clientify-2026-09/05-calendarios/referenciadoras/`):
- **Asignados a Mauricio** (`cXRMSnBx81rYivxQruKX`): en Clientify los tres eran de `administracion@venttur.com`,
  que en GHL es Mauricio. No es suposición: lo dice el campo `owner` de cada calendario de Clientify.
- Copiados de Clientify: duración (60/120/45), horarios cada 30 min, pausas antes y después, disponibilidad por
  día (lunes a viernes, mañana y tarde, hora de CDMX), 12 h de anticipación mínima y 13-14 días hacia adelante.
- Igual que los de producción: tipo personal, formulario `form-aventurera`, confirmación automática.

**Por qué un formulario de GHL y no W4 para `PMR`:** W4 está apagado hasta H (hoy el formulario no andaría), no
guarda país ni ciudad, y les pondría a las referenciadoras la etiqueta `Form Landing`, la misma que a los leads de
programas (quedarían mezcladas con leads y expuestas a sus automatizaciones). El formulario nativo funciona ya, no
toca n8n y guarda todos los campos del original.

- [ ] 👤 **Confirmar con Mauricio:**
  1. ✅ El programa de referenciadoras (aventureras) **sigue activo** (Max, 23/9). Falta confirmar que Mauricio
     sigue atendiendo los 3 calendarios.
  2. **Revisión de conflictos:** los calendarios de producción la tienen por el Google Calendar conectado de
     Rodrigo y Andrés. Mauricio tiene que conectar el suyo en GHL (Configuración → Calendarios → Conexiones); si
     no, estos 3 calendarios no ven su agenda y pueden ofrecer horarios en los que ya está ocupado.
  3. **Link de la reunión:** en Clientify eran por Google Meet. Los nuevos quedaron con ubicación personalizada
     vacía, igual que los de producción. Con Google conectado se puede pasar a Meet.
  4. **Contenido de `PMR`, que ya venía así del original:** dice "Únete sin costo" y "no necesitas… inversión
     inicial", pero la FAQ dice que sí hay inversión inicial y está el botón de PayPal "Comprar ahora". Conviene
     que decida qué versión es la vigente.
  5. La etiqueta `Prospecto Referenciacion` que Clientify ponía al agendar la plática no se replicó (en GHL haría
     falta un workflow). ¿La usan?
- Cambios de texto menores respecto del original: erratas ("guias", "de llevamos", "Experiancias"), "insights" →
  "ideas" en `graciasafil`, y el link de TikTok, que en el original no era una URL válida (`tiktok.com/venttur_` →
  `tiktok.com/@venttur_`).

## A5 · Workflows GHL publicados que pueden duplicar el inbound ✅ hecho 23/9

Hay **5 workflows publicados** en GHL. Dos son los de Camilo (correctos). Los otros tres son de antes y la API no
deja ver su contenido:

| Workflow | Publicado | Riesgo |
|---|---|---|
| `WF-01 Enrutador de Entrada` (`eb835383…`) | 11/9 | Si su trigger es "mensaje entrante", post-BSP procesa **cada mensaje dos veces** junto con el de Camilo |
| `WF-02 Rescate (disparador)` (`1ed7af47…`) | 11/9 | Si dispara el webhook `vtr-rescate-link`, el rescate sale **duplicado** (W9 ya lo dispara) |
| `WEBHOOK` (`8ba27838…`) | 21/9 | Probablemente apunta a `test - GHL WH Payload` (`2siyKI7xrVYw8H30`, n8n, activo, 0 ejecuciones) |
| `Inbound bot → main-venttur-ghl` (`bf2d731e…`) | 22/9 | ✅ Camilo |
| `Confirmación de cita → W6` (`48592233…`) | 22/9 | ✅ Camilo |

En GHL → Automatización → Flujos de trabajo, abrir cada uno y anotar trigger + acción:
- [x] WF-01, WF-02, WEBHOOK: **si alguno se dispara con mensajes entrantes, citas o links → queda marcado para
  pasar a Borrador en B2.** Si no hacen nada de eso, se dejan.
- [x] `Inbound bot → main-venttur-ghl`: la URL es exactamente
  `https://[TU-INSTANCIA-N8N]/webhook/main-venttur-ghl-44ce5e8a` y **filtra canal = WhatsApp** (si no filtra, un
  mail o un SMS entrante también despierta al bot).
- [x] `Confirmación de cita → W6`: URL `https://[TU-INSTANCIA-N8N]/webhook/vtr-confirmacion-agenda-ghl-a191d178`,
  trigger *Customer Booked Appointment* sobre los 8 calendarios de producción.

## A6 · Credencial OpenAI del bot ✅ hecho 23/9

El modelo del agente (`OpenAI Chat Model` y `Formatear mensaje WPP`) del main nuevo usa la credencial n8n
**`OpenAI | Venttur` (`ibkhdCMyhr3yqDQk`)**, no la rotada (`Venttur - OpenAI`, `4mYcYoPAC42ngJYz`, que sólo
usa `Transcribir audio/s`).

- [x] n8n → Credentials → `OpenAI | Venttur` → mirar el prefijo de la key.
- [x] **Si empieza con `sk-proj-OpKR…`** (la key expuesta que vas a revocar): reemplazarla por la key nueva
  **antes** de revocar la vieja. Si la revocás primero, el bot deja de responder.

## A7 · Logística del BSP 🔴 · 10 min

El procedimiento está en `clients/VTR_Venttur/06_docs/runbook-bsp-migration-waba-2026-09-19.md` (se ejecuta
**desde GHL**, con el popup de Meta — no desde WhatsApp Manager).

- [x] **Quién ejecuta:** una cuenta admin del Portafolio Venttur en Meta (la agencia, `[EMAIL-AGENCIA]`), con
  sesión abierta en `business.facebook.com` **y** en `app.gohighlevel.com` (sub-cuenta Venttur).
- [x] **El código OTP:** lo tiene **Max** (confirmado 23/9), que está con el teléfono para el traspaso de hoy.
  El runbook oficial dice que Meta lo manda **al número** (SMS o llamada), no al mail. Antes: confirmar **quién tiene el chip** del `+52 1 33 2627 4502` y que esté disponible **a la hora H**
  (la del traspaso de WhatsApp, que elegimos nosotros) para leer el código y pasarlo en el momento. Recibir un
  SMS no rompe nada; **instalar WhatsApp sí**. **Es lo único que falta para fijar H.**
- [x] **ManyChat no se cancela** hasta el 27/9: es el camino de vuelta si el BSP falla (runbook §7.1).
- [x] **Avisarle a Mauricio que la ventana deja de ser jueves 09:30 ART fija.** Él y Max saben que en la
  ventana puede haber minutos sin bot.
- [ ] **Avisarle a Mauricio la hora H** (desde el 23/9 ya no es la de la agencia) y qué cambia hasta T: el agente
  manda links de `vtr.[TU-DOMINIO]` (misma landing, con la marca de Venttur; sólo cambia el dominio).

## A8 · Aviso a los asesores · 5 min

Mensaje a Rodrigo y Andrés (vía Mauricio), con H ya fijada: *"Desde el [día, hora] el WhatsApp de Venttur
pasa a GHL: las conversaciones, los contactos y las oportunidades se trabajan en GHL, y las citas que agende el
bot entran en los calendarios de GHL. **Si toman una conversación, pónganle al contacto la etiqueta
`bot_pausado`: si no, el bot sigue contestando. Para devolvérsela al bot, sáquenla.** Cuando el bot pasa una
conversación a una persona, la etiqueta la pone él solo. Hasta que cambiemos el dominio de las landings (les avisamos), algunas citas
todavía pueden entrar por Clientify: las que vienen de anuncios o de links de aventureras. Revisen también el
calendario de Clientify. No carguen ni muevan oportunidades nuevas en Clientify: queda de consulta y se apaga
el sábado."*

Sin este aviso, lo que muevan en Clientify desde H se pierde (o obliga a un segundo delta en D1). Las citas que
entren por Clientify después de B6 no reciben la confirmación por WhatsApp del sistema viejo (salía por ManyChat,
que ya no tiene el número): el asesor la confirma a mano. Los recordatorios de Clientify siguen saliendo, porque
Clientify los manda desde su propio número.

## A9 · Presupuestos: lo que tiene que pasar Venttur 🔴 para D2

**Actualizado 23/9 tarde.** Leímos por API los 242 presupuestos de Clientify (lectura, sin tocar nada) y de ahí
salieron los datos bancarios, los términos, el emisor y el IVA. Ya no hace falta pedirles un presupuesto real
ni confirmar el IVA. Quedan 3 cosas que sólo ellos pueden resolver:
- [ ] **Cuentas bancarias.** Hoy cada asesor pone una distinta: Rodrigo **Banorte** (…3098), Juan José **BBVA**
  (…1809) y Andrés **Banamex + Banorte**. Las 3 son de GARDE. Que confirmen que siguen vigentes y si se queda
  así (una por asesor) o unifican. Las plantillas ya están armadas así; si cambia, se edita el texto.
- [ ] **Mercado Pago.** Es con lo que cobran con tarjeta en Clientify (37 de 47 presupuestos no vencidos) y GHL
  lo tiene como integración nativa, hoy sin conectar. Lo conecta quien tenga el acceso a la cuenta de Mercado
  Pago, en una llamada de 5 min con nosotros (GHL → Pagos → Integraciones → Mercado Pago). Primero en prueba.
- [ ] **Presupuestos pendientes de cobro.** Clientify no marca como pagados los que entran por transferencia
  (quedan "vencidos" o "aceptados"), así que no se puede saber por datos. De los 12 del 19/8 en adelante (lista en
  `06_docs/presupuestos-clientify-a-ghl-2026-09-22.md`), que digan cuáles **no** pagaron: esos se reemiten en
  GHL antes de apagar Clientify.

## A11 · Revisión E2E del stack nuevo ✅ hecho 23/9 tarde

El main nuevo nunca se había ejecutado con un payload de GHL (el staging se probó por Telegram, con otra entrada).
Revisado nodo por nodo, **no respondía ningún mensaje**:
1. `Check dedup` (un SELECT sin filas) no emitía ítems → el flujo moría en el primer nodo Postgres y GHL no recibía
   respuesta del webhook.
2. La entrada del bot pasaba por la cadena de Airtable y leía `body.custom_fields.respuesta_definitiva`, un campo
   de ManyChat → TypeError con el payload de GHL.
3. `Enviar WPP` mandaba `$json.parte1`, pero `Normalizar burbujas` devuelve `mcBody`/`texto` → mensaje vacío.

Parches (`scripts/batches-2026-09-23/vtr_pre_bsp_fixes.py`, idempotente; snapshots pre/post + sha256 en
`03_workflows/ghl-live-2026-09-23-pre-bsp-fixes/`). Todo sigue OFF.

| Workflow | Qué cambió |
|---|---|
| **main** `1eS1Z5k898c3ATnf` | Los 3 de arriba. La entrada del bot va directo de GHL al agente; Airtable queda como rama lateral que no puede cortarlo. Audios: el texto sale del webhook y los adjuntos del último mensaje entrante (API de GHL), porque la acción Webhook no siempre los trae. Una burbuja = un mensaje de WhatsApp, en orden y con 1,5 s entre cada una. **Pausa por tag `bot_pausado`**: si el contacto lo tiene, el bot no contesta. Guardrail de promesa fantasma: estaba muerto también en producción (leía `parte1` y el formateador lo devuelve en `message.content`); ahora corre, con el estado desde GHL y en tuteo. El filtro de nombre repetido borraba "ana" de "mañana" con una lead llamada Ana (también en producción). |
| **elevar** `v9XkOfL9dQtY2wyv` | `dnd:true` → tag `bot_pausado`. El DND de GHL bloquea también los mensajes del asesor, y el main no lo miraba (el bot seguía contestando). Telegram sin Markdown (un `_` del resumen rompía el aviso) y con link al contacto en GHL. |
| **W6** `AS9ZNhY3GJDfhY3P` | `{{appointment.start_time}}` llega formateado en inglés, no ISO → la fecha se toma de la API (cita más reciente del contacto) y el link de Meet también. **La cita se marca aunque el WhatsApp de confirmación no salga** (fuera de la ventana de 24 h, por ejemplo quien agenda desde un anuncio sin haber escrito): antes, sin marca, el rescate le escribía "no agendaste". |
| **rescate** `YB0UxwEVwzISdd54` | Los 12 mensajes llevaban links a `promo` (la guía decía que no): pasados a `vtr`; `dominio-links-agente.py --a promo` los vuelve en B5. Fase 2 a las 22 h (antes 24 h: a las 24 h 45 min del link un mensaje libre ya no sale por WhatsApp). Credencial GHL unificada al PIT. No rescata a quien tiene `bot_pausado` o está Cerrada. Memoria en el formato real de LangChain (`{type, data:{content}}`): con `{type, content}` el agente la leía vacía. |
| **despachador** `vrShEXQGGAo4FqAt` | No toca contactos con `bot_pausado`. |
| **clasificador** `Xmyoewwa1W5gm1fy` | Un solo resumen por contacto que se actualiza (antes: una nota nueva por cada mensaje del lead). Credencial OpenAI de Venttur (usaba la de la agencia). |
| **W14** `OaOyHA2tfjMtuWTk` | Faltaba el header `Version` en la consulta a GHL. |

Verificado sin prender nada: los 18 Code nodes compilan y se corrieron con payloads de ejemplo (texto, audio,
imagen, pausa, promesa fantasma, cita con fecha en 3 formatos, rescate con y sin pausa); los endpoints nuevos de
GHL responden con el PIT (conversaciones, mensajes, citas, notas); los 20 custom fields que usan existen.

**Lo que no se puede arreglar desde n8n:**
- **El bot no ve imágenes** (tampoco el de ManyChat): responde que no puede verlas.
- **Cuando un asesor toma una conversación, el bot sigue contestando** salvo que el contacto tenga el tag
  `bot_pausado`. ManyChat lo pausaba solo; GHL no. Va en el aviso de A8.

## A12 · Prueba E2E del main 🔴 · 10 min · antes de B3

Lo único de A11 que no se probó de punta a punta: el main recibiendo un POST como el de GHL. Se hace con el main
prendido (B1 lo prende igual) y el contacto de prueba **la agencia Test** (`YIv9OmbKw2vtXHdX9OOO`). Sin WhatsApp en GHL
todavía, `Enviar WPP` va a fallar con un error de canal: es lo esperado, y el error confirma que el cuerpo del
mensaje llegó bien armado.

```bash
curl -s -X POST https://[TU-INSTANCIA-N8N]/webhook/main-venttur-ghl-44ce5e8a -H 'Content-Type: application/json' -d '{"contact_id":"YIv9OmbKw2vtXHdX9OOO","phone":"59899999999","message":{"body":"Hola, me interesa el programa de internados para mi hija de 14"},"contact":{"firstName":"la agencia"}}'
```

En n8n → Executions del main:
- [ ] Llega hasta `Enviar WPP` (el agente respondió y se armaron las burbujas); el error de `Enviar WPP` es de canal
  de WhatsApp, **no** de `message` vacío.
- [ ] Hay ejecuciones de W11 (Estado Contestó) y del clasificador; en GHL, la agencia Test tiene `Contestó` y **una** nota
  "🤖 Resumen del bot".
- [ ] Mandar un segundo mensaje: el clasificador **actualiza** la misma nota (no crea otra).
- [ ] Ponerle el tag `bot_pausado` a la agencia Test y mandar otro: la ejecución termina en `¿Bot pausado?` sin llegar al
  agente. Sacar el tag.

Efecto secundario: la rama de Airtable crea una fila "la agencia Test" en Leads (base que se deja de usar).

**Resultado (23/9 noche, 6 mensajes de prueba a la agencia Test).** Todo en verde al final, después de corregir 5 fallas
que sólo aparecían ejecutando de verdad (scripts en `batches-2026-09-23/`, pre/post en la misma carpeta de snapshots):
1. `Compute idempotency hash` usaba `require('crypto')`, que este n8n bloquea en los Code nodes → el main fallaba
   en el 2.º nodo (`vtr_fix_hash_sin_crypto.py`).
2. 9 HTTP Request con `jsonBody` sin `specifyBody: json` mandaban `{"": ""}`: el envío de WhatsApp del main, el
   upsert de W4 y W10, confirmación y marca de W6, pausa y asignación de elevar, W9 (`vtr_fix_specify_body.py`).
3. 16 HTTP Request con los headers en el formato de las tools (`parametersHeaders`) no mandaban `Version` → 401
   silencioso (con onError=continue): despachador, barrido, clasificador y W11 no escribían ni leían nada.
4. La memoria de n8n guarda `{type, content}` plano; la consulta del clasificador leía `data.content` (conversación
   vacía). Revertido además el cambio de formato del rescate de A11, que era incorrecto (`vtr_fix_formato_memoria.py`).
5. El guardrail revivido interceptaba preguntas ("¿te queda hoy o mañana para agendar?"): ahora sólo mira oraciones
   afirmativas (`vtr_fix_headers_y_guardrail.py`).

Verificado: respuesta del agente en 3 burbujas aceptadas por GHL (quedan `failed` porque WhatsApp todavía no está
en GHL), W11 → `Contestó`, clasificador → una sola nota que se actualiza + tipo de contacto, W9 → `link_enviado` +
etiquetas, `bot_pausado` corta antes del agente. El rescate de ese link corre 45 min después sobre la agencia Test.

## A10 · Ensayo en seco ✅ hecho 23/9

```bash
python3 $S/cutover-toggles.py --verify
```

Tiene que mostrar los 6 viejos ON y los 9 nuevos OFF. Después:

```bash
python3 $S/cutover-toggles.py --solo-on
```

```bash
python3 $S/cutover-toggles.py --landings-on
```

Dry-run, no tocan nada. `--solo-on` lista **8** (todos los nuevos **menos el rescate**); `--landings-on` lista
**3** (W4, CAPI folio Supabase y el rescate `YB0UxwEVwzISdd54`). (El script prende lo nuevo antes de apagar lo
viejo y no intenta activar sub-workflows: n8n los ejecuta igual estando inactivos, y activarlos daba error.)

---

# FASE B · WhatsApp (hora H, la elegimos nosotros)

**H la fija la agencia** con quien tenga el chip del número (A7). No depende de la agencia. Conviene horario laboral de
CDMX con poco tráfico, y que la agencia o Camilo estén conectados ~1 h. **Hacerlo antes que T, o el mismo día:** si el
DNS cambiara días antes de H, el agente viejo (ManyChat) mandaría a landings de GHL y su rescate, que mira
Airtable, le escribiría "no agendaste" a quien sí agendó.

| Hora | Paso |
|---|---|
| H − 20 min | B0 · snapshot |
| H − 15 min | B1 · `--solo-on` (stack nuevo) |
| H − 10 min | B2 · links del agente → `vtr.[TU-DOMINIO]` + `--landings-on` (W4, CAPI folio Supabase, rescate) |
| H | B3 · BSP |
| H + 15 min | B4 · smoke por WhatsApp |
| H + 30 min | B6 · `--solo-off` (con B4 en verde) |
| H + 35 min | B7 · anuncio |

### Verificación pre-H · hecha por Claude el 23/9 (sólo lecturas, nada escrito)

Todo lo que depende de nosotros está en su lugar para arrancar B0:

| Qué | Estado |
|---|---|
| n8n viejos | 6 🟢 ON (siguen atendiendo hasta B6) |
| n8n nuevos | 9 ⚪ OFF, listos para B1/B2 |
| Links del main nuevo | 19 en `promo.venttur.com`, 0 en `vtr` → B2 los pasa (dry-run OK) |
| Main nuevo (`1eS1Z5k898c3ATnf`) | webhook `main-venttur-ghl-44ce5e8a` (el mismo que llama `Inbound bot` en GHL); `Enviar WPP` con la credencial `GHL VTR (PIT)`; modelo con `OpenAI \| Venttur` (A6) |
| Webhooks encadenados | W9 → `vtr-rescate-link` = webhook del rescate · `Confirmación de cita` (GHL) → `vtr-confirmacion-agenda-ghl-a191d178` = webhook de W6 |
| Despachador | 3 nodos de envío deshabilitados (corre en dry-run hasta C2) |
| GHL | WF-01, WF-02 y WEBHOOK en **Borrador**; `Inbound bot`, `Confirmación de cita`, `Handoff`, `Fallback` y los 23 de Rodrigo **publicados** |
| Meta CAPI | El nodo `Meta CAPI` del main llama al CAPI viejo (`z98w2…`), igual que el main de ManyChat. Tiene el disparador deshabilitado: la ejecución termina en el Trigger y no manda nada (verificado en las ejecuciones de hoy). No es un error; es el frente de la Fase F |
| Plantillas Meta | **No verificables por API**: el token `VTR_META_WABA_TOKEN` del `.env` venció el 19/9. Se ven en GHL en B3 (tienen que ser 11 `Approved`). Renovar el token no es necesario para el traspaso |

**Actualización 23/9 tarde:** esta verificación no alcanzaba (eran sólo lecturas de configuración, sin ejecutar el
main). La revisión de A11 encontró que el main no respondía y quedó parcheado. Antes de B0 quedan **A12** (prueba
E2E del main) y **A8** (aviso a los asesores con la hora y la etiqueta `bot_pausado`).

**Reglas de aborto:**
- Si algo del bloque B3-B4 falla y no se resuelve en 15 min: rollback (tabla al final). Ventana de aborto: hasta
  60 min después de B6.
- B5 (DNS) no forma parte de esta ventana. Si la agencia avisa el cambio en medio, terminar B3-B7 primero:
  mientras B5 no se complete, `promo` muestra error sólo a quien ya resuelva al dominio nuevo.

## B0 · H − 20 min · Snapshot

```bash
python3 $S/snapshot-workflows.py clients/VTR_Venttur/03_workflows/ghl-live-2026-09-23-pre-cutover
```

(Ya con la fecha de hoy, 23/9.)

## B1 · H − 15 min · Prender el stack nuevo

```bash
python3 $S/cutover-toggles.py --solo-on --execute
```

Prende 8 (todos los nuevos menos el rescate, que va en B2). Es inocuo antes del BSP: sin WABA en GHL no entra
tráfico de WhatsApp, el despachador corre en dry-run (sus 3 nodos de envío están deshabilitados) y W4 sólo recibe
de las landings nuevas. **Si alguno da ✗:** anotar el código y seguir; se reintenta en B6.

GHL → Automatización: tienen que seguir en Borrador WF-01, WF-02 y WEBHOOK (A5). Ya lo están desde el 23/9.

## B2 · H − 10 min · Links del agente a `vtr.[TU-DOMINIO]` + landings y rescate ON

**Si B5 ya está hecho** (la agencia cambió el DNS antes de H): saltear el primer comando. El agente ya manda a
`promo`, que sirve GHL.

```bash
python3 $S/dominio-links-agente.py --a vtr --execute
```

Cambia 19 links en 3 nodos del main: el prompt (`Agente IA WPP`), el guardrail `Detectar promesa fantasma` y el IF
`Envió link?` que dispara W9. Tiene que terminar en `✅ 19 links pasados a vtr.[TU-DOMINIO] · quedan 0`. Guarda
el main anterior en `05_ejecucion/snapshots/`.

```bash
python3 $S/cutover-toggles.py --landings-on --execute
python3 $S/cutover-toggles.py --verify
```

Los 9 nuevos en 🟢, **rescate incluido**. El rescate ya se puede prender: el agente manda a landings de GHL, así
que una cita agendada desde su link queda en GHL y el rescate la ve. `Formulario Clientify` y `CAPI Registro Folio
(Airtable)` viejos **siguen prendidos** hasta B5.8: `promo` todavía sirve Clientify y sus formularios los usan.

## B3 · H · BSP: WABA → GHL 🔴

Seguir `06_docs/runbook-bsp-migration-waba-2026-09-19.md` §3 (8 pasos en GHL → Settings → WhatsApp →
*Migrating from an existing BSP*): popup de Meta → Portafolio Venttur → WABA `1931874540684022` → número
`+52 1 33 2627 4502` → datos del negocio → **OTP al número** (A7) → confirmar.

Verificación (runbook §4), en los primeros 15 min:
- [ ] GHL → Settings → WhatsApp: WABA `1931874540684022`, número y nombre correctos.
- [ ] Plantillas: **11** en `Approved` (calidad `UNKNOWN` las primeras 24 h es normal).
- [ ] Anotar la hora: `BSP OK · HH:MM`.

**Si falla:** errores documentados en el runbook §8 (display name `131037`, 2SV, OTP). **Si queda "in transit"
más de 30 min: no reintentar** (duplica el pedido); ticket a Meta y a GHL, y rollback (tabla).

## B4 · H + 15 min · Smoke real por WhatsApp 🔴 · 10 min

Desde un celular que **no** sea de un lead real, al `+52 33 2627 4502`:
1. `Hola`
2. `Estoy interesado en el programa de Internados`
3. `Quiero agendar una cita`
4. Una foto
5. Una nota de voz de ~15 s

Verificar:
- [ ] Llegan las 5 respuestas, coherentes, sin re-saludo en el 2.º mensaje.
- [ ] La nota de voz se entendió (transcripción). La foto: el bot dice que no puede verla (no ve imágenes).
- [ ] GHL → Conversaciones: aparece la conversación completa, entrante y saliente.
- [ ] GHL → contacto: `Programa` = Internados; `Estado conversación` = Contestó.
- [ ] n8n → Executions de `main-venttur-ghl`: 5 ejecuciones en verde (o las que agrupe el debounce), **ninguna
  duplicada** (si hay dos por mensaje, hay un segundo workflow GHL disparando: revisar A5).
- [ ] El link de agendamiento que manda el bot es `vtr.[TU-DOMINIO]/…` (o `promo.venttur.com/…` si B5 ya está)
  y **abre la landing de GHL**.
- [ ] n8n → Executions de W9 (`TROsQ5h78baAuVOY`) de ese link: **en verde** y aparece una ejecución del rescate.
  Si no se agenda, a los 45 min le llega el rescate al celular de prueba: es el caso 8 de C3.

**Si el bot no responde:** Executions del main. Sin ejecuciones → el workflow GHL de Camilo no está disparando
(URL o filtro de canal). Con ejecuciones en rojo → el nodo en rojo dice qué falló. `Enviar WPP` en rojo con
error de sintaxis de la API de GHL → avisar por el grupo `-4925599962` y se parchea en el momento.

## B6 · H + 30 min · Apagar el stack viejo del agente

Recién con B4 en verde:

```bash
python3 $S/cutover-toggles.py --solo-off --execute
python3 $S/cutover-toggles.py --verify
```

Viejos del agente en ⚪ (main ManyChat, confirmación vieja, outreach viejo, interrumpida), nuevos en 🟢.
`Formulario Clientify` y `CAPI Registro Folio (Airtable)` **siguen prendidos** hasta B5.8. Si en B1 alguno había
dado ✗, correr `--solo-on --execute` otra vez.

## B7 · H + 35 min · Anuncio

Al grupo `-4925599962` y a Mauricio: *"WhatsApp en GHL desde las HH:MM. El bot atiende desde GHL con el mismo
número. Hasta que la agencia cambie el dominio, los links del bot son de vtr.[TU-DOMINIO]. Cualquier cosa rara,
avisen acá."*

## Rollback (WhatsApp)

| Falló | Qué hacer |
|---|---|
| B0-B2 (antes del BSP) | `cutover-toggles.py --rollback --execute` (apaga lo nuevo; lo viejo sigue ON). Los links del main pueden quedar en `vtr`: el main queda apagado. Reagendar H. |
| B3 (BSP no completa) | La WABA sigue en ManyChat. `--rollback --execute`. Reagendar el BSP en ≤ 24 h. |
| B4 (el bot no responde y no se arregla en 15 min) | Volver la WABA a ManyChat (runbook §7.1: Embedded Signup desde ManyChat) + `--rollback --execute`. |
| Respuestas parciales (audio, foto, un campo) | **No volver atrás.** Incidente en el grupo y parche del nodo puntual. |

Snapshot de referencia: el de B0.

---

# B5 · DNS de `promo.venttur.com` → GHL (hora T, la de la agencia)

Va cuando la agencia avise el cambio del CNAME, antes o después de H (mejor después, ver el inicio de la Fase B).
Hay que hacerlo en el acto: entre el cambio y el final de este paso, `promo.venttur.com` muestra un error de GHL
para quien ya resuelva al dominio nuevo. la agencia o Camilo, ~15 min.

1. Confirmar que el cambio está:

```bash
dig +short promo.venttur.com CNAME @ns1.dns-parking.com
```

   Tiene que devolver `sites.ludicrous.cloud.`

2. GHL → Configuración → **Dominios y redirecciones de URL** → **Conectar un dominio** → Embudo/Sitio web →
   Conectar → Dominio `promo.venttur.com` → Continuar → **Añadir registro manualmente** (no "Continuar": ése
   intenta entrar a la cuenta de DNS) → **Verificar registros**. Tarda ~30 s; si dice que no encuentra el
   registro, esperar 1-2 min y reintentar (TTL 300). *Ensayado en A3b con `vtr2`.*
3. En la misma pantalla ("¡Felicidades! ahora conectá … con un Producto"):
   - Tipo de producto: **Embudo** · Enlazar el embudo: **`LP · Calendarios`**
   - Página por defecto del dominio: **Programas** (viene preseleccionada Internados-Calendario: cambiarla)
   - Opciones adicionales → Página 404: **`LP · Calendarios / Programas`**
   - **Continuar para finalizar** (~1 min, incluye el certificado).

   Esto ya deja las páginas sirviendo en `promo`. **`vtr.[TU-DOMINIO]` deja de servirlas** (el funnel sólo
   sirve en el principal): los links de `vtr` que mandó el agente vuelven a andar con el puente del paso 9. Red de
   seguridad: cualquier link viejo que no conozcamos cae en
   Programas (los 8 programas + WhatsApp), no en un error.
4. Controles inmediatos (los tres tienen que dar bien antes de seguir):

```bash
python3 $S/verificar-landings-ghl.py --dominio promo.venttur.com                       # 56 OK
curl -sI "https://promo.venttur.com/ruta-inventada?atribuida_a=x" | grep -i location    # → https://promo.venttur.com/programas?atribuida_a=x
```

   - Funnel `LP · Calendarios` → Configuración → **Dominio** tiene que decir `promo.venttur.com` (el último
     dominio enlazado pasa a ser el principal, y de él sale el destino del 404). Si dice otro: elegir
     `promo.venttur.com` (el desplegable puede necesitar dos clics) → Guardar → aceptar el aviso de pruebas A/B
     → escribir `CHANGE` → Sí, cambiar. Repetir el `curl`.
   - Si alguna página diera 404 en el verificador (no pasó en el ensayo): abrirla en el editor → Publicar.
5. Webhooks de landings nuevos y rescate: si B2 ya se hizo, ya están prendidos. Si B5 va antes que H, prenderlos
   ahora (los formularios de `promo` necesitan W4 y CAPI folio Supabase):

```bash
python3 $S/cutover-toggles.py --landings-on --execute
```

6. Redirects de los 199 paths viejos (API, en serie, idempotente, ~2 min; ensayados en `vtr.[TU-DOMINIO]`).
   Incluyen los 2 con guion bajo (`/EstudiaryTrabajar_Agendar`, `/PW_Alemania_Agendar`) que usan el agente y las
   plantillas de Meta. Son **301**: el navegador los recuerda, así que revisar `landings-ghl/_ghl/REDIRECTS.md`
   antes de crearlos.

```bash
python3 $S/crear-redirects-ghl.py --execute
python3 $S/verificar-landings-ghl.py --redirects --dominio promo.venttur.com   # 199 OK
```

7. Verificación:
   - [ ] `curl -sI https://promo.venttur.com/agendar-ema | head -1` → `200`.
   - [ ] `curl -sI https://promo.venttur.com/agendar-abuendia-afamilia | grep -i location` →
     `/Intercambio-Calendario?atribuida_a=AlinaBuendia`.
   - [ ] `curl -sI https://promo.venttur.com/PW_Alemania_Agendar | grep -i location` → `/PW-Alemania-Agendar`
     (link del agente y de plantillas Meta).
   - [ ] Formulario real en `https://promo.venttur.com/agendar-ema?atribuida_a=smoke_dns` → en GHL aparece el
     contacto con `atribuida_a = smoke_dns` (W4) y el calendario abre prellenado. Agendar una cita de prueba →
     **cancelarla**.
   - [ ] `https://promo.venttur.com/un-path-inventado?atribuida_a=x` → página Programas; sus botones llevan `?atribuida_a=x`.
8. **Links del agente de vuelta a `promo`** (si B2 ya los había pasado a `vtr`):

```bash
python3 $S/dominio-links-agente.py --a promo --execute
```

   Tiene que terminar en `✅ 19 links pasados a promo.venttur.com · quedan 0` (main) y `✅ 12 links pasados a
   promo.venttur.com · quedan 0` (rescate, desde el 23/9 el script también lo cubre). Probar: pedirle un link al bot
   desde el celular de prueba → llega `promo.venttur.com/…` y abre la landing de GHL.
9. **Puente `vtr` → `promo`** (recién ahora, con `promo` como principal: antes rompería `vtr`). Los links de
   `vtr.[TU-DOMINIO]` que el agente mandó antes de B5 siguen llevando a su landing:

```bash
python3 $S/crear-redirects-ghl.py --puente --execute        # 56 redirects en vtr.[TU-DOMINIO]
curl -sI "https://vtr.[TU-DOMINIO]/agendar-ema?atribuida_a=x" | grep -i location   # → https://promo.venttur.com/agendar-ema?atribuida_a=x
```

10. **B5.8 · T + 4 h**, con la propagación completa: apagar los webhooks viejos de landings.

```bash
python3 $S/cutover-toggles.py --landings-off --execute
```

**Rollback de B5** (el dominio no verifica o no sale el certificado en 30 min): pedirle a la agencia que vuelva
el CNAME a `clientify.dony.clearalias.com` (mientras tanto `promo` está caído: es P1). No correr los pasos 8 ni 9: los
links del agente siguen en `vtr` y WhatsApp no se entera. Reagendar con la agencia.

---

# FASE C · POST (desde H)

## C1 · Flujos de Rodrigo ✅ publicados 22/9

Verificado por API el 23/9: los 23 (EMA · Agendó Cita + 10 de Idiomas + 12 de Internados) están publicados.

- [x] GHL → Automatización → Flujos de trabajo → cada uno → **Publicar**.
- **Dos más que la guía decía no publicar también quedaron publicados.** Revisados en la UI el 23/9:
  - `Handoff · Notificación al equipo` ✅ **queda así.** Con la etiqueta de atención humana manda 3 notificaciones
    internas por mail a los usuarios Max Almonte y Mauricio García. Ya no espera los mails del staff.
  - `Fallback · atribuida_a desde attributionSource` ⚠️ **decidir.** Con cualquier cita reservada en los
    calendarios corre un Código personalizado (acción *premium*: GHL cobra cada ejecución), que saca el slug de
    **`Attribution.First.Url`**, y después *Update contact field* → `atribuida_a` = ese slug, **sin condición**.
    Dos problemas: (1) sólo funciona si el contacto es nuevo; en la prueba de A3 (contacto ya existente) no llenó
    nada, porque la URL con el slug quedó en la *última* atribución; (2) si el slug sale vacío, puede pisar con
    vacío el `atribuida_a` que escribió W4 en una landing de formulario (formulario → calendario). Opciones:
    **(a)** pasarlo a Borrador y hacer lo de W6 en la Fase F; **(b)** arreglarlo acá. **la agencia eligió (b) el 23/9.**
  - [x] 🤖 **Arreglo del Fallback (b) aplicado por Claude el 23/9** (sigue publicado, versión 7). Probado en el
    probador de código de GHL: la última visita con slug gana (`AlinaBuendia`, aunque venga con `?fbclid`) y, sin slug, conserva el valor actual. Falta la prueba real del paso 6. Lo que se hizo:
    1. Dejar la propiedad `attribution_url` como está (es `{{contact.attributionSource.url}}`, la primera).
    2. **Añadir propiedad** `latest_url` = `{{contact.lastAttributionSource.url}}` (escribirlo a mano: el
       selector de valores no lista los campos de atribución; la sintaxis sale de la [lista de merge fields de
       GHL](https://help.gohighlevel.com/support/solutions/articles/48001078171-list-of-merge-fields)).
    3. **Añadir propiedad** `actual` = `{{contact.atribuida_a}}`.
    4. Reemplazar el código por:
       ```js
       const pick = (u) => { const m = String(u || "").match(/[?&]atribuida_a=([^&#?]+)/); return m ? decodeURIComponent(m[1]) : ""; };
       const slug = pick(inputData.latest_url) || String(inputData.actual || "").trim() || pick(inputData.attribution_url);
       return { atribuida_a: slug };
       ```
       Prioridad: el link de esta reserva → el valor que ya tenía el contacto (W4 u otra reserva) → el primer
       link. Si no hay nada, queda vacío como antes (no hay valor que perder).
    5. **Guardar acción** → **Guardar** el workflow (sigue publicado). `Update contact field` no se toca.
    6. [x] Prueba real (la agencia, 23/9). La primera vez dejó el campo **vacío**: al editar el código, la referencia
       vieja de *Update contact field* (`customCode.atribuida_a`, chip naranja) dejó de resolver y escribió vacío.
       Se volvió a elegir desde el selector: *Custom Code › #1 Código personalizado › Output › Atribuida A* (chip
       azul). Re-probado con "Probar flujo de trabajo" sobre el contacto de prueba → `atribuida_a = prueba_fb` ✅.
       **Ojo si se vuelve a tocar el código: re-elegir la salida en el paso siguiente.** Prueba original: agendar en `vtr.[TU-DOMINIO]/Internados-Calendario?atribuida_a=prueba_fb` con un contacto que ya
       exista → en GHL el contacto queda con `atribuida_a = prueba_fb` → cancelar la cita.
- `New Workflow : 1790059926444` (vacío) ya no existe.
- [ ] Smoke: a un contacto de prueba agregarle la etiqueta `necesita visa` → su oportunidad en
  `Operativo Idiomas` pasa a `Tramitar Visa`. Sacarle la etiqueta después.

Los que se disparan con presupuestos (`IDIOMAS · Presupuesto aceptado`, `INTERNADOS · Presupuesto abierto/pagado`)
quedan publicados pero no disparan hasta que exista D2 (revisar sus disparadores en D2 punto 5).

## C2 · Despachador proactivo · 10 min + 2-3 h de observación

**🔴 Gate: habilitar el envío sólo con B2 hecho** (los links del agente apuntan a landings de GHL, en `vtr` o en
`promo`). El carril `rescate` del despachador elige por `link_enviado = true` y sólo excluye a quien tiene la cita
en GHL: si el agente mandara a una landing de Clientify, le escribiría a gente que ya agendó. Las plantillas del
despachador y del rescate no llevan links (verificado 23/9), así que no dependen del DNS.

El despachador `vrShEXQGGAo4FqAt` quedó prendido en B1 **sin enviar nada** (dry-run). Ya tiene aplicada la
política de recontacto (22/9), que corrige dos problemas del motor original:
- **Toques pegados:** el gate no miraba la fecha del último toque; con el cron horario, un lead recibía sus 2
  toques con **1 h de diferencia**. Ahora hay un mínimo de **24 h** entre toques.
- **Históricos:** un lead importado sin fecha de actividad pasaba el filtro. Ahora rescate/nurturing exigen
  actividad en los últimos 30 días, y outreach exige un Touch 1 de los últimos 30 días. Sin fecha, no se toca.

1. [ ] Dejar pasar 2-3 corridas (es horario). n8n → Executions del despachador → nodo `Tiene templateId?`:
   cuántos items salen por la rama verdadera y de qué carril (`rescate` / `nurturing` / `outreach`). Tiene que
   ser un número chico y razonable, no cientos.
2. [ ] Si el número cierra **y B2 está hecho**:

```bash
python3 $S/batches-2026-09-22/vtr_post2_despachador.py --habilitar-envio --execute
```

3. [ ] En la siguiente corrida: nodo `Enviar template GHL` en verde con `messageId`. **Si da error** (por
   ejemplo, porque la plantilla exige variables y el nodo no las manda): freno de mano y avisar.

```bash
python3 $S/batches-2026-09-22/vtr_post2_despachador.py --deshabilitar-envio --execute
```

Los programas sin plantilla (Viajes educativos, Educación superior, Cursos de idiomas) se saltean solos.

## C3 · Testing E2E · 40 min

Con un celular de prueba contra `+52 33 2627 4502`:

| # | Caso | Esperado | OK |
|---|---|---|---|
| 1 | Saludo | Presentación + pregunta por el programa (no asume ninguno) | |
| 2 | Internados | Info + link `vtr.[TU-DOMINIO]/agendar-ema` (`promo.venttur.com/…` después de B5) | |
| 3 | Cursos de idiomas (huérfano) | No inventa precio; ofrece asesoría | |
| 4 | Pedir cita teniendo una agendada | Detecta la cita (`Cita: AGENDADA`) y no manda otro link | |
| 5 | Pedir hablar con una persona | Eleva: contacto asignado a Mauricio, tag `bot_pausado`, aviso en Telegram con link al contacto. El siguiente mensaje **no** tiene respuesta del bot. Sacar el tag al terminar | |
| 6 | Audio | Transcribe y responde al contenido | |
| 7 | Foto | Dice que no puede ver imágenes y sigue la conversación | |
| 8 | Recibe el link y no agenda | A los 45 min llega el rescate Fase 1 (una sola vez) | |

Rojos → al grupo `-4925599962` con captura + id de ejecución de n8n.

## C4 · Delta de folios CAPI · 5 min

La migración inicial (Batch B, 22/9) pasó 3.725 folios. Los que entraron por el workflow viejo quedaron en
Airtable: sigue prendido hasta B5.8 (T + 4 h), así que el delta se corre **después de B5.8**. Pedirle a Claude: *"Corré el delta de folios Airtable → Supabase post-cutover"* (mismo workflow B2
`FoDzrFAEynflWjeG`, idempotente).

## C5 · Watch mode (de H al sábado)

Dos veces por día:
- [ ] n8n → Executions filtradas por error: `main-venttur-ghl`, W6, W4, rescate, despachador, W9.
  W9 en rojo con 404 en `Disparar Rescate (webhook)` es un error: el rescate se prende en B2.
- [ ] GHL → Conversaciones: ningún mensaje entrante sin respuesta del bot (salvo contactos elevados).
- [ ] Telegram: el digest diario de las 08:00 CDMX (`BzBCMGxEdJy6zmA9`) sigue llegando.

Cero P1 acumulados el sábado = GO para E2.

## C6 · Limpieza · 10 min

- [ ] n8n: apagar `test - GHL WH Payload | VTR` (`2siyKI7xrVYw8H30`) si en A5 se confirmó que era el destino
  del workflow GHL `WEBHOOK`.
- [ ] n8n: las ejecuciones viejas en espera (seguimientos y rescate de ManyChat, con Waits de horas) van a
  despertar e intentar mandar por ManyChat: fallan sin efecto. Opcional: detenerlas desde Executions.

---

# FASE D · Gates para apagar Clientify (viernes 25 – sábado 26 mediodía)

**Si cualquiera de los 4 no está en verde el sábado a las 18:00 CDMX, Clientify no se apaga.**

## D1 · Delta de datos Clientify → GHL 🔴

El import a GHL (3-6/9) se hizo desde exports del **10/7 (Airtable) y 24/7 (Clientify)**. Conteo real de hoy
contra ese export:

| | Export 24/7 | Clientify hoy (22/9) | Diferencia |
|---|---:|---:|---|
| Contactos | 6.968 | 7.318 | **+350** (327 creados después del 24/7) |
| Deals | 2.338 | 2.440 | **+102** |
| Deals modificados después del 24/7 | — | 151 | etapas desactualizadas en GHL |

Nada de eso está en GHL. Si se apaga Clientify sin este paso, se pierden 2 meses de leads y el pipeline de los
asesores queda con etapas de julio.

**23/9 · plan armado, nada escrito en GHL todavía.** Script `$S/delta-clientify-ghl.py` (API de Clientify con
`VTR_CLIENTIFY_API_KEY`, mismo ETL y mismos payloads que el import, idmaps del import como base). Export guardado en
`backup-clientify-2026-09/08-delta-api/`, plan en `05_ejecucion/salida-delta/plan-2026-09-23.md`.

| | Cantidad |
|---|---:|
| Contactos nuevos a crear | **137** (134 creados después del 24/7) |
| Deals nuevos a crear | **99** (70 VENTAS EMA · 21 Seguimiento · 8 operativos) |
| Deals ya importados que cambiaron de etapa o estado | **82** (30 Operativo Internados · 27 VENTAS EMA · 14 Año Académico · resto) |
| Chequeo contra GHL de esos 82+7 | 0 conflictos: siguen como se importaron (si alguno se mueve en GHL, el script no lo pisa) |
| No se pueden llevar (igual que en el import) | 43 deals sin contacto con teléfono o email · 2.415 contactos sin teléfono ni email |
| **Etapas de Clientify que no existen en GHL** | **12 deals** (5 nuevos + 7 modificados), ver abajo |

~320 escrituras en serie, ~4 min. Los números cierran con la guía: la diferencia con "+350/+102/+151" es que ahí se
contaba todo lo creado o tocado, y acá sólo lo que no está en GHL o cambió de etapa/estado.

- [ ] 👤🔴 **Antes de escribir: los disparadores de los flujos de Rodrigo.** Cuando se hizo el import (3-6/9) los
  23 flujos estaban en borrador; hoy están publicados. Crear 99 oportunidades y mover 82 de etapa (30 en Operativo
  Internados) puede dispararlos: tareas, avisos y, desde el BSP, **WhatsApps a clientes reales**. La API no
  muestra los disparadores. Revisar en GHL → Automatización cuáles se disparan con *Opportunity Created*,
  *Pipeline Stage Changed* o *Contact Created* y qué hacen. Los que se disparen con eso y hagan algo hacia
  afuera (mensaje o mail al cliente) van **a borrador los ~5 min de la corrida** y se vuelven a publicar al
  terminar. (Un filtro por etiqueta no sirve: dejaría a esos contactos fuera del flujo para siempre.) Con el panel
  visible lo reviso yo.
- [ ] 👤 **Etapas sin equivalente** (las creó Rodrigo en Clientify después del 24/7; en GHL los operativos siguen su
  runbook): Pathway · *Abrir Cuenta Bloqueada (Expatrio)*, *Enviar documentos a Alemania*, *Recopilar Documentos
  Pre evaluación (PDF)* · Educación superior · *Realizar aplicación* · Gap Year · *Trámite Visa* · Summercamp ·
  *Cobro de inscripción*. Rodrigo decide: crear esas etapas en GHL o decir a qué etapa van. Mientras tanto el script
  los saltea y los lista.
**Paso a paso de la verificación (antes de aplicar, ~15 min):**

*En GHL: qué flujos se dispararían*
1. Automatización → Flujos de trabajo. Abrir cada flujo **publicado** (los 23 de Rodrigo + Handoff, Fallback,
   Confirmación de cita, Inbound bot).
2. Mirar el cuadro de disparador (arriba de todo). Anotar sólo los que usen alguno de estos:
   *Opportunity Created* · *Pipeline Stage Changed* · *Opportunity Status Changed* · *Contact Created*.
   Los demás (cita reservada, etiqueta, mensaje entrante, presupuesto) no los toca el delta: se dejan.
3. De los anotados, mirar las acciones:
   - Manda algo **al cliente** (WhatsApp, SMS, mail) → va a borrador durante la corrida.
   - Sólo tareas o avisos internos → decidir: borrador (sin ruido) o dejarlo (los asesores reciben ~180 avisos).
   - Sólo mueve etapa o pone etiquetas → se deja.
4. Pasar a borrador los marcados, avisarme, corro los 3 comandos (~5 min), y volver a publicarlos.

*Con Rodrigo (o en Clientify): 12 deals en etapas que GHL no tiene*

| Pipeline | Etapa de Clientify | Deals | Decisión (crear en GHL o a qué etapa va) |
|---|---|---:|---|
| Operativo Pathway | Abrir Cuenta Bloqueada (Expatrio) | 1 | |
| Operativo Pathway | Enviar documentos a Alemania | 3 | |
| Operativo Pathway | Recopilar Documentos Pre evaluación (PDF) | 2 | |
| Operativo Educación superior | Realizar aplicación | 2 | |
| Operativo Gap Year | Trámite Visa | 5 | |
| Operativo Summercamp | Cobro de inscripción | 2 | |

(Suman 15 porque 3 de esos deals tampoco tienen contacto y no se llevan igual.) Si Rodrigo no contesta a tiempo,
se aplica el resto y esos quedan para la pasada del viernes.

**Resultado de la revisión de disparadores (23/9, Claude, flujo por flujo en la UI):** de los 27 publicados,
**ninguno se dispara con lo que hace el delta**. 21 de Rodrigo arrancan con *etiqueta agregada*, `IDIOMAS ·
Documentos → Aplicación` con *formulario enviado*, Handoff con etiqueta, Fallback y Confirmación de cita con
*cita reservada*, Inbound con *mensaje entrante*. Los únicos con *cambio de etapa* son `EMA · Agendó Cita`
(Campaña Internados → Cita de venta: asigna usuario + crea/actualiza oportunidad) e `INTERNADOS · Cambiar a
Seguimiento` (Operativo Internados → Estudiante en destino: crea oportunidad en Seguimiento). **Los dos están en
borrador desde el 23/9 20:26 UTC** → volver a publicarlos después del paso `opps-update`. Nota para D2: los flujos
"Presupuesto aceptado/abierto/pagado" se disparan con **etiqueta**, no con el evento del presupuesto de GHL.

**Aplicado 23/9:** `contacts` ✅ 136 (1 falla: email mal cargado en Clientify, sin teléfono) · `opps-new` ✅ 99
(48 salteados: 43 sin contacto + 5 sin etapa) · `opps-update` ✅ 82 (7 salteados: etapas sin equivalente; 0 fallas). Los 2 flujos de cambio de etapa ya se volvieron a publicar (la agencia, 23/9). **Falta:** decisión de Rodrigo sobre las 12 etapas y la segunda pasada del viernes. Idmaps previos
respaldados en `salida-delta/*-antes-delta.json`.

- [ ] 🤖 Aplicar, en este orden (cada uno idempotente; sin `--apply` es dry-run):

```bash
python3 $S/delta-clientify-ghl.py --stage contacts --apply
python3 $S/delta-clientify-ghl.py --stage opps-new --apply
python3 $S/delta-clientify-ghl.py --stage opps-update --apply
```

- [ ] 🤖 **Viernes, después del freeze de A8**, una segunda pasada para lo que se movió desde hoy:
  `--export --plan --check-ghl` y los tres comandos otra vez. Sólo aplica lo nuevo (registra lo aplicado en
  `salida-delta/`).
- [ ] Verificación: `python3 $S/reconciliar-import.py` → contactos y opps en GHL = idmaps + delta.

## D2 · Presupuestos en GHL 🔴

Definición: `clients/VTR_Venttur/06_docs/presupuestos-clientify-a-ghl-2026-09-22.md`. Reemplazo: **Estimates**
(el presupuesto que el cliente acepta) + **Invoices** (la factura que paga) de GHL. **No es factura fiscal
(CFDI)**: igual que en Clientify, es una cotización con link de pago.

**Estado al 23/9 tarde:** configurado todo lo que no depende de Venttur. Scripts y snapshots en
`05_ejecucion/scripts/crear-plantillas-presupuesto-ghl.py` y `05_ejecucion/snapshots/ghl-productos-2026-09-23-antes-iva.json`.
Rodrigo, Andrés y Mauricio **ya tienen permiso** de facturas, pagos y registrar pagos.

**1. Lo que pasa Venttur** → A9 (cuentas bancarias, Mercado Pago, presupuestos pendientes). Bloquea 4 y 6.

**2. Configuración de la cuenta** ✅ hecho 23/9 (verificado por API):
- [x] Impuesto **IVA 16 %** creado (Pagos → Configuración → Tasas de impuestos, id `6ab4155291704e023e6d8625`).
- [x] IVA **por producto**, como en Clientify: 18 productos con IVA 16 % exclusivo (fees, perfilamientos,
  inscripciones) y 8 sin IVA (las 3 cuotas administrativas, ALPADIA, Learn&Study, AA Públicos y los 2 camps).
  Los totales dan igual que en Clientify: Perfilamiento $10,000 · Pathway $12,500.01 · Gap Year $13,500.08 ·
  Fee $14,999.99. Antes del 23/9 los 26 estaban sin impuesto: habrían salido 16 % más baratos.
- [x] Facturas y estimaciones → Configuración: emisor **Venttur Education & Travel**, tel `3320016463`,
  Juan Palomar y Arias 616, Guadalajara · títulos **PRESUPUESTO** / **FACTURA** · términos por defecto con razón
  social + RFC + correo + "enviar comprobante" · vigencia **7 días** (lo más usado en Clientify) · prefijos
  `VTR-` / `VTR-F-` · remitente "Venttur Education & Travel" · asuntos de correo al cliente en español.
- [ ] 👤 Perfil de la empresa (Configuración → Perfil): nombre legal y RFC. No afecta a los presupuestos (van
  en los términos); es cosmético. El nombre "Venttur " con espacio al final se deja como está.
- [ ] 👤 Revisar en la prueba del punto 6 si la página pública y el cuerpo del correo salen en español.

**3. Plantillas** ✅ hecho 23/9 (4 estimate templates, por API):
- [x] `Perfilamiento EMA · Rodrigo (Banorte)` · Perfilamiento 1 · términos EMA (pago total + garantía) + Banorte.
- [x] `Presupuesto · Rodrigo (Banorte)` · Perfilamiento 2.
- [x] `Presupuesto · Juan José (BBVA)` · Primera Inscripción Pathway.
- [x] `Presupuesto · Andrés (Banamex/Banorte)` · Primera Inscripción Pathway.
  El producto es el más usado por cada uno; se cambia al crear la cotización. Textos copiados del último
  presupuesto real de cada asesor. Si A9 cambia las cuentas, se editan (o se corre el script con otro texto).
- [ ] Correo de envío con el texto de Clientify (`Downloads/Clientify/recursos/presupuestos/Plantilla de envío
  correo.md`) si el cuerpo por defecto de GHL no convence al verlo en la prueba.

**4. Cobro:**
- [ ] 👤 **Mercado Pago** (A9): conectarlo en Pagos → Integraciones con quien tenga el acceso. Primero en
  prueba; después en vivo. GHL lo soporta nativo; hoy `mercadoPago.live = null`.
- [ ] 👤 **Transferencia (procedimiento para los asesores):** cuando entra la transferencia, abrir la factura →
  **Registrar pago** (manual). Es lo que la marca como pagada y dispara los flujos de "pagado". Si nadie lo
  registra, esos flujos nunca corren para quien paga por transferencia. (En Clientify pasaba lo mismo: por eso
  hay presupuestos cobrados que figuran como vencidos.)

**5. Flujos que dependen de los presupuestos** (👤 revisar en la UI con el panel visible; el editor es un
iframe y la API no muestra disparadores). Son 4, todos publicados:
- [ ] `IDIOMAS · Docs → Enviar Presupuesto` (`26c32d8c…`) · `IDIOMAS · Presupuesto aceptado` (`02095c7c…`) →
  *Estimate* aceptado · `INTERNADOS · Presupuesto abierto` (`1c4efe9b…`) → *Estimate* enviado ·
  `INTERNADOS · Presupuesto pagado` (`8c38b164…`) → *Invoice* pagada.
- [ ] **Que se distingan Idiomas de Internados.** Si el disparador es "cualquier cotización", un presupuesto
  de Idiomas crea una oportunidad en `Operativo Internados` y viceversa. Filtro sugerido: por el nombre del
  producto (Perfilamiento / EMA / Boarding → Internados; Idiomas / Summer / Pathway / Gap Year → Idiomas).
- [ ] Aviso al asesor cuando una factura se paga (notificación interna), si esos flujos no lo tienen.
- [ ] Convertir en factura al aceptar: confirmar en la prueba si GHL lo hace solo o si lo tiene que hacer el
  flujo de "aceptado". Sin factura no hay link de pago.

**6. Transición desde Clientify:**
- [ ] 👤 Reemitir en GHL los que Venttur diga que siguen pendientes (A9). Lista de candidatos en el doc de
  presupuestos. El link de Clientify muere con Clientify.
- [ ] 👤 Prueba de punta a punta con un contacto de prueba: crear la cotización desde una plantilla → enviarla →
  abrir el link y el PDF (marca, IVA, cuenta, términos, idioma) → aceptarla → factura → pagarla con Mercado Pago
  en prueba y registrar una transferencia en otra → que los flujos muevan la oportunidad. Anular todo al terminar.
- [ ] 👤 Capacitación de 15 min a Rodrigo y Andrés: crear la cotización desde el contacto con su plantilla,
  cambiar el producto o agregar una **línea manual** para los programas en moneda extranjera (a MXN al TC del día;
  referencia en `06_docs/presupuestos-productos-moneda-extranjera-referencia.md`), enviarla y registrar una
  transferencia. Rodrigo hace una él mismo.

**Si no llega a tiempo:** no se apaga Clientify el sábado; se pospone sólo el apagado (el bot y el CRM ya están
en GHL). Mientras tanto los presupuestos se siguen haciendo en Clientify.

## D3 · Cero dependencias de Clientify en n8n 🔴 · 🤖 2 min

Pedirle a Claude *"Verificá que ningún workflow activo de n8n llame a Clientify"*. Pre-chequeo del 23/9: los 13
workflows del stack nuevo (9 con toggle + 4 sub-workflows) no tienen ninguna URL de Clientify. Estado al 22/9: el main nuevo
ya no llama a Clientify (`crear_contacto` va a GHL; `primer_registro` y `Settear variables` están
deshabilitados). Los que sí lo llaman quedan apagados: el main viejo en B6 y `Formulario Clientify` en B5.8.

## D4 · B5 hecho 🔴

`promo.venttur.com` sirviendo GHL (B5 paso 7 en verde), links del agente de vuelta en `promo` (paso 8) y
`--landings-off` corrido (B5.8). Mientras `promo` apunte a Clientify, apagar Clientify deja caídas todas las
landings de anuncios y aventureras. Si la agencia todavía no hizo el cambio, el apagado se pospone.

---

# FASE E · CIERRE (sábado 26/9)

- [ ] **E1 · 18:00 CDMX · GO / NO-GO:** C5 sin P1 + D1, D2, D3, D4 en verde. Si no, se pospone (Clientify se paga
  unos días más; nada se rompe).
- [ ] **E2 · 21:00 CDMX · Apagar Clientify:** antes, exportar desde Clientify el historial de conversaciones que
  el cliente quiera conservar (no migra a GHL). Después, no renovar / desactivar la cuenta.
- [ ] **E3 · Snapshot final:**

```bash
python3 $S/snapshot-workflows.py clients/VTR_Venttur/03_workflows/ghl-live-cutover-final
```

- [ ] **E4 · Handoff con Mauricio (30 min):** conversaciones en GHL, contactos y oportunidades, reporte semanal
  (lunes 10:00 a `administracion@venttur.com`), cómo escalar (grupo `-4925599962`), reporte de aventureras
  (`reporte-aventureras.py --full`).
- [ ] **E5 · Postmortem:** `clients/VTR_Venttur/06_docs/postmortem-cutover-2026-09.md`.

---

# FASE F · Semana del 28/9 (no bloquea)

- [ ] **Nombres de calendario con Mauricio:** confirmar los 10 nombres que muestran las landings (lista en A2,
  "Ajustes del 22/9"). Si prefiere otro criterio (p. ej. "Asesoría · Internados"), se cambian por API con el
  mismo procedimiento; no afecta nada más (n8n no usa los nombres, sólo los IDs).

- [ ] **ManyChat:** cancelar el plan y revocar sus tokens de API (hay un bearer hardcodeado en workflows viejos
  que ya está en el repo). Rotar la credencial n8n `Venttur Header Auth account` (`9OZtsIsmuVEG9l6R`).
- [ ] **OpenAI:** revocar `sk-proj-OpKR…` en el dashboard de OpenAI, **después de A6** y con ≥24 h de bot
  respondiendo con la key nueva.
- [ ] **Rotar las 10 keys de `.env`** expuestas en una sesión previa (OpenAI, Anthropic, n8n, HPF n8n, GHL HPF,
  Airtable HPF, Apify, Groq, Cal.com, SYS webhook).
- [ ] **🔴 Meta CAPI (frente propio):** hoy no se manda ningún evento a Meta. El `Meta CAPI` viejo
  (`z98w2yWVEMOfifMl`) y el nuevo (`mf7VQJelfieCDJ5r`) tienen el Trigger **deshabilitado**; ya estaba así antes
  de la migración, así que el cutover no empeora nada. Necesita un pase dedicado (qué evento, cuándo, con qué
  folio) antes de reconectarlo: la rama falsa del flujo manda eventos reales a Meta.
- [ ] **Airtable:** el main nuevo todavía tiene 7 nodos que escriben la base de Airtable (trazabilidad durante
  el watch mode). Sacarlos y recién ahí dar de baja Airtable.
- [x] **Handoff por mail:** `Handoff · Notificación al equipo` publicado, avisa a Max y a Mauricio (visto 23/9).
  El aviso por Telegram desde `elevar` (grupo `-4925599962`) sigue saliendo también.
- [ ] **D7 · programas huérfanos:** cuando Mauricio pase textos y rangos de Viajes educativos, Educación
  superior y Cursos de idiomas → prompt v2.3 + plantillas Meta propias.
- [ ] **Aventureras nuevas:** las 32 actuales ya tienen su landing y sus links viejos redirigen con atribución.
  Para una aventurera nueva: agregarla a `landings-ghl/_data/aventureras.json`, regenerar y crear su step en
  el funnel `LP · Calendarios` clonando cualquier step (A2).
- [ ] **Reporte de aventureras:** semanal con `reporte-aventureras.py --full --csv …`.
- [ ] **`atribuida_a` visible en la ficha del contacto para las citas de landing de calendario** (pedido de la agencia,
  23/9; ver A3). Hoy sólo lo llena W4 (formularios). En las citas que entran por una landing de calendario o de
  aventurera, el slug queda sólo en la URL de `lastAttributionSource` / `attributionSource`, y el asesor no lo
  ve. **Alternativa más corta: arreglar el workflow GHL `Fallback · atribuida_a…`, que ya existe y está publicado
  (ver C1).** Si se elige W6: cambio en **W6** (`AS9ZNhY3GJDfhY3P`, 5 nodos). Se deja para después del cutover porque W6 manda la
  confirmación de cita y no se puede probar sin prenderlo:
  1. Nodo nuevo `GET contacto` entre `1. Enviar confirmación` y `2. Marcar agendan_cita=true`:
     `GET /contacts/{contact_id}` (misma credencial y headers que el nodo 2), con `onError: continueRegularOutput`.
  2. En el `jsonBody` del nodo 2: tomar `lastAttributionSource.url` y, si no trae el parámetro,
     `attributionSource.url`. Extraer el slug con `/[?&]atribuida_a=([^&#?]+)/` (la misma regex de
     `reporte-aventureras.py`). Si hay slug, agregar `{ id: 'yEgBeLQNnCPkTTv8OvfX', value: slug }` a
     `mark_body.customFields`. Si no hay, el body queda como hoy.
  3. Probar con una cita en `/Internados-Calendario?atribuida_a=prueba_w6`: la ficha del contacto tiene que mostrar
     `atribuida_a = prueba_w6` y la confirmación por WhatsApp tiene que salir igual que antes.
  4. Actualizar el snapshot `03_workflows/` y dejar anotado que el reporte puede leer el campo además de la URL.

---

# Canales nuevos (desde H)

No bloquean nada y no entran en la ventana de H. Instagram como bandeja no depende del DNS ni del BSP: se puede
conectar apenas pase B7 (o antes, si se cumplen los requisitos de abajo). Orden sugerido: Instagram como bandeja →
(opcional, cotizado aparte) agente en Instagram → TikTok cuando exista para México.

## Instagram · primero como bandeja para humanos

**Dónde:** GHL → Configuración → Integraciones → **Facebook e Instagram**.

**Requisitos:**
- Quien conecta es **admin de la página de Facebook** de Venttur **y** de la **cuenta profesional de Instagram**
  vinculada a esa página.
- En la app de Instagram, **permitir acceso a los mensajes** (configuración de mensajes). Sin eso los DMs no
  llegan a GHL.

**Antes de conectar:**
- [x] 🔴 **Confirmar que el workflow inbound de Camilo filtra sólo WhatsApp** (A5, confirmado 23/9). Si no filtra, cada DM de
  Instagram despierta al agente con la sesión rota: el agente guarda la memoria por teléfono (`session_key` en
  `Normalize GHL Payload`), un contacto de Instagram no tiene teléfono, y la respuesta sale como `type: WhatsApp`
  a alguien sin WhatsApp.
- [ ] **Verificar si Instagram está conectado hoy a otra herramienta** (ManyChat, Clientify, respuestas
  automáticas de Meta Business Suite). El análisis del 26/8 (`06_docs/analisis-manychat-vs-ghl-2026-08-26.md`)
  dice que IG/FB "están en otro lado" sin decir dónde. Si otra herramienta responde, apagar sus automatizaciones
  para que el lead no reciba dos respuestas.

Los DMs entran a GHL → Conversaciones y los responde un asesor. El agente no participa.

## Agente en Instagram · alcance nuevo

No es prender un canal: el agente está hecho para WhatsApp. Hace falta:
- **sessionKey sin teléfono:** la memoria tiene que colgar de una clave estable que exista en Instagram (por
  ejemplo el `contactId` de GHL).
- **Envío por el canal de Instagram:** `Enviar WPP` manda `type: WhatsApp`; para Instagram va el tipo de ese canal,
  y el filtro del workflow inbound tiene que dejar pasar Instagram.
- **Ventana de 24 h sin plantillas:** Instagram no tiene plantillas aprobadas. Pasadas 24 h desde el último mensaje
  del lead, un bot no puede escribirle: rescate, despachador y outreach no aplican a ese canal.

## TikTok · no prometerlo todavía

No está en ningún documento del proyecto. La documentación oficial de GHL (actualizada el 11/5/2026) dice que los
DMs y comentarios de TikTok **sí entran a Conversaciones**
([TikTok Messaging & Comment Automations](https://help.gohighlevel.com/support/solutions/articles/155000006703-tiktok-dms-comment-automations)),
pero que la función está disponible **sólo para cuentas business registradas en Estados Unidos**
([Integrate TikTok Messaging](https://help.gohighlevel.com/support/solutions/articles/155000006620-integrate-tiktok-messaging)).
Venttur es de México: hoy no se puede ofrecer. Antes de proponerlo, re-chequear en la sub-cuenta
(Configuración → Integraciones → TikTok) y en esa página.

---

## Referencia rápida

**Workflows n8n** (`https://[TU-INSTANCIA-N8N]`)

| Rol | ID | Post-cutover |
|---|---|---|
| main-venttur-ghl | `1eS1Z5k898c3ATnf` | ON · webhook `main-venttur-ghl-44ce5e8a` |
| W4 Formulario landing → GHL | `LhPSfMYtQbNcEK32` | ON desde B1 · webhook `vtr-form-landing-ghl-08d86c06` |
| W6 Confirmación agenda | `AS9ZNhY3GJDfhY3P` | ON · webhook `vtr-confirmacion-agenda-ghl-a191d178` |
| W10 Outreach Sheet → GHL | `MbPTKvy0bq8b4YAw` | ON (Sheets trigger) |
| W14 Correo semanal | `OaOyHA2tfjMtuWTk` | ON (lunes 10:00) |
| Despachador | `vrShEXQGGAo4FqAt` | ON (envío según C2) |
| Rescate GHL | `YB0UxwEVwzISdd54` | **ON desde B2** (`--landings-on`, no `--solo-on`) · webhook `vtr-rescate-link` |
| Barrido interrumpida | `LrJuzU7qDeELWiAl` | ON (horario) |
| CAPI Registro Folio Supabase | `4HgMkK34xqITULM3` | ON desde B1 · webhook `capi-registro-folio-vtr-supabase` |
| W9 · W11 · clasificador · elevar | `TROsQ5h78baAuVOY` · `qYgeTc9PCq3TiGDn` · `Xmyoewwa1W5gm1fy` · `v9XkOfL9dQtY2wyv` | sub-workflows, sin toggle |
| Meta CAPI Supabase | `mf7VQJelfieCDJ5r` | sin toggle · Trigger deshabilitado (Fase F) |
| Staging Telegram | `3sLd7KY3o8I7NvXi` | ON, no afecta producción |
| Digest guardrail | `BzBCMGxEdJy6zmA9` | ON |
| **Viejos del agente, se apagan en B6** | `k3aivKSP67S97IHn` · `2PSekVBxarsrnVBu` · `CUuFxbst3iHpgeXS` · `H6qYB3Oj97bxaTCX` | OFF |
| **Viejos de landings, se apagan en B5.8** | `ZB6erhWicZmDfC4I` (Formulario Clientify) · `9yCbynoKDt9hgiBq` (CAPI folio Airtable) | OFF (siguen ON mientras `promo` sirva Clientify) |

**GHL:** location `7aXb4JCKsWV5nUyBXeSF` · Rodrigo `IaSkyQuhbjGdwNyXg1VD` · Andrés `4VtbDVSjnoHm5125qa8I` ·
Mauricio `cXRMSnBx81rYivxQruKX` · custom field `atribuida_a` `yEgBeLQNnCPkTTv8OvfX`.

**Calendarios:** Internados `CIxOV100yyRFqPoa6LdK` · Intercambio `SiAPsk27X5yilff5bSS5` · Campamentos
`981EzNS7jf9HhJNkL41W` (Rodrigo) · Viajes educativos `j0jcAdaieJXaoPZBempp` · Educación superior
`RUjWx74NPK77FPUcs5ME` · Cursos de idiomas `5PxslDhdQxZeDcKmLYNq` · Pathway Alemania `oNN7oLWsNhQlWi7q7pDX` ·
Gap Year `Omgde6Ko8TGKYMtiUb1x` (Andrés).

**WhatsApp:** display `+52 33 2627 4502` · Meta/OTP `+52 1 33 2627 4502` · WABA `1931874540684022`.

**Scripts del cutover** (`$S`): `cutover-toggles.py` (`--verify`, `--solo-on` = 8 nuevos sin el rescate,
`--landings-on` = W4 + CAPI folio Supabase + rescate, `--solo-off`, `--landings-off`, `--rollback`; siempre dry-run
sin `--execute`) · `snapshot-workflows.py <dir>` · `preparar-landings-ghl.py` ·
`generar-renderer-ghl.py` (`--publicar`: sube el JSON de las landings y reescribe el cargador) ·
`verificar-landings-ghl.py` (`--dominio`, `--solo`, `--redirects`) ·
`crear-redirects-ghl.py` (`--execute`, `--borrar`, `--dominio` para ensayar en otro dominio, `--puente` en B5 paso 9) ·
`dominio-links-agente.py --a vtr|promo` (dominio de los links del agente: B2 y paso 8 de B5) ·
`batches-2026-09-22/vtr_post2_despachador.py` · `reporte-aventureras.py --full` · `reconciliar-import.py`.

**Documentos de detalle:** runbook BSP `06_docs/runbook-bsp-migration-waba-2026-09-19.md` · landings
`06_docs/guia-deploy-landings-2026-09-22.md` · presupuestos `06_docs/presupuestos-clientify-a-ghl-2026-09-22.md`
· decisiones del cliente `06_docs/decisiones-cliente-cutover-2026-09-24.md` · flujos de Rodrigo
`00_migracion_ghl/04_guia_migracion/14a_runbook_flujos_rodrigo.md` · batch C.2
`03_workflows/ghl-live-2026-09-22-batch-C2/README.md`.

## Reglas

- ❌ No instalar WhatsApp en el número del WABA (antes, durante ni después).
- ❌ No cancelar ManyChat ni Clientify antes del 27/9.
- ❌ No re-importar workflows completos a n8n: parches dirigidos por API, con snapshot antes.
- ❌ Nunca escrituras a GHL en paralelo (límite 10.000/día y ráfagas de 25 cada 10 s).
- ❌ No revocar la key vieja de OpenAI antes de A6.
- ✅ Supabase de VTR sólo vía la credencial n8n `ihpvM7nYMdLCwWDP`.
- ✅ Al lead nunca se le dan detalles técnicos.

**Escalamiento:** P1 (el bot no responde, no salen mensajes, se pierde la memoria) a cualquier hora · P2 (bug
que no bloquea) en menos de 4 h · P3 (cosmético) al backlog.
