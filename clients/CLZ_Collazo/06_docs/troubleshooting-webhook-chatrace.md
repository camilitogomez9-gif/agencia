# Troubleshooting — Agente no responde desde Chatrace

**Síntoma:** El mensaje llega a Chatrace pero el agente no se activa (n8n no ejecuta).

---

## Arquitectura del flujo

```
Chatrace → POST webhook n8n → If (¿Pregunta no vacía?) → Agente IA → OpenAI formateador → Respond to Webhook → Chatrace
```

**URL del webhook (producción):**
```
https://[TU-INSTANCIA-N8N]/webhook/493982f2-6ca9-4ab5-ba04-28643183ea3a
```

**Payload esperado (form-urlencoded):**
| Campo | Valor | Notas |
|-------|-------|-------|
| `Pregunta` | Mensaje del usuario | **P mayúscula — crítico** |
| `user_id` | ID del contacto en Chatrace | |
| `full_name` | Nombre del contacto | |
| `Telefono` | Teléfono del contacto | Opcional |

---

## Check 1 — ¿El workflow está activo en n8n?

**Por qué importa:** Si el workflow no está activado, n8n solo responde a la URL de
*test* (`/webhook-test/...`), no a la de producción (`/webhook/...`). El mensaje de
Chatrace llegaría a una URL que devuelve 404 y no ejecuta nada.

**Cómo verificar:**
1. Abrir el workflow en n8n
2. Confirmar que el toggle superior derecho dice **Active** (verde)
3. Si está inactivo → activarlo

**URL de test (solo para pruebas manuales en n8n):**
```
https://[TU-INSTANCIA-N8N]/webhook-test/493982f2-6ca9-4ab5-ba04-28643183ea3a
```

---

## Check 2 — ¿Chatrace está enviando a la URL correcta?

**Cómo verificar:**
1. En Chatrace → External Request configurado para este flow
2. Confirmar que la URL sea exactamente:
   ```
   https://[TU-INSTANCIA-N8N]/webhook/493982f2-6ca9-4ab5-ba04-28643183ea3a
   ```
3. Método: **POST**
4. Content-Type: **application/x-www-form-urlencoded** (no JSON)

---

## Check 3 — ¿El campo `Pregunta` llega con P mayúscula?

**Por qué es crítico:** El nodo `If` en n8n evalúa exactamente `$json.body.Pregunta`
(P mayúscula). Si Chatrace envía `pregunta` en minúscula, la condición da `false` y
el flujo termina en silencio sin ejecutar el agente.

**Cómo verificar:**
1. En Chatrace → External Request → ver el cuerpo del request
2. El campo debe llamarse `Pregunta` (no `pregunta`, no `PREGUNTA`)
3. Si está en minúscula → corregir el nombre del campo en Chatrace

**Consecuencia si falla:** n8n recibe el request (aparece en el log de ejecuciones)
pero el agente nunca se activa porque el `If` no tiene rama `false` conectada.

---

## Check 4 — ¿Aparecen ejecuciones en n8n?

Este check distingue entre dos problemas distintos:

**A) No aparece NINGUNA ejecución en n8n:**
→ El problema es de red o URL. Chatrace no está llegando al webhook.
→ Revisar Check 1 y Check 2.

**B) Aparecen ejecuciones pero el agente no responde:**
→ El problema está dentro del flujo. El request llega pero algo falla después.
→ Revisar Check 3 (campo Pregunta) o Check 5 (credenciales).

**Cómo ver el log:**
1. n8n → menú izquierdo → Executions
2. Filtrar por el workflow `[Collazo]`
3. Ver el status de cada ejecución (Success / Error / Waiting)

---

## Check 5 — ¿Las credenciales de OpenAI y Postgres están activas?

Si las ejecuciones aparecen pero terminan en error:

1. En n8n → Credentials
2. Verificar que `OpenAI | Collazo` (id: `acG9u3QTjVmvzcGO`) esté válida
3. Verificar que la credencial Postgres `Collazo` (id: `HRV9xsfYlr934XEB`) esté válida
4. Hacer click en "Test" en cada credencial para confirmar conexión

---

## Check 6 — Prueba directa del webhook (bypass Chatrace)

Para aislar si el problema es de Chatrace o de n8n, probar el webhook directamente:

```bash
curl -X POST "https://[TU-INSTANCIA-N8N]/webhook/493982f2-6ca9-4ab5-ba04-28643183ea3a" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Pregunta=Hola+necesito+ayuda&user_id=59899834794&full_name=Test"
```

**Resultado esperado:** n8n ejecuta el agente y devuelve un JSON con `parte1`, `parte2`, `parte3`.

- Si el curl funciona y Chatrace no → el problema está en la configuración de Chatrace
- Si el curl también falla → el problema está en n8n (workflow inactivo o error interno)

---

## Árbol de diagnóstico rápido

```
¿Aparecen ejecuciones en n8n?
├── NO → ¿El workflow está activo?
│         ├── NO → Activar el workflow (Check 1)
│         └── SÍ → URL incorrecta en Chatrace (Check 2)
│
└── SÍ → ¿La ejecución muestra error?
          ├── SÍ → Ver el nodo que falla en la ejecución
          │         → Probablemente credenciales (Check 5)
          └── NO (ejecución exitosa pero sin respuesta)
                → El If devuelve false → campo Pregunta mal escrito (Check 3)
```

---

## Causa más frecuente

En la mayoría de los casos el problema es el **Check 3**: el campo se llama `pregunta`
(minúscula) en el payload de Chatrace y el `If` no lo reconoce. El flujo ejecuta pero
termina silenciosamente porque no hay rama `false` conectada.
