# Guía Airtable — Edgardo / Sistemas y Soluciones

> **Para:** Edgardo (Sistemas y Soluciones)
> **De:** Equipo la agencia
> **Versión:** v1
> **Fecha:** 2026-05-28

Esta guía te explica cómo mantener actualizado el catálogo del agente desde Airtable. **Cualquier cambio que hagas se refleja en vivo** — no hay que avisarnos ni esperar despliegues.

---

## Acceso

- URL base: https://airtable.com (te llega el invite por mail)
- Base: **SyS Catalogo**
- Tu usuario tiene permiso **Editor** sobre toda la base

---

## ¿Qué edita cada quién?

| Tabla | Quién edita |
|---|---|
| Equipos | **Vos (Edgardo)** |
| Tecnologías | Vos (raras veces — son 8 fijas) |
| Líneas de Producto | Vos |
| Aplicaciones | Vos |
| Sustratos | Vos |
| Cabezales | Vos |
| Insumos | Vos / Equipo de la tienda online |
| FAQs | Vos + el equipo (juntos al principio) |
| Representantes | Gerente |
| Config Mensual | Gerente |
| Leads | NADIE (la rellena el agente) |

---

## Tareas más comunes

### 1. Agregar un equipo nuevo

**¿Cuándo?** Cuando reciben un modelo nuevo del proveedor o suman una marca al catálogo.

**Pasos:**

1. Abrí la tabla **Equipos**
2. Andá a la vista **"Para agente"**
3. Click en **"+ Add record"** (botón inferior izquierdo)
4. Completá los campos:
   - **Modelo**: nombre exacto como lo conoce el cliente. Ejemplo: `DTF-PRO-600`, `Mimaki UJF-3042 MkII`
   - **Marca**: elegí de la lista (Mimaki, Roland, Epson, Mutoh, Konica Minolta, RISO, Sinajet, Otro). Si la marca es nueva, agregala en el menú.
   - **Tecnología**: linkeá la(s) tecnología(s) que usa. Ejemplo: para una DTF híbrida, podés linkear "DTF Textil" Y "DTF UV".
   - **Línea de Producto**: linkeá una sola línea (Mimaki, Roland, Sinajet, etc.)
   - **Aplicaciones compatibles**: linkeá las aplicaciones que el equipo puede hacer (ej: "Estampado de remeras", "Estampado de gorras"). Múltiples OK.
   - **Sustratos compatibles**: linkeá los materiales sobre los que imprime (ej: Algodón, Poliéster).
   - **Cabezales**: si conocés los cabezales, linkealos.
   - **Formato**: elegí "Mesa plana", "Roll-to-roll", "Híbrido" o "Compacta".
   - **Ancho máx (mm)**: número sin decimales. Ejemplo: 600 para un equipo de 60cm.
   - **Velocidad (m²/h)**: número con hasta 1 decimal. Ejemplo: 12.5.
   - **Disponibilidad zona**: elegí una o varias (CABA, GBA, Interior).
   - **Descripción corta**: 1 párrafo que el agente leerá al cliente. **Importante**: debe sonar natural, no técnico. Ejemplo: "Equipo DTF compacto ideal para emprendedores que arrancan con estampado textil. Anchos hasta 60cm y velocidad media."
   - **Especificaciones técnicas**: ficha técnica completa (esto es para que el agente la consulte si el cliente quiere detalle).
   - **Status**: **Activo** si está disponible para venta. **Próximamente** si todavía no llegó. **Discontinuado** si ya no se vende.
   - **Notas internas**: lo que quieras anotar para uso interno. El agente NO lee esto.

5. Guardar (Airtable autoguarda — no hace falta apretar nada).

**Importante:**
- Si lo marcás como **Activo**, el agente ya lo va a usar inmediatamente.
- Si querés cargarlo pero todavía no mostrarlo, ponelo como **Próximamente**.

---

### 2. Modificar un equipo existente

**¿Cuándo?** Cuando cambia un precio, especificación, disponibilidad, etc.

**Pasos:**

1. En la tabla **Equipos**, encontrá el record (podés filtrar por Marca o Tecnología)
2. Click en el campo que querés modificar
3. Cambialo
4. Guarda automáticamente

**Si querés sacar un equipo del catálogo activo sin borrarlo:**
- Cambiá `Status` a **Discontinuado** o **Próximamente**
- El agente lo deja de mencionar inmediatamente

---

### 3. Marcar un equipo como discontinuado

**¿Cuándo?** Cuando dejaron de venderlo.

**Pasos:**

1. Buscá el record
2. Cambia `Status` de "Activo" a **Discontinuado**
3. Listo. El agente ya no lo va a recomendar.

NO BORRES el record. Mantenerlo como Discontinuado preserva el historial y no rompe Leads viejos que lo tenían como interés.

---

### 4. Agregar una FAQ

**¿Cuándo?** Cuando notás que clientes preguntan algo que el agente no sabe responder.

**Pasos:**

1. Abrí la tabla **FAQs**
2. Click en **"+ Add record"**
3. Completá:
   - **Pregunta**: resumida. Ejemplo: "Tienen showroom?"
   - **Respuesta corta**: respuesta que el agente va a decir verbatim al cliente. Debe sonar natural, breve, rioplatense. Ejemplo: "Sí, tenemos showroom y hacemos demos. Si querés coordinar, dejame tu nombre y teléfono y un representante te contacta."
   - **Categoría**: elegí (Showroom, Financiación, Servicio Técnico, Plazos, Garantía, Llamadas, Devoluciones, Distribuidores, Otros)
   - **Keywords**: palabras separadas por coma que pueden aparecer en la pregunta del cliente. Ejemplo: `cuotas, financiar, plan, pago, financiación` — esto ayuda al agente a encontrar la FAQ correcta.
   - **Status**: Activo

4. Guardar.

**Tip:** mirá las FAQs existentes para imitar el estilo de las respuestas.

---

### 5. Cambiar las líneas priorizadas del mes

**¿Cuándo?** Cuando el equipo comercial decide qué líneas destacar este mes. **Cambia mes a mes.**

**Quién lo hace:** Gerente (no Edgardo). Pero si te toca, así se hace.

**Pasos:**

1. Abrí la tabla **Config Mensual**
2. Si ya existe la fila del mes (ej: `2026-05`), abrila. Si no, creala.
3. Completá:
   - **Mes**: formato `2026-05`, `2026-06`, etc.
   - **Líneas priorizadas**: linkeá las líneas del mes (por ejemplo: RISO, DTF Textil)
   - **Notas para agente**: instrucciones como "Este mes hay promo en RISO, mencionar si pregunta por digital alta producción."
   - **Activo**: ✅ marcar para el mes en curso
4. **Importante**: solo UNA fila puede estar activa por mes. Si activás la nueva, desactivá la anterior.

---

### 6. Agregar un representante

**¿Cuándo?** Cuando entra un comercial nuevo o cambia el mapeo zona/línea.

**Quién lo hace:** Gerente.

**Pasos:**

1. Abrí la tabla **Representantes**
2. Click "+ Add record"
3. Completá:
   - **Nombre**: ej "Marcos R."
   - **Mail**: el que recibe las notificaciones de leads
   - **Teléfono**: opcional
   - **Líneas asignadas**: linkeá las líneas que maneja (multi)
   - **Zonas asignadas**: elegí CABA, GBA, Interior (multi)
   - **Backup**: opcional — linkeá a otro rep que cubre cuando éste no está
   - **Activo**: ✅
   - **Mail Gerente (copia)**: el mail del Gerente que recibe copia de notificaciones (puede repetirse)
4. Guardar.

**Importante:** debe haber siempre al menos un rep con `Activo = true` con `Zonas = CABA+GBA+Interior` y `Líneas = todas` para hacer de fallback.

---

## Cosas que NO hacés

- **No borres records** — preferí marcar como Discontinuado o Inactivo.
- **No renombres campos** — eso rompería las tools del agente. Si necesitás un campo nuevo, avisanos.
- **No modifiques la tabla Leads** — la llena el agente automáticamente. Si querés anotar algo sobre un lead, usá el campo `Notas internas`.
- **No cambies el campo `Modelo` de un equipo existente** — si querés renombrarlo, mejor crear uno nuevo y marcar el viejo como Discontinuado.

---

## Cuando algo no funciona

### "El agente dice que no encuentra un equipo que yo cargué"

Posibles causas:
- El equipo tiene `Status = Próximamente` o `Discontinuado` → cambialo a Activo.
- Falta linkear `Tecnología` o `Línea` → completalo.
- La descripción está vacía → agregá descripción corta.

### "Un cliente del Interior preguntó por un equipo y el agente dijo que no estaba disponible"

Posible causa: el equipo no tiene `Interior` en `Disponibilidad zona`. Si querés que se ofrezca al interior, agregá esa zona al campo.

### "Quiero cambiar una FAQ que ya está, ¿la pisó?"

Sí, podés editarla en vivo. El próximo cliente que pregunte va a recibir la versión nueva. No hay que avisarnos.

### "Necesito agregar una marca nueva que no está en la lista"

En el campo `Marca`, click → "Add an option" → escribir la nueva marca → Save. Quedará disponible para todos los equipos futuros.

---

## Cuando avisar a la agencia

- Querés agregar un **campo nuevo** a alguna tabla (ej: "Año modelo", "Garantía meses")
- Querés cambiar la **estructura** de una tabla
- Notás que el agente **se confunde** con un tipo de consulta (ej: siempre recomienda mal una tecnología para X aplicación)
- Cambiaron **datos de un representante** que rompen el ruteo (ej: zona reasignada)
- Hay un **bug**: agente no responde, da respuesta incoherente, no notifica un lead

Contactanos por WhatsApp / mail. Tiempo de respuesta: <24h en días hábiles.

---

## Mini-glosario

- **Record** = una fila de la tabla.
- **Field** = una columna.
- **Linked record** = un campo que apunta a una fila de otra tabla (relación). Ejemplo: en Equipos, `Tecnología` linkea a la tabla Tecnologías.
- **View** = una vista filtrada/ordenada de la misma tabla. Ejemplo: "Para agente" filtra solo equipos Activos.
- **Status Activo** = el agente lo usa. Cualquier otro status = no lo usa.

---

## Onboarding (primera vez)

Cuando arrancamos, vamos a hacer una sesión de 30 minutos donde:
1. Te muestro la base armada
2. Cargamos juntos 2-3 equipos como ejemplo
3. Cargamos 2-3 FAQs juntos
4. Vemos cómo cambiar una línea priorizada
5. Resolvemos dudas

Después de eso, el sistema queda en tus manos. Cualquier consulta, escribinos.

---

**Bienvenido al sistema. Cualquier cosa que no esté clara, preguntás y refinamos esta guía. 🚀**
