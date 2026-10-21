# Handoff Camilo · Redirecciones de `promo.venttur.com` (29/9/2026)

Pegar el bloque de abajo como primer mensaje en una sesión de Claude Code del workspace de Camilo.

---

```
Contexto para retomar un tema de VTR (Venttur) que se cerró hoy, 29/9/2026. Leelo entero antes de tocar nada.

## Qué pasó
Desde el 28/9 promo.venttur.com apunta a GHL y es el dominio principal del funnel "LP · Calendarios".
Mauricio (Venttur) reportó que las rutas viejas de Clientify (/ema, /agendar-Miabarba-internado,
/lagarenne-CDMX-carol, etc.) en promo.venttur.com caían en 301 a /programas y perdían el atribuida_a.
Esos links siguen circulando en anuncios, WhatsApp y los de las aventureras.

Causa: GHL aplica las URL Redirects por dominio. Todas las redirecciones de la cuenta estaban
registradas con dominio vtr.[TU-DOMINIO] (el dominio de ensayo). El paso de la guía de cutover que
las crea bajo promo (B5.5: `crear-redirects-ghl.py --execute`) quedó sin correr el día del cambio de DNS.
Fue un olvido, no una decisión.

## Qué se hizo (29/9)
- Se crearon las 199 redirecciones de rutas viejas bajo el dominio promo.venttur.com, con destino en
  promo.venttur.com. Lista fuente: landings-ghl/_ghl/redirects.json (legible en REDIRECTS.md).
- Control: `verificar-landings-ghl.py --redirects --dominio promo.venttur.com` → 199 OK, 0 problemas.
- A mano: /ema → /agendar-ema · /agendar-Miabarba-internado → /Internados-Calendario?atribuida_a=MiaBarba
  · /lagarenne-CDMX-carol → /agendar-ema?atribuida_a=carol · /agendar-abuendia-afamilia →
  /Intercambio-Calendario?atribuida_a=AlinaBuendia.
- En el navegador: promo.venttur.com/ema?atribuida_a=smoke_dns_0929 termina en /agendar-ema y el iframe
  del calendario recibe ?atribuida_a=smoke_dns_0929&programa=Internados.
- No se tocó nada de vtr.[TU-DOMINIO].
- En la guía raíz (guia-recta-final-ejecutable-2026-09-20.md) el B5.5 quedó marcado como hecho.

## Estado de la cuenta después del arreglo
- vtr.[TU-DOMINIO]: 255 redirects. 197 del ensayo (destino vtr), 56 del puente vtr → promo
  (una por landing; cubre los links de vtr que el agente mandó entre el 23 y el 28/9), 2 sueltos
  (Google Docs y Railway).
- promo.venttur.com: 199 redirects de rutas viejas de Clientify.
- Las landings sólo se sirven en el dominio principal del funnel (promo). En cualquier otro dominio GHL
  manda todo a <principal>/programas, salvo que exista un redirect para esa ruta.

## Cosas que parecen bugs y no lo son
- GHL pega el query entrante con un segundo "?" cuando el destino ya tiene query:
  /agendar-Miabarba-internado?fbclid=x → /Internados-Calendario?atribuida_a=MiaBarba?fbclid=x.
  Pasa igual en vtr. Las landings (formulario y calendario) normalizan el segundo "?" a "&" antes de leer
  el query y antes de pasárselo al iframe, así que atribuida_a llega limpio. No hay que tocarlo.
- La landing /agendar-ema ya es "calendario primero" (N10 aplicado): no hay formulario propio, el
  contacto y el atribuida_a entran por el widget de reserva de GHL.

## Pendientes
1. Smoke de reserva real (B5.6): reservar en promo.venttur.com/agendar-ema?atribuida_a=smoke_dns_0929
   con el contacto de prueba, verificar en GHL atribuida_a = smoke_dns_0929 y cancelar la cita.
   ✅ HECHO 29/9: reserva real con la agencia Test en el calendario Internados (Rodrigo) → en GHL el contacto
   quedó con atribuida_a = smoke_dns_0929 (antes prueba_fb). Cita QupUT5kkXSjTSmQArvc3 cancelada por API.
   Ojo para futuros smokes: el widget de GHL pide un challenge anti-bot al enviar (y a veces responde
   "Too many requests"); lo tiene que resolver una persona.
2. Plazo de vtr.[TU-DOMINIO]: es temporal. Propuesta a Mauricio: mantenerlo 60 a 90 días como puente
   y avisar antes de darlo de baja. [confirmar si la agencia lo aprobó / fecha de baja]
3. Opcional, no urgente: repuntar los 197 redirects del ensayo en vtr para que vayan directo a promo y
   no hagan doble salto (ruta vieja en vtr → landing en vtr → puente → promo). Hoy funcionan.
4. Si Mauricio reporta una ruta vieja que no redirige: agregarla a landings-ghl/_ghl/redirects.json y
   correr de nuevo crear-redirects-ghl.py --execute (sólo crea las que faltan).

## Cómo operar los redirects
Scripts en clients/VTR_Venttur/00_migracion_ghl/05_ejecucion/scripts/:
- crear-redirects-ghl.py: sin flags es dry-run (sólo GET). --execute crea los que faltan, uno por uno
  con pausa (nunca en paralelo, GHL corta ráfagas). Se puede correr dos veces sin duplicar.
  --borrar --execute es el rollback de la lista. --dominio X apunta a otro dominio. --puente crea
  vtr → promo por landing.
- verificar-landings-ghl.py --redirects --dominio promo.venttur.com: control con curl.
API GHL: POST /funnels/lookup/redirect · GET /funnels/lookup/redirect/list?locationId=…&limit=20&offset=…
· DELETE /funnels/lookup/redirect/{id}. Credenciales en clients/VTR_Venttur/06_docs/ghl-credentials.md
(no pegarlas en chats ni en el repo).

Regla: todo lo que escribe en el GHL de Venttur se confirma con la agencia antes de correrlo.
```
