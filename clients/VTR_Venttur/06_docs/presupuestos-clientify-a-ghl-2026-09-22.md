# Presupuestos Clientify → GHL · definición de integración (2026-09-22)

> **Actualización 23/9 tarde — datos reales leídos de la API de Clientify y configuración aplicada en GHL.**
> Lectura (sin escribir nada) de los 242 presupuestos, 47 detalles y 47 productos de Clientify:
> - **Estados:** 195 vencidos · 31 aceptados · 11 pagados · 5 enviados (los 5 son de 2024). "Pagado" sólo
>   aparece cuando cobró Mercado Pago: lo que entra por transferencia queda vencido o aceptado. Por eso no se
>   puede deducir por datos qué está pendiente de cobro (lo dice Venttur, A9).
> - **Cobro con tarjeta:** `list_permitted_payments = mercadopago` en 37 de 47. No es PayPal. GHL trae Mercado
>   Pago nativo (hoy sin conectar).
> - **Cuenta bancaria por asesor** (siempre a nombre de Viajes y Experiencias GARDE, S. DE R.L. DE C.V.):
>   Rodrigo → BANORTE CLABE 072 320 013237430986, cta 132 374 3098 · Juan José → BBVA CLABE 012 320 001196818093,
>   cta 011 968 1809 · Andrés → BANAMEX CLABE 002 320 701347461635 + BANORTE (último, 00260) y BBVA antes.
> - **Términos por programa:** Perfilamiento EMA agrega "liquidar en su totalidad para agendar la Evaluación" +
>   "GARANTÍA de reembolso del 100%…". El resto: beneficiario + cuenta + "enviar comprobante a cualquier
>   representante". Política de privacidad vacía en todos.
> - **IVA por producto:** 16 % exclusivo en fees/perfilamientos/inscripciones; 0 % en cuotas administrativas y
>   programas de terceros (campamentos, escuelas). Último folio: `00260` (18/9).
>
> Aplicado en GHL (detalle en D2 de la guía): impuesto IVA 16 % · IVA en 18 de 26 productos (totales idénticos
> a Clientify) · emisor, títulos, términos por defecto, vigencia 7 días, prefijos `VTR-`/`VTR-F-`, remitente y
> asuntos en español · 4 plantillas de cotización (una por asesor + la de Perfilamiento EMA).
>
> **Candidatos a reemitir** (no pagados según Clientify, del 19/8 en adelante; Venttur confirma cuáles siguen
> pendientes):
>
> | Folio | Fecha | Estado Clientify | Asesor | Contacto | Presupuesto | Total |
> |---|---|---|---|---|---|---|
> | 00260 | 18/9 | vencido | Andrés | Luis Fernando Granados | Pre-evaluación Pathway | $12,500.01 |
> | 00259 | 15/9 | vencido | Rodrigo | Alexia Vargas | Perfilamiento Alexia | $10,000.00 |
> | 00258 | 8/9 | vencido | Andrés | José Manuel Castellanos García | Pre-evaluación Valeria Castellanos | $12,500.01 |
> | 00257 | 8/9 | vencido | Rodrigo | Ricardo Falcon | Perfilamiento Lucía Falcon | $10,000.00 |
> | 00256 | 4/9 | vencido | Rodrigo | Victor Centeno | Perfilamiento Emilia Centeno | $10,000.00 |
> | 00255 | 4/9 | vencido | Juan José | Romina Becker Schafer | Venttur Fee (Pathway) | $12,500.01 |
> | 00254 | 26/8 | vencido | Rodrigo | Adrian Ortiz | Perfilamiento Sofia Ortiz | $10,000.00 |
> | 00253 | 26/8 | aceptado | Juan José | (sin contacto) | Fee Venttur Romina Valdes | $14,999.99 |
> | 00252 | 26/8 | vencido | Juan José | Patricio Treviño | Venttur fee Hermanas Treviño | $14,999.99 |
> | 00251 | 20/8 | vencido | Rodrigo | Adriana Quiroga | Fee Venttur | $14,999.99 |
> | 00250 | 19/8 | aceptado | Juan José | Ricardo Andreas Herbert Villagomez | Inscripción Gap Year Australia | $13,500.08 |
> | 00249 | 19/8 | vencido | Rodrigo | Erika Coello | Perfilamiento Fernanda Miller | $10,000.00 |
>
> Quedan fuera las pruebas `Viaje0247`–`Viaje0254` (22-23/7, "TEST BV").

> **Actualización 23/9 — el checklist vigente es D2 de `guia-recta-final-ejecutable-2026-09-20.md`** (y A9 para
> lo que pasa Venttur). Estado por API: 26 productos ✅ · 0 proveedores de pago · 0 plantillas de cotización y
> factura · perfil de la empresa sin razón social ni RFC · Rodrigo, Andrés y Mauricio con permiso de facturas y
> pagos. Novedades respecto de este documento: (1) lo que falta pedir se redujo a datos bancarios, un presupuesto
> real (de ahí salen términos, política y formato), la cuenta de cobro con tarjeta (propuesta: la de PayPal que ya
> usan en `PMR`) y confirmar IVA; (2) el "workflow Invoice Paid → pipeline" ya lo cubren los flujos publicados de
> Rodrigo: lo que falta es revisar sus disparadores y que distingan Idiomas de Internados; (3) se suman el
> procedimiento de transferencia (registrar el pago a mano) y la reemisión en GHL de los presupuestos abiertos
> en Clientify. Las menciones a "0 products" de §2 y §4 quedaron viejas.

> Disparado por Rodrigo (21/9): *"El presupuesto es el paso inicial de trigger para iniciar los procesos…
> es el cotizador paso 1 de todos los procesos de venta. Ahí es donde le enviamos la factura o cotización
> a los clientes potenciales, y una vez que lo pagan, ya son parte de nuestro proceso. En los presupuestos
> viene cada uno de los servicios que tenemos y parte importante es que también vienen nuestros datos
> bancarios y para hacer el pago con tarjeta."*
>
> **Este ítem NO estaba en el plan de migración.** Es real y hay que integrarlo antes de apagar Clientify.

## 1. Qué es hoy (Clientify)

El **módulo Budgets/Presupuestos de Clientify**. Un presupuesto es una cotización con:
- **Line items** = los servicios/programas de Venttur (nombre, cantidad, precio, impuesto, descuento, total).
- **PDF branded** (logo Venttur + datos fiscales de la empresa: *Viajes y Experiencias GARDE S de RL de CV*,
  RFC **VEG221012DA6**, Juan Palomar y Arias 616, Guadalajara, Jalisco, tel 3320016463, contacto@venttur.com).
- **URL externa** (`{budget_externalurl}`) donde el cliente **ve / acepta / rechaza / paga con tarjeta**.
- **Datos bancarios** para transferencia (según Rodrigo; en los templates dummy van en "Términos de compra").
- **Email de envío** (plantilla con `{firstname}`, `{budget_name}`, `{budget_externalurl}`, `{signature}`).

Rol en el funnel: **es el paso 1 / trigger del proceso de venta.** El lead califica → asesor manda
presupuesto → cliente paga → entra al pipeline como cliente. Fuente: `Downloads/Clientify/recursos/presupuestos/`
(2 PDFs template dummy + `Plantilla de envío correo.md`).

## 2. Respuestas a Rodrigo

- **"¿Qué vamos a hacer con los presupuestos?"** → Se reemplazan por **GHL Estimates + Invoices** (feature nativa
  de GHL, equivalente 1:1: line items, PDF, link para ver/aceptar/pagar, email de envío, trigger al pipeline).
- **"¿Ya los tenemos migrados?"** → **No todavía.** Lo que hay que migrar/armar en GHL:
  - **Catálogo de servicios** (los "programas" con precios) → GHL **Products**. Hoy la sub-cuenta VTR tiene
    **0 products** (verificado por API). ⚠️ El catálogo real (servicios + precios) **no está en los PDFs
    dummy** — hay que sacarlo de Clientify (módulo Budgets → Productos) o que Rodrigo/Mauricio lo pasen.
  - **Template de estimate/invoice** branded (logo + datos fiscales GARDE/RFC + datos bancarios + términos).
  - **Integración de pago con tarjeta** → hoy VTR tiene **0 payment providers conectados** (verificado por API).
  - **Los presupuestos históricos** (cotizaciones viejas ya enviadas) **NO hace falta migrarlos** — son
    transaccionales por lead; los aceptados ya convirtieron. Se migra la **capacidad** + el **catálogo** + el
    **template**, no el histórico.

## 3. Equivalencia Clientify → GHL

| Clientify (Budgets) | GHL (nativo) |
|---|---|
| Presupuesto / cotización | **Estimate** (cotización que el cliente acepta) → convierte a **Invoice** |
| Line items (servicios) | **Products** (catálogo) + line items del estimate/invoice |
| PDF branded | Template de Invoice/Estimate en GHL (logo + business info + terms) |
| `{budget_externalurl}` (ver/aceptar/pagar) | Link público del estimate/invoice de GHL (ver/aceptar/pagar) |
| Pago con tarjeta | **Payment integration** de GHL (Stripe / NMI / proveedor) — **falta conectar** |
| Datos bancarios (transferencia) | Bloque en "Terms & Notes" del template de invoice |
| Email de envío | Email nativo de GHL al mandar el estimate/invoice |
| "Pagó → entra al proceso" | **GHL Workflow** trigger *Invoice Paid* / *Estimate Accepted* → mueve el contacto de etapa en el pipeline |

## 3.bis Estado de ejecución (2026-09-22)

- ✅ **26 productos MXN cargados en GHL Products** (por API, `scripts/cargar-products-ghl.py`, idempotente
  por nombre + precio adjunto verificado). Fuente: `~/Downloads/ListProducts.csv` + `ListProducts-2.csv` (47
  filas). Curación: descartados **2 test** (ELTIS, Prueba) + **3 one-off** (cotizaciones de clientes puntuales:
  Marcelo Guadiana, Javier y Anna Heinze, Lia Mariana/China) + dedup (Perfilamiento 1). IVA 16%: se cargó el
  **precio base**; el IVA se aplica a nivel de invoice/template (Camilo).
  - ⚠️ 4 productos MXN llevan precio "según TC del día" (La Garenne, Camp Lyceum, ALPADIA, Learn&Study) —
    cargados con nota en la descripción; verificar antes de cotizar.
- ✅ **15 productos en moneda extranjera — decisión tomada (la agencia 2026-09-22): línea manual al cotizar.**
  NO se cargan como productos fijos (la location GHL es MXN). El asesor los agrega como **línea manual** en
  el Estimate, convertidos a MXN al TC del día (como en Clientify). Precios de referencia en su moneda:
  `06_docs/presupuestos-productos-moneda-extranjera-referencia.md`.
- 🔴 **Datos bancarios: NO encontrados** en los archivos de texto de `recursos/` ni en las capturas
  revisadas (son templates de email). Probablemente estén en la **vista externa del budget** (la URL de
  ejemplo `app.clientify.com/budgets/view_v2/2258304/...`) o en una captura específica. Pendiente: la agencia
  indica el archivo exacto, o se extraen de la vista del budget de Clientify antes de apagarlo.

## 4. Qué hay que construir (setup GHL)

1. **Products** — cargar el catálogo real de servicios/programas + precios (falta el dato; ver §5).
2. **Business info** de facturación en GHL → Settings → Business Profile: razón social *Viajes y Experiencias
   GARDE S de RL de CV*, RFC VEG221012DA6, dirección, logo Venttur.
3. **Template de Invoice/Estimate** → branded + **bloque de datos bancarios** en Terms/Notes + política.
4. **Payment integration** (para pago con tarjeta):
   - **MVP (rápido, sin dependencia):** solo transferencia (datos bancarios en el template) + link de pago
     con tarjeta que Venttur **ya use hoy** (si existe) pegado en el estimate. Sin integrar nada en GHL.
   - **Completo:** conectar el proveedor de pago de Venttur (Stripe u otro) a GHL → pago con tarjeta nativo
     dentro del link del estimate. Requiere las credenciales del proveedor de Venttur (dependencia Mauricio).
5. **Workflow "presupuesto pagado → pipeline"** — GHL Workflow con trigger *Invoice Paid* (o *Estimate Accepted*)
   → mueve el contacto a la etapa de venta correspondiente + notifica al asesor. (Reemplaza el trigger que hoy
   hace Clientify al pagar.)
6. **Email de envío** — usar el nativo de GHL (o replicar la plantilla de correo con las variables GHL).

## 5. Bloqueantes / decisiones (para avanzar)

- 🔴 **Catálogo real de servicios + precios** — no está en los PDFs dummy. Sacarlo de Clientify (Budgets →
  Productos) **antes de apagar Clientify (sábado)** o pedírselo a Rodrigo/Mauricio. Sin esto no se cargan los Products.
- 🔴 **Datos bancarios** de Venttur (cuenta/CLABE) — no están en los templates dummy. Pedírselos.
- 🟡 **Pago con tarjeta:** **la agencia lo consulta con Rodrigo/Mauricio** (2026-09-22) — qué usan hoy para cobrar
  con tarjeta. Con eso se decide MVP (link existente + transferencia) vs integración nativa en GHL.
- ✅ **Ownership del setup GHL (decidido 2026-09-22):** **la agencia/Claude cargan los Products por API** + arman el
  workflow *Invoice Paid → pipeline*. El **template de Estimate/Invoice branded** lo arma **Camilo en la UI**
  (es UI-céntrico). Business Profile (razón social/RFC) también UI.

## 6. Urgencia y encuadre en la recta final

- **NO es bloqueante del cutover del 24/9** (el presupuesto no es parte del flujo inbound del bot — pasa
  después, en la conversación de venta del asesor).
- **SÍ es bloqueante de CIERRE-1 (apagar Clientify, sábado 26/9):** si los presupuestos viven en Clientify y
  se apaga sin reemplazo GHL, los asesores pierden el cotizador. → La capacidad GHL debe estar lista **antes
  del sábado**, o se pospone el apagado de Clientify para este módulo.
- Encaje: nueva sección en la recta final entre POST y CIERRE (o §N nueva en la guía de raíz).

## 7. Plan sugerido (una vez confirmadas §5)

1. Rodrigo/Mauricio pasan: catálogo servicios+precios + datos bancarios + decisión de pago (MVP vs integrado).
2. Cargar **Products** en GHL (API o UI) con el catálogo.
3. Configurar **Business Profile** + **template de Estimate/Invoice** branded + bloque bancario.
4. (Fase 2 opc.) Conectar payment provider para tarjeta.
5. Armar **Workflow "Invoice Paid → pipeline"**.
6. Smoke: crear un estimate de prueba, mandarlo, verificar link + PDF + (pago) + trigger de pipeline.
7. Capacitar a los asesores (Rodrigo) en crear/enviar estimates desde GHL. **Antes de apagar Clientify.**
