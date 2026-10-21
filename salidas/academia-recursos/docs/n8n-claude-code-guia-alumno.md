# Claude Code + n8n — Guía del alumno

Esta guía cubre lo esencial para trabajar n8n desde Claude Code. Son **3 ideas**. Si te llevás
solo estas 3, ya podés operar mucho más rápido.

---

## Idea 1 — Todo en n8n es código (JSON)

Lo que ves en n8n como **nodos, cables y ejecuciones** es la interpretación visual de un **código
en formato JSON**. n8n es una aplicación que lee ese JSON y te lo dibuja para que interactúes.

- **Cada flujo es un JSON.**
- **Cada nodo es un JSON.**

¿Por qué importa? Porque **Claude maneja código con excelencia**. Si un flujo es código y Claude
entiende código, entonces Claude puede leer, analizar, corregir y crear flujos de n8n. Para esto
usá el modelo **Sonnet** (maneja texto y código sobrado, sin gastar créditos de más).

---

## Idea 2 — La mecánica clave: copiar y pegar entre n8n y Claude

Esta es **LA** mecánica que desbloquea todo. Va en los dos sentidos.

### De n8n → Claude
1. En n8n, seleccioná uno o varios nodos (o un flujo entero con Cmd/Ctrl+A).
2. Copiá con **Cmd/Ctrl+C**.
3. Pegá en el chat de Claude con **Cmd/Ctrl+V**.

Lo que se pega es el JSON con esta forma:

```json
{
  "nodes": [ { ...nodo A... }, { ...nodo B... } ],
  "connections": { ...cómo se cablean entre sí... }
}
```

No solo trae los nodos: trae **las conexiones** (cómo se relacionan). Con eso, Claude puede
"describime este flujo", "depurá este flujo y detectá errores/redundancias/fallas", "corregí este
nodo", etc.

### De Claude → n8n
1. Pedile a Claude un nodo o un flujo (ej: "dame el nodo HTTP corregido, con `nodes`").
2. Claude te devuelve un **bloque de código JSON**.
3. Copiá ese bloque y, parado en el canvas de n8n (clic en el vacío), pegá con **Cmd/Ctrl+V**.
   El nodo/flujo aparece cableado.

> ⚠️ **Formato obligatorio para pegar en n8n:** el JSON tiene que venir envuelto en
> `{ "nodes": [...], "connections": {...} }`. Si Claude te devuelve el objeto del nodo "pelado"
> (sin ese envoltorio), **n8n no lo pega**. Si te pasa, pedíselo de nuevo: "dámelo con el formato
> `nodes` y `connections` para pegar".

**Por qué esto le gana a hacerlo a mano o por MCP:** es instantáneo, no consume créditos extra, y
no requiere configurar la conexión MCP (que además tiene pasos, permisos y a veces se rompe). Para
el 90% del trabajo diario, copiar/pegar es lo más rápido.

---

## Idea 3 — n8n y tu carpeta viven en paralelo (y los sincronizás a mano)

Esta es la parte que más confunde al principio. La regla es simple:

| | Qué es | Fuente de verdad de… |
|---|---|---|
| **n8n** | Donde el flujo corre de verdad | **Producción** (lo que está vivo) |
| **Tu carpeta en Claude** | Copia de trabajo + historial de versiones | Tu **trabajo y tus backups** |

Son **dos espacios separados**. Un cambio en uno **no** se refleja automáticamente en el otro.

- Si tocás algo en **n8n** → para que quede en tu carpeta, lo descargás/copiás y le decís a Claude
  "actualizá la última versión de este flujo".
- Si Claude edita el **archivo** → para que corra, copiás el JSON y lo pegás en n8n.

> **Modelo mental (de Juan Pablo):** n8n es la **mano de obra** (ejecuta), Claude es la **mente
> maestra** (piensa y planifica). Dos cabezas piensan mejor que una — pero las mantenés en sincronía
> vos, con una línea, cuando hace falta.

**No te obsesiones con tenerlo sincronizado al milímetro todo el tiempo.** En la práctica: cuando
terminás un bloque de cambios, sincronizás. Con el uso se vuelve automático.

### Por qué conviene tener los flujos en la carpeta
- **Contexto completo:** si Claude tiene todos los flujos de un cliente, podés decir "está fallando
  la creación de citas, analizá los flujos y encontrá dónde" — sin pegarle nada, ya tiene todo.
- **Crear desde cero más rápido:** con el contexto de flujos anteriores (seguimientos, Supabase,
  Airtable…), pedís "creá un flujo de seguimiento para este cliente nuevo" y sale muy afinado.

---

## Cómo se estructura la carpeta

```
clients/
└── [XXX]_NombreCliente/
    ├── 01_discovery/      # relevamiento inicial
    ├── 02_architecture/   # arquitectura
    ├── 03_workflows/      # ← los JSON de los flujos de n8n
    ├── 04_agents/         # ← los system prompts de los agentes
    ├── 05_crm/            # CSVs / esquemas de Airtable, etc.
    ├── 06_docs/           # documentación
    ├── 07_testing/        # guías de testing
    ├── 08_delivery/       # entregables
    └── CLIENT_INFO.md
```

Las dos carpetas que más usás para n8n:
- **`03_workflows/`** → cada flujo del n8n de ese cliente, como archivo `.json`.
- **`04_agents/`** → los **system prompts** de los agentes que viven en esos flujos.

### ¿Por qué el system prompt va aparte, si ya está dentro del flujo?
Porque Claude (como cualquier LLM) tiende a tomar atajos: si le pasás el flujo entero para
analizarlo, a veces **saltea** el system prompt (que es la parte más delicada). Teniéndolo en un
archivo propio en `04_agents/`, te asegurás de poder trabajarlo con foco y versionarlo aparte.

### Cómo cargar la carpeta por primera vez
Si el cliente ya tiene flujos en n8n: descargalos, pasáselos a Claude y decile "guardá estos flujos
en la carpeta `03_workflows/` de [cliente]". Lo mismo con los prompts en `04_agents/`.
Si la carpeta no existe, pedile "creá la carpeta del cliente y guardá esto ahí".

---

## Versionado (la red de seguridad)

Convención:
- **Archivo principal sin sufijo** = última versión. Ej: `agente-collazo-system-prompt.md`.
- **Backups con sufijo `-vN`** = versiones congeladas. Ej: `-v1.md`, `-v2.md`, `-v3.md`.

Cuando guardás una versión nueva, la anterior se congela como `-vN` y el principal queda con lo
nuevo. Si algo sale mal, volvés atrás copiando el backup sobre el principal. Esto te salva de
rehacer trabajo cuando un cliente pide deshacer un cambio.

> Usá la **skill `versionar`** de este bundle para automatizarlo: le pasás el flujo/prompt
> actualizado y ella guarda el backup + actualiza el principal sola.

**Tip:** no crees una versión nueva por cada cambio chico. Iterá sobre la misma hasta que el cambio
esté estable / pase a producción, y recién ahí bumpeás a una versión nueva.

---

## Seguridad: dónde van las API keys

Nunca pongas API keys ni tokens en el chat (quedan expuestas). Se guardan en el archivo **`.env`**
de la carpeta de trabajo, que está protegido por **`.gitignore`** (nunca se sube a git).

- **`.gitignore`** lista todo lo que git debe ignorar (incluye `.env` y `*-credentials.md`).
- **`.env`** (de *environment*, entorno) guarda las variables sensibles.
- **`.env.example`** es la plantilla con placeholders que **sí** se comparte (sin valores reales).

**Cómo agregar una key nueva sin exponerla:** pedile a Claude "creá el placeholder en el `.env`
para tal key" y después **abrí el archivo vos** y reemplazás el placeholder por la key real. Así
editás el archivo directo y la key nunca pasa por el chat.

Para chequear que está bien protegido: pedile a Claude "confirmá que el `.env` está dentro del
`.gitignore` y no se está publicando".
