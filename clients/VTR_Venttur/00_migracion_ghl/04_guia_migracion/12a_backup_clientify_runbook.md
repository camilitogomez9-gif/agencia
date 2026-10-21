# 12a · Runbook operativo — Respaldo Clientify pre-cutover

**Ventana:** entre 22/9 (T-4) y 25/9 (T-1) · **Punto de no retorno:** 27/9 EOD (Clientify caduca) · **Ejecuta:** la agencia (la agencia o Camilo) con credenciales de Mauricio + Rodrigo + Andrés.

> **Por qué existe este runbook.** El aviso al cliente (`06_docs/clientify-que-respaldar-antes-de-apagar.md`) le pide que ellos respalden 3 cosas por su cuenta. **Como ya tenemos las 3 credenciales**, lo ejecutamos nosotros para no depender de que hagan clicks. Este doc es el paso a paso técnico interno — no se comparte con el cliente.
>
> Complementa `12_cutover.md §09` (que solo lista qué respaldar en 1 línea cada cosa). Acá está el cómo.

---

## 0. Precondiciones

- [ ] Credenciales Clientify de **Mauricio** (dueño), **Rodrigo** y **Andrés** — ya en `06_docs/clientify-credentials.md` (gitignored).
- [ ] Path destino creado: `mkdir -p clients/VTR_Venttur/00_migracion_ghl/05_ejecucion/backup-clientify-2026-09/`.
- [ ] `.gitignore` cubre `backup-clientify-*/` — verificar (contiene PII: emails, teléfonos, adjuntos con posibles docs de menores para Boarding School).
- [ ] Espacio libre: estimado ~500MB-2GB (contactos + conversaciones + adjuntos). Verificar disco.

---

## 1. Los 7 elementos a respaldar

### 1.1 · Contactos (CSV export)

**Qué:** las ~7.000 filas de contactos (5.000 leads históricos + ~2.000 nuevos), con toda su timeline y custom fields.

**Cómo:**
1. Login en Clientify con cuenta de **Mauricio** (dueño, tiene visibilidad total sobre todos los asesores).
2. `Contactos` → `Lista completa` → filtro "Todos" (sin filtro).
3. `Exportar` → CSV completo con todos los campos.
4. Guardar como `01-contactos-export-YYYY-MM-DD.csv` en el path destino.

**Verificar:** conteo de filas ≥ 6.500 (baseline conocido). Si es <5.000, algo salió mal.

**Estimado:** 10-20 min (Clientify puede tardar en generar el export para 7k filas + email de aviso cuando esté listo).

---

### 1.2 · Chats / conversaciones (los últimos 60 días abiertos)

**Qué:** las conversaciones activas de los últimos 60 días con adjuntos incluidos. El histórico completo (todos los chats) es demasiado pesado y no se necesita — se preserva solo lo caliente.

**Cómo:**
1. En Clientify: `Inbox` o `Conversaciones`.
2. Filtro: "Últimos 60 días" + "Con mensajes intercambiados".
3. Para cada conversación abierta:
   - Copiar el hilo completo a texto (o screenshot si Clientify no exporta hilos)
   - Guardar cada uno en `02-chats/conversacion-{contact_id}-{fecha_ultimo_mensaje}.txt`
4. Adjuntos: si el UI de Clientify permite descargarlos, bajarlos a `02-chats/adjuntos/{contact_id}/`.

**Verificar:** al menos las 30-50 conversaciones más recientes están capturadas.

**Estimado:** 30-90 min dependiendo del volumen. **Si son >100 conversaciones activas, priorizar las últimas 60 y documentar el corte.**

---

### 1.3 · Automatizaciones activas (screenshots + JSON export si aplica)

**Qué:** las secuencias/automatizaciones vivas en Clientify (probablemente los 2 flows de confirmación de cita + recordatorios que se apagan al migrar).

**Cómo:**
1. `Automatización` (o el módulo equivalente en el plan actual).
2. Para cada automatización activa:
   - Screenshot del diagrama de flujo completo
   - Si Clientify tiene "Exportar JSON" → bajarlo
   - Guardar como `03-automatizaciones/automatizacion-{nombre_slug}-{fecha}.png` + `.json`
3. Documentar en `03-automatizaciones/README.md`: nombre, trigger, acciones, contactos que impacta.

**Verificar:** todas las automatizaciones que estaban STOP + las ACTIVE están capturadas.

**Estimado:** 30 min si son <10 automatizaciones.

---

### 1.4 · Landing pages de aventureras (HTML + assets)

**Qué:** las ~100-125 landings de aventureras (una por combinación aventurera × programa). Se descargan en HTML por si el rediseño en GHL toma más tiempo o si el hidden field mechanism (§07 del runbook cutover) falla y necesitamos las landings viejas como fuente de contenido.

**Cómo:**
1. Extraer la lista completa de URLs `promo.venttur.com/*` del inventario ya capturado en `landings y calendarios/{Mauricio,Andrés,Max}/landings.md`.
2. Ejecutar:
   ```bash
   cd clients/VTR_Venttur/00_migracion_ghl/05_ejecucion/backup-clientify-2026-09/04-landings/
   # Opción A: wget mirror (si Clientify sirve las landings públicamente):
   wget --mirror --convert-links --adjust-extension --page-requisites --no-parent \
        --restrict-file-names=windows \
        -i lista-urls-landings.txt
   # Opción B: curl por URL individual guardando HTML + assets a mano
   ```
3. Verificar que se bajaron los CSS/JS/imágenes referenciados (no solo el HTML).

**Verificar:** por cada URL, existe una carpeta con `index.html` + `assets/`. Total ≥ 100 carpetas.

**Estimado:** 30-60 min (wget puede tardar por las 100+ landings).

---

### 1.5 · Calendarios embebidos (URLs + configuraciones)

**Qué:** los calendarios que Clientify embebe en las landings de agendamiento. En GHL se recrean desde cero (`04` del guia_migracion), así que necesitamos las URLs + configs como referencia.

**Cómo:**
1. Del inventario `landings y calendarios/*/landings.md`, extraer los `meeting_id` que aparecen.
2. Para cada `meeting_id`, capturar en Clientify:
   - Nombre del calendario
   - Asesor asignado (Rodrigo/Andrés/Mauricio/etc.)
   - Duración de la reunión
   - Ventana de disponibilidad
   - Buffer entre citas
   - Preguntas custom del formulario de booking
3. Guardar como `05-calendarios/calendario-{meeting_id}.json` (formato libre, pero consistente).

**Verificar:** listar todos los `meeting_id` mencionados en el inventario y confirmar que cada uno tiene su JSON.

**Estimado:** 20-40 min.

---

### 1.6 · Plantillas de WhatsApp (screenshots + copia literal)

**Qué:** las plantillas de WhatsApp que Clientify tenía cargadas (probablemente las 2 secuencias de confirmación de cita + recordatorios). Las plantillas del BOT (WABA `1931874540684022`) NO viven en Clientify — están en Meta y las migramos por otro camino (`05_templates_meta_waba.md`).

**Cómo:**
1. En Clientify: `Templates WhatsApp` (o donde estén las plantillas del canal Clientify si lo tenía activo).
2. Para cada plantilla:
   - Screenshot
   - Copia literal del texto (con las variables `{{X}}`)
   - Guardar en `06-templates-whatsapp/template-{nombre}.md`

**Verificar:** todas las plantillas activas están capturadas.

**Estimado:** 15-30 min.

**Nota:** si Clientify no tiene un módulo de templates propio (usa las de Meta directo), este paso puede ser N/A. Documentar como "no aplica" en el `README.md` del backup.

---

### 1.7 · Reportes (CSV de conversiones + atribuciones)

**Qué:** los reportes históricos de Clientify — conversiones por campaña, atribuciones por asesor, funnel de deals.

**Cómo:**
1. `Reportes` → seleccionar cada reporte relevante:
   - Conversiones por origen/campaña (últimos 12 meses)
   - Atribución por asesor (últimos 12 meses)
   - Funnel de pipeline (todos los pipelines vivos)
   - Actividad de contactos por mes
2. Exportar cada uno a CSV.
3. Guardar como `07-reportes/reporte-{nombre_slug}-YYYY-MM-DD.csv`.

**Verificar:** al menos los 3 reportes principales están capturados.

**Estimado:** 20-30 min.

---

## 2. Estructura final del backup

```
clients/VTR_Venttur/00_migracion_ghl/05_ejecucion/backup-clientify-2026-09/
├── README.md                    # ← este runbook + resultado de cada paso
├── 01-contactos-export-YYYY-MM-DD.csv
├── 02-chats/
│   ├── conversacion-{id}-YYYY-MM-DD.txt
│   └── adjuntos/{contact_id}/
├── 03-automatizaciones/
│   ├── README.md
│   ├── automatizacion-{slug}-{fecha}.png
│   └── automatizacion-{slug}-{fecha}.json
├── 04-landings/
│   ├── lista-urls-landings.txt
│   └── {url_slug}/index.html + assets/
├── 05-calendarios/
│   └── calendario-{meeting_id}.json
├── 06-templates-whatsapp/
│   └── template-{nombre}.md
└── 07-reportes/
    └── reporte-{slug}-YYYY-MM-DD.csv
```

---

## 3. Checklist de verificación post-backup

Antes de dar el paso 1.5 del cutover (D-day 26/9 09:00) como GO, chequear:

- [ ] `01-contactos-*.csv` existe, ≥ 6.500 filas, se abre en un editor sin caracteres corruptos.
- [ ] `02-chats/` tiene ≥ 30 archivos.
- [ ] `03-automatizaciones/README.md` existe y lista cada automatización con su screenshot.
- [ ] `04-landings/` tiene ≥ 100 subcarpetas + cada una con `index.html`.
- [ ] `05-calendarios/` tiene JSONs para todos los `meeting_id` del inventario.
- [ ] `06-templates-whatsapp/` tiene todas las plantillas (o `README.md` que dice "N/A - Clientify no tenía módulo propio").
- [ ] `07-reportes/` tiene al menos 3 CSVs.
- [ ] `README.md` del backup consolidado documenta: qué se hizo, cuándo, quién, qué NO se pudo respaldar (con motivo).
- [ ] `du -sh backup-clientify-2026-09/` reporta el tamaño total — dejar constancia en el README.
- [ ] `.gitignore` bloquea la carpeta — `git status` no debe listarla.

**Si algún ítem falla:** documentar en el README con "⚠️ Faltante: X porque Y", y decidir con la agencia si eso bloquea el cutover o si se procede con la ausencia registrada.

---

## 4. Punto de no retorno

**27/9 sábado EOD.** Después del apagado de Clientify:
- El acceso a datos históricos se pierde (no hay "trial extendido").
- Rollback del cutover ya no es posible (§10 escenario 5 del runbook cutover).
- La única fuente de verdad de contenido pre-migración es este backup.

**Regla dura:** si el 26/9 09:00 el checklist §3 no está 100% verde, se retrasa el cutover al 27/9 (todavía hay 1 día de margen). Si el 27/9 09:00 sigue sin estar verde, se comunica al cliente que el cutover se corre a la siguiente semana y se paga otro mes de Clientify.

---

## 5. Ownership + escalamiento

- **Owner del backup:** la agencia (o Camilo si la agencia está ocupado). Se ejecuta con las credenciales de Mauricio (o Rodrigo/Andrés si algún elemento requiere permisos específicos).
- **Escalamiento:** si Clientify da error de exportación repetido, escalar a soporte Clientify (Mauricio tiene el contacto). Los CSV grandes a veces requieren pedirlos por email.
- **Comunicación al cliente:** el aviso ya se le hizo (`clientify-que-respaldar-antes-de-apagar.md`). No necesita re-avisarlo — solo confirmarle al 26/9 09:00 que el backup está OK y que se procede.

---

## Referencias

- Aviso original al cliente: `06_docs/clientify-que-respaldar-antes-de-apagar.md`
- Auditoría de migrabilidad: `05_ejecucion/auditoria-migrabilidad-clientify.md`
- Inventario landings: `/Users/camilo/Downloads/Clientify/landings y calendarios/{Mauricio,Andrés,Max}/landings.md`
- Runbook cutover general: `12_cutover.md`
- Guía recta final: `../../06_docs/guia-recta-final-cutover-2026-09-16.md`
