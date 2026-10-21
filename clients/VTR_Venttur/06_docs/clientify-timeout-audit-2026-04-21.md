# Auditoría incidente Clientify timeout — 2026-04-21

## Contexto

Workflow webhook de landing que:

1. Recibe `nombre`, `apellidos`, `telefono` y `programa`.
2. Normaliza datos.
3. Hace upsert del lead en Airtable.
4. Crea contacto en Clientify.
5. Guarda `ID Clientify` en Airtable.
6. Etiqueta el contacto en Clientify.
7. Notifica ejecución o error por Telegram.

Error reportado:

```text
NodeApiError: Gateway timed out - perhaps try again later?
```

El stack trace corresponde a un nodo `HTTP Request` de n8n. En este workflow los únicos nodos de ese tipo son los llamados a Clientify.

## Diagnóstico

El error es un 504 Gateway Timeout devuelto durante una llamada HTTP a Clientify. No parece ser un error de expresión de n8n ni de Airtable.

Riesgos detectados:

- `Crear Contacto Clientify` no tiene salida de error configurada. Si ese nodo falla, el flujo se corta antes de llegar al Telegram de error.
- Ambos HTTP Request a Clientify dependen de una API externa sin retries explícitos.
- El token de Clientify está hardcodeado en los headers. Debe rotarse y moverse a credenciales o variables de entorno.
- El payload de creación manda un campo `id` con un string compuesto por programa y teléfono. En Clientify el `id` del contacto es un entero generado por la API; usarlo como campo externo puede causar rechazos o comportamiento no esperado.
- El flujo no es idempotente: cada ejecución intenta crear un contacto nuevo en Clientify antes de verificar si ya existe.
- La normalización de teléfono solo elimina el primer `+`; no limpia espacios, guiones, paréntesis u otros caracteres.

## Fix mínimo recomendado

1. Rotar el token expuesto de Clientify.
2. Reemplazar el header hardcodeado por `Token {{$env.CLIENTIFY_API_TOKEN}}` o una credencial n8n.
3. Agregar a `Crear Contacto Clientify`:
   - `onError: continueErrorOutput`
   - `retryOnFail: true`
   - 3 intentos
   - espera de 5 a 10 segundos entre intentos
   - timeout explícito de 15 a 30 segundos
4. Conectar la salida de error de `Crear Contacto Clientify` a `Mensaje de error`.
5. Agregar retries y timeout también a `Etiquetar Contacto`.
6. Quitar el campo `id` del body de creación en Clientify.

## Fix robusto recomendado

Reestructurar la rama Clientify:

1. `GET /v1/contacts/?phone=<telefono>` para buscar contacto existente.
2. IF existe:
   - usar el `id` existente.
3. IF no existe:
   - `POST /v1/contacts/` con `first_name`, `last_name`, `phone`, `contact_source` y/o campos personalizados.
4. `POST /v1/contacts/:contact_id/tags/` para aplicar etiqueta.
5. Actualizar Airtable con el `ID Clientify`.

Esto evita duplicados y hace seguro reintentar cuando Clientify devuelve 504.

## Prioridad

Alta. El timeout puede ser transitorio, pero el diseño actual puede generar ejecuciones incompletas, duplicados o falta de notificación cuando falla el primer request a Clientify.
