# Mensaje único a Mauricio — enviado 21/9

**Enviado por WhatsApp al chat de Venttur** el lunes 21/9/2026.

## Mensaje enviado (versión final · reemplaza cualquier draft previo)

```
@Mauricio Garcia cómo va? Te actualizo rápido

Este fin de semana surgieron un par de inconvenientes técnicos con las landings que ya resolvimos, y estamos terminándolas hoy. En paralelo, hoy mismo hacemos el traspaso del WABA a GHL nosotros directamente (sí, *no* hace falta que hagan nada de su lado) ✅

🔴 Solo una cosa CRÍTICA: *no* tengan (ni instalen) la app de whatsapp en el celular con ese número

Cuando me confirmes eso, lo único pendiente de su lado sería que @~Rodrigo García y @~Andrés García conecten sucalendar personal a GHL: Configuración → Integraciones → Conectar Google Calendar

Cronograma: hoy WABA + landings, mañana martes hasta el viernes monitoreamos y el sábado 26 apagamos clientify

Quedamos atentos por cualquier consulta 🤝
```

## Contexto de decisiones · qué NO se pidió (por diseño)

la agencia decidió simplificar vs draft interno. Estos accionables no se pidieron y se resuelven de otra forma:

| Draft interno | Decisión enviada | Consecuencia |
|---|---|---|
| Dominio destino GHL (promo.venttur.com vs otro) | No pedido | Se asume `promo.venttur.com` (heredado Clientify) por default. Flip CNAME viernes 25/9 §L2. |
| Slugs canónicos aventureras | No pedido | "Se dan por confirmados, editables después" (la agencia 21/9). |
| Fallback calendarios (test C1/C2) | No pedido | Mecanismo A ya confirmado en test C1 21/9 (§5.2). No hay fallback que aplicar. |
| Mails Mauricio + Max + chat_id Telegram | No pedido | Handoff §C queda con **solo Telegram fallback** (`botla agencia`). Email queda como upgrade post-cutover si Mauricio los provee. |
| Precios/textos programas huérfanos | No pedido | Bot responde "consulta con asesor" para Viajes/Ed.Superior/Cursos idiomas hasta que lleguen. Degradación aceptable. |

## Únicos accionables pedidos al cliente

1. **Confirmar "no instalar app WhatsApp"** en celular con `+52 1 33 2627 4502`.
2. **Rodrigo + Andrés conectan Google Calendar personal a GHL** (2 min cada uno).

## Cronograma comunicado

- Lunes 21/9 (hoy): WABA + landings.
- Martes 22/9 → viernes 25/9: watch mode con Clientify vivo (rollback available).
- Sábado 26/9: apagar Clientify EOD.

**Nota interna:** el apagado se corrió del domingo 27/9 (plan original) → sábado 26/9. Watch mode: 4-5 días (martes-viernes + primeras horas sábado).
