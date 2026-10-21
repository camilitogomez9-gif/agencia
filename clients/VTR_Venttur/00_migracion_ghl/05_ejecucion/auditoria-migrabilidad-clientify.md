# Auditoría de migrabilidad de Clientify — VTR → GHL

> **Entregable de la agencia (gate del cliente, `06 §6.3`).** Antes de apagar Clientify, esto lista **qué se puede pasar a GHL y qué NO** — para que el cliente respalde por su cuenta lo que no viaja. **No existe migración automática Clientify→GHL:** buena parte es reconstrucción por API/lote (que la agencia ejecuta en la Fase 3), y algunas categorías directamente no migran.
>
> Corroborado contra el snapshot 2026-07-24 (conteos reales) y el ETL de la Fase 2. Fecha: 2026-09-03.

## Resumen por categoría

| Qué | Volumen real | ¿Migra a GHL? | Cómo | Quién |
|---|---|---|---|---|
| **Contactos** | 6.968 | ✅ Sí | API (upsert por teléfono canónico + email), deduplicado con Airtable → **~8.525 GHL Contacts** | la agencia (Fase 3) |
| **Deals / pipelines** | 2.338 en ~19 pipelines | ✅ Sí | API a Opportunities, pipelines/stages verbatim; **reconstrucción por lote** | la agencia (Fase 1+3) |
| **Companies** | 266 | ✅ Sí | API a `/businesses/` (sin custom fields — GHL business no los soporta; sector/rfc → nota) | la agencia (Fase 3) |
| **Custom fields (definiciones)** | 22 | ✅ Sí | como CF de Contact (13 encuesta + estructurales); 6 genéricos según población (ver abajo) | la agencia (Fase 1) |
| **Owners / asesores** | 8 | ✅ Sí | mapeo por email → usuarios GHL (`assignedTo`) | la agencia + cliente (mapeo) |
| **GDPR (accept/fechas/disclaimer)** | por contacto | ✅ Sí | CF preservados por cumplimiento | la agencia (Fase 3) |
| **Historial de conversaciones** (chat/inbox de Clientify) | — | ❌ **NO (probable)** | no hay API de export a GHL Conversations | **⚠️ el cliente respalda por su cuenta** |
| **Adjuntos** (archivos en contactos/deals) | — | ❌ **NO (probable)** | no viajan en el import de datos | **⚠️ el cliente respalda por su cuenta** |
| **Automatizaciones de Clientify** | — | ❌ NO | se reconstruyen en GHL/n8n o mueren | la agencia (reconstruye lo vigente) / cliente |
| **Segundo número (recordatorios)** | 1 | ❌ muere | decisión cerrada: muere y **no se avisa** (`portabilidad §8`) | — |

## Datos que ancla el ETL (Fase 2)

- **Deals por estado:** 1.875 Expired (80%) · 381 Lost · 50 Open · 32 Won → los Expired van a `abandoned` (A3 ✅).
- **Moneda mixta:** 2.127 MXN + 211 USD → `monetaryValue` crudo + custom `moneda` (A6 ✅).
- **Colisión de opps:** **38 contactos con >1 deal en el mismo pipeline (85 deals)** → requiere `Allow Duplicate Opportunity = ON` **antes** de cargar (B-02).
- **6 CF genéricos — población real** (crear solo lo que aporta): `Timezone` **1.024** (crear) · `Textinput` 72 · `Guests` 54 · `Date` 45 · `File` 24 · `Task-Id` 10. Los 5 chicos huelen a ruido de widget de booking; se migran como TEXT por fidelidad (baratos) o se descartan — decisión menor de Fase 1.
- **Phone-less Clientify:** 2.467 sin teléfono canónico → match por email; los que no matcheen migran phone-less (sin canal WA hasta que aporten teléfono).

## ⚠️ Acción del cliente antes de apagar Clientify

Respaldar por su cuenta (no viajan a GHL): **(1) el historial de conversaciones/chat, (2) los adjuntos de contactos y deals, (3) cualquier automatización de Clientify que quiera conservar como referencia.** Una vez respaldado y confirmado el import reconciliado, Clientify se apaga (`12 §12.6`).

*Auditoría corroborada contra `vtr-data-snapshot-2026-07-24.json` (6.968/2.338/266/22) + el ETL `etl-preproceso.py`. 2026-09-03.*
