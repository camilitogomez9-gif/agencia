# Análisis tabla Airtable `Aplicaciones` — 2026-06-09

## Resumen

La tabla `Aplicaciones` tenía 34 filas. Análisis revela que **14 filas (22-35) no son aplicaciones** sino **formatos de equipos** que se mezclaron por error durante una migración. Las 20 filas correctas se enriquecieron con el campo `Tecnologías recomendadas` que estaba vacío.

CSV listo: `clients/SYS_SistemasYSoluciones/05_crm/airtable-csvs/Aplicaciones-enriquecido-2026-06-09.csv`.

---

## Filas a ELIMINAR de Airtable (causa: error de migración)

| # | Aplicación (mal cargado) | Qué es realmente |
|---|---|---|
| 22 | Rollo a Rollo | Formato de impresora |
| 23 | Híbrido | Formato de impresora |
| 24 | Cilindrica | Formato de impresora |
| 25 | Cama Plana | Formato de impresora |
| 26 | Plancha | Accesorio del kit DTF |
| 27 | Horno | Accesorio del kit DTF |
| 28 | Purificador | Accesorio del kit DTF |
| 29 | MESA | Tipo de equipo de corte (DUPLICADO de fila 34) |
| 30 | PLOTTER | Tipo de equipo de corte (DUPLICADO de fila 33) |
| 31 | PLIEGO | Formato de papel (RISO/IDL) |
| 32 | Bobina | Formato de papel |
| 33 | Plotter | Tipo de equipo de corte (DUPLICADO de fila 30) |
| 34 | Mesa | Tipo de equipo de corte (DUPLICADO de fila 29) |
| 35 | Compacta | Tipo de equipo de corte |

## Causa probable (con confianza alta)

Esta info **ya existe** en el campo `Formato` de la tabla `Equipos` — es donde corresponde semánticamente. Probable cadena de eventos durante la migración inicial del Excel del cliente:

1. **Primera migración** (correcta): se importaron las 20 aplicaciones del cliente con Categoría/Sustratos/Keywords. El campo `Equipos` quedó vacío porque no había mapeo desde el cliente.
2. **Segunda pasada errónea** (probablemente con un import-CSV de la columna `Formato` de Equipos): se appendearon 14 filas adicionales con sólo el campo `Equipos` poblado. Headers compatibles porque ambas tablas tienen columna `Equipos` linked. La distribución perfectamente complementaria (filas 2-21 sin Equipos, filas 22-35 sin Categoría/Sustratos/Keywords) confirma este patrón.
3. **Duplicación MAYÚSCULAS/minúsculas** (`MESA`/`Mesa`, `PLOTTER`/`Plotter`): indica que la segunda pasada se ejecutó al menos dos veces, una con normalización mayúsculas (probablemente desde un CSV) y otra sin (probablemente desde Excel). El usuario notará que algunas filas duplican entidades.

## Acción recomendada

**Eliminar las 14 filas (22-35) de la tabla `Aplicaciones`.** No mover a otra tabla — la información ya está en `Equipos.Formato`.

### Cómo hacerlo en Airtable

1. Abrir la base `SyS Catalogo` → tabla `Aplicaciones`.
2. Filtrar por `Categoría` is empty (eso captura las 14 filas).
3. Verificar que sean las que aparecen en la tabla de arriba.
4. Seleccionar todas → eliminar.

Alternativa más segura: importar el CSV enriquecido como tabla nueva, verificar, luego eliminar la vieja y renombrar.

---

## Filas correctas enriquecidas (1-20 → mapeo Tecnologías recomendadas)

Mapeo razonado por categoría + sustratos típicos. Todas las tecnologías son nombres canónicos del catálogo (10 valores válidos para invocar `consultar_tecnologia`).

| Aplicación | Categoría | Tecnologías recomendadas | Razonamiento |
|---|---|---|---|
| Estampado de remeras | Textil | DTF Textil, Sublimación | DTF cubre cualquier color/tela; Sublimación solo poliéster claro |
| Estampado de gorras | Textil | DTF Textil | Superficie curva favorece DTF sobre sublimación |
| Estampado de mochilas | Textil | DTF Textil, Sublimación | Nylon + poliéster: DTF principal, Sublimación opcional |
| Buzos y hoodies | Textil | DTF Textil | Algodón + diseños grandes: DTF (Sublimación no funciona en algodón) |
| Indumentaria deportiva | Textil | Sublimación, DTF Textil | Poliéster + Lycra es el sweet spot de Sublimación; DTF como alternativa |
| Banderas | Textil | Sublimación | Aplicación clásica de Sublimación |
| Tazas personalizadas | Promocional | Sublimación | Cerámica con coating de poliéster — estándar de la industria |
| Termos y botellas | Promocional | UV, Sublimación | UV imprime directo en rígidos; Sublimación para metal coated |
| Cascos | Personalización rígida | UV | Único método práctico para PVC espumado curvo |
| Trofeos | Promocional | UV, Sublimación | UV directo en acrílico; Sublimación para metal coated |
| Cartelería luminosa | Cartelería exterior | UV, Eco-Solvente | Sustratos rígidos backlit (acrílico, PVC) |
| Vinilos de corte | Cartelería exterior | Corte, Eco-Solvente | Plotter de corte + impresión previa con Eco-Solvente |
| Wrap vehicular | Vehicular | Eco-Solvente, UV | Vinilo wrap = aplicación clásica de Eco-Solvente |
| Lonas para eventos | Cartelería exterior | Gran Formato, Eco-Solvente | Anchos grandes + lona = Gran Formato |
| Banners | Cartelería exterior | Gran Formato, Eco-Solvente | Idem lonas |
| Stickers y calcomanías | Promocional | Eco-Solvente, Corte, UV | Eco-Solvente para vinilo adhesivo + Corte para forma + UV para rígidos |
| Packaging | Cartelería exterior | UV, Eco-Solvente | Cartulina/PVC = UV directo o Eco-Solvente |
| Producción editorial | Editorial | RISO, IDL Láser | Papel común alto volumen = RISO; cartulina/hojas = IDL Láser |
| Sobres alto volumen | Editorial | RISO | Sweet spot exacto de RISO (papel común + altísimo volumen) |
| Impresión vidrio/metal | Personalización rígida | UV | Aplicación canónica de UV |

---

## Notas técnicas para el import a Airtable

- El campo `Tecnologías recomendadas` debe ser **linked field** a tabla `Tecnologías` (o multi-select). Si es linked, Airtable hará match por nombre exacto del record en `Tecnologías`. Si es multi-select, los valores se crean como opciones nuevas si no existen.
- Los valores del CSV usan **coma como separador interno** dentro de comillas dobles (formato CSV estándar): `"DTF Textil,Sublimación"`.
- Si el match no funciona automáticamente, verificar que los nombres en la tabla `Tecnologías` sean exactamente: `DTF Textil`, `DTF UV`, `UV`, `Sublimación`, `Eco-Solvente`, `Solvente`, `RISO`, `IDL Láser`, `Gran Formato`, `Corte`.

## Verificación post-import

```sql
-- En el sub-workflow consultar_catalogo o consultar_aplicacion, el output debería incluir
-- las tecnologías recomendadas con NOMBRES (no IDs) gracias al Lookup field
-- "Nombre (from Tecnologías recomendadas)".
```

Test rápido en n8n con pin data sobre `consultar_aplicacion-v2`:
```json
{
  "descripcion": "wrap vehicular",
  "sustrato_mencionado": "",
  "session_id": "test_post_aplicaciones"
}
```
**Esperado**: `data.tecnologias_recomendadas: ["Eco-Solvente", "UV"]`, `message_to_agent` incluye los nombres.
