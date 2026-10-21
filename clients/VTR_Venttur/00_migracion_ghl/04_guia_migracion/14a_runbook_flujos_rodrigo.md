# 14a · Runbook operativo — 3 grupos de flujos Rodrigo (GHL Workflows, sin plantillas Meta)

**Ventana:** T-4 a T-2 (22-24/9) · **Ejecuta:** Camilo · **No bloquea por WABA** — puede arrancar apenas Etapa 4 GHL esté desbloqueada.

> **Por qué estos grupos primero.** Los 3 grupos de flujos de Rodrigo (EMA METODOLOGÍA, OPERATIVO IDIOMAS, OPERATIVO INTERNADOS) son puro CRM: mueven etapa de oportunidad, crean tareas, envían mails con plantillas Clientify internas, cambian propietario. **Ninguno envía plantillas Meta APPROVED por WhatsApp** — se pueden rebuild en paralelo mientras se destraba el canal WABA.
>
> **Total: 23 flujos** = 1 (EMA) + 10 (IDIOMAS) + 12 (INTERNADOS).
>
> **Naming convention del snapshot Clientify:** `_lanzador_X.png` = dialog de config del trigger; `_accion_X.png` = dialog de config de una acción puntual; `_notemplate_X.png` = **vista general del flujo** (nombre engañoso — no es el copy del mensaje). Los notemplates son la fuente primaria de este runbook.

---

## Precondiciones GHL (comunes a los 3 grupos)

- [ ] Sub-account VTR (`7aXb4JCKsWV5nUyBXeSF`) accesible
- [ ] Los 3 pipelines de Rodrigo creados en GHL con las etapas equivalentes de Clientify (ver `03_pipelines_ghl.md`):
  - `VENTAS EMA METODOLOGÍA` (con etapa `AGENDÓ REUNIÓN` como mínimo)
  - `Operativo Idiomas` (con etapas: `Recabar Datos`, `Realizar Aplicación`, `Recibir Documentos`, `Enviar Presupuesto`, `Cobrar Programa`, `Enviar Comprobante`, `Coordinar llegada`, `Tramitar Visa`, `Estudiante...`)
  - `Operativo Internados` (con etapas: `PRESUPUESTO`, `PERFILAMIENTO (INDIVIDUAL & FAMILIAR)`, `PRESENTACIÓN de escuelas`, `JUNTA escuela + familia`, `Envío aplicación`, `Aceptación`, `Pago del programa`, `Estudiante en destino`)
- [ ] Pipeline de origen `Campaña Internados Erika` (con etapa `Cita de Ventas concretada`) importado — es el trigger de EMA
- [ ] Tags equivalentes creados (Clientify usa etiquetas como trigger de casi todos los flujos — ver §Anexo A al final)
- [ ] Plantilla email Clientify `Solicitud de datos...` (id `732481`) recreada como GHL Email Template
- [ ] Usuario `Rodrigo Garcia de la Vega` (propietario destino) y `Diego Matus` (creador original) invitados a la sub-account con permisos de Workflows

**Nota merge fields:** Clientify usa `{fullname}`, `{firstname}`, `{lastname}`. GHL usa `{{contact.name}}`, `{{contact.first_name}}`, `{{contact.last_name}}`. Traducir en cada task/oportunidad al crear.

---

## GRUPO 1 · EMA METODOLOGÍA (1 flujo)

### Flujo 1.1 · AGENDÓ CITA

**Trigger:** Cambio en etapa de oportunidad
- Pipeline: `Campaña Internados Erika`
- Etapa que dispara: `Cita de Ventas concretada`

**Acciones (2):**

1. **Crear oportunidad**
   - Nombre: `{{contact.name}}` (equivalente `{fullname}`)
   - Pipeline: `VENTAS EMA METODOLOGÍA`
   - Etapa: `AGENDÓ REUNIÓN`
   - Vencimiento: mismo día
   - Propietario: Rodrigo Garcia de la Vega
   - Moneda: MXN
   - Importe: **25,000.00**

2. **Cambiar propietario** (de la oportunidad recién creada) → Rodrigo Garcia de la Vega

**Setup en GHL Workflows UI:**
1. New Workflow → nombre: `EMA · Agendó Cita`
2. Trigger: **Opportunity Status Changed** → filtrar por Pipeline `Campaña Internados Erika` + Stage `Cita de Ventas concretada`
3. Action 1: **Create/Update Opportunity** con los 6 campos arriba
4. Action 2: **Assign to User** → Rodrigo Garcia de la Vega (aplicado sobre la opp creada en Action 1)
5. Publish

**Verificación:** mover manualmente una opp de prueba a `Cita de Ventas concretada` → chequear que aparezca una opp nueva en pipeline `VENTAS EMA METODOLOGÍA` etapa `AGENDÓ REUNIÓN`, importe $25k, owner Rodrigo.

---

## GRUPO 2 · OPERATIVO IDIOMAS (10 flujos)

Todos los flujos de este grupo tienen el patrón: **tag/estado presupuesto dispara → cambia etapa de oportunidad (± crea tarea, ± envía mail)**. Rebuild uno por uno.

### Flujo 2.1 · Enviar correo con formulario idiomas prueba

**Trigger:** Cambio en estado de presupuesto = **Aceptado**

**Acciones (1):**
1. **Enviar email** — Plantilla Clientify `id 732481` "Solicitud de datos..."
   - En GHL: **Send Email** → seleccionar template `Solicitud de datos idiomas` (recreada desde Clientify)

---

### Flujo 2.2 · Cambio de oportunidad recabar datos y documentos idiomas

**Trigger:** Cambio en estado de presupuesto = **Aceptado** (mismo trigger que 2.1 — corren en paralelo)

**Acciones (1):**
1. **Cambiar etapa de oportunidad** → `Operativo Idiomas - Recabar Datos y Documentos`

⚠️ **AMBIGUO — Camilo confirmar:** el 2.1 y 2.2 comparten trigger. En GHL se puede unificar en 1 workflow con 2 acciones (enviar mail + cambiar etapa), o dejar como 2 workflows separados que corren en paralelo. Recomendación: **1 workflow unificado** para simplicidad.

---

### Flujo 2.3 · Cambiar oportunidad a Realizar Aplicación

**Trigger:** Formulario cumplimentado = **Documentos idiomas**
- En GHL: **Form Submitted** → seleccionar el form Documentos idiomas (necesita ser el form migrado desde Clientify — ver `13_landings_clientify_a_ghl_funnels.md`)

**Acciones (2):**
1. **Cambiar etapa de oportunidad** → `Operativo Idiomas - Realizar Aplicación`
2. **Crear tarea** → `Enviar documentación del alumno` (asignada al owner de la opp, vencimiento por default)

---

### Flujo 2.4 · Aplicación realizada en espera de documentos

**Trigger:** Asignación de etiqueta = **aplicación realizada en espera de documentos**

**Acciones (1):**
1. **Cambiar etapa de oportunidad** → `Operativo Idiomas - Recibir Documentos`

---

### Flujo 2.5 · Documentos recibidos, enviar presupuesto final

**Trigger:** Asignación de etiqueta = **documentos recibidos enviar presupuesto** (idiomas)

**Acciones (2):**
1. **Cambiar etapa de oportunidad** → `Operativo Idiomas - Enviar Presupuesto Final`
2. **Crear tarea** → `Enviar Presupuesto Final a {{contact.first_name}}`

---

### Flujo 2.6 · Cobrar Programa

**Trigger:** Asignación de etiqueta = **presupuesto final aceptado (idiomas)**

**Acciones (2):**
1. **Cambiar etapa de oportunidad** → `Operativo Idiomas - Cobrar Programa`
2. **Crear tarea** → `Cobranza Programa IDIOMAS de {{contact.first_name}}`

---

### Flujo 2.7 · Enviar comprobante de Pago

**Trigger:** Asignación de etiqueta = **programa pagado (idiomas)**

**Acciones (2):**
1. **Cambiar etapa de oportunidad** → `Operativo Idiomas - Enviar Comprobante`
2. **Crear tarea** → `Enviar comprobante de {{contact.first_name}}`

---

### Flujo 2.8 · Coordinar llegada IDIOMAS

**Triggers (2, OR):** Asignación de etiqueta = **no necesita visa** OR **trámite finalizado**

**Acciones (1):**
1. **Cambiar etapa de oportunidad** → `Operativo Idiomas - Coordinar llegada`

**Setup en GHL:** GHL Workflows soporta multi-trigger — agregar los 2 tag triggers al mismo workflow (no crear 2 workflows separados).

---

### Flujo 2.9 · Trámite Visa

**Trigger:** Asignación de etiqueta = **necesita visa**

**Acciones (1):**
1. **Cambiar etapa de oportunidad** → `Operativo Idiomas - Tramitar Visa`

---

### Flujo 2.10 · Cambiar a seguimiento (IDIOMAS)

**Trigger:** Asignación de etiqueta = **llegada coordinada (idiomas)**

**Acciones (mínimo 2, posiblemente más):**
1. **Crear oportunidad** → `Seguimiento {{contact.name}} idiomas` (pipeline y etapa por confirmar — probable pipeline `Seguimiento Idiomas`)
2. **Cambiar etapa de oportunidad** (de la opp original) → `Operativo Idiomas - Estudiante...` (nombre completo cortado en el screenshot)

⚠️ **AMBIGUO — Camilo verificar en Clientify vivo:** el screenshot del flujo muestra un símbolo `+` debajo de la acción 2, sugiriendo que hay al menos 1 acción más (probablemente cerrar la opp original o mover a etapa terminal). Abrir el flujo en Clientify UI antes del rebuild para confirmar acciones downstream.

---

## GRUPO 3 · OPERATIVO INTERNADOS (12 flujos)

Mismo patrón que IDIOMAS pero más largo: 12 flujos que forman una cadena secuencial completa desde presupuesto abierto hasta pago del programa. El "pegamento" son las etiquetas (tags) que se van asignando manualmente por Rodrigo/Cristy en cada punto de handoff.

### Flujo 3.1 · Presupuesto Abierto NO pagado

**Trigger:** Cambio en estado de presupuesto = **Abierto**

**Acciones (1):**
1. **Crear oportunidad** → `{{contact.name}} Operativo Internados` (pipeline `Operativo Internados`, etapa inicial — confirmar cuál)

⚠️ **AMBIGUO:** el screenshot muestra el nombre truncado (`{fullname} Operativo Internad...`) y no revela pipeline/etapa destino de la opp creada. Camilo verificar en Clientify.

---

### Flujo 3.2 · Presupuesto Pagado

**Trigger:** Cambio en estado de presupuesto = **Pagado**

**Acciones (mínimo 3, posiblemente más):**
1. **Cambiar etapa de oportunidad** → `Operativo Internados - PRESUPUESTO PAGADO` (nombre completo cortado)
2. **Añadir etiqueta** → `perfilamiento ema pagado` (nombre cortado en screenshot)
3. **Crear tarea** → `Agendar perfilamientos de {{contact.first_name}}`

⚠️ **AMBIGUO — Camilo verificar:** el flow shows `+` after action 3, likely more actions. Abrir en Clientify UI.

---

### Flujo 3.3 · Agendar cita perfilamientos con Cristy

**Trigger:** Asignación de etiqueta = **cita perfilamientos agendada (internados)**

**Acciones (1):**
1. **Cambiar etapa de oportunidad** → `Operativo Internados - PERFILAMIENTO (INDIVIDUAL & FAMILIAR)`

---

### Flujo 3.4 · Esperar resultados de perfilamientos y meter datos del alumno al sistema

**Trigger:** Asignación de etiqueta = **perfilamientos realizados en espera resultados**

**Acciones (1):**
1. **Crear tarea** → `Esperar resultados de perfilamientos y meter datos del alumno al sistema`

---

### Flujo 3.5 · Agendar cita para presentación de escuelas

**Trigger:** Asignación de etiqueta = **resultados de perfilamientos y presentación**

**Acciones (2):**
1. **Crear tarea** → `Agendar cita con {{contact.first_name}} {{contact.last_name}}`
2. **Cambiar etapa de oportunidad** → `Operativo Internados - PRESENTACIÓN de escuelas`

---

### Flujo 3.6 · Agendar cita escuela + familia

**Trigger:** Asignación de etiqueta = **escuela elegida agendar cita familia + escuela**

**Acciones (2):**
1. **Crear tarea** → `Agendar cita de {{contact.first_name}} {{contact.last_name}}`
2. **Cambiar etapa de oportunidad** → `Operativo Internados - JUNTA escuela + familia`

---

### Flujo 3.7 · Hacer Aplicación a escuela

**Trigger:** Asignación de etiqueta = **reunión familia + escuela efectuada (internados)**

**Acciones (2):**
1. **Cambiar etapa de oportunidad** → `Operativo Internados - Envío aplicación` (nombre cortado, probablemente `Envío de aplicación` o `Envío aplicación pt 1`)
2. **Crear tarea** → `Realizar aplicación a escuela de {{contact.first_name}}`

---

### Flujo 3.8 · Enviar aplicación a escuela

**Trigger:** Asignación de etiqueta = **aplicación autorizada por familia (internados)**

**Acciones (2):**
1. **Cambiar etapa de oportunidad** → `Operativo Internados - Envío aplicación` (probablemente misma etapa que 3.7, o `Envío aplicación pt 2`)
2. **Crear tarea** → `Enviar aplicación a escuela {{contact.first_name}}`

⚠️ **AMBIGUO — Camilo verificar:** los flujos 3.7, 3.8 y 3.9 usan nombres de etapa parecidos (todos empiezan `Operativo Internados - Envío ...`). Camilo debe confirmar en Clientify si son 3 etapas distintas o si se solapan.

---

### Flujo 3.9 · Aplicación internados pt 2

**Trigger:** Asignación de etiqueta = **aplicación realizada revisión con familia**

**Acciones (2):**
1. **Crear tarea** → `Enviar aplicación a {{contact.first_name}}`
2. **Cambiar etapa de oportunidad** → `Operativo Internados - Envío aplicación` (variante — confirmar)

---

### Flujo 3.10 · Espera de aceptación del alumno

**Trigger:** Asignación de etiqueta = **aplicación enviada a escuela en espera**

**Acciones (1):**
1. **Cambiar etapa de oportunidad** → `Operativo Internados - Aceptación` (nombre cortado)

---

### Flujo 3.11 · Estudiante aceptado inicio orientación

**Trigger:** Asignación de etiqueta = **estudiante aceptado inicio cobranza programa**

**Acciones (1):**
1. **Cambiar etapa de oportunidad** → `Operativo Internados - Pago del programa`

---

### Flujo 3.12 · Cambiar a seguimiento (INTERNADOS)

**Trigger:** Cambio en etapa de oportunidad
- Pipeline: `Operativo Internados`
- Etapa que dispara: `Estudiante en destino`

**Acciones (mínimo 1, posiblemente más):**
1. **Crear oportunidad** → `Seguimiento {{contact.name}} internados` (pipeline y etapa a confirmar)

⚠️ **AMBIGUO — Camilo verificar:** flujo posiblemente truncado en screenshot. Abrir en Clientify UI para confirmar acciones downstream (probable: cerrar opp original de Operativo Internados).

---

## Anexo A · Catálogo de tags/etiquetas Clientify a crear en GHL

Antes de arrancar el rebuild, crear estos tags en GHL (Settings → Tags). Todos los flujos IDIOMAS + INTERNADOS los usan como trigger:

**IDIOMAS:**
- `aplicación realizada en espera de documentos`
- `documentos recibidos enviar presupuesto` (idiomas)
- `presupuesto final aceptado (idiomas)`
- `programa pagado (idiomas)`
- `no necesita visa`
- `trámite finalizado`
- `necesita visa`
- `llegada coordinada (idiomas)`

**INTERNADOS:**
- `cita perfilamientos agendada (internados)`
- `perfilamientos realizados en espera resultados`
- `resultados de perfilamientos y presentación`
- `escuela elegida agendar cita familia + escuela`
- `reunión familia + escuela efectuada (internados)`
- `aplicación autorizada por familia (internados)`
- `aplicación realizada revisión con familia`
- `aplicación enviada a escuela en espera`
- `estudiante aceptado inicio cobranza programa`
- `perfilamiento ema pagado` (este lo asigna el propio flujo 3.2, pero conviene crearlo antes)

---

## Anexo B · Orden recomendado de rebuild

Arrancar por los flujos más simples (1 acción, sin dependencias) y terminar por los cadenados:

1. **EMA 1.1** (2 acciones, trigger simple)
2. **IDIOMAS 2.4, 2.7, 2.8, 2.9** (1-2 acciones cada uno, triggers tag)
3. **IDIOMAS 2.1, 2.2** (unificar en 1 workflow con doble acción)
4. **IDIOMAS 2.3** (necesita form migrado — verificar prereq)
5. **IDIOMAS 2.5, 2.6, 2.10** (cadena final)
6. **INTERNADOS 3.1, 3.2** (arranque de pipeline)
7. **INTERNADOS 3.3-3.11** (cadena secuencial, uno por uno)
8. **INTERNADOS 3.12** (cierre)

---

## Anexo C · Ambigüedades consolidadas (para verificar con la agencia/Rodrigo antes de publicar)

1. **Flujo 2.10 "Cambiar a seguimiento IDIOMAS"** — posibles acciones downstream cortadas en screenshot.
2. **Flujo 3.1 "Presupuesto Abierto NO pagado"** — pipeline/etapa destino de la opp creada no visible.
3. **Flujo 3.2 "Presupuesto Pagado"** — posibles acciones downstream cortadas después de la task de perfilamientos.
4. **Flujos 3.7, 3.8, 3.9** — 3 etapas destino con nombres parecidos (`Envío aplicación ...`). Confirmar si son 3 etapas distintas.
5. **Flujo 3.12 "Cambiar a seguimiento INTERNADOS"** — posibles acciones downstream cortadas.
6. **Pipeline destino de "Seguimiento" (2.10 y 3.12)** — no confirmado si es un pipeline `Seguimiento` compartido o uno por vertical.
7. **Wait times** — ninguno visible en los screenshots. Asumir que no hay delays entre acciones dentro de un mismo flujo (todo secuencial inmediato). Confirmar con Rodrigo.

**Recomendación operativa:** Camilo abre el flujo en Clientify UI justo antes de rebuild-earlo en GHL para chequear cada ambigüedad al momento. No hace falta cerrarlas todas de antemano.

---

## Referencias

- Snapshot Clientify: `/Users/camilo/Downloads/Clientify/flujos de trabajo/Rodrigo/`
- Guía general landings + funnels: `13_landings_clientify_a_ghl_funnels.md`
- Guía general workflows: `14_flujos_clientify_a_ghl_workflows.md`
- Pipelines GHL: `03_pipelines_ghl.md`
