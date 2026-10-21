# Plan de rotación de secretos — VTR (2026-09-11)

> **Para qué:** los secretos (keys/tokens) están hardcodeados o en credenciales que se filtraron a exports. Hay que rotarlos antes del cutover. Este plan dice **exactamente dónde vive cada uno** y **en qué orden rotarlo sin romper producción**.
>
> **Regla de oro (para no cortar el bot vivo):** para cada secreto → **1)** generar el nuevo, **2)** actualizarlo en todos lados, **3)** probar que el sistema sigue andando, **4)** RECIÉN AHÍ revocar/invalidar el viejo. Nunca revocar el viejo antes de confirmar que el nuevo funciona.

---

## Inventario (dónde vive cada secreto)

| Secreto | Dónde vive | ¿Vivo post-cutover? | Prioridad | Quién |
|---|---|---|---|---|
| **OpenAI key** | Credencial n8n `ibkhdCMyhr3yqDQk` ("OpenAI \| Venttur"). La usan el agente vivo + staging + correo semanal. | Sí (el agente sigue con OpenAI) | 🔴 ALTA | Camilo |
| **Tokens Meta CAPI** (uno por programa) | Tabla Airtable **"Programas CAPI"** (`access_token`), texto plano. Los lee el workflow CAPI en runtime. | **Sí (el CAPI sobrevive)** | 🔴 ALTA | Cliente (Meta BM) + Camilo |
| **Token ManyChat** (`Bearer 3256256:…`) | **Hardcodeado** en nodos HTTP de: `[Venttur]` main (`k3aivKSP67S97IHn`), `Confirmación de agenda`, `Resumen etiquetas seguimientos`, `Seguimiento agenda`. ~26 nodos. | **No** (muere con ManyChat en el cutover) | 🟡 MEDIA | Camilo |
| **Token Clientify** | En los workflows de Clientify (`Crear contacto Clientify`, `Formulario Clientify`, `Actualizar link enviado`, etc.). Verificar si es credencial o hardcodeado. | **No** (muere con Clientify) | 🟢 BAJA | Camilo |
| **GHL PIT** (`YkVmaA4jlRbO1TQD` "GHL VTR (PIT)" + `iVwUlPpQHp1SArJY`) | Credencial n8n; los scripts lo leen de un archivo externo (no hardcodeado). No se filtró. | Sí | ⚪ Opcional (solo si se sospecha compromiso) | Camilo |

---

## Orden de rotación (de más a menos urgente)

### 1. 🔴 OpenAI key — la más importante (y la más fácil)

**Por qué:** es una key **viva y funcionando** que quedó en exports. El agente productivo la usa.

**Es fácil porque está en UNA credencial**, no hardcodeada en los workflows.

Pasos:
1. **Generar** una key nueva en `platform.openai.com` → API keys → Create new secret key. Copiala.
2. En **n8n** → Settings → **Credentials** → abrir **"OpenAI | Venttur"** (`ibkhdCMyhr3yqDQk`) → pegar la key nueva → Save.
   - Con esto quedan cubiertos **todos** los nodos que usan esa credencial (agente vivo, staging, correo semanal).
3. **Verificar (nodo hardcodeado de audio):** abrir el nodo de transcripción de audio (Whisper) del main vivo. Si tiene la key pegada en el header `Authorization` (en vez de usar la credencial) → cambiarla también por la nueva, o mejor: apuntarlo a la credencial `OpenAI | Venttur`.
4. **Probar:** mandar un mensaje al bot vivo (o ejecutar el agente) y confirmar que responde. Probar también un audio si aplica.
5. **Recién ahí:** en OpenAI, **revocar la key vieja** (`sk-proj-OpKR…`). Si algo dejó de andar, NO revocar: falta un lugar.

---

### 2. 🔴 Tokens de Meta (CAPI) — sobreviven al cutover

**Por qué:** están en **texto plano** en la tabla Airtable "Programas CAPI", y el CAPI **sigue vivo** después del cutover. Es el secreto que más importa a largo plazo.

**Necesita al cliente** (los tokens se generan en el Business Manager de Meta de Venttur).

Pasos:
1. **Cliente/Meta:** por cada pixel/programa, generar un **System User token** nuevo en Meta Business (Business Settings → System Users → Generate token, con permiso del pixel).
2. **Airtable:** reemplazar el `access_token` viejo por el nuevo en la tabla **"Programas CAPI"** (una fila por programa).
3. **Probar:** disparar un evento de prueba del CAPI (con `test_event_code` de Meta → Events Manager → Test Events) y confirmar que llega.
4. **Recién ahí:** revocar los tokens viejos en Meta.

> Ojo: el archivo `programas-capi.csv` (con los tokens viejos en texto plano) quedó **fuera de git** (gitignored). Igual conviene borrarlo de Descargas cuando termine la rotación.

---

### 3. 🟡 Token ManyChat — muere en el cutover

**Por qué baja prioridad:** ManyChat se apaga en el cutover, así que el token se invalida solo. Rotarlo ahora = editar ~26 nodos hardcodeados, mucho laburo para algo que muere.

**Recomendación:** **no rotarlo manualmente**; simplemente, **al hacer el cutover, revocar el token en ManyChat** (Settings → API) para invalidarlo. Si por algún motivo ManyChat va a seguir vivo semanas, ahí sí conviene: generar token nuevo + reemplazarlo en los 4 workflows (main, confirmación, resumen, seguimiento).

---

### 4. 🟢 Token Clientify — muere con Clientify

Igual que ManyChat: se invalida solo al descomisionar Clientify. **Al cutover, revocar el token en Clientify.** No amerita rotación manual antes.

---

### 5. ⚪ GHL PIT — opcional

No se filtró (los scripts lo leen de un archivo externo, no está hardcodeado). Rotar **solo si se sospecha que se comprometió**. Si se rota: regenerar el Private Integration token en GHL → actualizar las credenciales n8n `GHL VTR (PIT)` (`YkVmaA4jlRbO1TQD`) y `GHL Venttur Header Auth` (`iVwUlPpQHp1SArJY`).

---

## Checklist

- [ ] **OpenAI:** key nueva → credencial `OpenAI | Venttur` actualizada → nodo de audio verificado → bot probado → key vieja revocada
- [ ] **Meta CAPI:** [cliente] tokens nuevos → Airtable "Programas CAPI" actualizada → evento de prueba OK → tokens viejos revocados → borrar `programas-capi.csv` de Descargas
- [ ] **ManyChat:** revocar token en el cutover (o rotar en los 4 workflows si ManyChat sigue vivo)
- [ ] **Clientify:** revocar token en el cutover
- [ ] **GHL PIT:** (solo si se sospecha compromiso)

---

## Notas

- El único secreto que exige tocar **producción viva** con cuidado es el de **OpenAI** (paso 1). Los demás son de servicios que mueren (ManyChat/Clientify) o dependen del cliente (Meta).
- Todo el trabajo de rotación es de Camilo (+ cliente para Meta). Esta guía es el mapa; ejecutar cuando haya cabeza, siguiendo la regla de oro (probar antes de revocar).
