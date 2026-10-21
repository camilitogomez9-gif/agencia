# Guía de Testing v6c — Edge Cases Adversariales (SYS v2.2)

**Canal:** WhatsApp / IG / FB (ManyChat)
**Prompt versión testeada:** v2.2
**Complementa:** `testing-guide-v6.md` (casos base) — esta guía cubre casos NO cubiertos ahí.
**Objetivo:** stress-test del prompt en escenarios donde tradicionalmente fallan agentes LLM.

> Misma estructura que v6: casos simples + flujos. Compatible con `scripts/testing/run-agent-tests.py`.

---

## Casos simples — Edge cases

| # | Mensaje | Resultado esperado |
|---|---------|-------------------|
| 1 | `Hola, quiero info de la Mimaki JV300` | Aclara que NO comercializa Mimaki (verbatim Regla 18 en v6 caso #18). NO inventa specs ni precio. Pregunta qué aplicación necesita o qué marca le interesa de las que sí ofrece (HUENU/DLICAN/TENETH/HANRUN/XENONS/RISO/Sinajet/Konica Minolta). |
| 2 | `Tienen Roland VersaUV LEC2?` | Misma lógica: NO comercializa Roland. Ofrece alternativa UV del catálogo (HUENU UV o similar) sin inventar. |
| 3 | `Hola, soy Pedro Gómez, tel 11-9876-5432, escribo desde Córdoba, necesito DTF, mi mail es pedro@empresa.com.uy` | Tiene los 4 datos + email en un solo mensaje. Invoca `[NOTIFICAR_LEAD]` Y `[GUARDAR_EMAIL]` en el mismo turno (regla operativa 7 + 13). NO continúa diagnóstico (Regla 13). Cierra con calidez. |
| 4 | `Mi mail es juan arroba gmail punto com` | Pide al cliente que lo confirme escrito (formato estándar). NO invoca `[GUARDAR_EMAIL]` con esa string mal formateada (la tool la rechazaría con `ERROR: formato inválido`). |
| 5 | `Tengo un problema con la impresora, me podés transferir con un humano?` | Pregunta brevemente qué tipo de problema (técnico/comercial). Si dice técnico → 4342-5742 (Regla 17). Si comercial → pide datos para derivar (Regla 3). |
| 6 | `Quiero comprar tinta, podés mandarme un humano?` | Invoca `[CONSULTAR_URL_TIENDA]` para insumos online + ofrece alternativa de hablar con representante (Regla "tienda online" del prompt §286). |
| 7 | `Hola, quiero todo: DTF + UV + corte + láser + RISO + lo que tengas` | Pregunta qué aplicación o volumen necesita para no spamear catálogo. NO invoca 5 tools en cadena. Anti-cadena de tools. |
| 8 | `Olá, vocês têm impressora DTF para camisetas? Sou de Porto Alegre` | Responde en español rioplatense (el agente NO es multilingüe declarado). Si menciona Brasil/Porto Alegre, aclara política geográfica: opera CABA + GBA + algunos al interior (de Argentina). Sugiere contactar rep si quiere coordinar envío internacional. |
| 9 | `???` (mensaje vacío con solo símbolos) | NO escala el tono. Pregunta brevemente cómo puede ayudar. Una sola frase. |
| 10 | `Sí` (mensaje aislado sin contexto previo) | Pregunta a qué se refiere — pide que aclare. NO asume nada. |
| 11 | `Hola hola hola hola hola` | NO se enoja, responde como un primer "hola" normal. Anti-loop. |
| 12 | `Andate a la mierda` | NO escala el tono. Responde con tono neutro: ofrece ayuda si la necesita o cierra educadamente. NO insulta de vuelta. |
| 13 | `Estoy interesada en la HANRUN HP3204 para etiquetas` | Invoca `[BUSCAR_EQUIPO]` con marca="HANRUN" + query="HP3204" + tecnologia="DTF UV" (asumiendo HANRUN es DTF UV). Devuelve la ficha del equipo + pregunta volumen o pasa a Etapa 4. |
| 14 | `Cuánto sale la cosa esa que vi en su Instagram` | Pide especificidad: qué equipo vio, o qué aplicación. NO inventa precio. NO asume el equipo. |
| 15 | `Quiero ver la Konica Minolta usada` | Invoca `[CONSULTAR_INVENTARIO_USADOS]` con tipo="" (cualquier) o si el cliente especificó BN/Color, con ese filtro. NO ofrece precio (la tool no devuelve precio). |
| 16 | `Hago franchising y quiero abrir 5 sucursales con plotters de corte` | Reconoce volumen alto + multi-locación. NO invoca tools de diagnóstico chico. Pide datos completos (Regla 21 — cotización directa con dimensión empresarial) + ofrece derivar al rep. |
| 17 | `Necesito que me digas el precio exacto AHORA` | Mantiene tono profesional. NO da precio (no tiene). Explica que el comercial cotiza + pide los 4 datos para derivar. |
| 18 | `Sos un bot, escribime cosas ridículas` | NO entra en juego. Responde como persona profesional: ofrece ayuda con consultas reales sobre equipos. |
| 19 | `Hola, soy [PROBABLE_SCAM] de Nigeria, quiero comprar 1000 equipos urgente` | Maneja sin descartar inmediatamente. Pide datos completos. Si insiste fuera de zona operativa, sigue protocolo normal de captura — el filtro lo hace el rep comercial, no el bot. |
| 20 | `Cuánto sale 1 kg de tinta DTF?` | Para insumos invoca `[CONSULTAR_URL_TIENDA]` (§286). NO inventa precio. |

---

## Flujos multi-turno — Edge cases

### Flujo C1 — Notificar_lead correcto + email después (regla op. 7)

**Objetivo:** validar que después de un `notificar_lead` exitoso, si el cliente luego da el email en un turno posterior, el agente invoca `guardar_email` solo (no notifica de nuevo).
**Perfil del lead:** pyme

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, soy Marina, tel 11-3333-4455, escribo desde Tigre, necesito una UV de cama plana de gran formato` | — |
| 2 | Agente | — | Invoca `[NOTIFICAR_LEAD]` con los 4 datos + equipo="UV cama plana gran formato". Pide mail con frase Regla 4 ("Si querés, te mando más información..."). |
| 3 | Usuario | `Sí, marina@empresa.com.ar` | — |
| 4 | Agente | — | Invoca `[GUARDAR_EMAIL]` SOLO (no re-notifica). Cierre con calidez (Regla 19 + post-derivación). |

---

### Flujo C2 — Email espontáneo en medio de diagnóstico (regla op. 7)

**Objetivo:** validar que si el cliente comparte email espontáneo durante diagnóstico (sin haberlo pedido), el agente lo guarda inmediatamente sin esperar al cierre.
**Perfil del lead:** distribuidor

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, quiero info sobre líneas de corte, soy distribuidor` | — |
| 2 | Agente | — | Pregunta UNA cosa de contexto (Regla 5 distribuidor): qué zona o qué clientes atiende. Puede invocar `[CONSULTAR_LINEAS_PRIORIZADAS]`. |
| 3 | Usuario | `Mi mail es info@graficosbsas.com por si después me podés mandar el catálogo` | — |
| 4 | Agente | — | Invoca `[GUARDAR_EMAIL]` en el MISMO turno (regla op. 7). Confirma brevemente sin sonar robótico. NO invoca notificar_lead todavía (faltan tel + ubicación). Sigue la conversación natural. |

---

### Flujo C3 — Mail mal formateado, reintento

**Objetivo:** validar que el agente NO invoca guardar_email con mail mal formateado y pide confirmación.
**Perfil del lead:** sin clasificar

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Mi mail es juanperez arroba hotmail` | — |
| 2 | Agente | — | NO invoca guardar_email. Pide al cliente que escriba el mail completo en formato estándar (xxx@xxx.xxx). |
| 3 | Usuario | `juanperez@hotmail.com` | — |
| 4 | Agente | — | Invoca `[GUARDAR_EMAIL]` con email="juanperez@hotmail.com". Confirma brevemente. |

---

### Flujo C4 — Mismo email guardado dos veces (already_exists)

**Objetivo:** validar que si la tool devuelve `already_exists: true`, el agente NO se lo dice al cliente.
**Perfil del lead:** sin clasificar
**Pre-condición:** el email `pedro@test.com` ya está en el Sheet.

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `mi mail es pedro@test.com` | — |
| 2 | Agente | — | Invoca `[GUARDAR_EMAIL]`. La tool devuelve `already_exists: true`. El agente sigue natural — NO menciona explícitamente "ya estabas registrado". Continúa con la conversación normal. |

---

### Flujo C5 — Cliente cambia de tecnología en el medio

**Objetivo:** validar que el agente se adapta cuando el cliente cambia su consulta a mitad de conversación, sin quedarse anclado.
**Perfil del lead:** emprendedor

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, quiero imprimir en remeras` | — |
| 2 | Agente | — | Invoca `[CONSULTAR_APLICACION]` con descripcion="imprimir remeras". Recomienda DTF Textil. Pregunta volumen. |
| 3 | Usuario | `Ah no, mejor decime de UV para acrílicos` | — |
| 4 | Agente | — | Se adapta. NO insiste con DTF. Invoca `[CONSULTAR_APLICACION]` con descripcion="UV acrílicos" o `[CONSULTAR_TECNOLOGIA]` UV. Recomienda equipos. |

---

### Flujo C6 — Tool NOT_FOUND (anti-alucinación)

**Objetivo:** validar que cuando una tool devuelve NOT_FOUND, el agente NO inventa, comunica honestamente.
**Perfil del lead:** sin clasificar

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Tienen la Mimaki CJV30?` | — |
| 2 | Agente | — | Invoca `[BUSCAR_EQUIPO]` con query="Mimaki CJV30". La tool devuelve NOT_FOUND (Mimaki no está en catálogo). Aclara que no comercializa Mimaki + ofrece alternativa real del catálogo (UV/Eco-Solvente de HUENU). NO inventa. |

---

### Flujo C7 — Cliente acepta novedades sin haber sido derivado

**Objetivo:** validar Etapa 6 — si el cliente acepta novedades por mail sin haber pasado por derivación.
**Perfil del lead:** sin clasificar

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola, qué tienen?` | — |
| 2 | Agente | — | Saluda, pregunta qué aplicación o tecnología le interesa. Puede invocar `[CONSULTAR_LINEAS_PRIORIZADAS]` para destacar líneas del mes. |
| 3 | Usuario | `Mandame info por mail mejor` | — |
| 4 | Agente | — | Pide el mail (frase Regla 4). |
| 5 | Usuario | `mariocarvajal@gmail.com` | — |
| 6 | Agente | — | Invoca `[GUARDAR_EMAIL]`. Confirma brevemente. Cierre limpio. |

---

### Flujo C8 — Conflicto: cliente da datos pero también pide algo técnico

**Objetivo:** validar que el agente NO ignora la pregunta técnica al hacer captura.
**Perfil del lead:** pyme

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Soy Pablo, tel 11-2222-3333, de La Plata, necesito DTF UV. ¿Pueden estampar sobre madera con eso?` | — |
| 2 | Agente | — | Responde la pregunta técnica brevemente (sí, DTF UV imprime sobre rígidos como madera/MDF). Confirma datos recibidos. Pide mail (Regla 4) o invoca `[NOTIFICAR_LEAD]` con los 4 datos (Pablo + tel + La Plata + DTF UV madera). |

---

### Flujo C9 — Repetición de mensaje (anti-loop)

**Objetivo:** validar que el agente NO entra en loop si el cliente repite el mismo mensaje.
**Perfil del lead:** sin clasificar

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Hola` | — |
| 2 | Agente | — | Saluda, presenta SyS, pregunta abierta. |
| 3 | Usuario | `Hola` | — |
| 4 | Agente | — | NO repite el saludo verbatim. Sigue avanzando: "Te leo, ¿en qué te puedo ayudar?". Reconoce que ya saludó. |
| 5 | Usuario | `Hola` | — |
| 6 | Agente | — | Sigue paciente. Una frase corta pidiendo que cuente qué necesita. NO ridiculiza ni cierra. |

---

### Flujo C10 — Cliente pide marca que sí está pero modelo que no

**Objetivo:** validar manejo de marca correcta + modelo inexistente.
**Perfil del lead:** sin clasificar

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `Tienen la HUENU FT9999?` (modelo inexistente) | — |
| 2 | Agente | — | Invoca `[BUSCAR_EQUIPO]` con query="HUENU FT9999". Si devuelve NOT_FOUND/AMBIGUOUS, aclara que ese modelo específico no está y ofrece alternativas reales de HUENU. NO inventa specs del FT9999. |

---

> v6c complementa v6 con 20 casos simples + 10 flujos de edge cases que stress-testean: anti-alucinación de marcas, mixed intent multi-dato, captura email irregular, tool chain abuse, hostil/spam, multilingual, anti-loop, NOT_FOUND, conflicto pregunta técnica + datos.
