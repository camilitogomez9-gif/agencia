# Guía técnica — Destrabar plantilla `seguimiento_ema_dia_10_3`

**Fecha:** 2026-09-19 · **Ejecuta:** la agencia con `VTR_META_WABA_TOKEN` vivo · **Tiempo estimado:** 30-60 min · **Bloqueante para:** cutover 26/9 (nice-to-have — el bot funciona in-session sin esta plantilla, ver `guia-recta-final-cutover-2026-09-16.md §16.1`).

> **Por qué necesita tratamiento especial.** Es la única de las 12 plantillas a migrar que tiene `HEADER format=IMAGE`. El `header_handle` original está atado al app del WABA de Rodrigo (id `141523652373940`) y **no es reusable** en el WABA del bot (id `1931874540684022`). Hay que descargar la imagen fuente + resubirla vía Meta Resumable Upload API al app del bot, obtener un nuevo `header_handle`, y armar el payload de template con ese handle nuevo. Las otras 11 plantillas se submitearon el 18/9 sin problema porque no tenían HEADER IMAGE (solo BUTTONS o BODY simple).
>
> **Referencias:** doc oficial Meta Resumable Upload API: <https://developers.facebook.com/docs/graph-api/guides/upload/> · docs WA Templates con media: <https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates/media-message-templates>.

---

## 0. Precondiciones

- [ ] **`VTR_META_WABA_TOKEN` seteado en `.env`** con scopes `whatsapp_business_management` + `whatsapp_business_messaging` sobre el App del WABA del bot. Token renovable en Graph API Explorer (dura ~2h).
- [ ] **App ID del WABA del bot** conocido — el que "posee" WABA `1931874540684022`. Se ve en Meta Business Manager → Apps → la app de la agencia/Venttur asociada al WABA del bot. **Anotar como `APP_ID_BOT` antes de empezar.**
- [ ] Directorio scratch disponible: `/tmp/vtr-ema-dia10-3/` (crear con `mkdir -p`).

---

## 1. Descargar la imagen fuente del handle vigente

La URL del handle actual (línea 808 del JSON `plantillas-meta-live-141523652373940-2026-09-17.json`):

```
https://scontent.whatsapp.net/v/t61.29466-34/455274687_560899806268814_3441258536977698721_n.jpg?ccb=1-7&_nc_sid=8b1bef&_nc_ohc=YfLJ_l2Pzv8Q7kNvwEyCByR&_nc_oc=AdpU3AE5J9SQZ8dARUU2zlm0wFk4etuvY8-3OAhJUWb7rOW1FdMk9BGOTmMcA_kLEyU&_nc_zt=3&_nc_ht=scontent.whatsapp.net&edm=AH51TzQEAAAA&_nc_gid=QafKhy0rSITS8Fm7toY6fw&_nc_tpa=Q5bMBQJMEQCmn-26X4-U8iRU5DSDkLzo9bYZI_JYtohiY0jrIoH8hyRFnHMAqwvcIFD_W0LZiLZeguHgVQ&oh=01_Q5Aa5gH_gIOeEhayJnMYV-GCAW9VM449xi6JraXkLl6VvqXQpQ&oe=6AD3FAF6
```

⚠️ El param `oe=6AD3FAF6` es la expiración del CDN. **Verificar que sigue vivo** antes de arrancar (ya pasó 1 día desde que el audit lo capturó — es un timestamp Unix pero no hex convencional; en la duda intentar el download y si falla pedir la imagen fuente a Erika/Mauricio).

```bash
mkdir -p /tmp/vtr-ema-dia10-3
cd /tmp/vtr-ema-dia10-3

# Paso 1a: intentar descargar del handle vigente
curl -sSL -o imagen.jpg 'https://scontent.whatsapp.net/v/t61.29466-34/455274687_560899806268814_3441258536977698721_n.jpg?ccb=1-7&_nc_sid=8b1bef&_nc_ohc=YfLJ_l2Pzv8Q7kNvwEyCByR&_nc_oc=AdpU3AE5J9SQZ8dARUU2zlm0wFk4etuvY8-3OAhJUWb7rOW1FdMk9BGOTmMcA_kLEyU&_nc_zt=3&_nc_ht=scontent.whatsapp.net&edm=AH51TzQEAAAA&_nc_gid=QafKhy0rSITS8Fm7toY6fw&_nc_tpa=Q5bMBQJMEQCmn-26X4-U8iRU5DSDkLzo9bYZI_JYtohiY0jrIoH8hyRFnHMAqwvcIFD_W0LZiLZeguHgVQ&oh=01_Q5Aa5gH_gIOeEhayJnMYV-GCAW9VM449xi6JraXkLl6VvqXQpQ&oe=6AD3FAF6'

# Verificar que se bajó y no es un HTML de error
ls -la imagen.jpg
file imagen.jpg   # debe decir "JPEG image data"
```

**Si el download falla o devuelve HTML/JSON de error:**
- Pedir la imagen fuente por WhatsApp a **Erika** (autora del flow EMA original) o **Mauricio**. Nombrar la búsqueda: "imagen del template `seguimiento_ema_dia_10_3` — el testimonio del video de SPE que se manda al día 10".
- Guardar la imagen recibida en `/tmp/vtr-ema-dia10-3/imagen.jpg`.

---

## 2. Resumable Upload API al app del WABA bot

Meta requiere 2 pasos para el Resumable Upload: (a) iniciar una sesión de upload, (b) subir el binario. El resultado del paso (b) es un `h` que es el `header_handle` que necesitamos para el template.

### 2.1 · Iniciar sesión de upload

```bash
# Setear variables (renombrar TOKEN y APP_ID según .env / Meta BM)
export APP_ID_BOT="TU_APP_ID_AQUI"   # ← poner el App ID del WABA del bot
FILE_SIZE=$(stat -f%z /tmp/vtr-ema-dia10-3/imagen.jpg)   # macOS
# En Linux sería: FILE_SIZE=$(stat -c%s /tmp/vtr-ema-dia10-3/imagen.jpg)

echo "File size: $FILE_SIZE bytes"

curl -s -X POST "https://graph.facebook.com/v20.0/${APP_ID_BOT}/uploads?file_name=seguimiento_ema_dia_10_3.jpg&file_length=${FILE_SIZE}&file_type=image/jpeg&access_token=${VTR_META_WABA_TOKEN}" | tee /tmp/vtr-ema-dia10-3/upload-session.json
```

**Respuesta esperada:**
```json
{"id": "upload:MTphdHRhY2h..."}
```

**Extraer el session ID:**
```bash
SESSION_ID=$(python3 -c "import json; print(json.load(open('/tmp/vtr-ema-dia10-3/upload-session.json'))['id'])")
echo "Session ID: $SESSION_ID"
```

### 2.2 · Subir el archivo binario

```bash
curl -s -X POST "https://graph.facebook.com/v20.0/${SESSION_ID}" \
  -H "Authorization: OAuth ${VTR_META_WABA_TOKEN}" \
  -H "file_offset: 0" \
  --data-binary "@/tmp/vtr-ema-dia10-3/imagen.jpg" | tee /tmp/vtr-ema-dia10-3/upload-result.json
```

**Respuesta esperada:**
```json
{"h": "4:aW1nLzE...="}
```

**Extraer el `h` (nuevo header_handle):**
```bash
HEADER_HANDLE=$(python3 -c "import json; print(json.load(open('/tmp/vtr-ema-dia10-3/upload-result.json'))['h'])")
echo "New header_handle: $HEADER_HANDLE"
```

⚠️ **Si el response NO tiene `h`:** posible causa (a) token sin scope suficiente, (b) App ID incorrecto, (c) archivo demasiado grande (Meta limita a 5MB para imagen). Debuguear antes de seguir.

---

## 3. Crear el template en el WABA del bot

Con el `HEADER_HANDLE` nuevo, armar el payload y submitearlo. El body y buttons son idénticos al original (línea 802-843 del JSON de referencia).

```bash
cat > /tmp/vtr-ema-dia10-3/template-payload.json <<EOF
{
  "name": "seguimiento_ema_dia_10_3",
  "language": "es_MX",
  "category": "MARKETING",
  "components": [
    {
      "type": "HEADER",
      "format": "IMAGE",
      "example": {
        "header_handle": ["${HEADER_HANDLE}"]
      }
    },
    {
      "type": "BODY",
      "text": "¡Hola {{1}}!\n\nSoy {{2}} nuevamente. 😊\n\nQuería compartir contigo un testimonio sobre cómo la metodología EMA para la busqueda y seleccion de escuelas en el extranjero, ayudó a estos estudiantes y sus familias a tener una experiencia que les cambió la vida. Creo que te será muy útil.\n\n¿Tienes algún tiempo esta semana para una breve llamada o reunión virtual? Me encantaría responder a todas tus dudas e inquietudes personalmente.\n\nSaludos,\n{{3}}",
      "example": {
        "body_text": [["Juan", "Mau", "Mau"]]
      }
    },
    {
      "type": "BUTTONS",
      "buttons": [
        {"type": "URL", "text": "Volver a Ver el Video", "url": "https://promo.venttur.com/entrenamientospe"},
        {"type": "URL", "text": "Agendar Asesoría Gratuita", "url": "https://promo.venttur.com/SPEagendar"},
        {"type": "QUICK_REPLY", "text": "¡Quiero Más Información!"}
      ]
    }
  ]
}
EOF

# Submit
curl -s -X POST "https://graph.facebook.com/v20.0/1931874540684022/message_templates" \
  -H "Authorization: Bearer ${VTR_META_WABA_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @/tmp/vtr-ema-dia10-3/template-payload.json | tee /tmp/vtr-ema-dia10-3/submit-result.json
```

**Respuesta esperada (exitosa):**
```json
{"id": "1234567890", "status": "PENDING", "category": "MARKETING"}
```

**Errores posibles:**
- `#100 · Invalid header_handle format` → paso 2 falló o pasó el string entero mal formado. Re-generar `HEADER_HANDLE`.
- `#100 · Template name already exists` → ya existe. Chequear con `GET /1931874540684022/message_templates?name=seguimiento_ema_dia_10_3`.
- `#131009 · Parameter value is not valid` → probablemente `promo.venttur.com` sigue rechazado por Meta (si el dominio nuevo ya se decidió, cambiar las URLs de los buttons antes de submit).

---

## 4. Actualizar el log

Editar `clients/VTR_Venttur/06_docs/submit-templates-log.json` para agregar la entrada:

```json
"seguimiento_ema_dia_10_3|es_MX": {
  "ts": "2026-09-XX...",
  "id": "1234567890",
  "status": "PENDING",
  "http": 200,
  "note": "submit via Resumable Upload API — HEADER IMAGE requiere handle nuevo, ver guia-destrabar-seguimiento-ema-dia-10-3.md"
}
```

Y actualizar `last_run` al timestamp actual.

---

## 5. Verificar aprobación (24-72h)

```bash
# Poll cada ~2h el estado de la plantilla
curl -s "https://graph.facebook.com/v20.0/1931874540684022/message_templates?fields=name,status,category&access_token=${VTR_META_WABA_TOKEN}" | jq '.data[] | select(.name == "seguimiento_ema_dia_10_3")'
```

Cuando pase de `PENDING` a `APPROVED`, actualizar el log.

**Si queda `REJECTED`:** Meta suele dar razón en el response detallado (`GET /{template_id}?fields=name,status,rejected_reason`). Iterar sobre el motivo.

---

## 6. Cleanup

```bash
rm -rf /tmp/vtr-ema-dia10-3/
```

La imagen queda como referencia en el `header_handle` del template — no necesita persistir localmente.

---

## Referencias

- JSON fuente del template original: `06_docs/plantillas-meta-live-141523652373940-2026-09-17.json` líneas 797-846
- Documento hermano (aviso al equipo): `06_docs/plantillas-waba-rodrigo-a-reaprobar-2026-09-18.md` líneas 232-254
- Log de submits: `06_docs/submit-templates-log.json`
- Script relacionado (submit sin HEADER IMAGE): `scripts/utilities/submit-vtr-templates-to-bot-waba.py`
- Doc oficial Meta Resumable Upload: <https://developers.facebook.com/docs/graph-api/guides/upload/>
- Doc oficial WA Media Templates: <https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates/media-message-templates>
