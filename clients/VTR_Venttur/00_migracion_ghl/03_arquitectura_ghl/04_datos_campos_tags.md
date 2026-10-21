# 04 · Custom fields + tags de los 3 sistemas → GHL

> **🟡 Riesgo medio.** Catálogo consolidado: los custom fields de Clientify (22), ManyChat (13) y las columnas custom de Airtable Leads convergen en el **Contact / Opportunity de GHL**, dedupeados a una **lista canónica**. Los tags de ManyChat (5) y Clientify (freeform) se limpian. Los transitorios se descartan.
>
> Corroborado contra el snapshot (`clientify.custom_fields`, `manychat.custom_fields`, `manychat.tags`).

---

## 1. Regla de consolidación

El mismo dato hoy puede vivir en 2-3 sistemas con nombres distintos. La lista canónica sigue el **source-of-truth de `02` §3**: el bot (Airtable) gana para el estado del lead; Clientify gana para identidad/comercial; ManyChat casi todo se descarta (transitorio). Un custom field **no se migra tres veces** — se define una vez, en la entidad GHL correcta (Contact u Opportunity), con la fuente autoritativa.

---

## 2. Contact custom fields — desde Airtable Leads

Ya enumerados campo-por-campo en `02` §4. Resumen de los que se vuelven **Contact custom fields** (source of truth = Airtable, el bot escribe):

`programa_interes` (enum `01`) · `tipo_contacto` · `grado_escolar` · `nivel_ingles` · `inicio_deseado` · `fuente_lead` · `origen` · `ad_name` · `platform` · `lead_score` (⚠️ cálculo fuera del wf, `02` §9.7) · `tipo_lead` · `estado_conversacion` (NO etapa) · `link_enviado` (NO etapa — gate del rescate) · `outreach_enviado` · `outreach_enviado_at` · `toques_enviados` · `ultimo_toque_at` · `touch1_programado_at` · `ultima_actividad`.

---

## 3. Contact custom fields — desde Clientify (22 CF)

Los 22 CF de Clientify son en su mayoría una **encuesta de satisfacción post-programa** (feedback de estudiantes que ya completaron). Migran como Contact custom fields; muchos están poco poblados.

| CF Clientify | Grupo | Destino | Nota |
|---|---|---|---|
| `Nombre del estudiante` | operativo | **Contact custom `nombre_estudiante`** | ≠ `first_name` (que es el que escribe, el padre/madre) |
| `Contact-Type` | CRM | **Contact custom `contact_type`** | convive con `tipo_contacto` de Airtable |
| `Procesos Internos` | operativo | **Contact custom `procesos_internos`** | |
| `Recomendación del programa`, `Experiencia Global Venttur`, `Mejora Venttur según cliente`, `Información Venttur`, `Atención en extranjero Venttur`, `Acompañamiento Venttur`, `Asesoría Venttur`, `Experiencia Cultural`, `Adaptación`, `Instalaciones`, `Calidad de clases/actividades`, `Experencia General Programa`, `Recomendaciones y comentarios clientes Venttur` (13) | **encuesta post-programa** | **Contact custom fields** (grupo "Encuesta Venttur") | feedback de NPS/experiencia; agrupar bajo un folder de CF |
| `Task-Id`, `File`, `Guests`, `Date`, `Timezone`, `Textinput` (6) | genéricos/integración | **evaluar por población** | huelen a widget de form/booking; migrar solo los poblados, descartar los vacíos |

> Los 13 de encuesta son **valores históricos** (opiniones ya dadas) — se migran como dato, no como campo vivo que el bot escriba.

---

## 4. ManyChat (13 CF) — mayormente se descarta

| CF ManyChat | Tipo | Destino | Por qué |
|---|---|---|---|
| `parte1` / `parte2` / `parte3` / `respuesta_definitiva` | text | **se descartan** | mecanismo de multi-burbuja transitorio; se rehace en n8n (`06` §4) |
| `agendan_cita` | boolean | **ya en Airtable → Opportunity/etapa** | no migra desde ManyChat |
| `programa_interes` / `programa_rescate` / `programa_wpp` | text | **ya en Airtable `Programa interés`** | no migra desde ManyChat |
| `ctwa_clid` / `ad_source_id` | text | **se quedan en CAPI** (`05`) | atribución, no CRM |
| `mensaje_inicial_asesoria` / `mensaje_link_asesoria` | text | **se rehacen en `07`** (confirmación) | efímeros |
| `wpp` | text | **se descarta** | huérfano |

**Ninguna identidad ni campo de negocio nuevo entra desde ManyChat** — todo lo que importa ya vive en Airtable o Clientify.

---

## 5. Opportunity custom fields — desde Clientify deals

De `03` §3 (lo que no es campo nativo de Opportunity):

`cierre_esperado` (`expected_closed_date`) · `cierre_real` (`actual_closed_date`) · `probabilidad` (`probability`) · `moneda` (MXN/USD, por la mezcla — `03` §6.1) + los `custom_fields` propios de cada deal (migrar los poblados).

---

## 6. Tags

### ManyChat (5 tags → Contact tags)

| Tag ManyChat | Destino | Nota |
|---|---|---|
| `RESCATE_PROGRAMA_NO_MAPEADO` (87501935) | **Contact tag** | señal de rescate sin programa → con la fusión de "Estudio y Trabajo" (`00` §6) debería dejar de aplicarse |
| `LINK_ABANDONADO_FRIO` (87501917) | **Contact tag** | terminal del rescate; convive con el estado |
| `seguimiento_agenda` (77385811) | **Contact tag** | del seguimiento-agenda (que se consolida, `09`) |
| `seguimiento` (68459367) | **Contact tag** | genérico de nurturing |
| `wpp` (72033971) | **se descarta** | huérfano — no lo aplica ningún flow (`00` §6) |

### Clientify (tags freeform → limpiar)

Los tags de Clientify son **freeform por-contacto** (códigos de programa `BSG`/`HF`, strings como "boarding school 25", tags de link `<programa>_link_enviado`, y hasta URLs). No hay un catálogo cerrado. Migración con **limpieza**:
- **Códigos de programa** (`BSG`, `BS`, `HF`, …) → **redundantes** con `programa_interes` (enum) → no migrar como tag, o normalizar.
- **Tags de link** (`<programa>_link_enviado`) → redundantes con el custom `link_enviado` → no migrar como tag.
- **Tags de negocio reales** (segmentos, campañas) → **Contact tags** limpios.
- El resto (ruido, URLs) → descartar.

---

## 7. Normalización de `channel` / `medium` (Clientify)

De `02` §9.4: `channel` (~15 valores) + `medium` (~5) están muy fragmentados (juntos ~20 valores). **Se migran 1:1** como custom fields (`canal_origen`, `medium`) — no se descarta el crudo — **y** se agrega un campo derivado/normalizado a una **lista corta** de canales de origen para segmentar. No colapsar el crudo sin un diccionario viejo→nuevo que demuestre redundancia (§8 bandera 6), porque los valores pueden codificar distinciones reales de origen/campaña.

---

## 8. Banderas de este mapping

1. **Los 6 CF genéricos de Clientify** (`Task-Id`/`File`/`Guests`/`Date`/`Timezone`/`Textinput`): decidir por población real (migrar los que tengan datos, descartar los vacíos) — no migrar campos muertos.
2. **`nombre_estudiante` vs `first_name`:** el estudiante (hijo/a) NO es el contacto (el que escribe es el padre/madre). Mantener separados (regla del agente, `06`).
3. **Tags de Clientify sin catálogo cerrado:** requiere una pasada de limpieza (códigos de programa y de link son redundantes; se descartan como tags).
4. **Encuesta post-programa (13 CF):** agrupar bajo un folder de custom fields; son histórico, no campos vivos.
5. **Tipado mejor en GHL:** los que en ManyChat/Airtable eran texto libre (programa, tipo, nivel) pasan a **dropdown** en GHL (mejor integridad).
6. **`channel`/`medium` no se colapsan a ciegas** (§7): se migran 1:1 + un campo derivado normalizado. Colapsar el crudo requiere un diccionario viejo→nuevo que demuestre redundancia (método `00` §1.3), no basta "está fragmentado".

---

*Corroborado contra `clientify.custom_fields` (22), `manychat.custom_fields` (13), `manychat.tags` (5) del snapshot. 2026-08-26.*
