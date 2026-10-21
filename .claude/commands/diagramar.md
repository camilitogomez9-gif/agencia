# Diagramar

Analizá el texto recibido y generá un diagrama draw.io claro y útil.

## Variables

input: $ARGUMENTS (texto a diagramar — transcripción, notas, llamada, etc.)

---

## Instrucciones

### Fase 1: Detección de Tipo

Determiná el tipo de input según estos criterios (en orden de prioridad):

- **llamada-ventas**: contiene diálogo vendedor/prospect, objeciones, pricing, cierre, próximos pasos. Señales: "¿cuánto cuesta?", "no estamos seguros", "agendamos", presencia de dos interlocutores claros.
- **youtube**: menciona creadores, canales, views, suscriptores, thumbnails, hooks, CTAs, retención, estructura de video.
- **proceso-reunion**: secuencia de pasos con orden lógico o temporal, responsables asignados, decisiones, entregables. Señales: "primero", "luego", "quien se encarga", "queda pendiente".
- **generico**: cualquier otro texto — conceptos, ideas sueltas, descripciones de sistemas o relaciones.

Indicá el tipo detectado antes de continuar.

---

### Fase 2: Extracción de Contenido

Según el tipo detectado, extraé los elementos clave del texto:

**llamada-ventas:**
- Etapas de la llamada (apertura, discovery, pitch, objeciones, cierre)
- Objeciones detectadas y cómo se manejaron
- Información clave del prospect (empresa, problema, presupuesto si se menciona)
- Próximos pasos acordados

**youtube:**
- Tema central del video o análisis
- Subtemas o secciones principales
- Ideas/insights clave mencionados
- Oportunidades de contenido identificadas

**proceso-reunion:**
- Pasos en secuencia lógica/temporal
- Puntos de decisión (sí/no, aprobado/rechazado)
- Responsables mencionados
- Outputs o entregables de cada etapa

**generico:**
- Entidades principales (personas, empresas, conceptos, sistemas)
- Relaciones entre ellas (depende de, genera, usa, conecta con)
- Jerarquías o flujos implícitos

Mostrá la lista de elementos extraídos antes de generar el XML.

---

### Fase 3: Generación del XML

Usá la plantilla del tipo correspondiente en `referencia/drawio-tipos-diagrama.md` como base.

Generá el XML completo con estas reglas:
- **Máximo 15 nodos** — priorizá claridad sobre exhaustividad
- **Labels concisos** — máximo 4 palabras por nodo
- **IDs únicos y secuenciales** — IDs 0 y 1 siempre son los mxCell raíz, empezá los nodos desde el ID 2
- **Flujo coherente** — top-down o izquierda a derecha para llamadas y procesos; radial para mapas mentales
- **Colores por rol** según la tabla en `referencia/drawio-tipos-diagrama.md`
- Cada conexión (`edge`) debe tener `source` y `target` apuntando a IDs existentes

El XML debe ser válido e importable directamente en draw.io sin edición manual.

---

### Fase 4: Guardar y Entregar

1. **Guardá el XML** en `salidas/diagramas/YYYY-MM-DD-{tipo}-{tema-corto}.drawio`
   - Ejemplo: `salidas/diagramas/2026-03-06-ventas-la agencia-discovery.drawio`
   - Usá la fecha actual y un nombre descriptivo en kebab-case

2. **Mostrá un resumen:**
   - Tipo detectado
   - Elementos principales extraídos
   - Nombre del archivo guardado

3. **Llamá al Skill de draw.io** con el XML generado.
   - [INTEGRACIÓN PENDIENTE: conectar con el Skill cuando esté disponible en la sesión]
   - El Skill recibe el XML como string o la ruta al archivo `.drawio`

4. **Confirmá al usuario** que el diagrama está listo e indicá cómo abrirlo si el Skill no está disponible:
   - Importar en draw.io: Archivo → Importar desde → Dispositivo → seleccionar el `.drawio`
   - O ir a app.diagrams.net y arrastrar el archivo
