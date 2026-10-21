// Detectar promesa fantasma · Capa 2 estructural · STAGING (Telegram, sin splitter)
// Se ejecuta ENTRE 'Agente IA WPP' y 'Enviar Telegram' en el workflow staging (12+1 nodos).
// Input:  $input.first().json = { output: "texto largo del agente" }
// Output: mismo shape. Si detecta promesa fantasma, reemplaza `output` con link + framing de disculpa.
// Réplica adaptada del guardrail del vivo (mismo detector, distinto output shape).

const item = $input.first();
const raw = String(item.json.output || '');
const fullText = raw.toLowerCase();

// Pass-through si el agente ya envió una URL canónica en el mismo turno
if (/promo\.venttur\.com\//i.test(fullText)) return item;

// Detector · dos caminos hacia INTERCEPT (mismo criterio que el vivo)
const RE_TIEMPO = /\b(a las \d{1,2}(:\d{2})?|\d{1,2}(:\d{2})?\s*(am|pm|hs|hrs|hr)|ma[ñn]ana|hoy|(el )?(lunes|martes|mi[ée]rcoles|jueves|viernes|s[áa]bado|domingo)|esta semana|pr[óo]xima semana|el fin de semana|en la ma[ñn]ana|en la tarde)\b/i;

// (A) verbo intrínseco de cita + tiempo
const RE_VERBO_CITA = /\b(qued(amos|amo|é|as|amos entonces|amos para)|nos vemos|te llamo|te llamamos|te contact(o|amos|aré)|te aviso|te confirmo)\b/i;

// (B) verbo neutro de coordinar + contexto de cita + tiempo
const RE_VERBO_COORD = /\b(coordin(o|a|amos|emos|é|ar[eé]?|aré|aremos)|voy a coordinar|program(o|a|amos|aremos|ar[eé]?)|reserv(o|amos|ar|é|aré)|te ap[aá]rt(o|ar[eé]|aré)|agend(o|amos|aré|é|ar[eé]?)|confirm(o|amos|é|amos la|aré) (el|la|los))\b/i;
const RE_CITA_CONTEXTO = /\b(cita|llamada|asesor[ií]a|videollamada|reuni[óo]n|reservar el turno|el horario)\b/i;

const hasTime = RE_TIEMPO.test(fullText);
const pathA = RE_VERBO_CITA.test(fullText) && hasTime;
const pathB = RE_VERBO_COORD.test(fullText) && RE_CITA_CONTEXTO.test(fullText) && hasTime;

if (!(pathA || pathB)) return item;

// ═══ INTERCEPCIÓN ═══
// Traer programa e identidad del lead desde el custom field de GHL
const FID_PROGRAMA = "xK2NFqtz1DYUw3gYdn8I";
let programa = '', nombre = '';
try {
  const r = $('Buscar Contact GHL').first().json || {};
  const arr = r.contacts || (r.body && r.body.contacts) || [];
  const hit = arr[0] || null;
  if (hit) {
    const cf = (hit.customFields || []).find(x => x.id === FID_PROGRAMA);
    programa = String((cf && cf.value) || '').trim();
    nombre = String((hit.firstName || '')).trim().split(' ')[0];
  }
} catch (e) { /* fallback */ }

// Mapeo programa → URL + experto (misma fuente de verdad que el vivo)
function mapProgramaToLink(prog) {
  const p = prog.toLowerCase();
  if (/pathway|alemania/.test(p))                                 return { url: 'promo.venttur.com/PW_Alemania_Agendar',              experto: 'Andrés' };
  if (/summer|campament|verano|invierno/.test(p))                 return { url: 'promo.venttur.com/SummerCamp-Agendar',               experto: 'Rodrigo' };
  if (/australia/.test(p))                                        return { url: 'promo.venttur.com/Estudiar-y-Trabajar-en-Australia', experto: 'Diego' };
  if (/gap.*year|estudi.*trabaj|trabaj.*estudi/.test(p))          return { url: 'promo.venttur.com/EstudiaryTrabajar_Agendar',        experto: 'Andrés' };
  if (/familiar|aa familiar|a[ñn]o acad[ée]mico|familia/.test(p)) return { url: 'promo.venttur.com/AAFamilia-Agendar',                experto: 'Rodrigo' };
  if (/boarding|internado/.test(p))                               return { url: 'promo.venttur.com/agendar-ema',                      experto: 'Rodrigo' };
  return { url: 'promo.venttur.com/agendar-ema', experto: 'Rodrigo' };
}

const link = mapProgramaToLink(programa);
const salut = nombre ? `${nombre}, ` : '';
const nuevo = `Perdón, ${salut}me anticipé — para reservar la asesoría necesito que elijas tu horario directo en el link, así se sincroniza con la agenda de ${link.experto}. Te lo dejo: ${link.url}. Vos elegís día y hora, y me llega la confirmación automáticamente. Si tenés alguna duda antes de la llamada, escribime por aquí.`;

return {
  json: {
    ...item.json,
    output: nuevo,
    _phantom_promise_intercepted: true,
    _phantom_original: raw,
    _phantom_programa: programa,
    _phantom_url: link.url,
    _phantom_experto: link.experto,
    _phantom_nombre: nombre
  }
};
