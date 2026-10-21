# la agencia — Workspace

Workspace operativo de la agencia. Organizado como agencia de IA: recursos compartidos reutilizables en `_core/`, proyectos de clientes en `clients/`, e infraestructura interna en `salidas/`.

## Estructura

```
.
├── _core/          # Templates, prompts, estándares — reutilizables entre clientes
├── clients/        # Un directorio por cliente (IMP_, SNR_, ...)
├── agents/         # Agentes IA propios de la agencia
├── workflows/      # Workflows n8n por integración y nicho
├── docs/           # Documentación interna, ADRs, runbooks
├── ops/            # Procesos del ciclo de vida de clientes
├── testing/        # QA, sandbox, bug reports
├── scripts/        # utilities/ y generators/
├── contexto/       # Contexto de negocio para Claude Code
└── salidas/        # Herramientas internas activas
```

## Convención de nombres

| Tipo | Formato | Ejemplo |
|------|---------|---------|
| Clientes | `[XXX]_Nombre` | `IMP_ImportadoresConectados` |
| Workflows n8n | `WF_[NICHE]_[FUNCION]_v[N]` | `WF_DENTAL_LeadCapture_v1` |
| Agentes IA | `AGT_[FUNCION]_v[N]` | `AGT_Booking_v2` |
| Prompts | `PRM_[ROL]_[NICHE]_v[N]` | `PRM_QualificationBot_Dental_v2` |
| Módulos | `MOD_[INTEGRACION]_[FUNCION]` | `MOD_WA_SendMessage` |

Ver `_core/standards/naming_conventions.md` para el diccionario completo.

## Flujo de trabajo estándar

Discovery → Architecture → Build → Test → Delivery → Iteration

## Inicio rápido — Nuevo cliente

1. Duplicar `clients/_template/` → renombrar con `[XXX]_NombreCliente`
2. Completar `CLIENT_INFO.md`
3. Completar `01_discovery/discovery_form.md`
4. Copiar workflows base de `_core/templates/workflows/`
5. Adaptar y testear en `testing/sandbox/`

## Clientes activos

| ID | Cliente | Status |
|----|---------|--------|
| IMP | Importadores Conectados | live |
| SNR | Sonrisas | live |

## Inicio de sesión Claude Code

```
/iniciar
```

Ver [CLAUDE.md](./CLAUDE.md) para contexto completo.
