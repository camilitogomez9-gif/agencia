// v2.6 (2026-07-08) — Capa 1+2 del fix re-saludo/re-pregunta + línea "Teléfono del lead".
// Refs por nombre (no $json) porque entre Build y AI Agent vive Get a document que rompe $json.

const data = $('Normalize Payload').first().json;
const parseOut = $('Parse datos del mensaje').first()?.json || {};
const stateRow = parseOut._stateRow || $('Get session_state').first()?.json || {};
const patch = parseOut.patch || {};

const fecha = new Date().toLocaleString('es-AR', { timeZone: 'America/Argentina/Buenos_Aires' });

const perfil = stateRow.perfil || 'sin clasificar';
const etapa = stateRow.etapa || 'bienvenida';

const datosCurrent = stateRow.datos_capturados || {};
const datosMerged = { ...datosCurrent, ...patch };
const productos = Array.isArray(stateRow.productos_mostrados) ? stateRow.productos_mostrados : [];

const datosLine = Object.keys(datosMerged).length ? JSON.stringify(datosMerged) : '(sin datos del lead aún)';
const productosLine = productos.length ? productos.join(', ') : '(ninguno todavía)';

// v2.6 — Teléfono del lead: coalesce determinístico (ManyChat) → capturado en chat.
// MISMO criterio que la tool registrar_datos_lead. Alimenta la Regla 26 del prompt.
const digitsOf = (s) => String(s || '').replace(/[^\d]/g, '');
const isValidPhone = (s) => {
  const raw = String(s || '').trim();
  if (!raw || raw === '{{phone}}') return false;
  if (!/^\+?[\d\s().-]+$/.test(raw)) return false;
  return digitsOf(raw).length >= 6;
};
const telWebhook = String(data.phone || '');
const telChat = String(datosMerged.telefono || '');
const telLead = isValidPhone(telWebhook) ? telWebhook : (isValidPhone(telChat) ? telChat : '');
const telefonoLine = telLead
  ? `\n- Teléfono del lead: ${telLead}`
  : `\n- Teléfono del lead: NO disponible (ManyChat no lo trajo — pedile al lead que lo escriba antes de registrar)`;

// Se mantiene la línea "Número del canal" para Regla 18 (ahora valida para no mostrar {{phone}}).
const numeroCanal = (data.channel === 'wa' && isValidPhone(data.phone)) ? data.phone : null;
const lineaNumero = numeroCanal ? `\n- Número del canal (WhatsApp): ${numeroCanal}` : '';

const contextoTurno = `[CONTEXTO TURNO]
- Canal: ${data.canalLabel}${telefonoLine}${lineaNumero}
- Fecha y hora actual: ${fecha}
- Perfil del lead: ${perfil}
- Etapa actual: ${etapa}
- Datos ya capturados: ${datosLine}
- Productos ya mostrados: ${productosLine}

[MENSAJE DEL USUARIO]
${data.mensajeActual}`;

return [{
  json: {
    ...data,
    userMessage: contextoTurno,
    _state: stateRow,
    _datosMerged: datosMerged
  }
}];
