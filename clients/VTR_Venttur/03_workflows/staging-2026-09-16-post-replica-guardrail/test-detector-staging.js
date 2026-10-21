// Test harness para el detector staging · 8 casos golden
const fs = require('fs');
const detectorCode = fs.readFileSync('/private/tmp/claude-501/-Users-la agencia-Downloads-camilo-workspace/672d2f23-98a1-44af-9e6d-14f30dcb9dac/scratchpad/detectar-promesa-fantasma-staging.js', 'utf8');

function runDetector(item, ghlContact) {
  const $input = { first: () => item };
  const $ = (name) => ({ first: () => ({ json: { contacts: ghlContact ? [ghlContact] : [] } }) });
  const fn = new Function('$input', '$', `${detectorCode}`);
  return fn($input, $);
}

const NAHE_GHL = {
  firstName: 'Nahe', lastName: '',
  customFields: [{ id: 'xK2NFqtz1DYUw3gYdn8I', value: 'AA Familiar IA' }]
};
const INT_GHL = {
  firstName: 'María', lastName: '',
  customFields: [{ id: 'xK2NFqtz1DYUw3gYdn8I', value: 'Boarding School' }]
};

const cases = [
  { name: 'C1 · output con URL canónica ya presente',
    output: 'Perfecto Nahe, te dejo el link: promo.venttur.com/AAFamilia-Agendar. Elegí día y hora.',
    contact: NAHE_GHL, expect: 'pass' },
  { name: 'C2 · saludo simple',
    output: '¡Hola Nahe! ¿En qué puedo ayudarte hoy?',
    contact: NAHE_GHL, expect: 'pass' },
  { name: 'C3 · explicación técnica sin coordinación',
    output: 'Los internados incluyen deportes y hospedaje en campus. Rondan entre USD 50k y 130k.',
    contact: INT_GHL, expect: 'pass' },
  { name: 'C4 · Nahe turno 19 verbatim (bug original)',
    output: 'Claro, Nahe. Voy a coordinar para que tengas la asesoría el lunes a las 11. Te confirmo el horario lo antes posible.',
    contact: NAHE_GHL, expect: 'intercept' },
  { name: 'C5 · "quedamos mañana a las 9"',
    output: 'Genial, Nahe. Quedamos entonces para mañana a las 9. Me aseguraré de que todo esté listo.',
    contact: NAHE_GHL, expect: 'intercept' },
  { name: 'C6 · "coordinamos la llamada esta semana"',
    output: 'Lamento mucho la confusión. ¿Te parece bien si coordinamos una nueva llamada para esta semana?',
    contact: NAHE_GHL, expect: 'intercept' },
  { name: 'C7 · "programar la llamada mañana"',
    output: 'Podemos programar la llamada para mañana a una hora que te acomode. Dime qué prefieres.',
    contact: INT_GHL, expect: 'intercept' },
  { name: 'C8 · "coordinar programa" (NO cita, no debe interceptar)',
    output: 'Buenísimo. Podemos coordinar qué programa se ajusta mejor a su perfil.',
    contact: INT_GHL, expect: 'pass' },
];

let ok = 0, fail = 0;
for (const c of cases) {
  const out = runDetector({ json: { output: c.output } }, c.contact);
  const intercepted = !!out.json._phantom_promise_intercepted;
  const gotExpected = (c.expect === 'intercept') === intercepted;
  const status = gotExpected ? '✅' : '❌';
  if (gotExpected) ok++; else fail++;
  console.log(`${status} ${c.name}: ${intercepted ? 'INTERCEPT' : 'pass'} (esperado: ${c.expect})`);
  if (intercepted && gotExpected) {
    console.log(`   → URL: ${out.json._phantom_url} · experto: ${out.json._phantom_experto}`);
    console.log(`   → output nuevo: "${out.json.output.slice(0,120)}..."`);
  } else if (!gotExpected) {
    console.log(`   INPUT: "${c.output}"`);
    console.log(`   OUTPUT: ${JSON.stringify(out.json).slice(0,200)}`);
  }
}
console.log(`\n${ok}/${ok+fail} OK · ${fail} fallos`);
process.exit(fail > 0 ? 1 : 0);
