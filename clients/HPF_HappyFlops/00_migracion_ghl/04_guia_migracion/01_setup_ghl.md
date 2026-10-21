# M1 — Setup Inicial GHL

> **Referencia:** `03_arquitectura_ghl/00_arquitectura_general.md`  
> **Tiempo estimado:** 2-3 horas  
> **Prerequisito:** Acceso admin a la cuenta GHL de la agencia (o cuenta propia de Oscar si tiene Agency)

---

## 1.1 Crear Sub-Account para Happy Flops

1. En GHL → **Settings → Sub-Accounts → Create Sub-Account**
2. Completar:
   - **Business Name:** `Happy Flops`
   - **Business Email:** `[email de Oscar]`
   - **Phone:** `+523315948670` (número de Rebeca)
   - **Timezone:** `America/Mexico_City`
   - **Country:** Mexico
3. Guardar. Anotar el **Sub-Account ID** (aparece en la URL: `https://app.gohighlevel.com/location/[SUB_ACCOUNT_ID]/...`)

```
SUB_ACCOUNT_ID = ________________________
```

✅ Verificar que el sub-account aparece en el listado y se puede acceder.

---

## 1.2 Configurar datos del negocio

Dentro del sub-account → **Settings → Business Info**:

| Campo | Valor |
|-------|-------|
| Business Name | Happy Flops |
| Phone | +523315948670 |
| Website | [si tiene, agregar] |
| Address | [dirección de HPF si Oscar la provee] |
| Timezone | America/Mexico_City |
| Business Hours | Lun–Vie 9:00–18:00 CST (configurar en M4) |

---

## 1.3 Crear usuario para Oscar

**Settings → Team → Add Employee**

| Campo | Valor |
|-------|-------|
| Name | Oscar [apellido] |
| Email | [email de Oscar] |
| Role | Admin (para que pueda editar Custom Values) |
| Phone | [teléfono de Oscar] |

Enviarle el link de invitación. Oscar necesita aceptar antes del go-live.

> **DECISIÓN (2026-06-19):** No se envía invitación por email — se le compartirán las credenciales directamente cuando sea necesario para que tenga acceso completo como owner.

---

## 1.4 Configurar Languages & Locale

**Settings → Company → Language:** Spanish (Mexico)  
**Date Format:** DD/MM/YYYY  
**Currency:** MXN

> ⚠️ **PENDIENTE (2026-06-19):** No se encontró la sección `Settings → Company → Language` en la UI de GHL. Buscar en otra ruta antes del cutover.

---

## 1.5 Activar módulos necesarios

Verificar en **Settings → Labs** que estén habilitados:

- [x] Conversations
- [x] Opportunities (CRM Pipeline)
- [ ] Custom Fields
- [ ] Custom Objects *(si el plan lo incluye)*
- [ ] Workflows
- [ ] Custom Values
- [ ] Tags

> ⚠️ **PENDIENTE (2026-06-19):** Custom Fields, Tags, Workflows, Custom Values y Custom Objects **no aparecen como módulos en Labs** — ya están como secciones incorporadas en el sidebar. Confirmar antes del cutover que cada una es accesible y funcional desde el sidebar (sin necesidad de activarlos).

---

## 1.6 Crear API Key del sub-account

**Settings → Integrations → API Keys → Add API Key**

- **Name:** `la agencia-n8n-integration`
- **Scope:** seleccionar todos (o al menos: Contacts, Opportunities, Conversations, Custom Fields, Custom Values, Workflows)

```
GHL_API_KEY = ________________________
GHL_LOCATION_ID = [mismo que SUB_ACCOUNT_ID]
```

⚠️ Guardar inmediatamente en el `.env` de n8n (y en 1Password / gestor de contraseñas).

---

## 1.7 Webhook de entrada (para WF-01)

GHL recibe webhooks de n8n en algunos workflows. GHL también envía webhooks a n8n cuando hay mensajes entrantes. Esto se configura en M4 al crear WF-01, pero anotá ya la URL base de tu instancia n8n:

```
N8N_BASE_URL = https://[tu-dominio-n8n].com
```

---

## ✅ Checklist M1

- [x] Sub-account creado con ID anotado
- [x] Datos del negocio completados
- [x] Usuario Oscar — **DECISIÓN: credenciales directas en vez de invitación** (2026-06-19)
- [ ] Language/locale en español México — **PENDIENTE: no se encontró la sección** (2026-06-19)
- [ ] Módulos habilitados — **PENDIENTE: Custom Fields/Tags/Workflows/Custom Values no son módulos Labs, son secciones del sidebar; verificar accesibilidad** (2026-06-19)
- [x] API Key creada y guardada en gestor de contraseñas
- [x] URL de n8n anotada

**Siguiente:** M2 → Pipeline y Custom Fields
