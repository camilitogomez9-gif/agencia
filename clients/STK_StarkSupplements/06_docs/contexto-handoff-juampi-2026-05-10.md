# Contexto: Handoff de Juampi → la agencia (2026-05-10)

Resumen técnico del traspaso del proyecto Stark Supplements. Basado en la llamada del 10 de mayo + análisis de los 4 workflows n8n.

---

## Sobre el cliente

- **Stark Supplements**: tienda de suplementos deportivos que opera en Bolivia (Santa Cruz, La Paz, Cochabamba). Producen en EEUU bajo marca propia **ISOX**.
- **Dueño**: Cristian. Facturan bastante, marca posicionada en Bolivia.
- **Múltiples e-commerce**: Cristian maneja ~5 tiendas online (FitClub, Pangarch, PedidoFit, etc.) que compiten entre sí para cubrir mercado. Todas en el mismo Kommo (problema de webhooks cruzados). Solo nos enfocamos en **Stark**.
- **5 vendedores a comisión** que quieren reemplazar con el agente. Ellos propusieron ponerlo en producción.
- **Comunicación**: responden una vez cada mil. "Todos los días hay que estar insistentes". Son "re chill" pero lentos.
- **Hackeo**: les hackearon Kommo recientemente, cambiaron contraseñas.
- **Bots borrados (x6)**: el cliente borra bots de Kommo repetidamente. Hay que reclamarles y reconstruir cada vez.

## Estado actual

- El agente fue construido por Juampi y ya fue probado por el cliente.
- El cliente quiere ponerlo en producción.
- **No poner en producción hasta que paguen**: USD 1.500 del build + primera transferencia de mantenimiento. Si no, empiezan los cambios y nunca pagan.
- Las credenciales están en el Notion de la agencia (sección Stark Supplements).
- Juampi pasa: catálogos de producto, manual de ventas del cliente, acceso a Airtable.

## Arquitectura técnica (4 workflows)

### 1. OFICIAL Stark Supplements (Agente principal)
- **Trigger**: webhook de Kommo (mensajes entrantes)
- **Filtro**: ignora mensajes de Telegram (solo producción), ignora leads que ya no están en pipeline de IA
- **Tipos de mensaje**: texto, voz (Whisper), imagen (detección de comprobantes de pago con GPT-4o)
- **Anti-spam**: Redis como buffer — acumula mensajes por 10 seg, procesa todos juntos
- **Contexto**: query SQL a Postgres trae últimas 8 interacciones formateadas (limpia tool traces, prefijos, etc.)
- **Primera interacción**: envía mensaje de bienvenida vía salesbot de Kommo, inserta en memoria manualmente
- **Agente "Kathe"**: GPT-4o, temperature 0.3, memoria Postgres (20 msgs)
- **3 herramientas (tools)**:
  - `verificar_producto` → sub-workflow que busca en Airtable, decide pack vs. unitario, envía imágenes
  - `enviar_info_producto` → sub-workflow externo (no está en los archivos compartidos, workflow id: `ohBBqP0ViMDOzYFp`)
  - `elevar_conversacion` → cambia pipeline en Kommo
- **Post-procesador**: GPT-4.1-mini limpia markdown, divide en parte1/parte2
- **Envío**: actualiza campo custom en Kommo (field 1717536) + dispara salesbot (bot_id 85808)
- **Activa seguimiento**: llama al workflow de seguimientos async al final

### 2. Seguimientos (4 toques automáticos)
- Se activa después de cada interacción del agente
- **Genera los 4 mensajes de seguimiento de una sola vez** con GPT-4.1-mini (JSON estructurado)
- Cadencia: 30min → 2h → 8h → 24h
- Antes de cada envío verifica en Postgres si el usuario respondió (compara último msg AI vs. esperado)
- Si el usuario responde, la cadena se corta
- Después de 24h sin respuesta, mueve el lead a pipeline "PERDIDOS"

### 3. Elevar Conversación
- Recibe: resumen, producto de interés, motivo (bucket), entity_id
- 4 buckets: PAGO_PENDIENTE, QUIERE_HUMANO_O_TIENDA, SALUD_SENSIBLE, RECLAMO_O_CASO_ESPECIFICO
- **Problema**: los 4 nodos PATCH existen pero están **desconectados** del flujo. Solo funciona el trigger → Edit Fields. Hay que cablear el routing.

### 4. Tool Verificar Producto
- Decide si recomendar **pack** o **unitario** (GPT-4.1-mini, clasificador binario)
- Busca en Airtable (base `appuXkgI7RaGv3Tjp`, tabla `Prods`)
- Agente matcher selecciona el mejor producto, maneja RESOLVED/AMBIGUOUS/NOT_FOUND
- Para cada producto: genera intro técnica en 2 partes (GPT-4o-mini), envía parte1 + parte2 + foto vía salesbot
- Tiene sistema de exclusión de productos ya mostrados (cache)

### Sub-workflow faltante
- **Stark | Enviar Información** (workflow id: `ohBBqP0ViMDOzYFp`): referenciado como tool `enviar_info_producto` pero **no fue exportado**. Hay que buscarlo en n8n o recrearlo.

## Integraciones y credenciales

| Servicio | Credential ID | Nombre |
|----------|--------------|--------|
| Kommo (OAuth2) | HxDUJfO30VIHpAiP | S.S \| Kommo |
| OpenAI | CWz84fUE1wUT8CXn | Stark Supplements |
| PostgreSQL | 6DnX94CDxROcqpbH | Stark Supplements |
| Redis | HuFrHjEG5LTpeAvh | Stark Supplements |
| Airtable | 4cTEmbk75advsozg | Stark Supplements |
| Telegram | 1Kt6KZ1kzoNHF7oJ | Telegram account |

- **Kommo domain**: `criscapitalbrothers.kommo.com`
- **Airtable base**: `appuXkgI7RaGv3Tjp`
- **Telegram grupo equipo**: `-4925599962`
- **Salesbot principal**: bot_id `85808`
- **Salesbot bienvenida**: bot_id `77760`
- **Campo custom Kommo para mensajes**: field_id `1717536`
- **Timezone agente**: America/La_Paz
- **Timezone horario comercial**: America/Mexico_City (L-V 9-18, S 9-14)

## Detalle de producto / Airtable

- **Productos unitarios (~22)**: Creatina Monohidratada, Whey Protein, ISO-X (Isolate), Pre Entrenamiento, Termogénico Stark Burner, Ashwagandha, Omega 3, Glutamina, Colágeno, Multivitaminas, BCAA
- **Packs**: combinaciones con tiers (COMBO → SUPER PACK → MEGA PACK → PRO PACK → MAX → INFINITI)
- **Shaker**: producto especial con variaciones de color, tiene herramienta dedicada (HTTP que dispara bot con imágenes de colores)
- **Campos Airtable**: Nombre, Sabor, Contenido Neto, Precio, Categoría, Estado (Activo), Tipo (Unitario/Packs), Casos de Uso, Como Ingerir, Datos Clave, bot_id
- Cada producto tiene un `bot_id` propio en Kommo para enviar la foto

## Pipelines Kommo

| Pipeline | Propósito |
|----------|-----------|
| 11622596 | Pipeline IA (el agente atiende) |
| 13155539 / status 101442331 | Seguimientos (SEG) |
| 13155539 / status 143 | Perdidos |
| 100395523 | Atención personalizada (elevado a humano) |

## Similitudes con Happy Flops

- Misma mecánica de envío de imágenes de producto vía Kommo salesbot
- Mismo patrón de variables custom en Kommo + bot trigger
- Mismo problema de webhooks cruzados por tener múltiples negocios en un Kommo
- Seguimiento con IA que lee contexto y genera mensajes personalizados (no template fijo)

## Notas de Juampi

- "Estos agentes trabajan con ubicaciones — cada sucursal es un nodo en el switch que envía horarios + imagen + link Google Maps"
- "El nodo de verificar producto es largo, pero infalible — tiene muchos puntos de apoyo"
- "Hay workflows obsoletos de pruebas en n8n — se pueden borrar (sacar screenshot antes)"
- "No quiero que lo modifiquemos más antes de producción, a no ser que nos lo digan"
- "Los precios no llegan al agente matcher — habría que sumarlos al formato del Code node para manejar 'más barato/más caro'"
- "Se podría eliminar el nodo que trae la última interacción por separado — el IF ya lo resuelve"
