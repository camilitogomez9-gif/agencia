# Recursos de la Academia — Claude Code + n8n

Bundle con los recursos prometidos en la clase de **Claude Code + n8n**. Todo autocontenido y
listo para compartir con los alumnos (podés zippear esta carpeta tal cual).

## Contenido

```
academia-recursos/
├── README.md                              # este archivo
├── skills/
│   └── versionar/SKILL.md                 # skill para versionar flujos y prompts
├── plantilla-workspace/
│   ├── .gitignore                         # ignora .env y credenciales (listo para usar)
│   ├── .env.example                       # plantilla de variables (solo placeholders)
│   └── clients/_template/                 # template de cliente COMPLETO (8 carpetas)
└── docs/
    └── n8n-claude-code-guia-alumno.md     # guía: las 3 ideas clave de la clase
```

## Cómo usar cada pieza

### 1. Guía del alumno (`docs/n8n-claude-code-guia-alumno.md`)
Empezá acá. Cubre las 3 ideas de la clase: (1) todo en n8n es JSON, (2) la mecánica copy-paste con
formato `{nodes, connections}`, (3) n8n y la carpeta viven en paralelo y se sincronizan a mano.

### 2. Skill `versionar` (`skills/versionar/SKILL.md`)
Automatiza el versionado: le pasás un flujo o prompt actualizado y guarda la versión anterior como
backup `-vN` mientras el archivo principal (sin sufijo) queda con lo nuevo.

**Instalar:** copiá la carpeta `versionar/` dentro de `.claude/skills/` de tu workspace:
```
cp -r skills/versionar TU_WORKSPACE/.claude/skills/
```
Luego se activa sola con frases como "versioná este flujo" o "guardá esta versión".

### 3. Plantilla de workspace (`plantilla-workspace/`)
- **`.gitignore`** — copialo a la raíz de tu workspace. Ya ignora `.env`, `.env.*` y
  `*-credentials.md`. Nunca subas secretos a git.
- **`.env.example`** — copialo a la raíz como base. Después: `cp .env.example .env` y reemplazá los
  placeholders por tus keys reales (el `.env` real nunca se comparte ni se sube).
- **`clients/_template/`** — template de cliente con las **8 carpetas** numeradas
  (`01_discovery` … `08_delivery`) incluyendo `03_workflows/` y `04_agents/`. Para un cliente nuevo:
  duplicá `_template/`, renombralo `[XXX]_NombreCliente` y completá `CLIENT_INFO.md`.

## Seguridad — importante
- El `.env.example` tiene **solo placeholders**. Nunca lo llenes con valores reales antes de
  compartirlo.
- Las API keys van en `.env` (protegido por `.gitignore`), nunca en el chat de Claude.
