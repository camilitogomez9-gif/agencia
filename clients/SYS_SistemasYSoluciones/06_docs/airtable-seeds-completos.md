# Airtable SyS Catalogo — Seeds completos para carga manual

> ⚠️ **OBSOLETO desde 2026-05-29.** Este doc fue generado cuando el catálogo era stub (Mimaki/Roland inventados, 5 equipos genéricos).
>
> El cliente entregó `BASE DE PRODUCTOS.xlsx` con el catálogo REAL. La fuente de verdad ahora son los **CSVs reales** en `airtable-csv/` (08-equipos.csv con 92 records reales, 09-cabezales.csv, 10-insumos.csv, 11-inventario-konica.csv).
>
> **Para la carga, usar:** `06_docs/airtable-csv/README.md` (actualizado 2026-05-29).
>
> **Para entender qué cambió:** `06_docs/realineacion-post-excel-2026-05-29.md`.
>
> Mantengo el contenido abajo por trazabilidad histórica (qué tenía el sistema antes de la re-alineación).

---

# Contenido histórico (pre-realineación 2026-05-28)

> **Para:** ejecución de Pasos 3–10 del plan F1 (versión stub).
> **Uso:** copiar/pegar cada record en Airtable UI durante la migración.
> **Fecha generación:** 2026-05-28
> **Fuente:** prompt v1.7 (descripciones técnicas) + schema doc (estructura).
>
> Cuando termines de cargar, actualizá la sección "Estado de carga" al final de este archivo.

---

## Tabla 1: Tecnologías — 8 records

Crear los 8 records con descripciones verbatim del system prompt v1.7. Cada uno con campo `Línea principal` = al mismo nombre que `Nombre`.

### Record 1
- **Nombre:** `DTF Textil`
- **Línea principal:** DTF Textil
- **Descripción larga:**
  > Estampado textil y personalización de prendas. Imprime imagen en film PET con tinta + capa de blanco, aplica polvo adhesivo de poliamida, cura en horno y transfiere a la tela con plancha de calor. Funciona en cualquier color de tela — especialmente indicado para prendas oscuras.
- **Materiales recomendados:** algodón, poliéster, nylon, denim, gorras, mochilas, etiquetas en cuellos y mangas
- **Restricciones / Limitaciones:** ninguna especial
- **Aplicaciones típicas:** Estampado textil, personalización de prendas
- **Notas para agente:** (vacío — completar después de testing)

### Record 2
- **Nombre:** `DTF UV`
- **Línea principal:** DTF UV
- **Descripción larga:**
  > Personalización de objetos rígidos e irregulares sin necesidad de meterlos en una impresora. Imprime en film especial con tintas UV + barniz + pegamento, se lamina y transfiere al objeto manualmente con presión (sin calor).
- **Materiales recomendados:** botellas, termos, tazas, cascos, carcasas de celular, trofeos, vidrio, metal, madera, acrílico
- **Restricciones / Limitaciones:** requiere presión manual; no apto para producción muy alta
- **Aplicaciones típicas:** personalización, objetos promocionales rígidos

### Record 3
- **Nombre:** `UV`
- **Línea principal:** UV
- **Descripción larga:**
  > Impresión directa sobre casi cualquier material mediante tintas que curan con luz LED al instante. Disponible en formatos roll-to-roll y cama plana.
- **Materiales recomendados:** Rígidos (acrílico, vidrio, madera, metales, PVC espumado, cerámica, cartón corrugado). Flexibles (lonas, viniles, cueros sintéticos, materiales backlit).
- **Restricciones / Limitaciones:** ninguna especial
- **Aplicaciones típicas:** cartelería, señalética, packaging, objetos personalizados, texturas en relieve, Braille

### Record 4
- **Nombre:** `Sublimación`
- **Línea principal:** Sublimación
- **Descripción larga:**
  > Personalización textil y artículos promocionales con recubrimiento de poliéster. Imprime en papel transfer; calor (180-200°C) y presión convierten la tinta en gas que penetra las fibras.
- **Materiales recomendados:** ropa deportiva, indumentaria, banderas, tapicería, tazas, láminas de metal tratadas
- **Restricciones / Limitaciones:** SOLO funciona en superficies blancas o claras con alto contenido de poliéster
- **Aplicaciones típicas:** deportiva, promocional, indumentaria

### Record 5
- **Nombre:** `Eco-Solvente`
- **Línea principal:** Eco-Solvente
- **Descripción larga:**
  > Señalización exterior y rotulación. Pigmentos en solventes biodegradables que penetran la superficie y se fijan al evaporarse con calor.
- **Materiales recomendados:** vallas publicitarias, lonas para eventos, vinilos de corte, microperforados, calcomanías, wrap vehicular
- **Restricciones / Limitaciones:** ninguna especial
- **Aplicaciones típicas:** rotulación exterior, vehicular, señalética

### Record 6
- **Nombre:** `RISO`
- **Línea principal:** RISO
- **Descripción larga:**
  > Impresión digital inkjet. Proyecta diminutas gotas de tinta líquida desde boquillas sobre el material. Ideal para alto volumen con buena calidad a velocidad sostenida.
- **Materiales recomendados:** papel, plástico, tela y otros sustratos
- **Restricciones / Limitaciones:** ver modelos específicos
- **Aplicaciones típicas:** alto volumen, publicaciones, sobres

### Record 7
- **Nombre:** `IDL Láser`
- **Línea principal:** IDL Láser
- **Descripción larga:**
  > Impresoras láser de producción Konica Minolta (Bizhub C368, C558, C3300i y similares). Alta velocidad y calidad de impresión.
- **Materiales recomendados:** papel, cartulina
- **Restricciones / Limitaciones:** solo papel/cartulina
- **Aplicaciones típicas:** diseño gráfico, producción editorial, oficina alto volumen

### Record 8
- **Nombre:** `Gran Formato`
- **Línea principal:** Gran Formato
- **Descripción larga:**
  > Plotters e impresoras para formatos de gran tamaño.
- **Materiales recomendados:** lonas, banners, vinilos
- **Restricciones / Limitaciones:** ninguna
- **Aplicaciones típicas:** cartelería exterior, impresión textil de gran formato

---

## Tabla 2: Sustratos — 16 records

| # | Sustrato | Tipo | Tecnologías compatibles (linkear) |
|---|---|---|---|
| 1 | Algodón | Textil | DTF Textil |
| 2 | Poliéster | Textil | DTF Textil, Sublimación |
| 3 | Nylon | Textil | DTF Textil |
| 4 | Denim | Textil | DTF Textil |
| 5 | Lycra | Textil | DTF Textil, Sublimación |
| 6 | Cuero sintético | Textil | DTF Textil, Eco-Solvente |
| 7 | Vidrio | Rígido | UV, DTF UV |
| 8 | Metal | Rígido | UV, DTF UV, Sublimación |
| 9 | Madera | Rígido | UV, DTF UV |
| 10 | Acrílico | Rígido | UV, DTF UV |
| 11 | Cerámica | Rígido | UV, DTF UV |
| 12 | PVC espumado | Rígido | UV |
| 13 | Lona | Flexible | Eco-Solvente, UV |
| 14 | Vinilo | Flexible | Eco-Solvente |
| 15 | Papel común | Papel | RISO, IDL Láser |
| 16 | Cartulina | Papel | IDL Láser, RISO |

**Notas:**
- Metal + Sublimación: solo si está revestido con poliéster (anotar en `Notas` del record).

---

## Tabla 3: Líneas de Producto — 10 records

`Representante asignado` → linkear a "Equipo Comercial" después de crear la tabla Representantes (Paso 8).

| # | Línea | Tipo | Descripción |
|---|---|---|---|
| 1 | Sinajet | Marca exclusiva | Mesas de corte y plotters de la marca Sinajet. |
| 2 | Konica Minolta IDL | Marca exclusiva | Línea Konica Minolta para impresión digital láser de producción. |
| 3 | RISO | Marca exclusiva | Impresoras RISO de alto volumen. |
| 4 | Mimaki | Marca exclusiva | Equipos Mimaki para DTF, UV y gran formato. |
| 5 | Roland | Marca exclusiva | Equipos Roland para impresión y corte. |
| 6 | DTF Textil | Familia tecnología | Equipos multi-marca de tecnología DTF Textil. |
| 7 | DTF UV | Familia tecnología | Equipos multi-marca de tecnología DTF UV. |
| 8 | UV | Familia tecnología | Equipos multi-marca de tecnología UV (LED). |
| 9 | Sublimación | Familia tecnología | Equipos multi-marca para sublimación. |
| 10 | Eco-Solvente | Familia tecnología | Equipos multi-marca para impresión eco-solvente. |

---

## Tabla 4: Aplicaciones — 20 records con links

Cada record con: Aplicación, Categoría, `Tecnologías recomendadas` (linkear), `Sustratos típicos` (linkear), Keywords cliente.

| # | Aplicación | Categoría | Tecnologías | Sustratos típicos | Keywords cliente |
|---|---|---|---|---|---|
| 1 | Estampado de remeras | Textil | DTF Textil, Sublimación | Algodón, Poliéster | remeras, camisetas, t-shirt |
| 2 | Estampado de gorras | Textil | DTF Textil | Algodón, Poliéster | gorras, viseras, cap |
| 3 | Estampado de mochilas | Textil | DTF Textil | Nylon, Poliéster | mochilas, bolsos, bags |
| 4 | Buzos y hoodies | Textil | DTF Textil | Algodón, Poliéster | buzos, hoodies, sweaters |
| 5 | Indumentaria deportiva | Textil | Sublimación | Poliéster, Lycra | deportiva, jersey, equipos |
| 6 | Banderas | Textil | Sublimación | Poliéster | banderas, flags |
| 7 | Tazas personalizadas | Promocional | Sublimación, DTF UV | Cerámica, Metal | tazas, mug |
| 8 | Termos y botellas | Promocional | DTF UV | Metal, Vidrio | termos, botellas, mate |
| 9 | Cascos | Personalización rígida | DTF UV | PVC espumado | cascos, helmets |
| 10 | Trofeos | Promocional | DTF UV | Metal, Acrílico | trofeos, premios |
| 11 | Cartelería luminosa | Cartelería exterior | UV | Acrílico, PVC espumado | carteles, señalética, backlit |
| 12 | Vinilos de corte | Cartelería exterior | Eco-Solvente | Vinilo | vinilos, rotulación |
| 13 | Wrap vehicular | Vehicular | Eco-Solvente | Vinilo | wrap, autos, vehículos |
| 14 | Lonas para eventos | Cartelería exterior | Eco-Solvente | Lona | lonas, eventos |
| 15 | Banners | Cartelería exterior | Eco-Solvente, UV | Lona | banners, banderolas |
| 16 | Stickers y calcomanías | Promocional | Eco-Solvente | Vinilo | stickers, calcos, calcomanías |
| 17 | Packaging | Cartelería exterior | UV | Cartulina, PVC espumado | packaging, cajas, envases |
| 18 | Producción editorial | Editorial | IDL Láser | Papel común, Cartulina | editorial, libros, folletos |
| 19 | Sobres alto volumen | Editorial | RISO | Papel común | sobres, alto volumen |
| 20 | Impresión vidrio/metal | Personalización rígida | UV, DTF UV | Vidrio, Metal, Acrílico | vidrio, metal, acrílico |

---

## Tabla 5: FAQs — 10 records

Todos con Status = **Activo**.

### FAQ 1
- **Pregunta:** ¿Tienen servicio técnico?
- **Categoría:** Servicio Técnico
- **Keywords:** servicio técnico, reparación, mantenimiento
- **Respuesta corta:** Para servicio técnico, comunicate al 4342-5742.

### FAQ 2
- **Pregunta:** ¿Hacen envíos al interior?
- **Categoría:** Plazos
- **Keywords:** interior, envío, despacho, mandar
- **Respuesta corta:** Algunos equipos están disponibles para todo el país. Para confirmar disponibilidad en tu zona, lo mejor es hablar con nuestro equipo comercial.

### FAQ 3
- **Pregunta:** ¿Pueden mostrarme el equipo?
- **Categoría:** Showroom
- **Keywords:** demo, showroom, ver, mostrar, prueba
- **Respuesta corta:** Sí, tenemos showroom y hacemos demos. Si querés coordinar, dejame tu nombre y teléfono y un representante te contacta.

### FAQ 4
- **Pregunta:** ¿Tienen financiación?
- **Categoría:** Financiación
- **Keywords:** cuotas, financiación, plan, pago, financiar
- **Respuesta corta:** Sí, ofrecemos financiación. Las condiciones se definen personalmente con cada cliente. Dejame tu nombre y teléfono y un representante te explica las opciones.

### FAQ 5
- **Pregunta:** ¿Diferencia entre DTF y UV?
- **Categoría:** Otros
- **Keywords:** dtf, uv, diferencia
- **Respuesta corta:** DTF es ideal para estampado textil y transferencias a prendas. UV imprime directamente sobre rígidos o materiales en rollo con alta durabilidad. La elección depende de sobre qué vas a imprimir.

### FAQ 6
- **Pregunta:** ¿Trabajan con distribuidores?
- **Categoría:** Distribuidores
- **Keywords:** distribuidor, revendedor, mayorista
- **Respuesta corta:** Sí, tenemos red de distribuidores consolidada. Si te interesa conocer las condiciones, podemos coordinar una charla con el equipo comercial.

### FAQ 7
- **Pregunta:** ¿Puedo llamar?
- **Categoría:** Llamadas
- **Keywords:** llamada, llamar, teléfono oficina
- **Respuesta corta:** Para comunicarte con la oficina, podés llamar al 4342-5742.

### FAQ 8
- **Pregunta:** ¿Cuál es el horario?
- **Categoría:** Llamadas
- **Keywords:** horario, atención, hora, abierto
- **Respuesta corta:** Atendemos de lunes a viernes de 9 a 18 hs.

### FAQ 9
- **Pregunta:** ¿Tienen garantía?
- **Categoría:** Garantía
- **Keywords:** garantía, warranty
- **Respuesta corta:** Sí, los equipos tienen garantía. Las condiciones específicas las explica el comercial cuando arma la cotización.

### FAQ 10
- **Pregunta:** ¿Tienen tienda online?
- **Categoría:** Otros
- **Keywords:** tienda, comprar online, web
- **Respuesta corta:** Sí, en https://www.sistemasysoluciones.com podés ver y comprar insumos y repuestos. Si necesitás un equipo, el comercial te arma la propuesta.

---

## Tabla 6: Representantes — 1 record (Opción A — sin especialización)

- **Nombre:** `Equipo Comercial`
- **Mail:** `info@sistemasysoluciones.com`
- **Teléfono:** `4342-5742`
- **Líneas asignadas:** linkear las 10 líneas de Tabla 3 (todas)
- **Zonas asignadas:** CABA, GBA, Interior (las 3)
- **Backup:** (vacío)
- **Activo:** ✅ true
- **Mail Gerente (copia):** (vacío — mismo destino que Mail principal, no duplicar)

**Después de crear este record:** volver a Tabla 3 (Líneas de Producto) y en cada una de las 10 líneas linkear `Representante asignado` → "Equipo Comercial".

---

## Tabla 7: Config Mensual — 1 record para el mes en curso

- **Mes:** `2026-05` (ajustar al mes real al ejecutar)
- **Líneas priorizadas:** (vacío)
- **Notas para agente:** `(Sin priorización este mes — el agente puede mencionar cualquier línea según necesidad del cliente)`
- **Activo:** ✅ true

---

## Tabla 8: Equipos — 5 records STUB (Status = Próximamente)

Stubs para que las tools tengan algo durante testing F7. Edgardo los reemplaza/completa después.

### Equipo Stub 1
- **Modelo:** `DTF-STD-600`
- **Marca:** Otro
- **Tecnología:** DTF Textil (linkear)
- **Línea de Producto:** DTF Textil (linkear)
- **Aplicaciones compatibles:** Estampado de remeras, Estampado de gorras, Estampado de mochilas, Buzos y hoodies (linkear)
- **Sustratos compatibles:** Algodón, Poliéster, Nylon, Denim (linkear)
- **Formato:** Roll-to-roll
- **Ancho máx (mm):** 600
- **Velocidad (m²/h):** (vacío)
- **Disponibilidad zona:** CABA, GBA
- **Descripción corta:** Equipo DTF textil estándar de 60cm. Pendiente confirmar modelos exactos con Edgardo.
- **Status:** Próximamente
- **Notas internas:** Stub creado en F1. Pendiente confirmar modelo exacto con Edgardo.

### Equipo Stub 2
- **Modelo:** `UV-STD-Cama`
- **Marca:** Otro
- **Tecnología:** UV (linkear)
- **Línea de Producto:** UV (linkear)
- **Aplicaciones compatibles:** Cartelería luminosa, Banners, Packaging, Impresión vidrio/metal (linkear)
- **Sustratos compatibles:** Vidrio, Metal, Madera, Acrílico, PVC espumado (linkear)
- **Formato:** Mesa plana
- **Ancho máx (mm):** 600
- **Disponibilidad zona:** CABA, GBA
- **Descripción corta:** Equipo UV de cama plana. Pendiente confirmar modelos exactos.
- **Status:** Próximamente
- **Notas internas:** Stub F1.

### Equipo Stub 3
- **Modelo:** `Sublimación-STD`
- **Marca:** Otro
- **Tecnología:** Sublimación (linkear)
- **Línea de Producto:** Sublimación (linkear)
- **Aplicaciones compatibles:** Indumentaria deportiva, Banderas, Tazas personalizadas (linkear)
- **Sustratos compatibles:** Poliéster, Lycra, Metal (linkear)
- **Formato:** Roll-to-roll
- **Ancho máx (mm):** 1100
- **Disponibilidad zona:** CABA, GBA, Interior
- **Descripción corta:** Equipo sublimación gran formato. Pendiente confirmar.
- **Status:** Próximamente
- **Notas internas:** Stub F1.

### Equipo Stub 4
- **Modelo:** `RISO-Modelo-Stub`
- **Marca:** RISO
- **Tecnología:** RISO (linkear)
- **Línea de Producto:** RISO (linkear)
- **Aplicaciones compatibles:** Sobres alto volumen, Producción editorial (linkear)
- **Sustratos compatibles:** Papel común (linkear)
- **Formato:** Compacta
- **Ancho máx (mm):** 297
- **Disponibilidad zona:** CABA, GBA
- **Descripción corta:** Equipo RISO de alto volumen. Pendiente especificaciones.
- **Status:** Próximamente
- **Notas internas:** Stub F1.

### Equipo Stub 5
- **Modelo:** `KM-IDL-Stub`
- **Marca:** Konica Minolta
- **Tecnología:** IDL Láser (linkear)
- **Línea de Producto:** Konica Minolta IDL (linkear)
- **Aplicaciones compatibles:** Producción editorial (linkear)
- **Sustratos compatibles:** Papel común, Cartulina (linkear)
- **Formato:** Compacta
- **Ancho máx (mm):** 297
- **Disponibilidad zona:** CABA, GBA
- **Descripción corta:** Konica Minolta producción editorial. Pendiente especificaciones.
- **Status:** Próximamente
- **Notas internas:** Stub F1.

---

## Estado de carga

Marcar a medida que se cargan los seeds en Airtable:

- [ ] Tabla Tecnologías — 8 records
- [ ] Tabla Sustratos — 16 records + links a Tecnologías
- [ ] Tabla Líneas de Producto — 10 records
- [ ] Tabla Aplicaciones — 20 records + links a Tecnologías + Sustratos
- [ ] Tabla FAQs — 10 records (Status=Activo)
- [ ] Tabla Representantes — 1 record (Equipo Comercial)
- [ ] Tabla Líneas de Producto — linkear Representante=Equipo Comercial en las 10
- [ ] Tabla Config Mensual — 1 record (mes en curso, Activo)
- [ ] Tabla Equipos — 5 stubs (Status=Próximamente)
- [ ] Tabla Cabezales — (vacío en F1)
- [ ] Tabla Insumos — (vacío en F1)
- [ ] Tabla Leads — (vacío en F1, se llena automático por n8n)

**Fecha de carga completada:** _____________
**Cargado por:** _____________

---

## Notas para quien ejecute

- **Orden de tablas importa**: crear primero Tecnologías, Sustratos, Líneas, Aplicaciones, Cabezales, Insumos, Equipos, FAQs, Representantes, Leads, Config Mensual. Los linked fields requieren la tabla destino ya existente.
- **Estrategia de carga rápida**: crear todas las tablas vacías primero (Paso 2), después seedear (Paso 3-9), después linkear los reverse fields que faltaban. Más ordenado que hacer record por record cerrando relaciones.
- **Para los Sustratos**: cargar primero los 16 sin links, después agregar la columna `Tecnologías compatibles` y linkear de a uno (más rápido en CSV import si hacés eso).
- **Para las Aplicaciones**: lo mismo — cargar primero las 20 con `Categoría` y `Keywords`, después linkear `Tecnologías recomendadas` y `Sustratos típicos`.
- **CSV import**: Airtable permite importar CSV. Si te resulta más rápido, podés copiar las tablas markdown de este doc, pegarlas en una Google Sheet, exportar como CSV y importar — pero los linked fields tendrás que armarlos manualmente después.
