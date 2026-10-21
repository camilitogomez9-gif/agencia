# Pieza web — Propuesta de mantenimiento Sonrisas (Cecilia)

Versión navegable de [`../propuesta-mantenimiento-2026-08.md`](../propuesta-mantenimiento-2026-08.md).
**El markdown es la fuente de verdad del contenido interno; esta pieza es la versión de cara al cliente** (sin mecánicas internas: no menciona reparto, ni Camilo, ni el fee de la agencia).

## Estado

🟢 Lista para enviar. Sin banner de borrador. Dos opciones A/B (la agencia US$500/mes · comunidad US$250–350/mes), tono rioplatense.

## Deploy

Sale **del directorio de la pieza**, nunca de la raíz:

```bash
cd clients/SNR_Sonrisas/06_docs/propuesta-web && npx vercel deploy --prod
```

🔴 **Al primer deploy se corrió `vercel link --project propuesta-sonrisas` explícito** para evitar que Vercel infiera el nombre del directorio genérico (`propuesta-web`) y pise la URL de otro cliente (incidente FAM↔CRB del 25-ago).

## En producción

**https://propuesta-sonrisas.vercel.app** (proyecto Vercel `propuesta-sonrisas`).

- Cabeceras vía `vercel.json`: `noindex, nofollow, noarchive, nosnippet` + `Referrer-Policy: no-referrer`.
- ⚠️ **Pública por URL.** Sin login: cualquiera con el link entra. Contiene precios y nombra a Cecilia → tratar como link privado.

## Diseño

Reutiliza el sistema de casa (paleta púrpura de las Brand Guidelines, oscuro con degradado violeta→magenta). Base tomada de la pieza de FAM (otro workspace/.../FAM_Finanzas_Amigables/06_docs/propuesta-web/`). Reveal on scroll, progress bar, print styles.
