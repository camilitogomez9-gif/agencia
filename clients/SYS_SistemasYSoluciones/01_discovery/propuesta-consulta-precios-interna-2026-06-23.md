# Propuesta — Consulta de precios interna para Rodrigo

**Cliente:** Sistemas y Soluciones
**Fecha:** 2026-06-23
**Origen:** Mail Edgardo del 2026-06-23, punto 3.

---

## Qué hace

Una mejora para que **Rodrigo pueda consultar precios reales al agente desde su WhatsApp** y recibir respuesta automática en menos de 2 segundos, leyendo directamente desde la planilla de Google Sheets que él ya mantiene actualizada.

El sistema reconoce automáticamente que es Rodrigo quien escribe, busca el precio en su sheet, y le devuelve los matches en el chat. Sin pasar por nadie, sin esperar respuesta humana, sin riesgo de filtración a leads externos.

## Cómo funciona en la práctica

1. Rodrigo le escribe al mismo número de WhatsApp del agente cualquier consulta de precio. Ejemplos:
   - "cuánto sale el HUENU UV 6004"
   - "precio Sinajet 60"
   - "DTF textil A3"
2. El sistema identifica que viene de Rodrigo (whitelist interna por número).
3. Lee la planilla de precios **en vivo**, en el momento — cualquier cambio que Rodri haga en su sheet impacta automáticamente. Sin sincronizaciones.
4. Devuelve hasta 5 matches en el chat, en texto plano, formato simple:
   ```
   Encontré 2 matches para "dtf textil":

   1. HUENU HR 6004 — DTF Textil
      Precio USD: 4.500
      Stock: SI

   2. HUENU HR 1602 — DTF Textil
      Precio USD: 2.800
      Stock: NO
   ```
5. Si la búsqueda es muy genérica (>5 resultados), el agente avisa y pide afinar con marca o modelo.
6. Si no encuentra match, lo dice directo.

## Qué entrega la agencia

- Detección automática del subscriber interno (whitelist por número de ManyChat).
- Lectura en vivo del Google Sheet de Rodri en cada consulta (cero sincronización manual, cero caché — cambios impactan al instante).
- Respuesta formateada con top 5 matches en texto plano simple.
- Logging en Supabase de cada consulta para auditoría y métricas (qué se consulta, cuántos matches devuelve, cuándo).
- Smoke tests pre-deploy: 5 casos validados (consulta válida, sin match, ambigua, lead externo bloqueado, robustez de consultas repetidas).
- Coexiste con el flujo del agente conversacional actual sin tocarlo — los leads externos siguen recibiendo el flujo normal.

## Qué necesitamos del equipo SyS

Para poder configurar el deploy:

1. **Link al Google Sheet de precios de Rodri** (URL completa) y nombre exacto de la pestaña que querés que el agente lea.
2. **Acceso al sheet para la cuenta** — confirmar que la cuenta de servicio de la agencia tiene permiso de lectura, o compartirla.
3. **Subscriber ID de Rodrigo en ManyChat** — lo conseguís entrando al chat de Rodri en ManyChat y copiando el ID de la URL.

Con esos 3 datos arrancamos.

## Inversión

**USD 240** — 2 horas de trabajo la agencia (curaduría del flujo, configuración, deploy y testing).

**Forma de pago:** 100% al aprobar la propuesta.

**Plazo de entrega:** 48 horas hábiles desde el pago + recepción de los 3 inputs del pre-flight.

## Garantía

14 días de fixes informales post-deploy si algo del comportamiento contratado no funciona como esperado.

## No incluido

Para evitar scope creep, los siguientes ítems se cotizan aparte si los necesitan más adelante:

- Agregar más usuarios al whitelist (otros vendedores, marketing, Edgardo).
- Migración de la fuente de precios desde Sheets a Airtable o base de datos.
- Modificaciones al sheet de Rodri o a su estructura.
- Alertas, reportes periódicos o dashboards sobre las consultas internas.
- Reformatear el output del agente (ej. enviar el match como imagen, agregar links de productos, etc.).

---

**¿Avanzamos?** Confirmá y mandanos los 3 inputs del pre-flight para arrancar.
