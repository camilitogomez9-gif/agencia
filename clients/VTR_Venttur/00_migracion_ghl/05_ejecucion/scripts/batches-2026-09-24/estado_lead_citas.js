// Construir estado lead — CITAS-0924. Portado del staging (3sLd7KY3o8I7NvXi), adaptado a GET /contacts/{id}.
// CITAS-0924: la cita sale de las citas REALES del contacto en GHL (GET /contacts/{id}/appointments), no del
// flag `agendan_cita` solo — ese flag no tiene fecha, no se apaga cuando la cita pasa y viene arrastrado de
// Clientify/Airtable en contactos importados (caso Mauricio 23/9: flag en true, cero citas en GHL → el bot se
// negaba a mandarle el link). Tres casos: cita futura (con fecha) · cita que ya pasó · flag sin cita registrada.
const FID = {"programa_interes": "xK2NFqtz1DYUw3gYdn8I", "origen": "BEhJWnXS9SQovJTLSA2W", "fuente_lead": "2hv0GovhSzZO3hj9cFqm", "link_enviado": "rHzGNiesWuESPmSZyviJ", "estado_conversacion": "Omg1BvHmpXR0MMGsrpFh", "toques_enviados": "ez934lu03v7nC4ZRS7LJ", "grado_escolar": "HjNeRtIv6XHHMgFbtsaR", "inicio_deseado": "dUvMI4NaamfRPOF1p95q", "nivel_ingles": "uOecQsOv9i3uwMeSgEkX", "agendan_cita": "LwXu8AxMLhVGCbNmgzm2"};
const TZ = 'America/Mexico_City';   // GHL devuelve startTime en la hora de la cuenta (CDMX), sin offset
let hit = null;
try {
  const r = $('GHL · Get contact (estado)').first().json || {};
  hit = r.contact || (r.body && r.body.contact) || null;
} catch (e) { hit = null; }
if (!hit || !hit.id) { return [{ json: { estado: 'Lead nuevo: no tenemos nada de esta persona todavia.', encontrado: false } }]; }
const cfs = {};
for (const x of (hit.customFields || [])) cfs[x.id] = x.value;
const V = (k) => cfs[FID[k]];
const truthy = (v) => v === true || v === 'true' || (Array.isArray(v) && v.includes('true'));
const tags = (hit.tags || []).map(t => String(t).toLowerCase());
const pausado = tags.includes('bot_pausado');  // PRE-BSP-0923 · lo pone la tool elevar; se saca a mano para reactivar el bot

// ── Citas reales (CITAS-0924) ──
let citasOk = false, futura = null, pasada = null;
try {
  const r = $('GHL · Citas (estado)').first().json || {};
  if (Array.isArray(r.events)) {
    citasOk = true;
    const ahora = DateTime.now().setZone(TZ);
    const parse = (s) => {
      if (!s) return null;
      let d = DateTime.fromFormat(String(s), 'yyyy-MM-dd HH:mm:ss', { zone: TZ });
      if (!d.isValid) d = DateTime.fromISO(String(s), { zone: TZ });
      return d.isValid ? d : null;
    };
    const vivas = r.events
      .filter(e => e && !e.deleted)
      .filter(e => !['cancelled', 'invalid'].includes(String(e.appointmentStatus || e.appoinmentStatus || '').toLowerCase()))
      .map(e => ({ e, ini: parse(e.startTime), fin: parse(e.endTime) || parse(e.startTime) }))
      .filter(x => x.ini);
    const fut = vivas.filter(x => x.fin >= ahora).sort((a, b) => a.ini - b.ini);
    const pas = vivas.filter(x => x.fin < ahora).sort((a, b) => b.ini - a.ini);
    futura = fut[0] || null;
    pasada = pas[0] || null;
  }
} catch (e) { citasOk = false; }
const fmt = (d) => d.setLocale('es').toFormat("cccc d 'de' LLLL, h:mm a") + ' (hora de CDMX)';
const progDe = (e) => { const t = String(e.title || ''); const i = t.lastIndexOf('·'); return i >= 0 ? t.slice(i + 1).trim() : ''; };
const flagCita = truthy(V('agendan_cita'));

const L = [];
const nom = ((hit.firstName||'') + ' ' + (hit.lastName||'')).trim();
L.push('Nombre: ' + (nom ? nom + ' (ya lo sabes, no se lo vuelvas a preguntar)' : 'no disponible'));
const prog = (V('programa_interes')||'').toString().trim();
L.push('Programa de interes: ' + (prog && prog !== 'No definido' ? prog : 'sin definir'));
const org = (V('origen')||'').toString().trim(); const fue = (V('fuente_lead')||'').toString().trim();
L.push('Origen: ' + (org || fue || 'DESCONOCIDO'));

const link = truthy(V('link_enviado'));
if (futura) {
  const p = progDe(futura.e);
  L.push('Link de agenda: ' + (link ? 'YA ENVIADO' : 'no enviado'));
  L.push('Cita: AGENDADA para el ' + fmt(futura.ini) + (p ? ' · ' + p : '')
    + '. No vuelvas a venderle la asesoria. Si pide cambiarla o reagendarla, mándale el link de su programa para que elija otro horario.');
} else if (pasada) {
  L.push('Link de agenda: ' + (link ? 'YA ENVIADO y NO tiene una cita vigente' : 'no enviado'));
  L.push('Cita: NO tiene una cita vigente. Tuvo una el ' + fmt(pasada.ini) + ' y ya paso.'
    + ' Si quiere otra o pregunta por agendar, mándale el link de su programa.');
} else if (flagCita) {
  // Flag en true sin cita en GHL: típico de contactos importados de Clientify. Puede ser una cita vieja o una
  // agendada fuera de GHL; no sabemos la fecha. No se ofrece el link por iniciativa propia, pero si lo pide, sí.
  L.push('Link de agenda: ' + (link ? 'YA ENVIADO' : 'no enviado'));
  L.push('Cita: el CRM la marca como agendada, pero no tenemos la fecha registrada (puede ser una cita anterior).'
    + ' No le ofrezcas el link por tu cuenta, pero si pide agendar, reagendar o dice que su cita ya paso, mándale el link de su programa en ese mismo mensaje.');
} else {
  L.push('Link de agenda: ' + (link ? 'YA ENVIADO y NO agendó todavía' : 'no enviado'));
  L.push('Cita: sin agendar');
}

let est = (V('estado_conversacion')||'').toString().trim();
if (est && /cita confirmada/i.test(est) && !futura) {
  est += pasada ? ' (de una cita anterior, hoy no tiene una vigente)' : ' (sin fecha registrada)';
}
if (est) L.push('Conversacion: ' + est);
const toq = V('toques_enviados'); if (toq) L.push('Toques enviados: ' + toq);
const form = [
  V('grado_escolar') ? 'grado ' + V('grado_escolar') : null,
  V('inicio_deseado') ? 'inicio ' + V('inicio_deseado') : null,
  V('nivel_ingles') ? 'ingles ' + V('nivel_ingles') : null,
].filter(Boolean);
if (form.length) L.push('Del formulario (ya los tenemos): ' + form.join(' - '));
return [{ json: { estado: L.join('\n'), encontrado: true, pausado, citas_ok: citasOk, cita_vigente: !!futura } }];
