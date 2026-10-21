# Airtable — Base `SyS Catalogo` (schema v1.1)

> **Cliente:** SYS — Sistemas y Soluciones
> **Base name:** SyS Catalogo
> **Workspace:** la agencia
> **Fecha v1:** 2026-05-28 | **Fecha v1.1:** 2026-05-29 (re-alineación post-Excel)
> **Versión actual:** v1.1
> **Total tablas:** **11 en la base viva** (este doc todavía dice 12 más abajo — la tabla `Leads` documentada nunca se creó o fue borrada, ver corrección abajo)
> **Records esperados:** ~230 (catálogo real del cliente + FAQs + rep) — **real al 2026-07-01: 245 records en 11 tablas** (post-limpieza de los 37 records basura de Sustratos)
> **⚠️ Ver primero:** [Correcciones 2026-07-01](#correcciones-2026-07-01---post-auditoría-leer-antes-que-las-secciones-de-tabla) — esta doc tiene drift confirmado contra la base viva en 6 tablas. El detalle completo con evidencia está en `../06_docs/airtable-auditoria-2026-07-01.md`.

---

## Correcciones 2026-07-01 — post-auditoría (leer antes que las secciones de tabla)

> Auditoría multi-agente 2026-07-01 comparó este doc contra la base viva (API) y encontró 65 findings de drift/data quality. Esta sección resume solo las correcciones de **documentación** (qué dice esta página vs qué hay realmente) — no repite los fixes de datos/schema ya aplicados o pendientes, eso está en `airtable-auditoria-2026-07-01.md`.

| Tabla | Este doc dice | La base viva tiene realmente |
|---|---|---|
| `Equipos` | `Cabezales` = Link a tabla `Cabezales` | **3 campos escalares**: `Cabezales hasta` (number), `Cabezales incluidos` (number), `Cabezales tipo` (texto libre). No hay link a la tabla `Cabezales` — esa tabla existe pero ningún tool la consulta hoy. |
| `Equipos` | `Especificaciones técnicas` y `Imagen principal` documentados | **No existen** como campos. |
| `Equipos` | `Notas internas` = Long text | Es `singleSelect` con 4 choices basura (valores de import congelados como opciones) — no se puede escribir texto libre hoy. |
| `Cabezales` | `Equipos compatibles` = Link a `Equipos` | **No existe.** Consistente con lo de arriba: la relación Equipos↔Cabezales vive como escalares en `Equipos`, no como link bidireccional. |
| `Cabezales` | `URL tienda` = URL, `Stock disponible` = Checkbox | Ambos son `multilineText` en vivo. |
| `Insumos` | `Categoría` con 6 choices (Tinta, Film DTF, Polvo DTF, Vinilo, Papel transfer, Otros) | Solo 3 choices reales: `TINTAS`, `FILM`, `POLVO`. |
| `Insumos` | `Equipos compatibles` = Link, `Stock disponible` = Checkbox | Ninguno de los 2 existe. Hay en cambio `Cantidad ML/G` (number). |
| `Konica Minolta` | 21 records esperados | **22 records** reales al 2026-07-01 (incluye 1 record fantasma con un system prompt guardado en `Notas` — pendiente que Edgardo confirme si se borra, ver reporte). |
| `Config Mensual` | `Líneas priorizadas` = Link a `Líneas de Producto`, multi | Es `multilineText` (texto libre). El tool `consultar_lineas_priorizadas` ya fue parcheado (2026-07-01) para aceptar el campo como string separado por comas en vez de asumir un array — no hace falta migrar el tipo de campo en Airtable. |
| `Leads` (tabla #10 de este doc) | Documentada con 20 campos | **No existe en la base viva.** El CRM está pausado (decisión 2026-05-28, Opción A) — no se sabe si esta tabla se creó y se borró después, o si nunca llegó a crearse. Confirmar con la agencia si hace falta crearla vacía para el día que se reactive el upsell de CRM. |
| Pares de linked records (reverse) | Nombres simétricos asumidos (ej. `Sustratos.Equipos` ↔ `Equipos.Sustratos compatibles`) | La asimetría de naming es real en 5 de 7 pares — no es un bug, es cómo Airtable nombra el reverse field por default cuando no se lo renombra a mano. No renombrar sin actualizar el tool que lo lee en el mismo cambio. |

**Nota sobre `Sustratos`:** al 2026-07-01 esta tabla tenía 37 de 53 records contaminados con anchos/dimensiones en vez de nombres de sustrato (bug reportado por Edgardo). **Ya se limpió** (ver `airtable-auditoria-2026-07-01.md` §S-01) — quedan los 16 sustratos legítimos listados en el seed original de esta misma página, sección Tabla 5.

**Nota sobre `Equipos.Aplicaciones compatibles`:** estaba en 0 links (P1 S-04). **Ya se regeneró** (aprobado por la agencia): 62 de 92 equipos linkeados a las Aplicaciones cuya Tecnología coincide, 370 links totales. Los 30 equipos sin link son los que no tienen Tecnología cargada o cuya Tecnología (Corte, IDL Láser, Gran Formato) no tiene ninguna Aplicación asociada todavía — no es un error, es data real faltante aguas arriba.

**Nota sobre choices basura (`Marca`, `Formato`, `Disponibilidad zona`, `Status`, `Notas internas` en `Equipos`):** siguen sin limpiar. El PAT usado por la agencia no tiene el scope `schema.bases:write` — dos intentos reales de PATCH vía la meta API fallaron con 422 en 2 sesiones distintas. Requiere limpieza manual en la UI (ver `06_docs/airtable-guia-edgardo-2026-07-02.md` §5) o un PAT nuevo con ese scope.

---

## ⚠️ Cambios v1 → v1.1 (post-Excel del cliente)

El cliente entregó `BASE DE PRODUCTOS.xlsx` (98 KB, 6 sheets, 164 records reales). Schema actualizado para reflejar el catálogo real. Detalle completo en `06_docs/realineacion-post-excel-2026-05-29.md`.

**Cambios clave:**
- **Marcas reales** (Equipos): HUENU, DLICAN, TENETH, HANRUN, XENONS, RISO, Sinajet, Konica Minolta, Otro (NO Mimaki/Roland).
- **Tecnologías**: 10 (+Solvente, +Corte) — antes eran 8.
- **Tabla `Equipos`**: nuevos campos `Cabezales hasta/incluidos/tipo`, `Datos extra`, `Tipo de Uso`, `Precio USD`. Renombrado `Ancho máx (mm)` → `Ancho` (text). 11 opciones de Formato (Mesa/Plotter/Cilíndrica/Pliego/Bobina/Horno/Purificador/Plancha agregadas).
- **Tabla `Cabezales`**: nuevos campos `Gama`, `Cabezal familia`, `Perfil de Usuario`, `Precio USD`. Marcas: EPSON, RICOH, KONICA MINOLTA, OTRO.
- **Tabla `Insumos`**: nuevos campos `Modelo de cabezal`, `Configuración de color`, `Cantidad ML/G`, `Tipo`, `Precio USD`. Categorías reales: TINTAS, FILM, POLVO.
- **Tabla nueva**: `Inventario Konica Minolta` (21 equipos refurbished).
- **`Líneas de Producto`**: eliminados Mimaki/Roland, agregados Solvente/Corte.
- **`FAQs`**: +2 (IVA + i1600 vs i3200).
- **Política de precios**: campo `Precio USD` en tablas relevantes pero EXCLUIDO de la vista "Para agente". El LLM nunca lee precios.

---

## Contexto

Esta base reemplaza las 6 Google Sheets actuales del cliente (Equipos, Sinajet, Cabezales, Tintas y DTF, RISO, IDL) y suma 5 tablas operativas (Aplicaciones, Sustratos, FAQs, Representantes, Leads, Config Mensual).

**Single source of truth**: el agente lee SOLO de Airtable. El cliente edita SOLO en Airtable. Adiós a sincronizaciones.

**Quién edita qué:**
- Edgardo (catálogo técnico): Equipos, Tecnologías, Líneas, Aplicaciones, Sustratos, Cabezales, Insumos
- Gerente: Representantes, Config Mensual
- la agencia + Edgardo: FAQs
- n8n (escribe automático): Leads

---

## Lista de tablas

| # | Tabla | Filas estimadas | Edita | Usado por tool |
|---|---|---|---|---|
| 1 | [Equipos](#tabla-1-equipos) | 30–80 | Edgardo | `buscar_equipo`, `consultar_compatibilidad` |
| 2 | [Tecnologías](#tabla-2-tecnologías) | 8 | Edgardo | `consultar_tecnologia` |
| 3 | [Líneas de Producto](#tabla-3-líneas-de-producto) | 5–10 | Edgardo | linked Equipos / Config |
| 4 | [Aplicaciones](#tabla-4-aplicaciones) | 15–30 | Edgardo | `consultar_aplicacion` |
| 5 | [Sustratos](#tabla-5-sustratos) | 10–20 | Edgardo | linked Aplicaciones/Equipos |
| 6 | [Cabezales](#tabla-6-cabezales) | 10–20 | Edgardo | linked Equipos |
| 7 | [Insumos](#tabla-7-insumos) | 30–100 | Edgardo / Tienda | `consultar_url_tienda` |
| 8 | [FAQs](#tabla-8-faqs) | 15–30 | la agencia + Edgardo | `consultar_faq` |
| 9 | [Representantes](#tabla-9-representantes) | 3–8 | Gerente | `notificar_lead` (asignación) |
| 10 | [Leads](#tabla-10-leads) | crece sin límite | n8n (write) | n8n al crear/actualizar |
| 11 | [Config Mensual](#tabla-11-config-mensual) | 12/año | Gerente | `consultar_lineas_priorizadas` |

---

## Tabla 1: Equipos

| Campo | Tipo | Notas |
|---|---|---|
| `Modelo` (primary) | Single line text | Ej: "DTF-PRO-600", "Mimaki UJF-3042 MkII" |
| `Marca` | Single select | Mimaki, Roland, Epson, Mutoh, Konica Minolta, RISO, Sinajet, Otro |
| `Tecnología` | Link to `Tecnologías` | Multi-link OK (ej: equipo híbrido DTF + UV) |
| `Línea de Producto` | Link to `Líneas de Producto` | Single |
| `Aplicaciones compatibles` | Link to `Aplicaciones` | Multi |
| `Sustratos compatibles` | Link to `Sustratos` | Multi |
| `Cabezales` | Link to `Cabezales` | Multi |
| `Formato` | Single select | "Mesa plana", "Roll-to-roll", "Híbrido", "Compacta" |
| `Ancho máx (mm)` | Number | Sin decimales |
| `Velocidad (m²/h)` | Number | 1 decimal |
| `Disponibilidad zona` | Multi select | CABA, GBA, Interior |
| `Descripción corta` | Long text | 1 párrafo, leído por el agente |
| `Especificaciones técnicas` | Long text | Markdown permitido para edición; el agente recibe texto plano |
| `Imagen principal` | Attachment | RESERVADO para v2.1 cuando imágenes se desbloqueen |
| `Status` | Single select | Activo, Discontinuado, Próximamente |
| `Notas internas` | Long text | El agente NO las lee (uso interno cliente) |
| `Última modificación` | Last modified time | Auto |

### Vistas críticas

| Vista | Filtro | Uso |
|---|---|---|
| **Para agente** | `Status = "Activo"` | La que leen las tools |
| **Por línea** | (sin filtro, group by Línea) | Vista de revisión cliente |
| **Pendientes Edgardo** | `Status = "Próximamente"` | Edgardo carga aquí |
| **Discontinuados** | `Status = "Discontinuado"` | Histórico |

### Restricciones / Reglas

- **Modelo único**: el nombre no se repite.
- **Tecnología obligatoria** para records con `Status = Activo`.
- **Disponibilidad zona obligatoria** (al menos 1).
- **Descripción corta obligatoria** (mínimo 50 caracteres).

---

## Tabla 2: Tecnologías

8 records fijos. Seed inicial desde `04_agents/agente-sistemasysoluciones-system-prompt.md:212-286` (v1.7).

| Campo | Tipo | Notas |
|---|---|---|
| `Nombre` (primary) | Single line text | DTF Textil, DTF UV, UV, Sublimación, Eco-Solvente, RISO, IDL Láser, Gran Formato |
| `Descripción larga` | Long text | El "qué es y cómo funciona" |
| `Materiales recomendados` | Long text | Lista comma-separated |
| `Restricciones / Limitaciones` | Long text | Ej: Sublimación solo blanco/claro + poliéster |
| `Aplicaciones típicas` | Long text | |
| `Equipos asociados` | Link to `Equipos` (reverse) | Auto-derivado |
| `Línea principal` | Single select | DTF Textil, DTF UV, UV, Sublimación, Eco-Solvente, RISO, IDL Láser, Gran Formato |
| `Notas para agente` | Long text | Tips de cómo presentar al cliente |

### Seed inicial (8 records)

```
Nombre: DTF Textil
Descripción larga: Estampado textil y personalización de prendas. Imprime imagen en film PET con tinta + capa de blanco, aplica polvo adhesivo de poliamida, cura en horno y transfiere a la tela con plancha de calor. Funciona en cualquier color de tela — especialmente indicado para prendas oscuras.
Materiales recomendados: algodón, poliéster, nylon, denim, gorras, mochilas, etiquetas en cuellos y mangas
Restricciones: ninguna especial
Aplicaciones típicas: Estampado textil, personalización de prendas

Nombre: DTF UV
Descripción larga: Personalización de objetos rígidos e irregulares sin necesidad de meterlos en una impresora. Imprime en film especial con tintas UV + barniz + pegamento, se lamina y transfiere al objeto manualmente con presión (sin calor).
Materiales recomendados: botellas, termos, tazas, cascos, carcasas de celular, trofeos, vidrio, metal, madera, acrílico
Restricciones: requiere presión manual; no apto para producción muy alta
Aplicaciones típicas: personalización, objetos promocionales rígidos

Nombre: UV
Descripción larga: Impresión directa sobre casi cualquier material mediante tintas que curan con luz LED al instante. Disponible en formatos roll-to-roll y cama plana.
Materiales recomendados: Rígidos (acrílico, vidrio, madera, metales, PVC espumado, cerámica, cartón corrugado). Flexibles (lonas, viniles, cueros sintéticos, materiales backlit).
Restricciones: ninguna especial
Aplicaciones típicas: cartelería, señalética, packaging, objetos personalizados, texturas en relieve, Braille

Nombre: Sublimación
Descripción larga: Personalización textil y artículos promocionales con recubrimiento de poliéster. Imprime en papel transfer; calor (180-200°C) y presión convierten la tinta en gas que penetra las fibras.
Materiales recomendados: ropa deportiva, indumentaria, banderas, tapicería, tazas, láminas de metal tratadas
Restricciones: SOLO funciona en superficies blancas o claras con alto contenido de poliéster
Aplicaciones típicas: deportiva, promocional, indumentaria

Nombre: Eco-Solvente
Descripción larga: Señalización exterior y rotulación. Pigmentos en solventes biodegradables que penetran la superficie y se fijan al evaporarse con calor.
Materiales recomendados: vallas publicitarias, lonas para eventos, vinilos de corte, microperforados, calcomanías, wrap vehicular
Restricciones: ninguna especial
Aplicaciones típicas: rotulación exterior, vehicular, señalética

Nombre: RISO
Descripción larga: Impresión digital inkjet. Proyecta diminutas gotas de tinta líquida desde boquillas sobre el material. Ideal para alto volumen con buena calidad a velocidad sostenida.
Materiales recomendados: papel, plástico, tela y otros sustratos
Restricciones: ver modelos específicos
Aplicaciones típicas: alto volumen, publicaciones, sobres

Nombre: IDL Láser
Descripción larga: Impresoras láser de producción Konica Minolta (Bizhub C368, C558, C3300i y similares). Alta velocidad y calidad de impresión.
Materiales recomendados: papel, cartulina
Restricciones: solo papel/cartulina
Aplicaciones típicas: diseño gráfico, producción editorial, oficina alto volumen

Nombre: Gran Formato
Descripción larga: Plotters e impresoras para formatos de gran tamaño.
Materiales recomendados: lonas, banners, vinilos
Restricciones: ninguna
Aplicaciones típicas: cartelería exterior, impresión textil de gran formato
```

### Vistas

- **Por línea** (sin filtro, group by Línea principal)
- **Activas para agente** (sin filtro — las 8 siempre disponibles)

---

## Tabla 3: Líneas de Producto

| Campo | Tipo | Notas |
|---|---|---|
| `Línea` (primary) | Single line text | Ej: "Sinajet", "Konica Minolta IDL", "RISO", "Mimaki", "Genérico DTF" |
| `Tipo` | Single select | "Marca exclusiva", "Familia tecnología", "Genérico" |
| `Representante asignado` | Link to `Representantes` | Single (responsable comercial principal) |
| `Descripción` | Long text | |

### Seed inicial sugerido

- Sinajet (Marca exclusiva)
- Konica Minolta IDL (Marca exclusiva)
- RISO (Marca exclusiva)
- Mimaki (Marca exclusiva)
- Roland (Marca exclusiva)
- DTF Textil (Familia tecnología — multi-marca)
- DTF UV (Familia tecnología)
- UV (Familia tecnología)
- Sublimación (Familia tecnología)
- Eco-Solvente (Familia tecnología)

---

## Tabla 4: Aplicaciones

| Campo | Tipo | Notas |
|---|---|---|
| `Aplicación` (primary) | Single line text | Ej: "Estampado de gorras", "Wrap vehicular", "Cartelería exterior" |
| `Categoría` | Single select | Textil, Promocional, Cartelería exterior, Vehicular, Editorial, Personalización rígida, Otros |
| `Tecnologías recomendadas` | Link to `Tecnologías` | Multi (ej: gorras → DTF Textil + Sublimación) |
| `Sustratos típicos` | Link to `Sustratos` | Multi |
| `Notas para asesoramiento` | Long text | Guía qué decir al cliente |
| `Keywords cliente` | Long text | Comma-separated: "gorras, viseras, cap" (para matching fuzzy) |

### Seed inicial sugerido (20 entradas)

| Aplicación | Categoría | Tecnologías | Keywords |
|---|---|---|---|
| Estampado de remeras | Textil | DTF Textil, Sublimación | remeras, camisetas, t-shirt |
| Estampado de gorras | Textil | DTF Textil | gorras, viseras, cap |
| Estampado de mochilas | Textil | DTF Textil | mochilas, bolsos, bags |
| Buzos y hoodies | Textil | DTF Textil | buzos, hoodies, sweaters |
| Indumentaria deportiva | Textil | Sublimación | deportiva, jersey, camisetas equipos |
| Banderas | Textil | Sublimación | banderas, flags |
| Tazas personalizadas | Promocional | Sublimación, DTF UV | tazas, mug |
| Termos y botellas | Promocional | DTF UV | termos, botellas, mate |
| Cascos | Personalización rígida | DTF UV | cascos, helmets |
| Trofeos | Promocional | DTF UV | trofeos, premios |
| Cartelería luminosa | Cartelería exterior | UV | carteles, señalética luminosa |
| Vinilos de corte | Cartelería exterior | Eco-Solvente | vinilos, rotulación |
| Wrap vehicular | Vehicular | Eco-Solvente | wrap, autos, vehículos |
| Lonas para eventos | Cartelería exterior | Eco-Solvente | lonas, eventos |
| Banners | Cartelería exterior | Eco-Solvente, UV | banners, banderolas |
| Stickers y calcomanías | Promocional | Eco-Solvente | stickers, calcos, calcomanías |
| Packaging | Cartelería exterior | UV | packaging, cajas, envases |
| Producción editorial | Editorial | IDL Láser | editorial, libros, folletos |
| Sobres alto volumen | Editorial | RISO | sobres, alto volumen |
| Impresión vidrio/metal | Personalización rígida | UV, DTF UV | vidrio, metal, acrílico |

---

## Tabla 5: Sustratos

| Campo | Tipo | Notas |
|---|---|---|
| `Sustrato` (primary) | Single line text | Algodón, Poliéster, Vidrio, Metal, Madera, Acrílico, Lona, Vinilo, etc. |
| `Tipo` | Single select | Textil, Rígido, Flexible, Papel |
| `Tecnologías compatibles` | Link to `Tecnologías` | Multi |
| `Notas` | Long text | Restricciones (ej: sublimación solo poliéster blanco) |

### Seed (15 sustratos)

Textiles: Algodón, Poliéster, Nylon, Denim, Lycra, Cuero sintético
Rígidos: Vidrio, Metal, Madera, Acrílico, Cerámica, PVC espumado
Flexibles: Lona, Vinilo, Cuero sintético
Papel: Papel común, Cartulina

---

## Tabla 6: Cabezales

| Campo | Tipo |
|---|---|
| `Modelo` (primary) | Single line text |
| `Marca` | Single select |
| `Equipos compatibles` | Link to `Equipos` |
| `Tipo` | Single select — Original, Compatible, Repuesto |
| `URL tienda` | URL — link directo si está en tienda online |
| `Stock disponible` | Checkbox |

---

## Tabla 7: Insumos

| Campo | Tipo |
|---|---|
| `Insumo` (primary) | Single line text |
| `Categoría` | Single select — Tinta, Film DTF, Polvo DTF, Vinilo, Papel transfer, Otros |
| `Marca` | Single select |
| `Equipos compatibles` | Link to `Equipos` |
| `URL tienda` | URL |
| `Stock disponible` | Checkbox |
| `Descripción` | Long text |

---

## Tabla 8: FAQs

| Campo | Tipo | Notas |
|---|---|---|
| `Pregunta` (primary) | Single line text | Resumida — ej: "Hacen financiación?" |
| `Respuesta corta` | Long text | Copy-paste lista para que el agente integre verbatim |
| `Categoría` | Single select | Showroom, Financiación, Servicio Técnico, Plazos, Garantía, Llamadas, Devoluciones, Distribuidores, Otros |
| `Keywords` | Long text | Comma-separated: "cuotas, financiar, plan, pago" |
| `Status` | Single select | Activo, Revisión, Archivado |

### Seed inicial (10 FAQs — desde v1.7)

| Pregunta | Categoría | Keywords | Respuesta corta |
|---|---|---|---|
| ¿Tienen servicio técnico? | Servicio Técnico | servicio técnico, reparación, mantenimiento | Para servicio técnico, comunicate al 4342-5742. |
| ¿Hacen envíos al interior? | Plazos | interior, envío, despacho, mandar | Algunos equipos están disponibles para todo el país. Para confirmar disponibilidad en tu zona, lo mejor es hablar con nuestro equipo comercial. |
| ¿Pueden mostrarme el equipo? | Showroom | demo, showroom, ver, mostrar, prueba | Sí, tenemos showroom y hacemos demos. Si querés coordinar, dejame tu nombre y teléfono y un representante te contacta. |
| ¿Tienen financiación? | Financiación | cuotas, financiación, plan, pago, financiar | Sí, ofrecemos financiación. Las condiciones se definen personalmente con cada cliente. Dejame tu nombre y teléfono y un representante te explica las opciones. |
| ¿Diferencia entre DTF y UV? | Otros | dtf, uv, diferencia | DTF es ideal para estampado textil y transferencias a prendas. UV imprime directamente sobre rígidos o materiales en rollo con alta durabilidad. La elección depende de sobre qué vas a imprimir. |
| ¿Trabajan con distribuidores? | Distribuidores | distribuidor, revendedor, mayorista | Sí, tenemos red de distribuidores consolidada. Si te interesa conocer las condiciones, podemos coordinar una charla con el equipo comercial. |
| ¿Puedo llamar? | Llamadas | llamada, llamar, teléfono oficina | Para comunicarte con la oficina, podés llamar al 4342-5742. |
| ¿Cuál es el horario? | Llamadas | horario, atención, hora, abierto | Atendemos de lunes a viernes de 9 a 18 hs. |
| ¿Tienen garantía? | Garantía | garantía, warranty | Sí, los equipos tienen garantía. Las condiciones específicas las explica el comercial cuando arma la cotización. |
| ¿Tienen tienda online? | Otros | tienda, comprar online, web | Sí, en {{URL_TIENDA}} podés ver y comprar insumos y repuestos. Si necesitás un equipo, el comercial te arma la propuesta. |

---

## Tabla 9: Representantes

> ⚠️ **Decisión 2026-05-28 — Opción A (sin especialización):** la tool `notificar_lead` NO consulta esta tabla. Todos los leads se mandan a `info@sistemasysoluciones.com`. La tabla queda creada para futuro (Opción B con especialización por línea + zona). Mientras tanto, se sugiere agregar 1 sola fila "Equipo Comercial" con mail `info@sistemasysoluciones.com`, líneas=todas, zonas=todas, Activo=true. Si más adelante se quiere especializar, se completan reps reales y se reactiva el lookup en la tool.

| Campo | Tipo | Notas |
|---|---|---|
| `Nombre` (primary) | Single line text | Ej: "Marcos R." |
| `Mail` | Email | Recibe notificaciones de leads |
| `Teléfono` | Phone | |
| `Líneas asignadas` | Link to `Líneas de Producto` | Multi |
| `Zonas asignadas` | Multi select | CABA, GBA, Interior |
| `Backup` | Link to `Representantes` | Single — si no disponible |
| `Activo` | Checkbox | |
| `Mail Gerente (copia)` | Email | Mail del Gerente que recibe copia (puede repetirse entre reps) |

### Fórmula de asignación (en `notificar_lead`)

```
filterByFormula:
  AND(
    {Activo} = TRUE(),
    FIND("{zona_lead}", ARRAYJOIN({Zonas asignadas})) > 0,
    FIND("{linea_equipo}", ARRAYJOIN({Líneas asignadas})) > 0
  )
```

- Si 0 matches → asignar primer rep activo (fallback) + flag `REP_NOT_FOUND` a Telegram.
- Si N matches → tomar el primero (alfabético por Nombre).

### Setup mínimo

- 1 rep "Comercial Genérico" (zonas CABA+GBA+Interior, todas las líneas) como fallback.
- Idealmente 3+ reps reales asignados por zona/línea (pendiente del cliente, Fase 0).

---

## Tabla 10: Leads

n8n escribe automático. El cliente lee/anota en `Notas internas`.

| Campo | Tipo | Origen |
|---|---|---|
| `Lead ID` (primary, formula) | Formula `"LEAD-" & RECORD_ID()` | Auto |
| `Fecha creación` | Created time | Auto |
| `Canal` | Single select | WA, IG, FB (n8n) |
| `Subscriber ID` | Single line text | de ManyChat |
| `Nombre` | Single line text | Capturado |
| `Empresa` | Single line text | Opcional |
| `Mail` | Email | |
| `Teléfono` | Phone | |
| `Ubicación` | Single line text | Texto libre del cliente |
| `Zona` | Single select | CABA, GBA, Interior (derivada por n8n) |
| `Perfil` | Single select | Distribuidor, Pyme, Emprendedor, Sin clasificar |
| `Equipo / Aplicación consultada` | Long text | |
| `Tecnología de interés` | Link to `Tecnologías` | |
| `Línea de interés` | Link to `Líneas de Producto` | |
| `Status` | Single select | Nuevo, En conversación, Derivado, Cotizado, Cerrado-Ganado, Cerrado-Perdido, Descalificado |
| `Representante asignado` | Link to `Representantes` | |
| `Notificación enviada` | Checkbox | true cuando mail al rep se mandó |
| `Fecha derivación` | Date | n8n |
| `Última actividad` | Date | n8n actualiza cada turno |
| `Conversación session_id` | Single line text | = leadIdentifier de Postgres |
| `Notas internas` | Long text | El rep escribe acá |

### Vistas críticas

| Vista | Filtro | Uso |
|---|---|---|
| **Nuevos hoy** | `Fecha creación = TODAY()` | Monitoreo diario |
| **En conversación** | `Status = "En conversación"` | Active leads |
| **Derivados** | `Status = "Derivado"` | Cola de reps |
| **Pendientes derivación >24h** | `Status = "En conversación" AND Última actividad < NOW()-1d` | Follow-up automático |
| **Por representante** | (group by Rep asignado) | Vista para reps |
| **Cerrados ganados** | `Status = "Cerrado-Ganado"` | ROI tracking |

---

## Tabla 11: Config Mensual

| Campo | Tipo | Notas |
|---|---|---|
| `Mes` (primary) | Single line text | Formato "2026-05", "2026-06" |
| `Líneas priorizadas` | Link to `Líneas de Producto` | Multi |
| `Notas para agente` | Long text | "Este mes hay promo en RISO, mencionar si pregunta por digital alta producción" |
| `Activo` | Checkbox | Solo 1 fila activa por mes (Gerente cambia manualmente) |

La tool `consultar_lineas_priorizadas` busca `{Activo} = TRUE()` y devuelve esa única fila.

---

## Vistas globales (cross-table)

Ninguna en v1. Si en v2.1 se necesita un "panel general", construir con Airtable Interfaces.

---

## Setup paso a paso (Fase 1 del roadmap)

1. **Crear workspace y base**:
   - https://airtable.com → New workspace "la agencia" (si no existe).
   - Inside: New base → name "SyS Catalogo".

2. **Crear las 11 tablas** en este orden (las later linkean a las earlier):
   1. Tecnologías → seed los 8 records (copy-paste desde §Tabla 2).
   2. Sustratos → seed (15 entries).
   3. Líneas de Producto → seed (10 entries).
   4. Aplicaciones → seed (20 entries; link Tecnologías + Sustratos).
   5. Cabezales → empezar vacía.
   6. Insumos → empezar vacía o seed inicial si Edgardo tiene datos.
   7. Equipos → seed con lo que tenga Edgardo (link Tecnología + Línea + Aplicaciones + Sustratos + Cabezales).
   8. FAQs → seed los 10 records.
   9. Representantes → seed con lo que dé el Gerente (mínimo 1 fallback).
   10. Leads → empezar vacía (n8n escribe).
   11. Config Mensual → 1 fila para el mes en curso.

3. **Configurar vistas críticas** (ver cada tabla).

4. **Generar Personal Access Token**:
   - Account → Developer hub → Personal access tokens → Create.
   - Scopes: `data.records:read`, `data.records:write`, `schema.bases:read`.
   - Bases: solo `SyS Catalogo`.
   - Copiar token → guardar como `AIRTABLE_TOKEN_SYS` en n8n env vars.

5. **Capturar Base ID**:
   - URL de la base: `https://airtable.com/appXXXXX/...` → `appXXXXX` es el Base ID.
   - Guardar como `AIRTABLE_BASE_ID_SYS` en n8n env vars.

6. **Probar conexión desde n8n**:
   - Credentials → New → Airtable Personal Access Token → pegar token.
   - Test con un nodo Airtable Search en Equipos → debería retornar records.

7. **Onboarding Edgardo**: entregar `06_docs/guia-airtable-edgardo-v1.md`.

---

## Notas de operación

- **Backups**: Airtable hace snapshots automáticos diarios (Pro plan). En Free, considerar exportar CSV cada 15 días.
- **Límites Free tier**: 1000 records/base. Si Leads crece >800, plan upgrade a Team ($20/mes) o archivar leads cerrados >6 meses.
- **Edición concurrente**: Airtable soporta multi-usuario en vivo. No hay riesgo de conflictos.
- **Cambios estructurales** (agregar/eliminar campo): coordinar con la agencia (rompe tools). Cambios de contenido (FAQ nueva, equipo nuevo): libres.
