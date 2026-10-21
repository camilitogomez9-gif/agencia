// Detectar promesa fantasma · Capa 2 estructural (guardrail determinístico)
// Se ejecuta ENTRE 'Formatear mensaje WPP' y 'Normalizar burbujas' en main-venttur.
// Input:  $input.first().json = { parte1, parte2, parte3 } — output de Formatear
// Output: mismo shape. Si detecta promesa fantasma, reemplaza con link canónico + flag para alerta.

const item = $input.first();
const p1 = String(item.json.parte1 || '');
const p2 = String(item.json.parte2 || '');
const p3 = String(item.json.parte3 || '');
const fullText = (p1 + ' ' + p2 + ' ' + p3).toLowerCase();

// Si el output ya trae un link canónico, dejamos pasar (el prompt hizo lo correcto).
if (/promo\.venttur\.com\//i.test(fullText)) {
  return item;
}

// Detector — 2 caminos hacia INTERCEPT:
//
// (A) camino fuerte · verbo intrínsecamente de cita ("quedamos/nos vemos/te llamo/te confirmo")
//     + referencia temporal.
//     Estos verbos SIEMPRE implican una cita — no hace falta que el texto también diga "cita".
//
// (B) camino combinado · verbo neutro de coordinación ("coordinar/programar/agendar/reservar/apartar")
//     + contexto de cita/llamada/asesoría/videollamada
//     + referencia temporal.
//     Los tres tienen que estar presentes para evitar falso positivo tipo "coordinar programa".

const RE_TIEMPO = /\b(a las \d{1,2}(:\d{2})?|\d{1,2}(:\d{2})?\s*(am|pm|hs|hrs|hr)|ma[ñn]ana|hoy|(el )?(lunes|martes|mi[ée]rcoles|jueves|viernes|s[áa]bado|domingo)|esta semana|pr[óo]xima semana|el fin de semana|en la ma[ñn]ana|en la tarde)\b/i;

// Camino A · verbos intrínsecos de cita
const RE_VERBO_CITA = /\b(qued(amos|amo|é|as|amos entonces|amos para)|nos vemos|te llamo|te llamamos|te contact(o|amos|aré)|te aviso|te confirmo)\b/i;

// Camino B · verbos neutros de coordinar (necesitan contexto explícito)
const RE_VERBO_COORD = /\b(coordin(o|a|amos|emos|é|ar[eé]?|aré|aremos)|voy a coordinar|program(o|a|amos|aremos|ar[eé]?)|reserv(o|amos|ar|é|aré)|te ap[aá]rt(o|ar[eé]|aré)|agend(o|amos|aré|é|ar[eé]?)|confirm(o|amos|é|amos la|aré) (el|la|los))\b/i;
const RE_CITA_CONTEXTO = /\b(cita|llamada|asesor[ií]a|videollamada|reuni[óo]n|reservar el turno|el horario)\b/i;

const hasTime = RE_TIEMPO.test(fullText);
const pathA   = RE_VERBO_CITA.test(fullText)  && hasTime;
const pathB   = RE_VERBO_COORD.test(fullText) && RE_CITA_CONTEXTO.test(fullText) && hasTime;

// Pass-through si ningún camino se cumple
if (!(pathA || pathB)) {
  return item;
}

// ═══════════════ PROMESA FANTASMA DETECTADA ═══════════════
// Reemplazar burbujas con redirect determinístico al link + flag para alerta P1.

// Estado del lead
let lead = {};
try {
  lead = $('Buscar si ya existe').first().json || {};
} catch (e) { lead = {}; }

const programa = String(lead['Programa interés'] || lead['Programa interes'] || '').trim();
const nombre   = String(lead['Nombre'] || '').trim();

// Mapeo programa → link canónico + nombre del experto
// Fuente de verdad: system prompt v2.1, sección "📲 Enlaces de asesoría" (líneas ~554-570).
// Fallback ante duda: agendar-ema (Rodrigo).
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

const newP1 = `Perdón, ${salut}me anticipé — para reservar la asesoría necesito que elijas tu horario directo en el link, así se sincroniza con la agenda de ${link.experto}`;
const newP2 = `Te lo dejo: ${link.url}`;
const newP3 = `Vos elegís día y hora, y me llega la confirmación automáticamente. Si tenés alguna duda antes de la llamada, escribime por aquí`;

return {
  json: {
    parte1: newP1,
    parte2: newP2,
    parte3: newP3,
    // Metadata para alerta P1 downstream (nodo IF + Telegram)
    _phantom_promise_intercepted: true,
    _phantom_original_parte1: p1,
    _phantom_original_parte2: p2,
    _phantom_original_parte3: p3,
    _phantom_programa: programa,
    _phantom_url: link.url,
    _phantom_experto: link.experto,
    _phantom_nombre: nombre
  }
};
