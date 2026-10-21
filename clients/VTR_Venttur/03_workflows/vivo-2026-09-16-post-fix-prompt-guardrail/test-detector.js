// Test harness para el detector · valida con 12 casos golden en Node local.
// Simula el context n8n: $input.first() y $('Buscar si ya existe').first().

const fs = require('fs');
const detectorCode = fs.readFileSync('/tmp/vtr-diagnose/detectar-promesa-fantasma.js', 'utf8');

function runDetector(item, leadData) {
  const $input = { first: () => item };
  const $ = (name) => ({ first: () => leadData });
  const fn = new Function('$input', '$', `${detectorCode}`);
  return fn($input, $);
}

const LEAD_NAHE = { 'Nombre': 'Nahe', 'Programa interés': 'AA Familiar IA' };
const LEAD_INT  = { 'Nombre': 'María', 'Programa interés': 'Boarding School' };

const cases = [
  // PASS-THROUGH ESPERADO
  { name: 'C1 · mensaje con link ya presente',
    input: { parte1: 'Perfecto, María', parte2: 'Te dejo el link: promo.venttur.com/agendar-ema', parte3: 'Elegís horario' },
    lead: LEAD_INT, expect: 'pass' },
  { name: 'C2 · solo saludo',
    input: { parte1: '¡Hola Nahe!', parte2: '¿Cómo estás?', parte3: '' },
    lead: LEAD_NAHE, expect: 'pass' },
  { name: 'C3 · explicación sin coordinación',
    input: { parte1: 'Los internados incluyen deportes y hospedaje en campus', parte2: 'Rondan entre USD 50k y 130k', parte3: '¿Qué te llama más de esa experiencia?' },
    lead: LEAD_INT, expect: 'pass' },
  { name: 'C4 · coordinar PROGRAMA (no cita)',
    input: { parte1: 'Buenísimo', parte2: 'Podemos coordinar qué programa se ajusta mejor a su perfil', parte3: '¿Qué edad tiene tu hijo?' },
    lead: LEAD_INT, expect: 'pass' },
  { name: 'C5 · "hoy es martes" sin coordinar',
    input: { parte1: 'Hoy revisamos algunas opciones juntos', parte2: '', parte3: '' },
    lead: LEAD_INT, expect: 'pass' },
  { name: 'C6 · confirm sin tiempo',
    input: { parte1: 'Podés confirmar la asesoría a través del link', parte2: '', parte3: '' },
    lead: LEAD_INT, expect: 'pass' },

  // INTERCEPT ESPERADO — casos reales de Nahe
  { name: 'C7 · Nahe turno 19 (verbatim)',
    input: {
      parte1: 'Claro, Nahe',
      parte2: 'Voy a coordinar para que tengas la asesoría el lunes a las 11',
      parte3: 'Te confirmo el horario lo antes posible'
    },
    lead: LEAD_NAHE, expect: 'intercept' },
  { name: 'C8 · Nahe turno 35 (verbatim)',
    input: {
      parte1: 'Perfecto, Nahe',
      parte2: 'Entonces coordinamos la llamada para mañana a las 9 de la mañana',
      parte3: 'Me aseguraré de que todo esté listo'
    },
    lead: LEAD_NAHE, expect: 'intercept' },
  { name: 'C9 · Nahe turno 29 (verbatim)',
    input: {
      parte1: 'Lamento mucho la confusión',
      parte2: '¿Te parece bien si coordinamos una nueva llamada para esta semana?',
      parte3: 'Dime qué día prefieres'
    },
    lead: LEAD_NAHE, expect: 'intercept' },
  { name: 'C10 · "quedamos mañana a las 9"',
    input: {
      parte1: 'Genial',
      parte2: 'Quedamos entonces para mañana a las 9',
      parte3: ''
    },
    lead: LEAD_NAHE, expect: 'intercept' },
  { name: 'C11 · "programar la llamada"',
    input: {
      parte1: '',
      parte2: 'Podemos programar la llamada para mañana a una hora que te acomode',
      parte3: 'Dime qué prefieres'
    },
    lead: LEAD_INT, expect: 'intercept' },
  { name: 'C12 · "te confirmo el horario a las 11 mañana"',
    input: {
      parte1: 'Perfecto',
      parte2: 'Te confirmo el horario de la asesoría mañana a las 11',
      parte3: ''
    },
    lead: LEAD_NAHE, expect: 'intercept' },
];

let ok = 0, fail = 0;
for (const c of cases) {
  const out = runDetector({ json: c.input }, c.lead);
  const intercepted = !!out.json._phantom_promise_intercepted;
  const gotExpected = (c.expect === 'intercept') === intercepted;
  const status = gotExpected ? '✅' : '❌';
  if (gotExpected) ok++; else fail++;
  console.log(`${status} ${c.name}: ${intercepted ? 'INTERCEPT' : 'pass'} (esperado: ${c.expect})`);
  if (!gotExpected) {
    console.log(`   INPUT: ${JSON.stringify(c.input)}`);
    console.log(`   OUTPUT: ${JSON.stringify(out.json)}`);
  } else if (intercepted) {
    console.log(`   → URL: ${out.json._phantom_url} · experto: ${out.json._phantom_experto}`);
    console.log(`   → parte1: "${out.json.parte1.slice(0,100)}"`);
    console.log(`   → parte2: "${out.json.parte2}"`);
  }
}
console.log(`\n${ok}/${ok+fail} OK · ${fail} fallos`);
process.exit(fail > 0 ? 1 : 0);
