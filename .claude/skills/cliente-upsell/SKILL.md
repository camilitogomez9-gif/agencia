---
name: cliente-upsell
description: >
  Usar este skill cuando el usuario quiera documentar, planificar o registrar un upsell
  para un cliente existente. Se activa con frases como "upsell para X", "proponer expansión
  a X", "X quiere agregar X funcionalidad", "nueva oportunidad con X". Documenta el upsell
  en ops/04_upsells/, vincula al cliente y sugiere los próximos pasos.
---

# Skill: Cliente Upsell

## Descripción

Registra y documenta una oportunidad de expansión (upsell) para un cliente existente.
Puede ser una nueva funcionalidad, un canal adicional, una integración nueva, o un
nuevo agente. Crea el documento de upsell en `ops/04_upsells/` y actualiza el cliente.

---

## Proceso

### Paso 1 — Identificar el cliente y la oportunidad

Si el usuario no los proveyó, preguntar:

- **¿Para qué cliente es el upsell?** (listar clientes activos si no se especificó)
- **¿Qué se quiere agregar o expandir?** (funcionalidad, canal, integración, agente)
- **¿De dónde surgió la oportunidad?** (pedido del cliente, propuesta nuestra, reunión)
- **¿Hay un valor económico estimado o presupuesto?**
- **¿Hay urgencia o timeline?**

### Paso 2 — Leer el contexto del cliente

1. Leer `clients/[CLTXXX_Nombre]/CLIENT_INFO.md`
2. Revisar qué está activo en su stack y qué fase del ciclo está
3. Entender la solución actual para no proponer algo redundante

### Paso 3 — Crear documento de upsell

Crear el archivo: `ops/04_upsells/[CLTXXX]-upsell-[descripcion-corta]-[YYYY-MM-DD].md`

Estructura del documento:

```markdown
# Upsell: [Descripción corta]

## Cliente
- ID: CLT[NNN]
- Nombre: [Nombre]
- Fecha identificación: [YYYY-MM-DD]

## Oportunidad
[Descripción de qué se va a agregar y por qué tiene valor para el cliente]

## Origen
- [ ] Pedido del cliente
- [ ] Propuesta nuestra
- [ ] Reunión de revisión
- [ ] Otro: ___

## Solución propuesta
[Qué se construiría, qué integraría, qué problema adicional resuelve]

## Stack involucrado
[Herramientas nuevas o extensión del stack actual]

## Estimación económica
- Valor: $[monto o rango]
- Modalidad: único | mensual | por evento

## Próximos pasos
- [ ] [Acción 1]
- [ ] [Acción 2]

## Estado
- [ ] Identificado
- [ ] Propuesto al cliente
- [ ] Aprobado
- [ ] En desarrollo
- [ ] Entregado

## Notas
```

### Paso 4 — Actualizar CLIENT_INFO.md (si aplica)

Si el upsell fue aprobado o está en desarrollo:
- Actualizar el **Status** del cliente si cambió
- Agregar nota en **Notas críticas** sobre el upsell activo

### Paso 5 — Sincronizar

Ejecutar el skill `cliente-sync` sobre el cliente trabajado. El sync reportará qué se registró.

---

## Reglas

- Un archivo de upsell por oportunidad
- No mezclar múltiples upsells en un mismo documento
- Si el upsell fue aprobado, considerar usar `/cliente-avance` para registrar el progreso del desarrollo
- Responder en español
