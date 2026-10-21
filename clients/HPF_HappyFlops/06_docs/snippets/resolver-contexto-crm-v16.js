// Resuelve el contexto real de GHL para un chat de Telegram.
// Equivale a lo que en produccion trae el webhook de WF-01: contact_id, opportunity_id,
// stage (nombre) y custom_fields (por key). Ademas construye los mapas de stage ids y
// custom field ids, que en produccion viven hardcodeados.
const LOCATION_ID   = 'onRwi0ZF4uYi0Lp6GAbE';
const PIPELINE_NAME = 'Happy Flops IA';

const grab = (node) => { try { return $(node).first().json || {}; } catch (e) { return {}; } };

// ─────────── contacto ───────────
const up = grab('GHL: Upsert Contacto');
const contact = up.contact || up.data || up || {};
const contact_id = String(contact.id || '');
const contact_tags = (contact.tags || []).map(t => String(t).trim().toLowerCase());

// ─────────── pipeline + stages ───────────
const pipesRaw = grab('GHL: Pipelines');
const pipelines = pipesRaw.pipelines || pipesRaw.data || [];
const pipe =
  pipelines.find(p => String(p.name || '').trim().toLowerCase() === PIPELINE_NAME.toLowerCase()) ||
  pipelines[0] || null;

const STAGE_ID_BY_NAME = {};
const STAGE_NAME_BY_ID = {};
for (const s of (pipe && pipe.stages) || []) {
  STAGE_ID_BY_NAME[String(s.name).trim()] = s.id;
  STAGE_NAME_BY_ID[s.id] = String(s.name).trim();
}
// Fallback: ids conocidos por hardcode historico (sirven si el GET de pipelines falla).
const STAGE_FALLBACK = {
  'Cotizado':        '96fa0ade-c853-4db3-97f4-56d58d69af8c',
  'Esperando Pago':  '843a06f1-1214-4baa-a3a0-f197cb240b5d',
  'Pago Confirmado': '96d760e5-f290-456c-a117-57e61ce6c27d',
};
for (const [k, v] of Object.entries(STAGE_FALLBACK)) {
  if (!STAGE_ID_BY_NAME[k]) { STAGE_ID_BY_NAME[k] = v; STAGE_NAME_BY_ID[v] = k; }
}

// ─────────── definiciones de custom fields ───────────
const cfRaw  = grab('GHL: Custom Fields Opp');
const cfDefs = cfRaw.customFields || cfRaw.data || [];
const CF_ID_BY_KEY = {};
const CF_KEY_BY_ID = {};
for (const f of cfDefs) {
  const key = String(f.fieldKey || f.key || '').replace(/^opportunity\./, '').replace(/^contact\./, '');
  if (!key || !f.id) continue;
  CF_ID_BY_KEY[key] = f.id;
  CF_KEY_BY_ID[f.id] = key;
}
// El unico id conocido por hardcode historico.
if (!CF_KEY_BY_ID['ahVpF5ldsRcuOIn9Mxdk']) {
  CF_KEY_BY_ID['ahVpF5ldsRcuOIn9Mxdk'] = 'evento_detectado';
  CF_ID_BY_KEY['evento_detectado'] = CF_ID_BY_KEY['evento_detectado'] || 'ahVpF5ldsRcuOIn9Mxdk';
}

// customFields de un opportunity -> objeto plano por key
function cfObject(opp) {
  const out = {};
  for (const cf of (opp && opp.customFields) || []) {
    const key = CF_KEY_BY_ID[cf.id] || String(cf.key || cf.fieldKey || '').replace(/^opportunity\./, '');
    if (!key) continue;
    let v = cf.fieldValue !== undefined ? cf.fieldValue
          : cf.field_value !== undefined ? cf.field_value
          : cf.value;
    if (Array.isArray(v)) v = v[0];
    out[key] = v;
  }
  return out;
}

// ─────────── oportunidad ───────────
const searchRaw = grab('GHL: Buscar Oportunidad');
// distinguir "la busqueda respondio vacio" de "la busqueda fallo": si falla y lo tomamos
// como lista vacia, creariamos una oportunidad nueva en CADA mensaje.
const searchOk = Array.isArray(searchRaw.opportunities) || Array.isArray(searchRaw.data);
let opps = searchRaw.opportunities || searchRaw.data || [];
if (!Array.isArray(opps)) opps = [];
if (pipe) {
  const delPipe = opps.filter(o => String(o.pipelineId || '') === String(pipe.id));
  if (delPipe.length) opps = delPipe;
}
// preferimos la abierta mas reciente
opps.sort((a, b) => {
  const ao = (a.status === 'open') ? 1 : 0;
  const bo = (b.status === 'open') ? 1 : 0;
  if (ao !== bo) return bo - ao;
  return String(b.updatedAt || b.dateUpdated || '').localeCompare(String(a.updatedAt || a.dateUpdated || ''));
});
const opp = opps[0] || null;

const stageName = opp
  ? (STAGE_NAME_BY_ID[opp.pipelineStageId] || String(opp.pipelineStageName || '').trim() || 'Lead Nuevo')
  : 'Lead Nuevo';

const base = $('Normalizar Telegram').first().json;

return {
  ...base,
  crm_ok: !!contact_id,
  location_id: LOCATION_ID,
  pipeline_id: pipe ? pipe.id : '',
  pipeline_name: pipe ? pipe.name : '',
  contact_id,
  contact_tags,
  opportunity_id: opp ? opp.id : '',
  // solo creamos oportunidad si la busqueda REALMENTE respondio y vino vacia
  needs_opportunity: !opp && searchOk,
  search_ok: searchOk,
  stage: stageName,
  custom_fields: cfObject(opp),
  stage_ids: STAGE_ID_BY_NAME,
  stage_names: STAGE_NAME_BY_ID,
  cf_ids: CF_ID_BY_KEY,
  cf_keys: CF_KEY_BY_ID,
  _diag: {
    pipelines_encontrados: pipelines.length,
    cf_defs_encontradas: cfDefs.length,
    opps_encontradas: opps.length,
  },
};
