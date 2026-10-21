# Pendientes para Producción — Stark Supplements

Lista de tareas para dejar al agente al 100%. Prioridad: poner en producción lo antes posible.

---

## BLOQUEO: Cobro

- [ ] **Cobrar USD 1.500 del build** — no poner en producción hasta que paguen
- [ ] **Cobrar primera transferencia de mantenimiento** — acordar monto y forma de pago
- [ ] **Educar al cliente sobre qué incluye mantenimiento** — Cristian no sabe qué es, hay que explicárselo

---

## Crítico: Bots de Kommo (borrados por el cliente)

- [ ] **Reconstruir TODOS los bots en Kommo** — los borraron por 6ta vez. Incluye:
  - [ ] Bot de bienvenida (bot_id: 77760)
  - [ ] Bot de envío de mensajes principal (bot_id: 85808)
  - [ ] Bots de cada producto unitario (cada uno tiene su `bot_id` en Airtable para enviar fotos)
  - [ ] Bots de cada pack
  - [ ] Bots de ubicaciones (4 sucursales: Santa Cruz Equipetrol, La Paz Torres Mall, La Paz Calacoto, Cochabamba Zafiro) — cada uno envía horarios + imagen + link Google Maps
  - [ ] Bot de Shaker (colores)
- [ ] **Hacer backup de bots via API de Kommo** — para tener registro si los vuelven a borrar. Traer ID del bot, texto, contenido. (la agencia hizo algo similar en migración de Happy Flops)
- [ ] **Reclamar al cliente** que dejen de borrar bots. Decirles que hay >50 bots corriendo en simultáneo.

---

## Crítico: Workflows pendientes

- [ ] **Cablear el workflow "Elevar Conversación"** — los 4 nodos PATCH (PAGO_PENDIENTE, QUIERE_HUMANO_O_TIENDA, SALUD_SENSIBLE, RECLAMO_O_CASO_ESPECIFICO) existen pero están **desconectados**. Hay que:
  - Agregar un Switch/IF que rutee por `motivo_bucket`
  - Conectar cada rama a su nodo PATCH correspondiente
  - Conectar la salida de cada PATCH al nodo de respuesta
- [ ] **Mapear variables de elevación** — el prompt del agente ya identifica los 4 buckets, pero las variables en el sub-workflow de elevar no están mapeadas a los pipelines/status correctos de Kommo

---

## Mejoras técnicas identificadas

- [ ] **Eliminar nodo redundante de "última interacción"** — el nodo `GET_PREVIOUS_INTERACTION` que trae la última interacción es redundante porque el `IF` ya puede verificar si existe con el resultado del query de las 8 interacciones. Juampi estuvo de acuerdo en eliminarlo.
- [ ] **Agregar precio al formato del Code node del Tool Verificar Producto** — actualmente el agente matcher no recibe precio en el texto formateado de productos. Si el usuario dice "más barato" o "más caro", el agente no puede comparar. Hay que sumar `Precio` al string de cada producto en el nodo de JavaScript que limpia los datos de Airtable.
- [ ] **Token JWT hardcodeado en All_Data** — hay un token de Kommo API hardcodeado en el nodo. Moverlo a una credencial o variable de entorno.

---

## Configuración de Kommo

- [ ] **Pedirle al cliente que separe los e-commerce en cuentas Kommo distintas** — tienen todos los negocios en `criscapitalbrothers.kommo.com`, lo cual cruza webhooks (mismo problema que Happy Flops)
- [ ] **Obtener contraseñas actualizadas de Kommo** — las cambiaron post-hackeo. Pedir al cliente cuando la agencia entre al grupo.
- [ ] **Verificar que los pipelines sigan existiendo** en Kommo:
  - Pipeline IA: 11622596
  - Seguimientos: 13155539 / status 101442331
  - Perdidos: 13155539 / status 143
  - Atención personalizada: status 100395523
- [ ] **Verificar campo custom 1717536** siga existiendo (el cliente podría haberlo borrado también)

---

## Datos por recibir

- [ ] **Manual de ventas** del cliente (Juampi lo tiene, debe pasarlo)
- [ ] **Catálogos de producto** actualizados
- [ ] **Acceso a Airtable** (base `appuXkgI7RaGv3Tjp`)
- [ ] **Links de Google Maps** de las 4 sucursales (para reconstruir los bots de ubicación)
- [ ] **Horarios de cada sucursal**
- [ ] **Imágenes de ubicaciones** (para los bots de Kommo)

---

## Limpieza

- [ ] **Revisar workflows obsoletos en n8n** — hay muchos flujos de prueba. Sacar screenshot antes de borrar.
- [ ] **Activar los 4 workflows** — todos están en `active: false` actualmente

---

## Presentación al cliente

- [ ] **la agencia se presenta en el grupo** (mañana del handoff, 2026-05-11)
- [ ] **Insistir diariamente** hasta obtener respuesta — "con el cuchillo entre los dientes"
