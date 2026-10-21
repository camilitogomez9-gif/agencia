// ── Sanitize + Split Output (v3 — fotos determinísticas) ───────────────────────
// CAMBIO CLAVE vs v2: la foto ya NO depende de que el LLM escriba el marcador
// [FOTO:...]. Se deriva de la tool call REAL a MOSTRAR_PRODUCTOS, que queda en
// $json.intermediateSteps (requiere "Return Intermediate Steps" ON en el agente).
// El marcador sigue funcionando como refuerzo y para emparejar foto <-> línea.

const agent = $json;
let text = agent.output || '';

const IMAGENES = {
  BODA:  'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/94d1527d-83d1-40e2-bfac-05dd969c3ea7.jpg',
  XV:    'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/136d7ce1-0487-4767-a408-16742a068939.jpg',
  OTROS: 'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/10880c83-56c2-4ee3-b30d-71e910093962.jpg',
};
const ALIAS = { BODA:'BODA', XV:'XV', 'XV AÑOS':'XV', 'XVAÑOS':'XV',
  BAUTIZO:'OTROS', CUMPLEANIOS:'OTROS', CUMPLEAÑOS:'OTROS', EMPRESARIAL:'OTROS', OTRO:'OTROS', OTROS:'OTROS' };

// g = grupo (para no mandar 2 fotos del mismo producto). Orden = de más específico a más genérico.
const FOTOS_PRODUCTO = [
  { g:'pantufla', t:'*Pantuflas moño peluche*',  k:['peluche'],                                                     u:'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3e0e0316cbe00f334c.jpeg' },
  { g:'pantufla', t:'*Pantuflas moño satín*',    k:['mono satin','moño satin','moño satín','mono satín'],           u:'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3ffb06386edeb05b71.jpeg' },
  { g:'pantufla', t:'*Pantuflas*',               k:['pantufla','pantuflas'],                                        u:'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3cdf29341f4d8b2f6f.png' },
  { g:'sandalia', t:'*Sandalias*',               k:['sandalia','chancla','ojota','huarache','chancleta'],            u:'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf41b86ae4203405cbf9.jpeg' },
  { g:'mandil',   t:'*Mandiles*',                k:['mandil'],                                                      u:'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3eb86ae4203405cbc1.png' },
  { g:'kit',      t:'*Kit anticruda*',           k:['anticruda','anti cruda','kit','costal','costalito'],            u:'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3df9c6f6a920d2e198.png' },
  { g:'cilindro', t:'*Cilindros 500ml*',         k:['cilindro','termo','bule'],                                     u:'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf3df7d31b0eb454cf57.png' },
  { g:'vaso',     t:'*Vasos popote 24oz*',       k:['vaso','popote'],                                               u:'https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a62bf42ca81015f1c93cf8d.jpeg' },
];
const porUrl = (url) => FOTOS_PRODUCTO.find(e => e.u === url) || null;

// Devuelve la URL del match MÁS ESPECÍFICO (recorre de específico a genérico).
function buscarFoto(nombre) {
  const p = String(nombre || '').toLowerCase();
  if (!p) return null;
  for (const e of FOTOS_PRODUCTO) if (e.k.some(kw => p.includes(kw))) return e.u;
  return null;
}

// Todas las fotos mencionadas en un texto, 1 por grupo, en orden de aparición.
function fotosEnTexto(nombre) {
  const p = String(nombre || '').toLowerCase();
  const res = [];
  const grupos = new Set();
  for (const e of FOTOS_PRODUCTO) {
    if (grupos.has(e.g)) continue;
    const hit = e.k.find(kw => p.includes(kw));
    if (!hit) continue;
    grupos.add(e.g);
    res.push({ url: e.u, pos: p.indexOf(hit) });
  }
  return res.sort((a, b) => a.pos - b.pos).map(x => x.url);
}

// ── CAPA 1 (determinística): qué productos pidió mostrar la tool ──────────────
function urlsDesdeTool(steps) {
  if (!Array.isArray(steps)) return [];
  const urls = [];
  for (const s of steps) {
    const a = (s && (s.action || s)) || {};
    const tool = String(a.tool || a.toolName || a.name || '').toUpperCase();
    if (tool !== 'MOSTRAR_PRODUCTOS') continue;
    const ti = a.toolInput ?? a.input ?? a.args ?? '';
    let raw = '';
    if (typeof ti === 'string') raw = ti;
    else if (ti && typeof ti === 'object') {
      raw = String(ti.productos ?? ti.query ?? ti.input ?? Object.values(ti).join(', '));
    }
    for (const u of fotosEnTexto(raw)) if (!urls.includes(u)) urls.push(u);
  }
  return urls;
}
const urlsTool = urlsDesdeTool(agent.intermediateSteps);

// ── Imagen de evento por marcador [IMAGEN:evento] ─────────────────────────────
let eventoImg = null;
text = text.replace(/\[IMAGEN:\s*([^\]]+)\]/gi, (_, ev) => {
  eventoImg = ALIAS[String(ev).trim().toUpperCase()] || 'OTROS';
  return '';
});

text = text.trim();
if ((text.startsWith('"') && text.endsWith('"')) || (text.startsWith("'") && text.endsWith("'"))) {
  text = text.slice(1, -1);
}
text = text.replace(/\*\*/g, '*');
text = text.replace(/^#{1,6}\s*/gm, '');

const isCanon = (l) =>
  /⏳|HAZ TU PEDIDO|SENCILLOS PASOS|SEMANA LOCA|DIAS DE PROMO|MUESTRA DIGITAL|PAGO FINAL|FOTO DEL PRODUCTO|COTIZACION de los|ANTICIPO para desarrollar/i.test(l) ||
  /^\s*\d+[.)]\s/.test(l) ||
  /x\s*\$|^\s*(Total|Env[íi]o|Anticipo|Subtotal)\s*[:(]/i.test(l);

text = text.split('\n').filter(l => !/\bkg\b|\bpeso\b|\bkilogramos?\b/i.test(l)).join('\n');
text = text.split('\n').map(l => isCanon(l) ? l : l.replace(/[¿¡]/g, '')).join('\n');

const OFICIAL = '3315948670';
text = text.replace(/\b\d{7,10}\b/g, (m) => (m === OFICIAL ? m : ''));
text = text.replace(/[ \t]{2,}/g, ' ');

// ── Split en partes + CAPA 2: marcadores [FOTO:producto] ─────────────────────
const parts = [];
let buf = [], bufCanon = false;
const flush = () => { const s = buf.join('\n').trim(); if (s) parts.push({ message_part: s }); buf = []; };

for (const raw of text.split('\n')) {
  let line = raw.trim();
  if (!line) { flush(); bufCanon = false; continue; }

  let lineFoto = null;
  line = line.replace(/\[FOTO:\s*([^\]]+)\]/gi, (_, prod) => { lineFoto = buscarFoto(prod); return ''; }).trim();

  // Una línea con marcador NUNCA entra al bloque canónico: ese bloque descarta photo_url.
  if (isCanon(line) && !lineFoto) {
    if (!bufCanon) flush();
    buf.push(line); bufCanon = true;
  } else {
    if (bufCanon) { flush(); bufCanon = false; }
    if (line) {
      const part = { message_part: line };
      if (lineFoto) part.photo_url = lineFoto;
      parts.push(part);
    } else if (lineFoto) {
      parts.push({ message_part: '', photo_url: lineFoto, _soloFoto: true });
    }
  }
}
flush();

let out = parts.filter(p => p.message_part || p.photo_url);

// ── CAPA 3: adjuntar las fotos que la tool pidió y el LLM no marcó ───────────
const esCTA = (s) => /le interesa|d[íi]game|cuales te interesan|qu[ée] color|me confirma|cantidad/i.test(s || '');
const yaEstan = new Set(out.filter(p => p.photo_url).map(p => p.photo_url));

const MAX_FOTOS = 3;   // regla del prompt: máximo 3 fotos por turno

for (const url of urlsTool) {
  if (yaEstan.has(url) || yaEstan.size >= MAX_FOTOS) continue;
  const meta = porUrl(url);
  const kws = meta ? meta.k : [];
  // 1) la parte no canónica, sin foto, que menciona ese producto
  let idx = out.findIndex(p => !p.photo_url && !isCanon(p.message_part) &&
                               kws.some(k => (p.message_part || '').toLowerCase().includes(k)));
  if (idx !== -1) { out[idx].photo_url = url; yaEstan.add(url); continue; }
  // 2) si el texto no lo nombra, va como mensaje propio con su título, antes del CTA
  const nueva = { message_part: meta ? meta.t : '', photo_url: url, _auto: true };
  const ctaIdx = out.findIndex(p => esCTA(p.message_part) && !p.photo_url);
  if (ctaIdx === -1) out.push(nueva); else out.splice(ctaIdx, 0, nueva);
  yaEstan.add(url);
}

// Tope duro de fotos por turno (por si los marcadores solos ya se pasan de 3).
let vistas = 0;
for (const p of out) {
  if (!p.photo_url) continue;
  vistas++;
  if (vistas > MAX_FOTOS) p.photo_url = '';
}
out = out.filter(p => (p.message_part && !p._auto) || p.photo_url);

if (!out.length && !eventoImg) out = [{ message_part: text.trim() }];

// ── Tope de mensajes: nunca se fusiona una parte que tiene foto ──────────────
const MAX = 3;
const fotosCount = out.filter(p => p.photo_url).length;
const limite = Math.max(MAX, fotosCount + 1);
if (out.length > limite) {
  const cabeza = out.slice(0, limite - 1);
  const cola = out.slice(limite - 1);
  const conFoto = cola.filter(p => p.photo_url);
  const sinFoto = cola.filter(p => !p.photo_url);
  const mergedTxt = sinFoto.map(p => p.message_part).filter(Boolean).join('\n');
  out = cabeza.concat(conFoto);
  if (mergedTxt) {
    const ultimo = out[out.length - 1];
    if (ultimo && !ultimo.photo_url) ultimo.message_part = (ultimo.message_part + '\n' + mergedTxt).trim();
    else out.push({ message_part: mergedTxt });
  }
}

if (eventoImg) {
  const mandil = eventoImg === 'BODA' ? '*Mandiles para Boda*\n' : '';
  out.push({
    message_part: 'TENEMOS ESTOS PRODUCTOS PARA TU EVENTO:\n\n*Sandalias*\n*Cilindros*\n' +
                  mandil + '*Kit anti cruda*\n*Pantuflas*\n\nCuales te interesan?',
    photo_url: IMAGENES[eventoImg],
  });
  out.push({
    message_part: '🎉 *¡SEMANA LOCA DE PROMOS! SOLO 7 DÍAS PARA LLEVARTE TUS RECUERDITOS PERSONALIZADOS CON DESCUENTAZO* 🎉\n\n*(Pedidos solo para eventos 2026 por tema de tiempos)*',
  });
}

// Telegram rechaza sendPhoto con caption > 1024 chars (400) y eso mata la ejecución.
const final = [];
for (const p of out) {
  const url = p.photo_url || '';
  const txt = p.message_part || '';
  if (url && txt.length > 1000) {
    final.push({ message_part: txt.slice(0, 1000), photo_url: url });
    final.push({ message_part: txt.slice(1000).trim(), photo_url: '' });
  } else {
    final.push({ message_part: txt, photo_url: url });
  }
}
return final.filter(p => p.message_part || p.photo_url);
