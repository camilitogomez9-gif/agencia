// ═══════════════════════════════════════════════════════════════════════════
// HPF — Sanitize + Split Output · v5 (paridad de voz con el Rebeca de Kommo)
// ═══════════════════════════════════════════════════════════════════════════
// El original tenía DOS caminos de salida y de ahí sale toda su estética:
//
//  A) Texto libre del LLM  → Character_Cleaner + actualizar19/20/21 → bot 60854
//     Perdía  ¿ ¡  y TODOS los emojis del plano astral (😊 📦 🚀 👍 🎨).
//     Sobrevivían solo los BMP: ✨ ⏳ ✏ ☺
//
//  B) Bloques pre-horneados → n8n DETECTABA una cadena en la salida del LLM
//     y la REEMPLAZABA por un salesbot con el texto cargado a mano, que no
//     pasaba por ningún filtro (If24 → saludo · If26/27 → 7 pasos ·
//     Search_Main_Image → imagen de evento · Search_Products → fichas).
//
// Este nodo replica las dos cosas. Todo lo inyectado por código entra DESPUÉS
// del filtro, así que es imposible que un filtro lo toque por accidente.
// ═══════════════════════════════════════════════════════════════════════════

const agent = $json;

// ── Calibración ────────────────────────────────────────────────────────────
const MAX_BURBUJAS = 3;   // partes de texto por turno (parte1/parte2/parte3)
const MAX_FOTOS    = 3;   // fichas con foto por turno
const REENVIAR_SI_PIDE_EXPLICITO = true;

const CATALOGO = [
  { id:"pantufla_peluche", g:"pantufla", tipo:"principal",
    k:["peluche"],
    u:"https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3e0e0316cbe00f334c.jpeg",
    f:"✨ Pantufla de moño de peluche{EV}\n🥿 Suela y esponja más gruesa\n📏 Es unitalla, les queda desde el 23 al 26\n🎨 1 diseño cada 50 pares\n🌈 Colores disponibles: blanca, negra, morada y rosa\n\n💰 Precio promo: $35 el par\n📦 Pedido mínimo: 50 pares\n\n🎁 Elige entre:\n* Bolsa tipo SHEIN no personalizada, tal cual como en la imagen\n* Bolsa de tela personalizada (+$7 c/u)" },
  { id:"pantufla_satin", g:"pantufla", tipo:"principal",
    k:["mono satin", "moño satin", "moño satín", "mono satín", "mono de satin", "moño de satín", "moño de satin"],
    u:"https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3ffb06386edeb05b71.jpeg",
    f:"✨ Pantufla de moño de satín{EV}\n🥿 Suela y esponja más gruesa\n📏 Es unitalla, les queda desde el 23 al 26\n🎨 1 diseño cada 50 pares\n🌈 Colores disponibles: blanca, negra, morada, rosa, cielo y beige\n\n💰 Precio promo: $30 el par\n📦 Pedido mínimo: 50 pares\n\n🎁 Elige entre:\n* Bolsa tipo SHEIN no personalizada, tal cual como en la imagen\n* Bolsa de tela personalizada (+$7 c/u)" },
  { id:"pantuflas", g:"pantufla", tipo:"principal",
    k:["pantufla", "pantuflas"],
    u:"https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3cdf29341f4d8b2f6f.png",
    f:"✨ Pantuflas de satín personalizadas\n💖 Un detalle elegante y cómodo para tu evento\n🥿 Suela y esponja más gruesa\n🎨 Personalizadas con nombre y fecha\n\n📏 Unitalla (les queda del 23 al 26)\n💰 Precio promo: $30 el par\n📦 Pedido mínimo de 50 pares\n\n🎁 Opción de bolsa:\n* Bolsa de tela personalizada (+$7 c/u)\n* Bolsa tipo SHEIN no personalizada (tal cual la imagen)" },
  { id:"sandalias", g:"sandalia", tipo:"principal",
    k:["sandalia", "chancla", "ojota", "huarache", "chancleta"],
    u:"https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf41b86ae4203405cbf9.jpeg",
    f:"✨ Sandalias personalizadas\n💕 Un detalle que todos van a agradecer en tu evento\n👡 Súper cómodas y personalizadas\n\n💡 Disponibles en suela delgada ($25) o suela gruesa ($30), según la comodidad que estés buscando.\n📦 Pedido mínimo de 50 pares." },
  { id:"mandiles", g:"mandil", tipo:"principal", ev:["BODA"],
    k:["mandil"],
    u:"https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3eb86ae4203405cbc1.png",
    f:"✨ Mandiles para boda\n🍾 Ideales para el novio y sus amigos\n🖤 Diseño divertido para la fiesta\n\nℹ️ No se personalizan.\n\n💰 Precio promo: $12 c/u\n📦 Pedido mínimo de 12 piezas." },
  { id:"kit_anticruda", g:"kit", tipo:"principal",
    k:["anticruda", "anti cruda", "kit", "costal", "costalito"],
    u:"https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3df9c6f6a920d2e198.png",
    f:"✨ Kit anticruda personalizado\n🎉 Ideal para cualquier tipo de evento\n🛍️ Costal de tela personalizado a 1 tinta\n📏 Medidas: 16 x 22 cm\n\n💡 Solo incluye el costal, tú lo llenas con los productos que prefieras.\n\n💰 Precio promo: $10 c/u\n📦 Pedido mínimo de 35 piezas." },
  { id:"cilindros", g:"cilindro", tipo:"principal",
    k:["cilindro", "termo", "bule"],
    u:"https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3df7d31b0eb454cf57.png",
    f:"✨ Cilindros personalizados\n🎉 Ideales para todo tipo de evento\n\n🎨 Por cada 20 piezas se realiza un diseño diferente.\n\n💰 Precio promo: $10 c/u\n📦 Pedido mínimo de 40 piezas" },
  { id:"vaso_popote", g:"vaso", tipo:"principal",
    k:["vaso", "popote"],
    u:"https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf42ca81015f1c93cf8d.jpeg",
    f:"✨ Vaso con popote 24 oz{EV}\n🖨️ Diseño en serigrafía\n🥤 Vasos personalizados\n🎨 Mismo diseño y tinta para todas las piezas\n🎨 1 diseño cada 50 vasos\n\n🌈 Tenemos varios colores de vasos\n🥤 Puede escoger 1 color de vaso por cada 20 vasos\n\n💰 Precio promo: $35\n📦 Pedido mínimo: 50 piezas\n⏳ Tiempo de fabricación: 15 días" },
  { id:"tintas", g:"tinta", tipo:"accesorio",
    k:["tinta", "color de tinta", "colores de tinta"],
    u:"https://i.ibb.co/rRVGZtqL/6843598253827.jpg",
    f:"Aqui te muestro los *colores disponibles* para las *TINTAS*" },
  { id:"correa15", g:"correa15", tipo:"accesorio",
    k:["correa 15", "correas 15", "15mm", "15 mm", "suela gruesa", "correa gruesa", "correas gruesas"],
    u:"https://i.ibb.co/bgGFrHcD/6843598e72a98.jpg",
    f:"CORREAS DE SUELA GRUESA" },
  { id:"correa9", g:"correa9", tipo:"accesorio",
    k:["correa 9", "correas 9", "9mm", "9 mm", "suela delgada", "correa delgada", "correas delgadas"],
    u:"https://i.ibb.co/s9VcrD8n/684359a1847ef.jpg",
    f:"CORREAS DE SUELA DELGADA" },
  { id:"bolsa_shein", g:"bolsa", tipo:"accesorio",
    k:["shein", "bolsa tipo shein", "bolsita"],
    u:"https://i.ibb.co/N696v1yV/6843596fd985c.jpg",
    f:"De *REGALO* Cada par viene en *BOLSA TIPO SHEIN* para meter los tacones.\n\n*LA FRASE VIENE TAL CUAL COMO EN LA IMAGEN Y NO SE MODIFICA*\n\n*NO SE PERSONALIZA*\n\nSi quiere el *COSTALITO PERSONALIZADO $7C/U*" },
  { id:"tapas", g:"tapa", tipo:"accesorio",
    k:["tapa", "tapas"],
    u:"https://i.ibb.co/5xBmhSdK/684359acdcdba.jpg",
    f:"Colores de *tapas* disponibles, puede ir surtido en los *colores* que gustes" },
  { id:"cat_cilindros", g:"cat_cilindro", tipo:"catalogo",
    k:["catalogo de cilindro", "catálogo de cilindro", "catalogo cilindro", "catálogo cilindro", "diseños de cilindro", "diseno de cilindro"],
    u:"https://i.ibb.co/TMNBpPgZ/684359bde4dec.jpg",
    f:"Te comparto el *catalogo de diseños* que tenemos para *Cilindros*" },
  { id:"cat_anticrudas", g:"cat_kit", tipo:"catalogo",
    k:["catalogo de anticruda", "catálogo de anticruda", "catalogo anticruda", "catálogo anticruda", "frases anticruda", "frases de anticruda", "frases del kit"],
    u:"https://i.ibb.co/k6vzkZns/68435a4e8ae4e.jpg",
    f:"Te dejo el catalogo de frases que tenemos para los *ANTICRUDAS*" },
];

// ── Imagen principal por evento + sus textos canónicos ─────────────────────
const IMAGENES = {
  BODA:  'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/94d1527d-83d1-40e2-bfac-05dd969c3ea7.jpg',
  XV:    'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/136d7ce1-0487-4767-a408-16742a068939.jpg',
  OTROS: 'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/10880c83-56c2-4ee3-b30d-71e910093962.jpg',
};
// Captions verbatim del Airtable original (Imagen Principal-Grid view.csv, campo CURL.text).
// Sí: XV lleva DOS espacios antes del 😊. Está así en producción.
const CAPTION_EVENTO = {
  BODA:  'TENEMOS ESTOS PRODUCTOS PARA TU EVENTO:\n\n*Sandalias*\n*Cilindros*\n*Mandiles para Boda*\n*Kit anti cruda*\n*Pantuflas*\n\nDime cuales te interesan, así te mostramos toda su información 😊',
  XV:    'TENEMOS ESTOS PRODUCTOS PARA TU EVENTO:\n\n*Sandalias*\n*Cilindros*\n*Kit anti cruda*\n*Pantuflas*\n\nDime cuales te interesan, así te mostramos toda su información  😊',
  OTROS: 'TENEMOS ESTOS PRODUCTOS PARA TU EVENTO:\n\n*Sandalias*\n*Cilindros*\n*Kit anti cruda*\n*Pantuflas*\n\nDime cuales te interesan, así te mostramos toda su información 😊',
};
const PROMO = 'Qué padre! 😊  \n🎉 *¡SEMANA LOCA DE PROMOS! SOLO 7 DÍAS PARA LLEVARTE TUS RECUERDITOS PERSONALIZADOS CON DESCUENTAZO* 🎉\n*(Pedidos solo para eventos 2026 por tema de tiempos)*';

const ALIAS = {
  BODA:'BODA', BODAS:'BODA', 'BODA DE ORO':'BODA', 'BODA DE PLATA':'BODA',
  XV:'XV', 'XV AÑOS':'XV', XVAÑOS:'XV', QUINCE:'XV', 'QUINCE AÑOS':'XV', QUINCEAÑERA:'XV', '15 AÑOS':'XV',
  BAUTIZO:'OTROS', CUMPLEANIOS:'OTROS', CUMPLEAÑOS:'OTROS', EMPRESARIAL:'OTROS',
  GRADUACION:'OTROS', 'GRADUACIÓN':'OTROS', OTRO:'OTROS', OTROS:'OTROS',
};
const EV_SUF = { BODA: ' para boda', XV: ' para XV años', OTROS: '' };

// ── Bloques canónicos (detect-and-swap, igual que los salesbots de Kommo) ──
const SALUDO_PARTES = [
  'Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀',
  'Me podría decir de que es su evento? ',
  '🤵👰 - Boda\n🎂🥳 - XV Años\n👼🏢 - Otros',
];
// Verbatim del salesbot 60958. La línea 2 es UN espacio, no está vacía.
// Preserva los errores del original: COTIZACION/PRODUCCION sin tilde, "Hace el",
// y el punto extra después de 🛠️.
const SIETE_PASOS = '*¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀\n \n1. *COTIZACION de los PRODUCTOS que requiere para su PEDIDO*\n2. Se requiere del *50% de ANTICIPO* para desarrollar los diseños.\n3. *Elige tu DISEÑO favorito* 🎨 y proporciona los *DATOS* que deseas incluir.\n4. Mandamos la *MUESTRA DIGITAL* para tu aprobación o cambios ✏️.\n5. Una vez *AUTORIZADO, COMENZAMOS LA PRODUCCION*, son *15 DIAS EN PRODUCCION*. 🛠️.\n6. Al terminar, te enviamos una *FOTO DEL PRODUCTO* para que confirmes que todo está perfecto 📸.\n7. Hace el *PAGO FINAL* y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días).';
// Verbatim del nodo actualizar23. Conserva ¿ ¡ y la línea en blanco: no pasaba por el filtro.
const CTA_DATOS = (fem) => '¿Le interesa sumarl' + (fem ? 'as' : 'os') + ' a la cotización?\nDígame:\n- Cantidad\n- Código postal\n\n¡Gracias!';
const GRUPOS_FEMENINOS = ['sandalia', 'pantufla', 'tapa', 'bolsa', 'correa15', 'correa9', 'tinta'];

// ── Helpers ───────────────────────────────────────────────────────────────
const ABREV = /(?:^|\s)(?:sr|sra|dr|dra|av|no|núm|num|pág|c\/u|aprox|ej|etc|c\.p|p\.ej)\.?$/i;
const S = (v) => (v === undefined || v === null) ? '' : String(v);
function nodo(nombre, ruta, def) {
  try {
    let v = $(nombre).first().json;
    for (const k of ruta) { if (v == null) return def; v = v[k]; }
    return v == null ? def : v;
  } catch (e) { return def; }
}
// El filtro del original: astral + variation selectors + ZWJ. NO colapsa
// espacios, así que quedan huecos dobles donde había un emoji — igual que antes.
function stripAstral(s) {
  return S(s)
    .replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, '')
    .replace(/[︎️]/g, '')
    .replace(/‍/g, '');
}
function filtrarLibre(s) {
  return stripAstral(S(s).replace(/[¿¡]/g, '').replace(/\n{2,}/g, '\n'))
    .split('\n').map(l => l.replace(/\s+$/,'')).join('\n').trim();
}
const porId  = (id)  => CATALOGO.find(e => e.id === id) || null;
const normEv = (raw) => ALIAS[S(raw).trim().toUpperCase()] || (S(raw).trim() ? 'OTROS' : '');
const fichaDe = (e, ev) => e.f.replace('{EV}', EV_SUF[ev] !== undefined ? EV_SUF[ev] : '');

// Matchea un texto contra el catálogo: 1 item por grupo, el más específico gana,
// en orden de aparición.
function matchCatalogo(txt, ev) {
  const p = S(txt).toLowerCase();
  const vistos = new Set(); const res = [];
  for (const e of CATALOGO) {
    if (vistos.has(e.g)) continue;
    if (e.ev && ev && e.ev.indexOf(ev) === -1) continue;
    const hit = e.k.find(kw => p.indexOf(kw) !== -1);
    if (!hit) continue;
    vistos.add(e.g);
    res.push({ e, pos: p.indexOf(hit) });
  }
  return res.sort((a, b) => a.pos - b.pos).map(x => x.e);
}

// ── E1 · Intenciones desde las tool calls reales ───────────────────────────
function leerSteps(steps) {
  const out = { productos: [], evento: '' };
  if (!Array.isArray(steps)) return out;
  for (const s of steps) {
    const a = (s && (s.action || s)) || {};
    const tool = S(a.tool || a.toolName || a.name).toUpperCase();
    let ti = a.toolInput !== undefined ? a.toolInput : (a.input !== undefined ? a.input : a.args);
    if (typeof ti === 'string') { try { ti = JSON.parse(ti); } catch (e) { ti = { productos: ti, evento: ti }; } }
    if (!ti || typeof ti !== 'object') ti = {};
    if (tool === 'MOSTRAR_PRODUCTOS') {
      const raw = S(ti.productos !== undefined ? ti.productos : (ti.query !== undefined ? ti.query : Object.values(ti).join(', ')));
      if (raw) out.productos.push(raw);
    } else if (tool === 'IDENTIFICAR_EVENTO') {
      const raw = S(ti.evento !== undefined ? ti.evento : Object.values(ti).join(' '));
      if (raw && !out.evento) out.evento = raw;
    }
  }
  return out;
}
const intenciones = leerSteps(agent.intermediateSteps);

let text = S(agent.output);

// ── E2 · Marcadores legacy: se capturan y se sacan del texto ───────────────
let eventoMarcador = '';
text = text.replace(/\[IMAGEN:\s*([^\]]+)\]/gi, (_, ev) => { eventoMarcador = S(ev).trim(); return ''; });
const fotosMarcador = [];   // { idx: nº de línea, id }

// ── E3 · Evento: cascada determinística ────────────────────────────────────
const eventoPrevio = normEv(
  nodo('Mapear Custom Fields', ['custom_fields', 'evento_detectado'],
    nodo('Auth + Normalize', ['custom_fields', 'evento_detectado'], ''))
);
const mensajeLead = S(nodo('Combine Messages', ['message_text'], nodo('Auth + Normalize', ['message_text'], '')));
function eventoHeuristica(m) {
  if (/\bbodas?\b/i.test(m)) return 'BODA';
  if (/\bxv\b|quince|15\s*a[ñn]os/i.test(m)) return 'XV';
  return '';
}
const eventoTool = normEv(intenciones.evento);
const evento = eventoTool || eventoPrevio || normEv(eventoMarcador) || eventoHeuristica(mensajeLead) || 'OTROS';
const eventoReciente = !!(eventoTool || eventoMarcador) && !eventoPrevio;

// ── Fichas pedidas ─────────────────────────────────────────────────────────
const yaMostrados = S(nodo('Mapear Custom Fields', ['custom_fields', 'productos_mostrados'], ''));
const pidioDeNuevo = /\b(foto|fotos|imagen|im[aá]genes|mu[eé]stra|mu[eé]strame|ver|otra vez|de nuevo|reenv[ií])\b/i.test(mensajeLead);
let fichas = [];   // se completa tras la segmentación (capa tool + capa marcador)
for (const raw of intenciones.productos) {
  for (const e of matchCatalogo(raw, evento)) if (fichas.indexOf(e) === -1) fichas.push(e);
}

// ── SALUDO · detect-and-swap total (replica If24 → Saludo PTE 1/2/3) ───────
if (text.indexOf('👼🏢') !== -1) {
  return SALUDO_PARTES.map(p => ({ message_part: p, photo_url: '' }));
}

// ── E4 · Normalización estructural ─────────────────────────────────────────
text = text.trim();
if ((text.startsWith('"') && text.endsWith('"')) || (text.startsWith("'") && text.endsWith("'"))) text = text.slice(1, -1);
text = text.replace(/\*\*/g, '*').replace(/^#{1,6}\s*/gm, '');
text = text.split('\n').filter(l => !/\bkg\b|\bpeso\b|\bkilogramos?\b/i.test(l)).join('\n');
const TEL_OFICIAL = '3315948670';
text = text.replace(/\b\d{7,10}\b/g, (m) => (m === TEL_OFICIAL ? m : ''));

// ── E5 · Guillotina de CTA agresivos ──────────────────────────────────────
// Regla explícita del splitter original: "pueden sonar agresivas, queremos que
// salga del usuario la iniciativa".
const CTA_AGRESIVOS = [
  /(?:^|\s)(?:o\s+)?(?:te|le)\s+gustar[íi]a\s+ver\s+(?:los\s+)?dise[ñn]os\s+disponibles\s*\??/gi,
  /(?:^|\s)(?:o\s+)?(?:te|le)\s+gustar[íi]a\s+cotizar\s+una\s+cantidad\s+espec[íi]fica\s*\??/gi,
  /(?:^|\s)(?:o\s+)?quieres?\s+cotizar\s+una\s+cantidad\s+espec[íi]fica\s*\??/gi,
];
text = text.split('\n').map(linea => {
  let l = linea;
  for (const re of CTA_AGRESIVOS) l = l.replace(re, ' ');
  if (l !== linea) l = l.replace(/^\s*(si\s+s[íi]|si\s+es\s+as[íi]|de\s+ser\s+as[íi])\s*,?\s*/i, '');
  return l.replace(/\s{2,}$/, '').replace(/^\s+/, '');
}).join('\n');

// ── E6 · Segmentar en bloques atómicos vs libres ──────────────────────────
const RE_COTIZ_ABRE = /(?:^|\s)cotizaci[óo]n\s*:\s*$|⏳|7 DIAS DE PROMO/i;
const RE_COTIZ_LINEA = /x\s*\$|^\s*\*?(Total|Env[íi]o|Anticipo|Subtotal)\*?\s*[:(]/i;
const RE_SIETE = /HAZ TU PEDIDO EN 7 SENCILLOS PASOS/i;
const RE_SIETE_LINEA = /^\s*\d+[.)]\s|MUESTRA DIGITAL|PAGO FINAL|FOTO DEL PRODUCTO|COTIZACION de los|ANTICIPO para desarrollar|SENCILLOS PASOS/i;
const RE_CTA_DATOS = /interesa\s+sumarl|^\s*d[íi]game\s*:?\s*$|^\s*-\s*(cantidad|c[óo]digo postal)\s*$|^\s*¡?gracias!?\s*$/i;
const RE_FIJOS = /ESTAFETA, FEDEX y PAQUETEXPRESS|facebook\.com\/happyflops|referencias de confianza|Vis[íi]tanos en Facebook|hacemos env[íi]os a todo M[ée]xico|SEMANA LOCA/i;
const esAtomica = (l) => RE_COTIZ_ABRE.test(l) || RE_COTIZ_LINEA.test(l) || RE_SIETE.test(l) || RE_SIETE_LINEA.test(l) || RE_CTA_DATOS.test(l) || RE_FIJOS.test(l);

const lineas = text.split('\n');
const bloques = [];
let buf = [], tipoBuf = null;
const cerrar = () => { if (buf.length) { const s = buf.join('\n').replace(/^\n+|\n+$/g, ''); if (s.trim()) bloques.push({ tipo: tipoBuf, text: s }); } buf = []; tipoBuf = null; };
for (let i = 0; i < lineas.length; i++) {
  let l = lineas[i].replace(/\s+$/, '');
  // marcador de foto: fija la posición de la ficha, no decide cuál
  l = l.replace(/\[FOTO:\s*([^\]]+)\]/gi, (_, prod) => {
    const m = matchCatalogo(prod, evento)[0];
    if (m) fotosMarcador.push({ bloque: bloques.length, id: m.id });
    return '';
  }).replace(/\s+$/, '');
  if (!l.trim()) {
    if (tipoBuf === 'atomico') {
      let j = i + 1; while (j < lineas.length && !lineas[j].trim()) j++;
      if (j < lineas.length && esAtomica(lineas[j])) { buf.push(''); continue; }
    }
    cerrar(); continue;
  }
  const t = esAtomica(l) ? 'atomico' : 'libre';
  if (tipoBuf !== null && t !== tipoBuf) cerrar();
  tipoBuf = t; buf.push(l);
}
cerrar();

// Capa marcador: si el LLM escribió [FOTO:x] y la tool no lo pidió, igual va.
for (const m of fotosMarcador) { const e = porId(m.id); if (e && fichas.indexOf(e) === -1) fichas.push(e); }
// 1 ficha por grupo, y nunca re-enviar algo que el lead ya vio (salvo que lo pida)
const gruposVistos = new Set();
fichas = fichas.filter(e => { if (gruposVistos.has(e.g)) return false; gruposVistos.add(e.g); return true; });
if (yaMostrados && !(REENVIAR_SI_PIDE_EXPLICITO && pidioDeNuevo)) {
  const prev = yaMostrados.toLowerCase();
  fichas = fichas.filter(e => !e.k.some(kw => prev.indexOf(kw) !== -1));
}

// ── E7 · CORTE DEL FILTRO: aplica a todo lo que escribió el LLM ───────────
for (const b of bloques) b.text = filtrarLibre(b.text);

// ── E8 · Detect-and-swap de los bloques pre-horneados ─────────────────────
// Si vamos a inyectar el CTA canónico, el LLM no tiene que pedir los mismos datos.
const RE_PIDE_DATOS = /(?:necesit\w*|d[ií]game|me\s+(?:diga|pasa|confirma)|indicar\w*|proporcion\w*|me\s+puede\s+pasar)[^.!?]*\b(cantidad|cu[áa]nt\w+|c[óo]digo\s+postal|\bcp\b)[^.!?]*[.!?]?/gi;
const RE_ANUNCIA_FOTO = /un momento|enseguida|permíta|perm[ií]tame|ya (?:le|te) (?:paso|mando|env[íi]o|muestro|comparto)|(?:le|te) (?:paso|mando|comparto) las (?:fotos|im[áa]genes)|a continuaci[óo]n/i;
const habraCTA = fichas.length > 0 && fichas.slice(0, MAX_FOTOS).some(e => e.tipo === 'principal');
let ctaYaEscrito = false;
const bloquesFinal = [];
for (const b of bloques) {
  if (!b.text.trim()) continue;
  if (RE_SIETE.test(b.text)) {
    const m = b.text.match(/\*?¡?HAZ TU PEDIDO EN 7 SENCILLOS PASOS/i);
    const antes = b.text.slice(0, m.index).replace(/[*\s]+$/, '');
    if (antes.trim()) bloquesFinal.push({ tipo: b.tipo, text: antes });
    bloquesFinal.push({ tipo: 'canon', text: SIETE_PASOS });
    continue;
  }
  if (/interesa\s+sumarl/i.test(b.text)) { ctaYaEscrito = true; continue; }   // se re-inyecta al final
  if (habraCTA && b.tipo === 'libre') {
    b.text = b.text.replace(RE_PIDE_DATOS, '');
    // el CTA canónico ya pregunta: fuera las preguntas del LLM y los anuncios de foto
    b.text = partirOraciones(b.text.replace(/\n+/g, ' '))
      .filter(o => !/\?\s*$/.test(o.trim()) && !RE_ANUNCIA_FOTO.test(o))
      .join(' ').replace(/\s{2,}/g, ' ').trim();
    if (!b.text) continue;
  }
  bloquesFinal.push(b);
}

// ── E9 · Splitter determinístico (replica Message a model1) ───────────────
function partirOraciones(p) {
  const out = []; let cur = '';
  const toks = p.split(/(?<=[.!?…])\s+/);
  for (const t of toks) {
    cur = cur ? cur + ' ' + t : t;
    const sinCierre = /\d[.,]$/.test(cur) || ABREV.test(cur) || /https?:\/\/\S*$/.test(cur);
    if (!sinCierre && /[.!?…]$/.test(cur)) { out.push(cur); cur = ''; }
  }
  if (cur.trim()) out.push(cur);
  const res = [];
  for (const x of out.filter(y => y.trim())) {
    if (!/[a-záéíóúñü]/i.test(x) && res.length) res[res.length - 1] += ' ' + x.trim();
    else res.push(x);
  }
  return res;
}
let burbujas = [];
for (const b of bloquesFinal) {
  if (b.tipo !== 'libre') { burbujas.push({ text: b.text, atomica: true }); continue; }
  for (const parrafo of b.text.split(/\n{2,}/)) {
    const lineasP = parrafo.split('\n');
    const esLista = lineasP.length > 1 && lineasP.every(l => /^\s*[-*·•]|^\s*\d+[.)]\s/.test(l));
    if (esLista) { burbujas.push({ text: parrafo, atomica: false }); continue; }
    const sents = partirOraciones(parrafo.replace(/\n/g, ' '));
    if (sents.length <= 2) { burbujas.push({ text: sents.join(' ') || parrafo, atomica: false }); }
    else {
      const mitad = Math.ceil(sents.length / 2);
      burbujas.push({ text: sents.slice(0, mitad).join(' '), atomica: false });
      burbujas.push({ text: sents.slice(mitad).join(' '), atomica: false });
    }
  }
}
burbujas = burbujas.filter(b => b.text && b.text.trim());
// tope: fusiona el último par adyacente de burbujas libres
while (burbujas.length > MAX_BURBUJAS) {
  let i = -1;
  for (let k = burbujas.length - 2; k >= 0; k--) if (!burbujas[k].atomica && !burbujas[k + 1].atomica) { i = k; break; }
  if (i === -1) break;
  burbujas[i].text = (burbujas[i].text + '\n' + burbujas[i + 1].text).trim();
  burbujas.splice(i + 1, 1);
}
// "que ninguna parte termine en un punto" — solo texto libre
for (const b of burbujas) {
  if (b.atomica) continue;
  b.text = b.text.replace(/(?<![.\d])\.$/, '');
}

// ── E10 · Ensamblado: texto + fichas + CTA + imagen de evento ─────────────
let out = burbujas.map(b => ({ message_part: b.text, photo_url: '' }));
const fichasFinal = fichas.slice(0, MAX_FOTOS);
if (fichasFinal.length) {
  const msgs = fichasFinal.map(e => ({ message_part: fichaDe(e, evento), photo_url: e.u || '' }));
  const insertar = out.length ? 1 : 0;   // después de la frase de contexto del LLM
  out = out.slice(0, insertar).concat(msgs, out.slice(insertar));
  const principales = fichasFinal.filter(e => e.tipo === 'principal');
  if (principales.length) {
    const fem = principales.every(e => GRUPOS_FEMENINOS.indexOf(e.g) !== -1);
    out.push({ message_part: CTA_DATOS(fem), photo_url: '' });
  }
} else if (ctaYaEscrito) {
  out.push({ message_part: CTA_DATOS(false), photo_url: '' });
}
if (eventoReciente) {
  const ev = IMAGENES[evento] ? evento : 'OTROS';
  const cabecera = [{ message_part: PROMO, photo_url: '' }, { message_part: CAPTION_EVENTO[ev], photo_url: IMAGENES[ev] }];
  out = fichasFinal.length ? cabecera.concat(out) : cabecera;   // el original no mandaba nada más en ese turno
}

// ── E11 · Guards ──────────────────────────────────────────────────────────
if (!out.length) { const t = filtrarLibre(text); if (t) out = [{ message_part: t, photo_url: '' }]; }
const final = [];
for (const p of out) {
  const url = p.photo_url || ''; const txt = S(p.message_part);
  if (url && txt.length > 1000) {   // Telegram rechaza caption > 1024 y mata la ejecución
    let corte = txt.lastIndexOf(' ', 1000); if (corte < 500) corte = 1000;
    final.push({ message_part: txt.slice(0, corte), photo_url: url });
    final.push({ message_part: txt.slice(corte).trim(), photo_url: '' });
  } else final.push({ message_part: txt, photo_url: url });
}
return final.filter(p => p.message_part || p.photo_url);
