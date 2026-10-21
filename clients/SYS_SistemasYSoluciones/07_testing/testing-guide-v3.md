# Guía de Testing — Agente Sistemas y Soluciones v1.3 (resultados) + Re-test v1.4

**Versión:** v1.3 (resultados completos)
**Fecha:** 2026-04-20
**Canal de prueba:** Telegram
**Estado:** Testing v1.3 completado — correcciones aplicadas en v1.4

---

## Resultados testing v1.3 — resumen

| Estado | Cantidad |
|--------|----------|
| ✅ Aprobado | 23 |
| ⚠️ Issue menor | 1 |
| ❌ Fallo | 7 |

**Correcciones aplicadas en v1.4:**
- **Flujo 2 T1:** distribuidor salta a pedir datos sin calificar → regla de contexto previa
- **Flujo 3 T1:** pide mail antes que ubicación → orden de datos corregido (nombre → tel → ubicación → mail al final)
- **Flujo 5:** no reconoce dump de datos → Regla 13 (derivar inmediato)
- **Flujo 8 T2:** pide mail sin elevar en showroom → Regla 14 (nombre+tel suficiente)
- **Flujo 9 T2:** pide mail sin elevar en financiación → Regla 14
- **Flujo 10 Rama A:** sigue preguntando post-derivación → REGLA POST-DERIVACIÓN
- **Flujo 10 Rama B T1:** no llama tool Equipos para "modelos DTF" → descripción de Equipos ampliada
- **Placeholder:** agente usaba "ELEVAR" → instrucción reforzada para "[NOTIFICAR_LEAD]" exacto

---

## Re-test v1.4 — casos corregidos

Testear cada caso en conversación nueva. Verificar el comportamiento específico indicado.

---

### Re-test 1: Flujo 2 — Distribuidor (Turno 1)

**Comportamiento a verificar:** el agente NO salta a pedir datos. Primero hace UNA pregunta de contexto.

| Turno | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|---------|-------------------|-------------------|----|
| 1 | `Soy distribuidor y quiero agregar equipos a mi catálogo` | Reconoce el perfil; pregunta por líneas de interés o zona — UNA sola pregunta | | |
| 2 | `Equipos DTF, opero en Córdoba` | Toma nota; pide datos de contacto para derivar. No dice "(si aplica)" para empresa | | |
| 3 | `Roberto Díaz, Gráfica Norte, roberto@graficanorte.com, 351-555-0000` | Confirma datos; incluye `[NOTIFICAR_LEAD]` con formato correcto (no "ELEVAR") | | |

---

### Re-test 2: Flujo 3 — Orden de datos (Turno 1)

**Comportamiento a verificar:** el agente pide nombre, teléfono y ubicación — NO mail en este paso.

| Turno | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|---------|-------------------|-------------------|----|
| 1 | `Quiero que me llame alguien` | Pide nombre, teléfono y ubicación (NO mail) | | |
| 2 | `Juan Perez, 59899000001, Montevideo` | Pide mail con la frase estándar ("Si querés, te mando más información...") | | |
| 3 | `juan@mail.com` | Confirma derivación; cierra con calidez; incluye `[NOTIFICAR_LEAD]` y `[REGISTRAR_LEAD]` | | |

---

### Re-test 3: Flujo 5 — Dump de datos

**Comportamiento a verificar:** el agente NO hace diagnóstico. Confirma datos y deriva de inmediato.

| Turno | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|---------|-------------------|-------------------|----|
| 1 | `Soy María López, de Imprenta Rápida, maria@imprentarapida.com, 11-1234-5678, CABA, me interesa una mesa de corte` | Confirma los datos recibidos; informa que el equipo comercial se va a contactar; incluye `[NOTIFICAR_LEAD]` y `[REGISTRAR_LEAD]`; NO continúa con diagnóstico | | |

---

### Re-test 4: Flujo 8 — Showroom (post-datos)

**Comportamiento a verificar:** con nombre + teléfono el agente eleva. No bloquea por falta de mail.

| Turno | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|---------|-------------------|-------------------|----|
| 1 | `Quisiera ver los equipos funcionando antes de decidir` | Confirma showroom y demos; pide nombre y teléfono | | |
| 2 | `Soy Carlos Mendez, 11-8888-7777` | Confirma que el equipo se va a contactar para coordinar la visita; incluye `[NOTIFICAR_LEAD]`; NO pide mail como requisito | | |

---

### Re-test 5: Flujo 9 — Financiación (post-datos)

**Comportamiento a verificar:** con nombre + teléfono el agente eleva. No bloquea por falta de mail.

| Turno | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|---------|-------------------|-------------------|----|
| 1 | `¿Cómo funciona la financiación?` | Confirma que ofrecen; aclara que las condiciones se definen personalmente; pide nombre y teléfono | | |
| 2 | `Ana Flores, 351-444-3333` | Confirma que un representante se contacta; incluye `[NOTIFICAR_LEAD]`; NO inventa condiciones ni pide mail como requisito | | |

---

### Re-test 6: Flujo 10 Rama A — Post-derivación sin preguntas extra

**Comportamiento a verificar:** el agente eleva y cierra. No hace preguntas de diagnóstico después.

| Turno | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|---------|-------------------|-------------------|----|
| 1 | `Soy Laura García, de Imprenta Central, laura@central.com, 11-5555-4444, CABA, quiero cotizar una DTF` | Confirma los datos; incluye `[NOTIFICAR_LEAD]` y `[REGISTRAR_LEAD]` con formato correcto; NO hace preguntas adicionales post-derivación | | |

---

### Re-test 7: Flujo 10 Rama B — Tool Equipos para modelos DTF

**Comportamiento a verificar:** el agente llama la tool `Equipos` en lugar de responder que no tiene info.

| Turno | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|---------|-------------------|-------------------|----|
| 1 | `¿Qué modelos de impresoras DTF tienen disponibles?` | Llama la tool `Equipos` y usa los datos devueltos; NO dice que no tiene información | | |

---

### Re-test 8: Placeholder [NOTIFICAR_LEAD] exacto

**Comportamiento a verificar:** el tag es exactamente `[NOTIFICAR_LEAD]`, no "ELEVAR" ni variantes.

| Turno | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|---------|-------------------|-------------------|----|
| 1 | `Soy Pedro Sánchez, 11-7777-6666, CABA, me interesa una DTF` | Respuesta incluye `[NOTIFICAR_LEAD]` (con corchetes, sin variantes) | | |

---

## Resultados de testing v1.3 completos (referencia)

Los resultados completos del testing v1.3 están en `testing-guide-v2.md` con la columna "Resultado obtenido" completada.

> Re-test v1.4 — 8 casos que cubren las 7 correcciones aplicadas en la iteración post-testing.
