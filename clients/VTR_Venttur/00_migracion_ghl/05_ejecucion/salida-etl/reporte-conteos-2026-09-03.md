# FASE 2 · Reporte de conteos (dry-run ETL) — 2026-09-03

```
Airtable Leads: 3819 · Clientify contacts: 6968 deals: 2338 companies: 266

Clientify: teléfonos canónicos únicos=4496 · phone-less=2467 · emails únicos=2653 · variantes MX malformadas=47
Airtable: teléfonos canónicos únicos=3434 (de 3819 leads)

Merge por teléfono: intersección Airtable∩Clientify=1844 · solo-Airtable=1590 · solo-Clientify=2652
FK Airtable: ID Clientify=1730 (45%) · ID Manychat=2907 (76%)

Población de los 6 CF genéricos de Clientify (crear solo los poblados):
  Task-Id: 10
  File: 24
  Guests: 54
  Date: 45
  Timezone: 1024
  Textinput: 72

Deals status: {'Open': 50, 'Expired': 1875, 'Lost': 381, 'Won': 32}
Deals moneda: {'MXN': 2127, 'USD': 211}
OPPORTUNITY_NO_DUPLICATE: 38 contactos con >1 deal en el mismo pipeline (85 deals afectados) → requiere 'Allow Duplicate Opportunity' ON o dedupe

UNIVERSO GHL Contacts: por teléfono=6086 + phone-less=2467 = 8553 (cota superior)

Remapeo `Programa interés` (Airtable):
  Internados: 919
  Pathway Alemania: 881
  Intercambio académico con familias: 632
  Campamentos de verano: 42
  Gap Year / Estudia y Trabaja: 25
  (sin programa): 1320

Salidas: contacts.jsonl=8525 · opportunities.jsonl=2338 · companies.jsonl=266
Verificación dedup: canónicos duplicados en salida = 0 (esperado 0)
```
