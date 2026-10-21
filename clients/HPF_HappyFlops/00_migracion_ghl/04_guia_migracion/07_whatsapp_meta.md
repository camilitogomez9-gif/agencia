# M7 — WhatsApp WABA y Plantillas Meta

> **Referencia:** `03_arquitectura_ghl/06_integraciones.md §2`  
> **Tiempo estimado:** 2-4 horas (+ 24-72 hs de espera por aprobación Meta)  
> **Prerequisito:** M1 completo (sub-account GHL creado)  
> **Hacer temprano:** este módulo se hace antes de M4/M5 porque la aprobación de plantillas tarda

---

## 7.1 Conectar WhatsApp en GHL

GHL integra con WhatsApp Business API via BSP (Business Solution Provider) propio.

### Paso 1: Acceder a la integración

**Settings → Integrations → WhatsApp**

Si GHL es el BSP:  
→ Hacer click en "Connect WhatsApp" → seguir el flujo de Facebook OAuth → seleccionar el Business Manager de HPF.

Si Oscar ya tiene WABA propia (número activo en otro BSP):  
→ Migrar el número. Este proceso requiere un paso de verificación donde Meta envía un SMS/llamada al número. Oscar debe estar disponible para confirmarlo.

### Paso 2: Número a conectar

```
Número: +52 331 594 8670 (número de Rebeca / HPF)
```

⚠️ Este es el número ACTIVO en Kommo actualmente. Durante el período paralelo, este número **no puede** migrarse a GHL hasta el cutover final. Opciones:

**Opción A (recomendada para testing):**  
Usar un número secundario para las pruebas en GHL durante M8.  
Oscar provee un número de testing (puede ser un número nuevo).

**Opción B (migración directa):**  
Migrar el número el día del cutover. Implica ~10 minutos de downtime mientras Meta procesa la migración.

> Confirmar con Oscar qué número usa para el entorno de pruebas antes de proceder.

### Paso 3: Verificar conexión

Una vez conectado, en GHL → Conversations → New Message → debe aparecer la opción de enviar WhatsApp.

---

## 7.2 Plantillas Meta (Message Templates)

Para enviar mensajes **fuera de la ventana de 24 horas** de conversación activa, Meta requiere plantillas aprobadas. Esto aplica principalmente a los re-engagement (Fase 2) y mensajes de post-venta.

### Plantillas a crear y enviar a aprobación

#### Template 1: Re-engagement genérico

**Nombre:** `hpf_reengagement_v1`  
**Categoría:** MARKETING  
**Idioma:** Spanish (Mexico)  
**Tipo:** Text

```
Hola {{1}} 👋 Te escribo de Happy Flops.

{{2}}

Si querés retomar tu pedido, responde este mensaje y te atiendo de inmediato 😊
```

Variables:
- `{{1}}` = nombre del lead (o "amiga/amigo" si no hay nombre)
- `{{2}}` = texto personalizado generado por LLM

> ⚠️ Meta solo aprueba templates con contenido predecible. El texto variable va en `{{2}}` pero debe ser razonable. Si Meta rechaza, usar un template más conservador con texto fijo.

**Template alternativo (más conservador, mayor chance de aprobación):**

```
Hola 👋 Soy Rebeca de Happy Flops. Hace unos días consultaste sobre nuestros recuerditos para tu evento.

¿Pudiste ver la información que te compartí? Estamos aquí para ayudarte a definir todo 😊

Responde este mensaje para continuar.
```

#### Template 2: Pago confirmado

**Nombre:** `hpf_pago_confirmado`  
**Categoría:** UTILITY  
**Idioma:** Spanish (Mexico)

```
¡Hola! 🎉 Tu pago fue confirmado.

Ahora pasamos a la etapa de diseño de tus recuerditos. Te estaremos contactando para coordinar los detalles.

¡Gracias por elegir Happy Flops! 🩴
```

#### Template 3: Diseño aprobado

**Nombre:** `hpf_diseno_aprobado`  
**Categoría:** UTILITY  
**Idioma:** Spanish (Mexico)

```
¡Hola! ✅ Tu diseño fue aprobado.

Tu pedido entra en producción. El tiempo estimado es de {{1}} días hábiles.

Te avisaremos cuando esté listo para envío 📦
```

Variable:
- `{{1}}` = días de producción

#### Template 4: Envío confirmado

**Nombre:** `hpf_envio_confirmado`  
**Categoría:** UTILITY  
**Idioma:** Spanish (Mexico)

```
¡Hola! 📦 Tu pedido está en camino.

Paquetería: {{1}}
Número de rastreo: {{2}}

Podés rastrear tu pedido en {{3}}

¡Gracias por tu compra! 🩴🎊
```

Variables:
- `{{1}}` = nombre de paquetería
- `{{2}}` = número de tracking
- `{{3}}` = link de rastreo

---

## 7.3 Enviar plantillas a aprobación

**En GHL → Settings → WhatsApp → Message Templates → Create Template**

Para cada template:
1. Nombre (snake_case, sin espacios, máximo 512 chars)
2. Categoría
3. Idioma
4. Cuerpo del mensaje (exactamente como está arriba)
5. Variables (si aplica)
6. Enviar a aprobación

El proceso tarda **24-72 horas**. Por eso este módulo se hace primero.

> Las plantillas en estado PENDING no pueden usarse. Si Meta rechaza, editar y reenviar. El rechazo más común es texto "demasiado promocional" → cambiar palabras como "gratis", "oferta", "descuento".

---

## 7.4 Configuración del número en GHL

Una vez conectado el WABA:

**Settings → Phone Numbers → [el número de HPF]**

- **Caller ID Name:** `Happy Flops`  
- **SMS Forwarding:** apagado (solo WA)
- **Opt-out message:** desactivar o configurar según normativa México

---

## 7.5 Durante el período paralelo

Mientras Kommo sigue activo, las conversaciones de testing en GHL usan un número distinto. El número de Rebeca (`3315948670`) sigue en Kommo hasta el cutover.

**Workflow de testing:**
1. Usar un número de WhatsApp de testing (puede ser el de la agencia u otro número HPF que Oscar tenga disponible)
2. Conectar ese número a GHL
3. Hacer todas las pruebas de M8 con ese número
4. El día del cutover, migrar el número principal

---

## ✅ Checklist M7

- [ ] Determinar número de testing para GHL (confirmar con Oscar)
- [ ] Conectar WABA en GHL (número de testing o número secundario)
- [ ] 4 templates enviados a aprobación en Meta
- [ ] Anotar estado de aprobación de cada template
- [ ] Verificar envío de mensaje WA de prueba desde GHL Conversations

```
Estado templates:
- hpf_reengagement_v1: PENDING / APPROVED / REJECTED
- hpf_pago_confirmado: PENDING / APPROVED / REJECTED
- hpf_diseno_aprobado: PENDING / APPROVED / REJECTED
- hpf_envio_confirmado: PENDING / APPROVED / REJECTED
```

**Siguiente:** M8 → Testing y validación pre-cutover
