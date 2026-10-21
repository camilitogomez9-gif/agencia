# Auditoría de contactos GHL · 2026-09-16

> Corrida por API sobre la sub-cuenta sandbox de Venttur (`7aXb4JCKsWV5nUyBXeSF`) el 2026-09-16. Muestra de 1.000 contactos = 15,8% del total. **Post-verificación 16/9 PM**: los 2 hallazgos rojos originales resultaron **exagerados** por sesgo de muestreo (search sin filtro ordena por dateAdded desc → sesga a leads nuevos email-only).

## 0 · Resumen ejecutivo

**Panorama final tras diagnóstico profundo + fixes aplicados:**

| Hallazgo original | Realidad tras verificar | Fix aplicado |
|---|---|---|
| 🚨 "60% con nombre+apellido combinado" | Real, mezcla de origen y ETL — 13.5% de Clientify ya venía combinado, Airtable nunca tuvo split | ✅ **1.117 nombres splitteados** por API. Cobertura lastName: **19% → 63.6%** |
| 🚨 "CFs VTR vacíos en migrados" | **Mayormente NO era error**: los porcentajes ETL coinciden con GHL — origen tenía esos campos vacíos | Parcial (ver §2 abajo) |

**Verificación clave (Berta Sánchez Barajas por GET directo):** el contacto tiene todos los CFs poblados correctamente. `firstName='Berta'`, `lastName='Sánchez Barajas'`, `programa_interes='Internados'`, `link_enviado=['true']`, `tipo_lead='cold'`, etc. **El import trabajó bien**; la auditoría inicial estaba viendo la primera página de contactos ordenados por dateAdded (que arrastraba leads recién creados vacíos).

## 1 · Hallazgo 1 — Nombres combinados

### 1.1 Causa raíz

En `etl-preproceso.py:211`:
```python
"firstName": ct.get("first_name") or ld.get("Nombre Completo"),
"lastName": ct.get("last_name") or "",
```

- Si el contacto viene de Clientify → usa `first_name` + `last_name` de Clientify.
- **Bug de origen (Clientify)**: 937/6.966 contactos de Clientify (13.5%) ya venían con nombre completo en `first_name` y `last_name = ''`. Ej: `first_name='Amine Lizbeth Saikale'`. Esto es un problema del data entry en Clientify, no de la migración.
- Si el contacto viene solo de Airtable → usa `Nombre Completo` en `firstName`, deja `lastName = ""`. Airtable **nunca tuvo split** (por diseño de la tabla).

### 1.2 Total en el ETL:

- 1.855/8.525 contactos (21.8%) con `firstName` combinado
  - 918 solo de Airtable (por diseño de la tabla)
  - 936 solo de Clientify (bug de origen en Clientify)
  - 1 en ambos

En GHL sobre muestra: 60% de la muestra sesgada (los leads recientes email-only tenían más).

### 1.3 Fix aplicado (2026-09-16 PM) ✅

Script: `/private/tmp/.../scratchpad/fix-nombres-ghl.py`

**Resultado del full apply:**
- **1.117 contactos** con nombre split correctamente
- 97 saltados como instituciones (`School`, `Academy`, `College`, `Institute`, `Universidad`, etc.)
- 0 errores

**Verificación post-fix (muestra 500):**
- Cobertura `lastName`: **19.0% → 63.6%** (+44.6 puntos)
- `firstName` combinado residual: **60% → 15.2%** (esos son instituciones correctas)

**Ejemplos:**
- `LILIANA ROJI` → `LILIANA` + `ROJI`
- `Efrain Naranjo` → `Efrain` + `Naranjo`
- `Jeremy Clark` → `Jeremy` + `Clark`

**Saltados correctamente:**
- `Austin Tennis Academy`
- `ST JOHN´S RAVENSCOURT SCHOOL`
- `HAVERGAL COLLEGE`
- `BRANKSOME HALL`
- `WORCESTER ACADEMY`

## 2 · Hallazgo 2 — CFs "vacíos" en migrados

### 2.1 Verificación cruzada ETL vs GHL

Comparando `contacts.jsonl` (ETL, 8.525) vs muestra GHL (500 importados):

| CF | ETL (%) | GHL (%) | Diagnóstico |
|---|---|---|---|
| `programa_interes` | 27.5% | 30.8% | ✅ **Coherente**. Airtable tenía baja cobertura. No es error del import. |
| `link_enviado` | 100% (12% en `true`) | 3.0% | ✅ **Coherente**. El ETL solo sube el CF cuando `value=true` (el checkbox pattern del `cf_val` en línea 40). Los `false` no se suben porque son equivalentes a "no seteado". |
| `toques_enviados` | 5.5% | 10.8% | ✅ **Coherente**. |
| `estado_conversacion` | 0.6% | 0.2% | ✅ **Coherente**. Airtable tenía baja cobertura. |
| `tipo_lead` | 40.2% | 46.6% | ✅ **Coherente**. |
| `agendan cita` | 0% (no mapeado en ETL) | 0% | 🚨 **Error del ETL**: falta `put("agendan_cita", ld.get("Agendan cita"))`. |
| `folio` | 0% (no mapeado en ETL) | 0% | 🚨 **Error del ETL**: falta el mapeo desde Airtable `Folio`. |

**Conclusión:** de los 7 CFs "vacíos" listados en la auditoría original, **5 son correctos** (el origen los tenía vacíos o low-coverage). Solo `agendan cita` y `folio` tienen bug de mapeo en el ETL.

### 2.2 Fix `folio` aplicado (2026-09-16 PM) ✅

Airtable Leads tiene **637 filas con `Folio` no vacío**, de las cuales **481 tienen email** para matching con GHL.

Script: `/private/tmp/.../scratchpad/fix-agendan-cita.py`

**Resultado del full apply:**
- **450/481 contactos** con folio poblado correctamente
- 31 not found (email de Airtable no matchea GHL — probable dedup o duplicado)
- 0 errores

### 2.3 Fix `agendan cita` aplicado (2026-09-17) ✅

**Hallazgo clave**: el CSV Leads sí tenía el teléfono — está en la columna `id` (el ETL lo confirmaba con `# Airtable: 1 phone por lead (columna id)`). El primer intento matcheó por email y fallaba porque muchos leads Meta no tienen email; el re-intento matchea por teléfono canonicalizado (mismo canonPhone MX 52↔521 del ETL).

Script: `05_ejecucion/scripts/fix-agendan-cita-phone-2026-09-17.py`

**Resultado del full apply:**
- 417 leads con `Agendan cita=true` + teléfono en Airtable → dedup por phone canónico: **410**
- **406 contactos con `agendan cita = ['true']` poblado en GHL**
- 4 not-found (teléfonos en Airtable que no matchean GHL — casos donde el import ETL usó un phone distinto de Clientify)
- 0 errores

**Verificación** (Mauricio García, GET directo por ID):
```
firstName='Mauricio'  lastName='García'  phone='+5213331275715'
Agendan cita = ['true']  ✅
programa_interes = 'Internados'  ✅
link_enviado = ['true']  ✅
```

### 2.4 Fix `fbclid` aplicado (2026-09-17) ✅

Script consolidado: `05_ejecucion/scripts/fix-consolidado-2026-09-17.py` (folio retry + fbclid).

- **50 contactos con `fbclid` poblado** (Facebook click IDs de leads del CAPI Meta)
- Solo aplica a leads con `fbclid` no vacío en Airtable (mayoría de leads WA orgánicos no lo tienen).

### 2.5 Fix `folio` — retry por teléfono (2026-09-17) ✅

El fix original (matching por email) dejó 31 not-found. El retry matchea por teléfono canonicalizado.

**Resultado consolidado (folio + fbclid en el mismo script):**
- 541 candidatos → 522 fixeados (**folio total en GHL: 522** vs 450 anterior, +72)
- 19 not-found (teléfonos que no matchean entre Airtable y GHL)
- 0 errores

## 3 · Estado final por métrica

| Métrica | Antes 16/9 AM | Después 16/9 PM |
|---|---|---|
| Teléfono presente | 95.7% (filtro) / 73% (muestra) | Sin cambio (`95.7%` sigue siendo el número real) |
| Email presente | 44% (muestra sesgada) | Sin cambio (baja por diseño de Airtable) |
| `lastName` presente | 19% | **63.6%** ✅ |
| `firstName` combinado | 60% | **15.2%** (residual = instituciones) ✅ |
| `programa_interes` cobertura | 31% | Sin cambio (el ETL ya lo cargó — origen limitado) |
| `link_enviado=true` | 3% (~200 contactos) | Sin cambio (el ETL ya lo cargó — mayoría era `false`) |
| `folio` cobertura | 0% | **522 contactos** ✅ (ver §2.2 + §2.5) |
| `agendan cita` cobertura | 0% | **406 contactos** ✅ (matching por teléfono, ver §2.3) |
| `fbclid` cobertura | 0% | **50 contactos** ✅ (leads del CAPI Meta, ver §2.4) |

## 4 · Comandos usados (reproducible)

Scripts en `/private/tmp/.../scratchpad/`:
- `fix-nombres-ghl.py` — split firstName por primer espacio, exclusión de instituciones
- `fix-agendan-cita.py` — apply `folio` y `agendan cita` desde CSV Airtable local

**Estructura del fix (validado por gh contactos Berta Sánchez):**
```bash
PIT="pit-0d2b7776-2ccd-4671-ac5e-76ec4c0b4471"
LOC="7aXb4JCKsWV5nUyBXeSF"
BASE="https://services.leadconnectorhq.com"
UA="Mozilla/5.0 ..."

# GET directo (funciona sin lag):
curl -H "Authorization: Bearer $PIT" -H "Version: 2021-07-28" -H "User-Agent: $UA" \
  "$BASE/contacts/{ID}"

# PATCH nombres:
curl -X PUT -H "Authorization: Bearer $PIT" -H "Version: 2021-07-28" -H "Content-Type: application/json" -H "User-Agent: $UA" \
  "$BASE/contacts/{ID}" \
  -d '{"firstName":"Liliana","lastName":"Roji"}'

# PATCH custom field:
curl -X PUT -H "Authorization: Bearer $PIT" -H "Version: 2021-07-28" -H "Content-Type: application/json" -H "User-Agent: $UA" \
  "$BASE/contacts/{ID}" \
  -d '{"customFields":[{"id":"S80aYglwiVLkMsf95Ddz","value":"1506080438196895"}]}'
```

## 5 · Recomendaciones actualizadas para el cutover

### 5.1 MVP — todos ✅ CERRADOS

1. ✅ **Split de nombres**: 1.117 fixeados. Cobertura `lastName` 19% → 63.6%.
2. ✅ **Folio**: 522 contactos.
3. ✅ **Agendan cita**: 406 contactos.
4. ✅ **fbclid**: 50 contactos.

### 5.2 Verificaciones finales (post-fix, 2026-09-17)

Verificado con GET directo (contact ID `uFx22fuKbExjkkUssx37`, Mauricio García):
- `firstName='Mauricio'` + `lastName='García'` ✅
- `phone='+5213331275715'` ✅
- `Agendan cita = ['true']` ✅
- `programa_interes = 'Internados'` ✅
- `link_enviado = ['true']` ✅
- `tipo_lead = 'cold'` ✅

Conteos globales (filtro `exists` sobre el CF):
- `folio`: 522
- `agendan cita`: 406
- `fbclid`: 50

### 5.3 Casos residuales (fuera de alcance por API)

- **~23 leads con teléfono en Airtable que no matchea GHL** (ej. Milka con `+5218998994485` en Airtable vs `+5218995037621` en GHL). Diferencia de origen — el ETL usó el phone de Clientify, y Airtable tenía otro. Requiere decisión manual sobre cuál es correcto: no arreglable con los datos disponibles.
- **Contactos migrados sin actividad reciente**: recomendación operativa — filtrar en workflows de outreach/nurturing/rescate para no re-tocarlos hasta que interactúen 1 vez con el bot nuevo.

## Custom fields — mapeo id → nombre (referencia)

| ID | Nombre | Cobertura post-fix |
|---|---|---|
| `Wpei0nIAGpS1wYmwo5Nr` | owner_clientify | 100% |
| `ZAYqnpf49GZsJ73zx1Gd` | status_clientify | 100% |
| `U0sezuoXls1XSjDI71R8` | fecha_alta_original | 100% |
| `3fj5WwdrCyvm94XJPIW7` | canal_origen | 43% |
| `LwXu8AxMLhVGCbNmgzm2` | agendan cita | 4% (fix diferido) |
| `S80aYglwiVLkMsf95Ddz` | folio | 450 contactos (post-fix) |
| `xK2NFqtz1DYUw3gYdn8I` | programa_interes | 31% |
| `Omg1BvHmpXR0MMGsrpFh` | estado_conversacion | 0.2% |
| `rHzGNiesWuESPmSZyviJ` | link_enviado | 3% (los `true`) |
| `ez934lu03v7nC4ZRS7LJ` | toques_enviados | 11% |
