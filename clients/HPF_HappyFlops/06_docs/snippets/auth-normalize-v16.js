// Contrato unico de contexto para TODO el flujo aguas abajo.
// Dos entradas posibles, misma salida:
//   (A) TELEGRAM  -> viene de "Resolver Contexto CRM" (+ "GHL: Crear Oportunidad" si hubo que crearla)
//   (B) GHL WF-01 -> viene del webhook con contact_id/opportunity_id/stage/custom_fields ya resueltos
//
// PAYLOAD REAL DE GHL (WF-01, accion Webhook con CUSTOM DATA):
//   contact_id={{contact.id}} · opportunity_id={{opportunity.id}} · phone={{contact.phone}}
//   stage={{opportunity.stage_name}} · message_type="text" (LITERAL) · message_text={{message.body}}
//   media_url={{message.attachments}} (ARRAY serializado)
// Por eso NO confiamos en message_type: si hay media, el tipo real lo define el media.
const grab = (node) => { try { return $(node).first().json || null; } catch (e) { return null; } };

const S = (v) => (v === undefined || v === null) ? '' : String(v);
const pick = (...v) => { for (const x of v) if (x !== undefined && x !== null && x !== '') return x; return ''; };

const crm = grab('Resolver Contexto CRM');

// ─────────────────────────── (A) TELEGRAM ───────────────────────────
if (crm && crm.source === 'telegram') {
  const creada = grab('GHL: Crear Oportunidad');
  const oppNueva = creada ? (creada.opportunity || creada.data || creada) : null;

  const opportunity_id = S(pick(crm.opportunity_id, oppNueva && oppNueva.id));
  const stage = crm.opportunity_id
    ? crm.stage
    : (oppNueva ? (crm.stage_names[oppNueva.pipelineStageId] || 'Lead Nuevo') : 'Lead Nuevo');

  if (!crm.contact_id) {
    // GHL no respondio: seguimos igual (el lead nunca se queda sin respuesta), pero queda marcado.
    console.log('[HPF] AVISO: no se pudo resolver el contacto en GHL. Se sigue sin CRM.');
  }

  return {
    // identidad
    contact_id: crm.contact_id,
    opportunity_id,
    phone: '',
    session_key: crm.session_key,
    telegram_chat_id: crm.telegram_chat_id,
    channel: 'telegram',
    is_telegram: true,
    is_telegram_test: true,   // compat con nodos heredados
    crm_ok: !!(crm.contact_id && opportunity_id),
    // mensaje
    message_type: crm.message_type,
    message_text: crm.message_text,
    media_url: '',
    media_type: '',
    telegram_file_id: crm.telegram_file_id,
    is_command: crm.is_command,
    // estado CRM
    stage,
    custom_fields: crm.custom_fields || {},
    contact_tags: crm.contact_tags || [],
    // mapas
    location_id: crm.location_id,
    pipeline_id: crm.pipeline_id,
    stage_ids: crm.stage_ids,
    stage_names: crm.stage_names,
    cf_ids: crm.cf_ids,
    // datos del lead
    first_name: crm.first_name,
    last_name: crm.last_name,
    full_name: crm.full_name,
    raw: { channel: 'telegram' },
  };
}

// ─────────────────────────── (B) GHL / WEBHOOK ───────────────────────────
const item = $input.first();
const b  = item.json?.body || item.body || item.json || {};
const m  = b.message || {};
const cd = b.customData || b.custom_data || {};

function firstUrl(v) {
  if (Array.isArray(v)) return S(v[0]);
  let s = S(v).trim();
  if (!s || s === '[object Object]' || s === 'null' || s === 'undefined' || s.startsWith('{{')) return '';
  if (s.startsWith('[')) {
    try { const arr = JSON.parse(s); if (Array.isArray(arr)) return S(arr[0]); } catch (e) {}
    s = s.replace(/^\[|\]$/g, '').replace(/["']/g, '');
  }
  return s.split(',')[0].trim();
}

const contact_id     = S(pick(b.contact_id, b.contactId, cd.contact_id, m.contactId));
const opportunity_id = S(pick(b.opportunity_id, b.opportunityId, cd.opportunity_id, b.id));
const phone          = S(pick(b.phone, b.phoneNumber, cd.phone, b.contact?.phone));
const message_text   = S(pick(b.message_text, b.messageText, m.body, m.text, cd.message_text, b.text));
const media_url      = firstUrl(pick(b.media_url, b.mediaUrl, b.attachments, m.attachments, m.media_url, cd.media_url));
const media_type     = S(pick(b.media_type, b.mediaType, m.media_type, m.contentType));

let message_type = S(pick(b.message_type, b.messageType, m.type)).toLowerCase();
if (media_url) {
  message_type = /\.(ogg|oga|mp3|m4a|wav|amr|mpeg)(\?|$)|audio|voice/i.test(media_type + ' ' + media_url)
    ? 'audio' : 'image';
} else if (!message_type || ['sms','whatsapp','ig','fb','live_chat','email','custom'].includes(message_type)) {
  message_type = 'text';
}
if (message_type === 'photo' || message_type === 'picture') message_type = 'image';
if (message_type === 'voice') message_type = 'audio';

const channel = S(pick(b.channel, cd.channel, 'whatsapp'));
const keys = Object.keys(b).join(', ') || '(body vacio)';
if (!contact_id) throw new Error(`Inbound sin contact_id. Keys recibidas: ${keys}`);
if (!message_text && !media_url) {
  throw new Error(`Inbound sin texto ni media (el agente recibiria un mensaje vacio). Keys: ${keys}`);
}

return {
  contact_id, opportunity_id, phone,
  session_key: phone || contact_id,
  telegram_chat_id: '',
  channel,
  is_telegram: false,
  is_telegram_test: false,
  crm_ok: !!opportunity_id,
  message_type, message_text, media_url, media_type,
  telegram_file_id: '',
  is_command: false,
  stage: S(pick(b.stage, b.pipleline_stage, b.pipeline_stage, cd.stage)),
  custom_fields: b.custom_fields || b.customFields || {},
  contact_tags: [],
  location_id: 'onRwi0ZF4uYi0Lp6GAbE',
  pipeline_id: '',
  stage_ids: {
    'Cotizado':        '96fa0ade-c853-4db3-97f4-56d58d69af8c',
    'Esperando Pago':  '843a06f1-1214-4baa-a3a0-f197cb240b5d',
    'Pago Confirmado': '96d760e5-f290-456c-a117-57e61ce6c27d',
  },
  stage_names: {},
  cf_ids: {},
  first_name: S(b.first_name || b.firstName),
  last_name: S(b.last_name || b.lastName),
  full_name: S(pick(b.full_name, b.name, [b.first_name, b.last_name].filter(Boolean).join(' '))),
  raw: { ...b, channel },
};
