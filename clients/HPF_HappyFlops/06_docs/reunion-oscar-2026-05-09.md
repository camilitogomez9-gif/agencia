# Análisis de Reunión — HappyFlops + la agencia

**Fecha:** 2026-05-09
**Duración:** 39 minutos
**Participantes:** Oscar (HappyFlops Sandalias, dueño) · la agencia (la agencia)
**Grabación:** [Fathom](https://fathom.video/share/qxXykQznNxc3D5_6nxj3C6FPzT9iawZA)

---

## 1. Resumen ejecutivo

Reunión de seguimiento sobre la migración de HappyFlops desde Kommo a GoHighLevel (GHL). Oscar planteó mejoras concretas que quiere implementar una vez migrados: seguimientos personalizados basados en contexto de conversación, reportes de métricas de cierre, sistema de promociones rotativas con A/B testing, y mejora en detección de imágenes usando Claude (Anthropic). Se definió timeline de migración: iniciar implementación en GHL a mediados de julio, transición completa en agosto (la suscripción de Kommo se renueva el 26 de agosto). la agencia confirmó que él liderará la migración y solución post-migración (no Juan Pablo). Se discutió el manejo de memoria/historial de conversaciones y la posibilidad de una base de datos indefinida (~USD 25/mes extra).

**Decisiones clave:** mantener tiempos fijos de seguimiento (24h, 48h, 72h) pero personalizar los mensajes con contexto; crear etapa real de "ventas perdidas" vs. "en espera"; evaluar costo de memoria indefinida; implementar Claude para análisis de imágenes; arrancar GHL a mediados de julio.

---

## 2. Temas tratados

### 2.1 Personalización de seguimientos (reactivadores)

**Contexto:** Actualmente los seguimientos son rígidos — mismo mensaje para todos, tiempos fijos de 7 días. Oscar quiere que cada reactivador mencione los productos específicos que cotizó el lead ("te quedan 3 días para la cotización de 100 sandalias y 50 pantuflas").

**Decisión:** Personalizar el **texto** de los reactivadores usando contexto de la conversación y cotización. **No** personalizar los tiempos — mantener cadencia fija (24h, 48h, 72h hasta 7 días) porque presionar demasiado puede espantar al cliente.

**Impacto en migración:** Requiere que el agente de seguimiento lea el historial de conversación/cotización antes de generar el mensaje. Cambia la arquitectura de seguimientos de mensajes hardcodeados a mensajes generados por LLM con contexto.

---

### 2.2 Pipeline post-venta y etapas

**Contexto:** Oscar aclaró el flujo completo post-Etapa 4:

| Etapa | Responsable | Descripción |
|-------|-------------|-------------|
| Confirmar pago | IA → Humano | IA detecta pago, manda mensaje de "gracias, te confirmamos en la brevedad". **IA se detiene aquí.** Equipo humano confirma manualmente. |
| Pago sin diseño | Diseñadora | Lead pagó pero no tiene diseño. **Prioridad alta** — el cliente siente incertidumbre post-pago. |
| Diseño | Diseñadora | Diseño enviado, pendiente aprobación del cliente. Prioridad menor. |
| Producción | Equipo | Diseño aprobado, en producción física. |
| Pago de liquidación | IA + Humano | Al terminar producción, se envía saldo. **IA detecta segundo pago** y mueve a esta etapa. Luego se genera guía de envío. |
| Logrado con éxito | — | Venta completada, sale del pipeline visible. |

**Decisión:** Mantener las tres etapas post-pago (sin diseño / diseño / producción) como separadas. Oscar, la diseñadora y Rebeca ven diferentes vistas del mismo pipeline — cada una necesita su visibilidad.

**Problema resuelto:** Se confirmó que la IA debe reactivarse en "Producción" para detectar el pago de liquidación (segundo pago).

---

### 2.3 Manejo de "Ventas perdidas" y memoria

**Problema actual:** En Kommo, "ventas perdidas" se usaba para vaciar memoria (tope de 10,000 leads, se llenaba en ~1 semana). Al mover a ventas perdidas, la IA se desactivaba. Pero si quedaba activa, generaba contradicciones (le decía al cliente que no se podía → luego le pedía anticipo).

**Decisión:** Crear **dos etapas** diferenciadas:
1. **Ventas perdidas (real):** Lead genuinamente perdido (ej: evento es mañana, no llegamos a tiempo). IA no responde. Movimiento **manual** por el equipo.
2. **En espera:** Lead que no compró en el ciclo de reactivadores pero podría volver. **IA sigue activa** y responde si escribe.

**Dato crítico:** Hay clientes que compran hasta **6 meses** después del primer contacto. Rebeca contesta ~50 mensajes diarios de leads en "ventas perdidas" que escriben de vuelta — esto le quita tiempo que podría usar en otras tareas.

---

### 2.4 Memoria / historial de conversaciones

**Opciones discutidas:**

| Opción | Descripción | Costo |
|--------|-------------|-------|
| A | Borrar historial periódicamente (ej: 6 meses) | Incluido |
| B | Base de datos indefinida — guardar todo | ~USD 25/mes extra |

**Consenso tentativo:** Leads que completaron compra ("logrado con éxito") se borran a los 6 meses. Solo ~1% vuelve a comprar después de eso. Leads en espera también 6 meses.

**Pendiente:** la agencia va a pasar detalle de costos exactos de la opción B (memoria indefinida) para que Oscar decida.

---

### 2.5 Métricas y reportes

**Necesidad de Oscar:** Saber en qué momento del funnel compra la gente — día 1, día 3, día 5, día 7, después de un mes. Objetivo: medir tiempo de cierre para diseñar estrategias que aceleren la conversión.

**Estado actual:** No existe ningún reporte de métricas.

**Acción:** Implementar tracking de tiempo de cierre por lead (fecha de primer contacto → fecha de compra).

---

### 2.6 Sistema de promociones rotativas (A/B testing)

**Idea de Oscar:** Usar ahorros de una inversión en reducción de costos para trasladarlos como promociones al cliente. Quiere rotar promociones cada mes/quincena y medir cuál cierra más:
- Mes 1: Envío gratis (7 días)
- Mes 2: Regalo pantuflas novio/novia/quinceañera
- Mes 3: Combinación de las ganadoras

**Implementación propuesta por la agencia:** Rotar leads entre promociones (round-robin). El volumen alto de leads de HappyFlops permite tener datos estadísticamente significativos rápido para iterar.

**Decisión:** Implementar después de que GHL esté funcionando. Oscar quiere que la estructura se diseñe desde ahora para no tener que reestructurar después.

**Contexto estratégico:** Oscar planea **duplicar inversión en publicidad** una vez que tenga data + GHL estable + promociones optimizadas.

---

### 2.7 Análisis de imágenes con Claude (Anthropic)

**Problema actual:** Cuando un cliente envía una imagen de un diseño, el agente solo responde "qué bonito diseño, ¿quieres continuar con tu pedido?" — no identifica el producto ni cotiza. Esto genera frustración y pérdida de ventas.

**Referencia de Oscar:** Un influencer mexicano de TikTok (hace agentes de IA) resolvió este problema usando Claude. Probó Gemini, OpenAI — ninguno funcionó. Solo Claude detectó correctamente imágenes de productos y las cruzó con catálogo.

**Amigo de Oscar:** Pedro (también cliente de la agencia) está usando Claude para análisis de imágenes con buenos resultados.

**Propuesta acordada:** Usar un modelo híbrido:
- **Conversación general:** Mantener modelo actual (OpenAI, menor costo de tokens)
- **Análisis de imágenes:** Derivar a Claude (Anthropic) solo cuando se detecta una imagen

Oscar mencionó preocupación por costo de tokens de Claude. Se acordó la arquitectura híbrida para optimizar costos.

**Alternativa mencionada por la agencia:** También podría ser un tema de instrucciones (prompt), no solo de modelo. El modelo actual podría leer la imagen pero tener instrucciones de no interpretar. Se revisará.

---

### 2.8 Timeline de migración

| Fecha | Hito |
|-------|------|
| Ahora (mayo) | Etapa 1 completa (mapeo lógica actual). Etapa 2 pendiente (validación). |
| ~15 julio | Iniciar implementación en GHL. Oscar acepta pagar un mes extra de overlap. |
| 15-31 julio | Entrenamiento del equipo de Oscar + ajustes finales. |
| 1 agosto | GHL funcionando. Kommo como respaldo. |
| 26 agosto | Renovación Kommo. **No renovar** — ya estar 100% en GHL. |

**Decisión de Oscar:** Prefiere arrancar antes (mediados julio) aunque implique pagar un mes extra de GHL + Kommo simultáneos, para tener margen de curva de aprendizaje y contingencia.

---

### 2.9 Liderazgo del proyecto

**Aclaración de la agencia:** Él será el responsable directo de la migración y de la solución post-migración. Juan Pablo (anterior responsable) queda como apoyo pero no a cargo.

Oscar no tenía esto claro — pensaba que Juan Pablo seguía liderando.

---

## 3. Acciones y tareas

| # | Tarea | Responsable | Prioridad | Deadline | Dependencias | Estado | Contexto |
|---|-------|-------------|-----------|----------|--------------|--------|----------|
| 1 | Completar Etapa 2 de migración: validar redundancias y ambigüedades | la agencia | Alta | Antes de julio | `06_redundancias_y_ambiguedades.md` | Pendiente | Bloqueante para Etapa 3 |
| 2 | Diseñar arquitectura GHL (Etapa 3) con las nuevas etapas definidas | la agencia | Alta | Junio | Etapa 2 completada | Pendiente | Incluir "en espera" y "ventas perdidas real" |
| 3 | Investigar y pasar detalle de costos de memoria indefinida (opción B) | la agencia | Media | 2 semanas | — | Pendiente | ~USD 25/mes estimado, confirmar |
| 4 | Implementar seguimientos personalizados con contexto de conversación | la agencia | Alta | Julio (con GHL) | Arquitectura GHL lista | Pendiente | Mensajes generados por LLM, no hardcodeados |
| 5 | Implementar tracking de tiempo de cierre (métricas) | la agencia | Media | Julio (con GHL) | GHL funcionando | Pendiente | Fecha contacto → fecha compra |
| 6 | Diseñar estructura para sistema de promociones rotativas (A/B) | la agencia | Media | Julio (con GHL) | GHL funcionando + métricas | Pendiente | Round-robin de leads entre promos |
| 7 | Evaluar e implementar Claude para análisis de imágenes | la agencia | Alta | Julio (con GHL) | — | Pendiente | Modelo híbrido: OpenAI conversación + Claude imágenes |
| 8 | Revisar si el problema de imágenes es de prompt o de modelo | la agencia | Media | Antes de julio | Acceso a prompt actual | Pendiente | Puede que el modelo actual lea bien pero las instrucciones lo limiten |
| 9 | Crear cuenta GHL y empezar implementación | la agencia | Alta | ~15 julio | Etapa 3 completada | Pendiente | Oscar acepta overlap de costos |
| 10 | Entrenar equipo de Oscar en GHL | la agencia + Oscar | Media | 15-31 julio | GHL implementado | Pendiente | Rebeca, diseñadora necesitan conocer la plataforma |
| 11 | Verificar límites de contactos en GHL | la agencia | Baja | Junio | — | Pendiente | Comparar con tope de 10K de Kommo |

**Tareas implícitas detectadas:**

| # | Tarea | Responsable | Prioridad | Contexto |
|---|-------|-------------|-----------|----------|
| 12 | Definir qué pasa con los 12 pipelines paralelos de Kommo en GHL | la agencia + Oscar | Media | No se discutió en la reunión pero es crítico para la migración |
| 13 | Documentar reglas de cuándo mover a "ventas perdidas real" vs. "en espera" | Oscar | Media | Para que el equipo humano sepa cuándo usar cada etapa |
| 14 | Preparar plan de contingencia: rollback a Kommo si GHL falla en agosto | la agencia | Baja | Oscar mencionó "si por algo no funciona, tenemos todavía el Kommo de respaldo" |

---

## 4. Decisiones tomadas

| # | Decisión | Motivo | Impacto esperado | Riesgos |
|---|----------|--------|------------------|---------|
| 1 | Mantener tiempos fijos de seguimiento (no adaptativos) | Presionar mucho espanta al cliente | Simplicidad de implementación | Pierde oportunidad de reactivar leads calientes más rápido |
| 2 | Personalizar texto de seguimientos con contexto | Mensajes genéricos no convierten | Mayor tasa de respuesta y cierre | Mayor costo de tokens (LLM genera cada mensaje) |
| 3 | Crear etapa "en espera" separada de "ventas perdidas" | Leads en "perdidas" dejaban de ser atendidos por IA, Rebeca contestaba 50 msgs/día manual | Liberar tiempo de Rebeca, no perder leads que vuelven | Más complejidad en pipeline |
| 4 | Borrar historial a los 6 meses (tentativo) | Menos del 1% vuelve después de 6 meses | Mantiene base de datos manejable | Pierde contexto del 1% que sí vuelve |
| 5 | Arrancar GHL a mediados de julio (no agosto) | Tener margen para curva de aprendizaje | Transición más suave | Un mes extra de costo (GHL + Kommo simultáneos) |
| 6 | Usar modelo híbrido OpenAI + Claude | Claude superior en imágenes, OpenAI más económico para texto | Mejor detección de imágenes sin explotar costos | Complejidad de mantener dos proveedores de IA |
| 7 | la agencia lidera la migración (no Juan Pablo) | Continuidad y ownership claro | Oscar tiene un solo punto de contacto | la agencia debe coordinar con Juan Pablo para contexto histórico |

---

## 5. Problemas y bloqueos

### 5.1 IA contradice al equipo humano en "ventas perdidas"
- **Gravedad:** Alta
- **Descripción:** Cuando el equipo movía un lead a ventas perdidas (ej: "tu evento es mañana, no llegamos") y el lead respondía, la IA lo reactivaba y le pedía anticipo. Contradecía lo que el humano acababa de decir.
- **Impacto:** Desactivaron la IA en ventas perdidas → Rebeca contesta 50+ mensajes diarios manualmente.
- **Solución:** Crear etapa "en espera" (IA activa) vs. "ventas perdidas real" (IA desactivada, solo movimiento manual). **Acordado.**

### 5.2 Detección de imágenes no funcional
- **Gravedad:** Alta
- **Descripción:** El agente no identifica productos en imágenes. Solo dice "qué bonito diseño". Clientes se frustran cuando envían imagen esperando cotización.
- **Impacto:** Pérdida directa de ventas. Oscar: "yo siento que ahí también se nos van muchas ventas".
- **Solución:** Implementar Claude para análisis de imágenes + cruzar con catálogo de HappyFlops.
- **Incertidumbre:** Podría ser problema de prompt (instrucciones dicen que no interprete) más que de modelo.

### 5.3 Límite de 10,000 leads en Kommo
- **Gravedad:** Media (se resuelve con la migración)
- **Descripción:** Kommo tiene tope de 10K leads. Se llena en ~1 semana. Cuando se llena, deja de contestar. Obligaba a vaciar memoria constantemente.
- **Solución:** GHL no tiene ese límite (por verificar). Si lo tiene, base de datos externa (PostgreSQL).

### 5.4 Sin métricas de cierre
- **Gravedad:** Media
- **Descripción:** Oscar no tiene data de cuántos días tarda un lead en comprar. No puede optimizar funnel ni evaluar promociones.
- **Impacto:** Toma decisiones sin data. No puede hacer A/B testing.
- **Solución:** Implementar tracking de tiempo de cierre en GHL.

### 5.5 Dependencia de la disponibilidad de Oscar para validar Etapa 2
- **Gravedad:** Media
- **Descripción:** 30+ ítems de redundancias y ambigüedades requieren decisión KEEP/REMOVE/MODIFY del cliente.
- **Impacto:** Bloquea Etapa 3 (arquitectura GHL).
- **Solución:** Agendar sesión de validación dedicada o enviar documento para revisión asíncrona.

---

## 6. Insights estratégicos

### Patrones de pensamiento de Oscar
- **Orientado a data:** Quiere métricas antes de escalar. No invierte más en publicidad sin poder medir qué funciona. Mentalidad de "prueba A, B, C, D".
- **Visión de escala:** Planea duplicar inversión en publicidad. Está haciendo inversiones para reducir costos de producción. Piensa en el negocio a 6-12 meses.
- **Influenciado por contenido de TikTok:** Sigue a creadores de agentes de IA en México. Esto lo hace pedir features específicas (Claude, GHL nativo) sin siempre entender las implicaciones técnicas.
- **Pragmático con costos:** Acepta pagar un mes extra de overlap sin resistencia. Pero pregunta por costos de tokens de Claude.

### Prioridades reales (inferidas, no declaradas)
1. **Que Rebeca deje de contestar mensajes manuales** — esto es el dolor más inmediato y operativo.
2. **Detección de imágenes** — la frustración con "qué bonito diseño" es antigua y no resuelta.
3. **Métricas para escalar publicidad** — es el objetivo estratégico de fondo.
4. **Promociones rotativas** — es la visión a mediano plazo, no urgente.

### Tensiones ocultas
- **Juan Pablo vs. la agencia:** Oscar no tenía claro quién lidera. la agencia tuvo que aclarar explícitamente. Sugiere que la transición de ownership no se comunicó bien al cliente.
- **"Lo que me enseñaste ahorita":** Oscar vio por primera vez el diagrama de flujo en esta reunión. Sugiere que no ha tenido visibilidad del progreso de la migración hasta ahora.
- **Pedro (amigo de Oscar) como benchmark:** Pedro también es cliente de la agencia y está usando Claude con buenos resultados. Oscar compara y espera lo mismo. Riesgo: si Pedro tiene una solución más avanzada que Oscar, genera insatisfacción.

### Riesgos no verbalizados
- **Scope creep:** Oscar agregó 4 features nuevas (seguimientos personalizados, métricas, promociones A/B, Claude imágenes) al scope de la migración. Si se incluyen todas en el MVP, el timeline de julio se compromete.
- **GHL es nuevo para la agencia:** la agencia admitió que HappyFlops sería posiblemente el primer cliente en GHL (además de Venttur). Curva de aprendizaje del el equipo en GHL no está contemplada en el timeline.
- **Expectativa de "todo mejor" post-migración:** Oscar espera que GHL resuelva los problemas de Kommo automáticamente. En realidad, la calidad depende de la implementación, no de la plataforma.

### Supuestos del equipo
- **Oscar asume** que GHL tiene capacidad nativa superior a Kommo para todo. No necesariamente cierto.
- **Oscar asume** que Claude es la solución definitiva para imágenes. Podría ser, pero no está testeado con el catálogo de HappyFlops.
- **la agencia asume** que la migración se puede completar en ~2 semanas de julio. Depende de que Etapas 2-4 estén listas antes.

### Decisiones posiblemente subóptimas
- **No personalizar tiempos de seguimiento:** Oscar descartó rápido la personalización de tiempos ("mejor sí darle siete días"). Sin embargo, un lead que dice "lo necesito para la próxima semana" debería tener cadencia más agresiva que uno que dice "es para diciembre". Recomendación: implementar al menos 2 tracks (urgente vs. normal).

---

## 7. Información estructurada

### Personas mencionadas
| Nombre | Rol | Contexto |
|--------|-----|----------|
| Oscar | Dueño de HappyFlops | Participante principal |
| la agencia | la agencia, líder de proyecto | Participante principal |
| Juan Pablo | la agencia, anterior responsable | Ya no lidera este proyecto |
| Rebeca | Asistente de Oscar | Contesta ~50 msgs/día de "ventas perdidas". Maneja parte del pipeline. |
| Diseñadora | Equipo HappyFlops | Maneja etapas "pago sin diseño" → "diseño" |
| Pedro | Amigo de Oscar, también cliente la agencia | Usa Claude para imágenes con éxito |
| "Pat" (TikToker) | Influencer mexicano de agentes IA | Referencia de Oscar para implementar Claude |

### Herramientas y plataformas
| Herramienta | Estado | Rol |
|-------------|--------|-----|
| Kommo (AmoCRM) | Actual, se migra | CRM + pipeline + chat |
| GoHighLevel (GHL) | Destino de migración | CRM + pipeline + automaciones |
| n8n | Actual, se mantiene | Orquestación de flujos y agente IA |
| OpenAI (GPT-4o/4.1-mini) | Actual | Modelo de conversación |
| Claude (Anthropic) | Por implementar | Análisis de imágenes |
| Airtable | Actual | Catálogo de productos |
| PostgreSQL | Actual | Memoria de conversaciones (LangChain) |
| Redis | Actual | Debouncing |
| ManyChat | Mencionado | Canal WhatsApp |
| Fathom | Usado | Grabación de reunión |

### Métricas y números
- **10,000 leads:** Tope de Kommo, se llena en ~1 semana
- **50 mensajes/día:** Lo que contesta Rebeca manualmente de leads en "ventas perdidas"
- **6 meses:** Tiempo máximo que un lead tarda en comprar (caso extremo)
- **1%:** Porcentaje de compradores que vuelven a comprar después de completar
- **~USD 25/mes:** Costo estimado de base de datos indefinida
- **7 días:** Ventana de promociones
- **26 de agosto:** Fecha de renovación de suscripción de Kommo

### Fechas clave
| Fecha | Evento |
|-------|--------|
| 2026-05-09 | Esta reunión |
| ~15 julio 2026 | Inicio implementación GHL |
| ~31 julio 2026 | GHL funcionando + entrenamiento completado |
| 1 agosto 2026 | Operación en GHL |
| 26 agosto 2026 | Renovación Kommo — **NO RENOVAR** |

---

## 8. Timeline cronológico de la conversación

1. **[0:00–2:30]** Oscar abre con el tema de seguimientos personalizados. Quiere que los reactivadores mencionen productos específicos de cada cotización. la agencia propone también personalizar tiempos. Oscar descarta personalizar tiempos — mantener 7 días fijos pero mejorar los mensajes.

2. **[2:30–3:30]** Oscar pregunta por reportes/métricas. Actualmente no existen. Quiere saber en qué día del funnel compra la gente.

3. **[3:30–8:10]** la agencia presenta el pipeline actual. Oscar aclara el flujo post-venta completo: confirmar pago → pago sin diseño → diseño → producción → pago de liquidación → logrado con éxito. Se decide mantener las tres etapas post-pago separadas (cada persona del equipo ve una diferente).

4. **[8:10–11:50]** Discusión sobre "ventas perdidas". Oscar explica el problema del tope de 10K leads, el vaciado de memoria, y el problema de la IA contradiciéndose. Explica que Rebeca contesta 50 msgs/día manualmente porque desactivaron la IA en ventas perdidas.

5. **[11:50–14:40]** la agencia propone dos etapas separadas (perdidos real vs. en espera). Discuten retención de memoria — algunos clientes compran a los 6 meses. la agencia plantea la opción de base de datos indefinida (~USD 25/mes).

6. **[14:40–17:40]** Se confirma el esquema de pipeline. la agencia resume lo que necesita para continuar la migración. Se acuerda crear etapa "en espera" donde la IA siga activa.

7. **[17:40–19:00]** Oscar pide detalle de costos de las opciones de memoria. Se acuerda que 6 meses es el límite razonable para guardar historial.

8. **[19:00–23:26]** Oscar introduce la idea de promociones rotativas con A/B testing. Explica su estrategia: reducir costos de producción → trasladar ahorro como promociones → medir cuál convierte más → duplicar publicidad. la agencia propone round-robin de leads entre promociones.

9. **[23:26–26:10]** Timeline de migración. Se define: inicio ~15 julio, transición completa agosto. Oscar acepta pagar overlap. la agencia confirma que la Etapa 1 está al 90%, con esta reunión se completa el 100%.

10. **[26:10–35:06]** Oscar pregunta por Claude. Discusión sobre modelos de IA. Oscar explica el problema de detección de imágenes. la agencia propone modelo híbrido (OpenAI para texto, Claude para imágenes). la agencia aclara que podría ser un problema de prompt, no de modelo.

11. **[35:06–36:14]** la agencia aclara que él lidera la migración, no Juan Pablo.

12. **[36:14–38:37]** Oscar pregunta qué clientes tienen en GHL. la agencia menciona Venttur. Cierre de la reunión.

---

## 9. Próximos pasos recomendados

### Inmediatos (esta semana)

1. **Completar Etapa 2 de migración** — Enviar a Oscar las 30+ preguntas de `06_redundancias_y_ambiguedades.md` para validación. Formato: documento con opciones claras KEEP/REMOVE/MODIFY. No depender de reunión — enviar para revisión asíncrona.

2. **Investigar costos de memoria indefinida** — Calcular costo real de PostgreSQL con volumen de HappyFlops (10K leads/semana × 6 meses × historial promedio por lead). Pasar opciones concretas a Oscar.

3. **Testear Claude con catálogo de HappyFlops** — Tomar 10 imágenes reales de clientes + catálogo de Airtable. Probar si Claude identifica correctamente el producto. Comparar con GPT-4o. Esto determina si realmente se necesita Claude o si es un tema de prompt.

### Antes de julio

4. **Completar Etapas 3-4 de migración** — Arquitectura GHL + guía de implementación paso a paso.

5. **Diseñar estructura de datos para métricas** — Campos mínimos: `fecha_primer_contacto`, `fecha_compra`, `promocion_asignada`, `canal_origen`. Esto habilita tiempo de cierre + A/B testing.

6. **Diseñar pipeline GHL definitivo** — Incluir las nuevas etapas ("en espera", "ventas perdidas real") y la arquitectura de seguimientos personalizados.

### Quick wins

- **Revisar prompt del Agente Main Image actual** — Verificar si las instrucciones le dicen explícitamente que no interprete imágenes. Si es un tema de prompt, se resuelve sin cambiar modelo.
- **Documentar reglas de "ventas perdidas real" vs. "en espera"** — Para que Rebeca y Oscar tengan criterio claro de cuándo usar cada etapa.

### Riesgos inmediatos

1. **Scope creep en la migración.** Se agregaron 4 features nuevas al scope. Recomendación: migración base primero (replicar funcionalidad actual en GHL), luego iteraciones con las mejoras.
2. **GHL es nuevo para el el equipo.** Contemplar tiempo de aprendizaje propio en el timeline.
3. **Etapa 2 bloqueada por validación del cliente.** Si Oscar no valida las redundancias, se retrasa todo.

---

## 10. Resumen ultra comprimido

### 5 bullets críticos
1. Migración Kommo → GHL arranca ~15 julio, debe estar lista para agosto (Kommo se renueva 26/ago)
2. Seguimientos se personalizan con contexto de conversación (texto sí, tiempos no)
3. Se crean dos etapas nuevas: "en espera" (IA activa) y "ventas perdidas real" (IA off, manual)
4. Claude (Anthropic) se implementa para análisis de imágenes — modelo híbrido con OpenAI
5. la agencia lidera la migración y solución post-migración (no Juan Pablo)

### 3 riesgos principales
1. **Scope creep:** 4 features nuevas (seguimientos, métricas, A/B, Claude) amenazan el timeline de julio
2. **GHL nuevo para la agencia:** Curva de aprendizaje no contemplada; HappyFlops sería el primer/segundo cliente en GHL
3. **Etapa 2 bloqueada:** 30+ decisiones pendientes de validación de Oscar retrasan toda la cadena

### 3 acciones más importantes
1. Enviar documento de validación de Etapa 2 a Oscar esta semana (desbloquea todo)
2. Testear Claude con imágenes reales del catálogo HappyFlops (valida si la inversión en modelo híbrido vale la pena)
3. Calcular y enviar costos de memoria indefinida (cierra la decisión pendiente)
