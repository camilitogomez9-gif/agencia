# Email HTML Generator

Generá un HTML elegante, responsivo y email-safe para reportes que se envían por correo desde n8n. Recibe el JSON con datos del reporte y el HTML actual del nodo "Send a message" como referencia, y devuelve un nuevo HTML mejorado, listo para copiar y pegar en n8n.

## Variables

input: $ARGUMENTS (opcional — puede contener un override de tema y/o contexto del cliente, ej: `tema:duolingo cliente:Narvaja`; si no se especifica tema, se infiere automáticamente)

---

## Instrucciones

### Fase 0: Recepción de Inputs

Si el usuario no pegó el JSON y el HTML viejo en el mismo mensaje del comando, pedíselos así:

```
Para generar el HTML necesito 2 cosas:

1. **JSON con datos del reporte** — el output del nodo previo en n8n (ej: el JSON que devuelve el agente IA o el query SQL).
2. **HTML actual** — el contenido actual del campo "Message" del nodo Gmail/SMTP en n8n.

Pegámelos a continuación. Opcionalmente podés indicar:
- Cliente: nombre del cliente (si no está claro del HTML)
- Override de tema: `duolingo` | `corporate` | `minimal` | `warm` (si no se especifica, lo infiero automáticamente del contexto)
- Requisitos especiales: ej. "incluir logo", "secciones colapsables", etc.
```

Si el usuario sí pegó los inputs, procedé a Fase 1.

---

### Fase 1: Análisis de Inputs

#### 1.1 Analizar el JSON

Identificá:
- **Estructura:** ¿es plano? ¿anidado? ¿tiene arrays?
- **Campos disponibles:** listá todos los keys, agrupando por tipo:
  - **Métricas numéricas** (integers, floats): para hero/KPIs
  - **Strings cortos** (ej: nombres, categorías): para badges/pills
  - **Strings largos** (ej: insights, recomendaciones): para cards
  - **Pares relacionados** (ej: `producto_1` + `cantidad_1`): para tablas ranked
  - **Porcentajes**: para barras de progreso
  - **Fechas/timestamps**: para footer/header
- **Patrones repetidos:** ej. `producto_1`, `producto_2`, `producto_3` → es una tabla top-3

#### 1.2 Analizar el HTML viejo

Extraé:
- **Variables de interpolación n8n:** todas las ocurrencias de `{{ $json.X }}`, `{{ $json.output[0].content[0].text.Y }}`, etc. Hacé una lista. **Estas deben preservarse exactamente en el HTML nuevo.**
- **Mapping JSON ↔ Variables:** cruzá los keys del JSON con las variables del HTML para entender cómo se referencian.
- **Estructura actual:** ¿qué secciones tiene? (header, métricas, listas, footer, etc.)
- **Cliente / contexto:** ¿hay nombre del cliente, emoji, branding visible?
- **Paleta actual:** ¿hay colores dominantes? (extraé hex codes)

#### 1.3 Reportá brevemente al usuario lo que encontraste

Antes de generar el HTML, mostrá:

```
📊 **Análisis completado:**

- **JSON:** [N] campos detectados — [breve descripción de la estructura]
- **HTML viejo:** [N] variables n8n preservadas
- **Cliente detectado:** [Narvaja Hogar / desconocido]
- **Tema inferido:** [duolingo / corporate / minimal / warm] — [razón: ej. "contexto dental → minimal" / "override explícito del usuario"]

Procedo a generar el HTML nuevo.
```

---

### Fase 2: Selección de Tema (Auto-detección)

**El tema se infiere automáticamente.** Si el usuario incluyó `tema:X` en `$ARGUMENTS`, ese override tiene prioridad absoluta. Si no, aplicá las siguientes reglas en orden:

#### Reglas de inferencia (en orden de prioridad)

**1. Override explícito:** si `$ARGUMENTS` contiene `tema:duolingo`, `tema:corporate`, `tema:minimal` o `tema:warm` → usar ese tema sin inferir.

**2. Palabras clave en el HTML viejo o nombre del cliente:**

| Contexto detectado | Tema |
|---|---|
| dental, médico, clínica, odontología, salud, farmacia, legal | `minimal` |
| finanzas, reporte ejecutivo, facturación B2B, empresa, CFO, balance | `corporate` |
| conversaciones, leads, agente, WhatsApp, escalamientos, IA, agente, bot, métricas de engagement | `duolingo` |
| CRM, clientes, ventas, retail, tienda, reservas, hospitality, e-commerce | `warm` |

**3. Estructura del JSON:**
- Solo fechas/rangos sin métricas de volumen → `minimal`
- Muchas métricas numéricas + campos de texto/insights → `duolingo`
- Campos financieros (montos, porcentajes, períodos contables) → `corporate`
- Campos de contactos/leads sin métricas complejas → `warm`

**4. Default si no hay señal clara → `corporate`**

---

#### Tema 1: **Duolingo**

Vibrante, moderno, con header oscuro y acentos vivos. Ideal para reportes de operaciones, agentes conversacionales, métricas de engagement.

```
Colores propios:
- Primary:   #6366f1  (Indigo)
- Secondary: #a855f7  (Purple)
- Accent:    #ec4899  (Pink)
- BG light:  #f0f0f0
- BG card:   #ffffff
- Text:      #1f2937 (dark) / #6b7280 (muted)
- Border:    #e5e7eb

Capa la agencia en este tema:
- Header bg: #0d0a1f (navy) con gradient lateral sutil si es posible
- Accent bar: #7c3aed (3px)
- Outer bg:  #f0f0f0 (se mantiene, el tema ya es oscuro en header)
- Footer bg: #0d0a1f | Footer name: #ffffff | Footer tagline: #a78bfa

Tipografía:
- Family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif
- H1: 32-48px, weight 700
- H2: 18-22px, weight 600
- Body: 14-15px

Spacing:
- Padding sección: 32-40px
- Border-radius: 16px (cards), 8px (badges)
```

#### Tema 2: **Corporate**

Profesional, sobrio, B2B. Ideal para reportes ejecutivos, finanzas, servicios profesionales.

```
Colores propios:
- Primary:   #2563eb  (Blue 600)
- Secondary: #1e40af  (Blue 800)
- Accent:    #0ea5e9  (Sky)
- BG light:  #f8fafc
- BG card:   #ffffff
- Text:      #0f172a (dark) / #475569 (muted)
- Border:    #cbd5e1

Capa la agencia en este tema:
- Header bg: #0d0a1f (navy) — reemplaza el slate-800 original
- Accent bar: #7c3aed (3px) — reemplaza el blue de acento
- Outer bg:  #f5f3ff (lavender claro) — tono la agencia suave
- Footer bg: #0d0a1f | Footer name: #ffffff | Footer tagline: #a78bfa
- CTAs y left bars: #2563eb (blue del tema) o #7c3aed según contexto

Tipografía:
- Family: 'Inter', -apple-system, sans-serif
- H1: 28-36px, weight 600
- H2: 18-20px, weight 600
- Body: 14px

Spacing:
- Padding sección: 28-36px
- Border-radius: 8px (cards), 4px (badges)
```

#### Tema 3: **Minimal**

Limpio, tipografía como protagonista. Ideal para dental, médico, legal, reportes ejecutivos simples.

```
Colores propios:
- Primary:   #1a1a2e  (dark navy-tinted, reemplaza #000000 puro)
- Secondary: #404040
- Accent:    #737373
- BG light:  #ffffff
- BG card:   #fafafa
- Text:      #1a1a2e (dark) / #6b7280 (muted)
- Border:    #e5e7eb

Capa la agencia en este tema:
- Header bg: #0d0a1f (navy)
- Accent bar: #7c3aed (3px) — el único toque de color del tema
- Left bars en items: #7c3aed
- Outer bg:  #f5f3ff (lavender muy suave)
- Secciones destacadas (fechas, KPIs): bg #f5f3ff, border #ddd6fe, label en #7c3aed
- Footer bg: #0d0a1f | Footer name: #ffffff | Footer tagline: #a78bfa

Tipografía:
- Family: 'Helvetica Neue', Helvetica, Arial, sans-serif
- H1: 36-48px, weight 300 (light)
- H2: 16-18px, weight 500
- Body: 14px

Spacing:
- Padding sección: 40-48px (más aire)
- Border-radius: 0 (sin redondeo)
```

#### Tema 4: **Warm**

Cálido, acogedor. Ideal para CRM, atención al cliente, retail, hospitality.

```
Colores propios:
- Primary:   #f97316  (Orange 500)
- Secondary: #dc2626  (Red 600)
- Accent:    #fbbf24  (Amber 400)
- BG light:  #fff7ed
- BG card:   #ffffff
- Text:      #431407 (dark) / #9a3412 (muted)
- Border:    #fed7aa

Capa la agencia en este tema:
- Header bg: #0d0a1f (navy) — reemplaza el orange-900 original
- Accent bar: #7c3aed (3px) — toque de marca sobre header navy
- Outer bg:  #fff7ed (se mantiene el warm del tema)
- Footer bg: #0d0a1f | Footer name: #ffffff | Footer tagline: #a78bfa
- El resto del cuerpo (cards, pills, texto) mantiene la paleta naranja/roja

Tipografía:
- Family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
- H1: 30-40px, weight 700
- H2: 18-20px, weight 600
- Body: 14px

Spacing:
- Padding sección: 32-40px
- Border-radius: 12px (cards), 9999px (pills)
```

---

### Capa de Marca la agencia (aplica a todos los temas)

La paleta de marca de la agencia se aplica en los puntos de contacto estructurales del email. Los colores propios de cada tema rigen el contenido; la agencia rige el marco.

```
Paleta la agencia (email-safe):
- Dark navy:      #0d0a1f  → header bg, footer bg
- Brand purple:   #7c3aed  → accent bar 3px, left bars en items, borders activos, labels uppercase en secciones destacadas
- Light purple:   #a78bfa  → texto secundario en superficies oscuras (header, footer)
- Lavender bg:    #f5f3ff  → outer background del email, secciones destacadas (fechas, KPIs)
- Purple border:  #ddd6fe  → bordes de secciones sobre lavender bg

Reglas universales:
- Outer bg:   #f5f3ff (lavender la agencia) — salvo duolingo/warm que tienen outer propio
- Header bg:  #0d0a1f siempre
- Accent bar: 3px sólido #7c3aed justo debajo del header
- Footer bg:  #0d0a1f | nombre: #ffffff | tagline "la agencia®": #a78bfa

Excepciones estéticas permitidas (no son errores):
- Colores semáforo para datos con umbrales o estado:
  verde #16a34a / amarillo #ca8a04 / rojo #dc2626
  Tienen prioridad visual sobre el branding cuando la claridad del dato lo requiere.
- Fondo blanco #ffffff en el cuerpo principal — siempre, para máxima legibilidad.
- Si un tema tiene un color primario muy fuerte (naranja, azul), puede usarse en CTAs y pills
  del cuerpo aunque no sea purple; la barra de acento sigue siendo #7c3aed.
```

---

### Fase 3: Diseño del Nuevo HTML

#### 3.1 Mapeo Inteligente de Datos → Visualización

Según los campos del JSON, usá la siguiente tabla para decidir qué tipo de visualización generar:

| Patrón de Campos | Visualización Sugerida |
|-------------------|------------------------|
| Un solo número grande (ej: `total`, `count`) | **Hero**: número 50-60px centrado con etiqueta debajo |
| Múltiples métricas numéricas independientes | **Grid de KPIs**: 2-3 columnas, cada uno con número + label |
| Pares ranked (`item_1`+`count_1`, `item_2`+`count_2`...) | **Tabla ranked**: número + texto + badge con cantidad |
| Lista de categorías sin conteos | **Pills/badges horizontales** |
| Strings largos numerados (`insight_1/2/3`, `recomendacion_1/2/3`) | **Cards numeradas**: círculo con número + texto |
| Porcentajes (`porcentaje_X`) | **Barra de progreso** o **donut chart** (con CSS puro) |
| Campo de problemas/alertas | **Box destacado** con borde de color (rojo/naranja) |
| Pares de motivos de escalamiento | **Lista con bullet** o tags |
| Texto explicativo / contexto | **Párrafo sobrio** con jerarquía clara |

#### 3.2 Estructura HTML Recomendada (Email-Safe)

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:[BG_LIGHT];font-family:[FONT_FAMILY];">
  <!-- Container principal: tabla para compatibilidad email -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="[BG_LIGHT]">
    <tr>
      <td align="center" style="padding:32px 16px;">
        <!-- Container de 600px max -->
        <table width="600" cellpadding="0" cellspacing="0" border="0"
               style="max-width:600px;width:100%;background:#ffffff;border-radius:[RADIUS];overflow:hidden;">

          <!-- HEADER -->
          <tr><td style="...">[Header]</td></tr>

          <!-- HERO (métrica principal) -->
          <tr><td style="...">[Hero]</td></tr>

          <!-- SECCIONES dinámicas según JSON -->
          <tr><td style="...">[Sección 1]</td></tr>
          <tr><td style="...">[Sección 2]</td></tr>
          ...

          <!-- FOOTER -->
          <tr><td style="...">[Footer la agencia]</td></tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
```

#### 3.3 Reglas Email-Safe (CRÍTICAS)

✅ **HACER:**
- Todo el CSS **inline** (en atributos `style`)
- Layout con **tablas** (`<table>`, `<tr>`, `<td>`)
- `cellpadding="0"` `cellspacing="0"` `border="0"` en todas las tablas
- Colores en **HEX** (ej: `#6366f1`)
- Fallback fonts: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif`
- `max-width: 600px` en container principal
- Imágenes con `display: block;` para evitar gaps
- Padding/margin en `<td>` (no en divs)
- DOCTYPE HTML5 + `<meta name="viewport">`
- Emojis para iconos (universalmente soportados)

❌ **NO HACER:**
- `<style>` tags (varios clientes los stripean)
- Clases CSS (mismo motivo)
- Flexbox / Grid CSS (no soportado en Outlook viejo)
- `position: absolute` / `fixed`
- JavaScript
- Web fonts críticos (Google Fonts ok solo como mejora, no como dependencia)
- Background images (Outlook no las renderiza)
- Border-radius en imágenes (Outlook no lo soporta)

#### 3.4 Preservación de Variables n8n (CRÍTICO)

Las variables del HTML viejo del estilo `{{ $json.output[0].content[0].text.FIELD }}` deben **copiarse exactamente** en el HTML nuevo, en los lugares correspondientes según el mapping del JSON.

**Ejemplo:**
- HTML viejo: `<p>Total: {{ $json.output[0].content[0].text.conversaciones_total }}</p>`
- HTML nuevo (Hero): `<p style="font-size:60px;color:#6366f1;font-weight:700;margin:0;">{{ $json.output[0].content[0].text.conversaciones_total }}</p>`

**Reglas:**
- ✅ Preservar el path completo (`$json.X.Y.Z`)
- ✅ Preservar las llaves dobles `{{ }}`
- ✅ Preservar los espacios dentro de las llaves (la sintaxis n8n los tolera)
- ❌ NUNCA reemplazar la variable con el valor del JSON (el JSON solo sirve para entender estructura)

---

### Fase 4: Generación del Output

Devolvé al usuario:

#### 4.1 HTML completo en bloque de código

```html
<!DOCTYPE html>
... (HTML completo aquí)
```

#### 4.2 Resumen de cambios

```
✅ **HTML generado**

📐 **Diseño:**
- Tema: [duolingo / corporate / minimal / warm] — [inferido por: contexto dental / override explícito / etc.]
- Capa la agencia: header #0d0a1f · accent bar #7c3aed · footer #0d0a1f / #a78bfa
- Secciones: [Header → Hero → Sección X → Sección Y → Footer]
- Layout: tabla 600px max-width, responsive

🔗 **Variables n8n preservadas:** [N]
- `{{ $json.output[0].content[0].text.conversaciones_total }}`
- `{{ $json.output[0].content[0].text.producto_1 }}`
- ... (lista completa)

📋 **Próximos pasos:**
1. Copiá el HTML del bloque de arriba.
2. Pegalo en el campo "Message" del nodo "Send a message" en n8n (reemplazando el HTML actual).
3. Asegurate que el campo está en modo HTML (no plain text).
4. Ejecutá el workflow una vez para testear.
5. Verificá la renderización en Gmail desktop, Gmail mobile y Outlook si es posible.

⚠️ **Notas:**
- [Cualquier warning relevante: ej. variables del HTML viejo que no estaban en el JSON, secciones que se omitieron por falta de datos, etc.]
```

---

### Fase 5: Validación Final (Checklist Interno)

Antes de entregar, Claude verifica mentalmente:

- [ ] Todo el CSS es **inline** (no hay `<style>` tags)
- [ ] El layout usa **tablas** (no divs para estructura)
- [ ] `max-width: 600px` en container principal
- [ ] Todos los colores están en **HEX**
- [ ] **Variables n8n preservadas** exactamente como en el HTML viejo
- [ ] Fallback fonts incluidos
- [ ] DOCTYPE y meta viewport presentes
- [ ] No hay JS, no hay flexbox/grid
- [ ] El tema se aplicó consistentemente en el cuerpo del email
- [ ] **Capa la agencia presente:** header `#0d0a1f`, accent bar `#7c3aed` (3px), footer `#0d0a1f` con tagline `#a78bfa`
- [ ] El HTML es **válido** (todas las tags cerradas, atributos correctamente comillados)

Si algún check falla → corregir antes de entregar.

---

## Notas Operativas

- **No guardes el HTML en un archivo** — el output va directo al chat para que el usuario lo copie. (Salvo que el usuario lo pida explícitamente.)
- **Si el JSON tiene campos no usados** en el HTML viejo, mencionalos como "campos disponibles que podríamos visualizar" pero **no los uses sin permiso del usuario** — puede que sean campos internos no destinados al email.
- **Si el HTML viejo tiene variables que no están en el JSON**, mencionalo como warning. Puede ser un bug del workflow o un campo que el LLM ocasionalmente no devuelve.
- **Si el JSON está vacío o malformado**, pedí al usuario que verifique la fuente antes de generar.
- **Iteración:** si el usuario pide cambios sobre el HTML generado (ej. "cambiá el color a verde", "agregá una sección de…"), aplicá los cambios sobre la última versión generada.
