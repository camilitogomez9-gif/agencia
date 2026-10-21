# F1 Migración Airtable — Log de ejecución

> **Plan táctico:** `planes/sys-f1-migracion-airtable-2026-05-28.md`
> **Plan maestro:** `/Users/camilo/.claude/plans/contexto-general-del-dapper-sun.md`
> **Llenar a medida que se ejecutan los pasos.**

---

## Estado general

- **Estado:** F1 técnicamente COMPLETADA ✅. Smoke test pasado 2026-05-29. Solo queda (a) onboarding Edgardo — no bloquea ninguna fase siguiente.
- **Fecha inicio:** 2026-05-28
- **Fecha re-alineación post-Excel:** 2026-05-29
- **Fecha smoke test OK:** 2026-05-29
- **Fecha fin (técnica):** 2026-05-29
- **Ejecutado por:** la agencia + Claude

---

## Resumen de pasos

| Paso | Descripción | Estado | Quién | Cuándo | Notas |
|---|---|---|---|---|---|
| 1 | Crear workspace + base Airtable | ⏳ Pendiente manual | | | |
| 2 | Crear las 11 tablas con campos | ⏳ Pendiente manual | | | |
| 3 | Seed Tecnologías (8) | ⏳ Pendiente manual | | | |
| 4 | Seed Sustratos (16 + links) | ⏳ Pendiente manual | | | |
| 5 | Seed Líneas de Producto (10) | ⏳ Pendiente manual | | | |
| 6 | Seed Aplicaciones (20 + links) | ⏳ Pendiente manual | | | |
| 7 | Seed FAQs (10) | ⏳ Pendiente manual | | | |
| 8 | Seed Representantes (1 fallback) + linkear líneas | ⏳ Pendiente manual | | | |
| 9 | Seed Config Mensual (1) | ⏳ Pendiente manual | | | |
| 10 | Seed Equipos stub (5 en Próximamente) | ⏳ Pendiente manual | | | |
| 11 | Configurar 8 vistas críticas | ⏳ Pendiente manual | | | |
| 12 | Generar token + capturar IDs | ⏳ Pendiente manual | | | |
| 13 | Crear credencial n8n + smoke test | ✅ Hecho 2026-05-29 | Usuario | 2026-05-29 | Credencial `Airtable SYS` ID `3zohdTBWzW8UUN6P` |
| 14 | Setup variables n8n | ⚠ Resuelto con Opción C (hardcoded) | Usuario + Claude | 2026-05-29 | Plan n8n actual no soporta Variables UI. Decisión: hardcoded directo en workflows. Catálogo único en `airtable-credentials.md` sección "Valores hardcoded". Migración a `$env.X` documentada para futuro. |
| 15 | Backup seeds documentado | ✅ Hecho local | Claude | 2026-05-28 | `airtable-seeds-completos.md` (markdown copia-pega) + `airtable-csv/` (8 CSVs importables = 71 records totales) + README con tipos de campo |
| 16 | Onboarding Edgardo | ⏳ Pendiente coord humana | | | |
| 17 | Actualizar docs (CLIENT_INFO, schema, CLAUDE.md, datos-actuales) | 🟡 Parcial (CLIENT_INFO en intermedio) | Claude / pendiente final | 2026-05-28 | Resto cuando F1 esté 100% |
| 18 | git commit con `/cliente-sync` | ⏳ Pendiente fin de F1 | | | |

---

## Tiempos efectivos

| Paso | Tiempo estimado | Tiempo real |
|---|---|---|
| 1 (workspace + base) | 10 min | |
| 2 (11 tablas + campos) | 2-3 hs | |
| 3-9 (seeds principales) | 2 hs | |
| 10 (stubs Equipos) | 30 min | |
| 11 (vistas) | 45 min | |
| 12 (token + IDs) | 20 min | |
| 13 (credencial n8n + test) | 20 min | |
| 14 (vars n8n) | 10 min | |
| 16 (onboarding Edgardo) | 30 min call | |
| 17 (docs) | 30 min | |
| 18 (sync git) | 5 min | |
| **TOTAL** | **8-10 hs** | |

---

## Decisiones tomadas durante ejecución

(Llenar a medida que aparecen)

| # | Decisión | Razón | Quién | Cuándo |
|---|---|---|---|---|
| 1 | _ej: se renombró un campo_ | _justificación_ | | |

---

## Divergencias del schema teórico

Si durante la carga aparece algo que no coincide con `airtable-syscatalogo-schema.md`, anotarlo acá y actualizar el schema doc.

| Divergencia | Schema dice | Realidad | Acción tomada |
|---|---|---|---|
| Vistas Leads NO creadas (`Nuevos hoy`, `Pendientes derivación >24h`) | Schema doc Tabla 10 lista 6 vistas críticas para Leads | Cliente decidió 2026-05-28 NO avanzar con CRM; solo se crean vistas/uso productivo cuando apruebe el upsell | Documentado en `ops/04_upsells/SYS-upsell-crm-leads-2026-05-28.md`. Tabla Leads queda creada vacía. Tool `notificar_lead` se ajusta a versión reducida (mail + Telegram, sin write Airtable). |
| **Catálogo real vs stub** | Schema teórico tenía 5 equipos stub + marcas Mimaki/Roland | Cliente entregó `BASE DE PRODUCTOS.xlsx` 2026-05-29 con 92 equipos reales + marcas HUENU/DLICAN/TENETH/HANRUN/XENONS + 10 cabezales + 33 insumos + 21 equipos Konica refurbished | Re-alineación completa: nuevo schema, nuevos CSVs, prompt v2.0 → v2.1, +1 tool (`consultar_inventario_usados`), +1 tabla (Inventario Konica). Doc maestro: `06_docs/realineacion-post-excel-2026-05-29.md`. Usuario re-importa CSVs nuevos. |
| **Tecnologías** | 8 tecnologías hardcoded | Excel revela 10 (las 8 + Solvente + Corte) | Agregadas al CSV 01-tecnologias.csv + al system prompt v2.1 |
| **Precios USD** | "El agente nunca da precios" → asumimos catálogo sin precios | Excel los tiene todos | Decisión: cargar precios en campo `Precio USD` con vista filtrada "Para agente" que los oculta. Cliente edita en vista completa; agente nunca los ve. |

---

## Problemas encontrados

| Problema | Resolución | Quién | Cuándo |
|---|---|---|---|

---

## Validación post-setup

Marcar después de completar Pasos 1-14:

- [ ] Base `SyS Catalogo` visible en Airtable workspace la agencia
- [ ] 11 tablas creadas con todos los campos del schema
- [ ] Linked fields funcionando en ambas direcciones (test: clickear una Tecnología desde un Equipo abre la Tecnología; volver desde Tecnología → ver Equipos asociados)
- [ ] Seeds cargados según `airtable-seeds-completos.md`
- [ ] 8 vistas críticas configuradas y devolviendo lo esperado
- [ ] Token n8n creado con scopes correctos
- [ ] Base ID + 11 Table IDs + 4 View IDs documentados en `airtable-credentials.md` (gitignored)
- [ ] Credencial n8n `Airtable SYS` probada (Search en Tecnologías retorna 8 records)
- [ ] Variables n8n configuradas

---

## Onboarding Edgardo

- **Fecha sesión:** _____________
- **Mail Edgardo:** _____________
- **Invitación enviada:** ⏳ Pendiente
- **Acceso confirmado:** ⏳ Pendiente
- **Equipos cargados durante sesión:** _____ (número)
- **Compromiso GO LIVE:** mínimo 10 equipos en Status=Activo antes de F8
- **Dudas resueltas:** _____________
- **Pendientes para Edgardo:** _____________

---

## Cierre F1

Cuando todos los checkboxes de validación estén ✅:

1. Actualizar `CLIENT_INFO.md`: status "F1 COMPLETADA"
2. Actualizar `CLAUDE.md`: sección SYS refleja Etapa 2 / F0 + F1 completadas
3. Actualizar `contexto/datos-actuales.md`: fila SYS con "BUILD F1✅", próximo paso "F2 Supabase setup"
4. Ejecutar `/cliente-sync SYS` para commit (NO incluye `airtable-credentials.md`)
5. Marcar este log como `Estado: COMPLETADA`
6. Cambiar estado del plan `planes/sys-f1-migracion-airtable-2026-05-28.md` a `Implementado`

**Fecha cierre:** _____________
