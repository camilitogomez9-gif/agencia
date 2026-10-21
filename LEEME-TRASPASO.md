# Traspaso del workspace de la agencia

Esta es una copia limpia del workspace, **sin historial de git** y depurada de la identidad del dueño anterior. De acá en adelante, la fuente de verdad es este repo.

## Qué incluye
- Todos los clientes de la agencia (`clients/`), con sus docs, prompts versionados, workflows y testing.
- La infraestructura del workspace: `_core/` (estándares y plantillas), `scripts/`, `.claude/skills/`, `workflows/`, `testing/`, `docs/`, `ops/` y `salidas/`.
- `CLAUDE.md` y `AGENTS.md`, depurados.

## Qué NO incluye (a propósito)
- **Paso a Paso (PAP):** no forma parte del traspaso.
- **Credenciales:** no hay `.env`, `*-credentials.md` ni `export-secrets.json`. Las claves que estaban escritas en los workflows se reemplazaron por `<REDACTED>` o `[REDACTED_TOKEN]`. Las credenciales se pasan aparte y de forma segura.
- **Datos personales crudos de clientes:** contactos, oportunidades, CSV de leads y exports de CRM (sobre todo de VTR, HPF y CLZ). **No están en este repo para que no lleguen a GitHub.** Se entregan aparte en `agency-camilo-datos.zip`. Ese zip no se sube a ningún repo.
- **Facturas emitidas por el dueño anterior** (CLZ) y un PDF de TFO con la marca anterior grabada. El `.md` de origen de ese PDF sí está.

## Cosas a resolver
1. **Regenerar las claves.** Las que estaban escritas en los workflows **siguen activas en los servidores** aunque acá estén tapadas: OpenAI, Notion, Google y Kommo (HPF). Regeneralas y cargá las nuevas en tus credenciales de n8n.
2. **Dominio de los links de VTR.** Algunos workflows de VTR todavía tienen el dominio de links anterior (en producción). Si migrás a un dominio propio, actualizalo en esos workflows.
5. **Placeholders.** Hosts, cuentas y IDs internos se reemplazaron por marcadores como `[TU-INSTANCIA-N8N]`, `[TU-DOMINIO]`, `[EMAIL-AGENCIA]` o `[AIRTABLE_BASE_ID]`. Los workflows exportados son referencia: antes de reimportar uno, reemplazá esos marcadores.
3. **VPS.** Varios clientes siguen alojados en los servidores anteriores. Hay que completar la migración que tenías en curso.
4. **Hooks de Claude Code** (`.claude/settings.json`): hay auto-commit con `git add -A` en cada edición. Antes del primer uso revisá que `.gitignore` cubra todo lo que no tiene que entrar al repo.
