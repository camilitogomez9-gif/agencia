# Convenciones de Nomenclatura — la agencia

## IDs de Cliente
- Formato: `CLT[NNN]` (NNN = número correlativo desde 001)
- Ejemplo: IMP, SNR, VTR

## Workflows n8n
- `WF_[NICHE]_[FUNCION]_v[N]`
- NICHE: DENTAL | REALESTATE | AGENCY | AUTO | GENERIC
- Ejemplo: `WF_DENTAL_LeadQualification_v1.json`

## Agentes IA
- `AGT_[FUNCION]_v[N]`
- Funciones: Booking | Qualification | FollowUp | Support | Sales
- Ejemplo: `AGT_Booking_v3`

## Prompts
- `PRM_[ROL]_[NICHE]_v[N]`
- Ejemplo: `PRM_QualificationBot_Dental_v2.md`

## Documentos cliente
- `[CLIENTEID]_[TIPO]_[YYYY-MM]`
- TIPO: Scope | Discovery | Architecture | Proposal | Report
- Ejemplo: `IMP_Scope_2025-06.pdf`

## Ramas (si se usa Git)
- `feat/IMP-whatsapp-flow`
- `fix/SYS-airtable-sync`
- `core/template-booking-agent`
