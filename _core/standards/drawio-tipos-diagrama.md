# draw.io — Tipos de Diagrama y Plantillas XML

Referencia para el comando `/diagramar`. Define los 4 tipos de diagrama, criterios de detección, plantillas XML y convenciones de estilo.

---

## Tipos de Diagrama

### 1. Llamada de Ventas → Diagrama de Flujo

**Criterios de detección:**
- Contiene diálogo entre vendedor y prospect
- Menciona objeciones, pricing, propuesta, cierre, próximos pasos
- Tiene frases como "¿cuánto cuesta?", "no estamos seguros", "nos interesa", "agendamos"
- Viene de Fathom u otra herramienta de grabación de llamadas

**Qué extraer:**
- Etapas de la llamada (apertura → discovery → pitch → objeciones → cierre)
- Objeciones detectadas y cómo se respondieron
- Información clave del prospect (empresa, problema, presupuesto si se menciona)
- Próximos pasos acordados

**Estructura del diagrama:**
- Flujo top-down o izquierda a derecha
- Etapas principales como rectángulos
- Objeciones como rombos con ramas de resolución
- Próximos pasos como elipses al final

---

### 2. Video de YouTube → Mapa Mental

**Criterios de detección:**
- Menciona creadores, canales, views, suscriptores, thumbnails
- Habla de estructura de video, hooks, CTAs, retención
- Viene de una transcripción de YouTube o análisis de contenido

**Qué extraer:**
- Tema central del video
- Subtemas o secciones principales
- Ideas/insights clave
- Oportunidades de contenido identificadas

**Estructura del diagrama:**
- Nodo central con el tema principal
- Ramas para cada subtema
- Sub-ramas para insights clave
- Flujo radial desde el centro

---

### 3. Proceso / Reunión → Diagrama de Proceso

**Criterios de detección:**
- Contiene secuencia de pasos numerados o con conectores temporales ("primero", "luego", "después")
- Menciona responsables, áreas o personas asignadas
- Habla de decisiones, aprobaciones, entregables
- Notas de reunión con acuerdos y acciones

**Qué extraer:**
- Pasos en orden cronológico/lógico
- Puntos de decisión (sí/no, aprobado/rechazado)
- Responsables de cada paso
- Outputs o entregables de cada etapa

**Estructura del diagrama:**
- Flujo izquierda a derecha
- Inicio y fin con elipses
- Pasos como rectángulos
- Decisiones como rombos con ramas
- Responsables como labels sobre las flechas

---

### 4. Genérico → Mapa de Relaciones

**Criterios de detección:**
- No encaja claramente en ninguno de los anteriores
- Texto descriptivo sobre entidades, conceptos o sistemas
- Notas informales, ideas sueltas, brainstorming

**Qué extraer:**
- Entidades principales (personas, empresas, conceptos, sistemas)
- Relaciones entre ellas (depende de, conecta con, genera, usa)
- Jerarquías implícitas
- Flujos de información o valor

**Estructura del diagrama:**
- Nodos como rectángulos redondeados
- Conexiones con labels descriptivos
- Agrupaciones por categoría si aplica

---

## Plantillas XML Base

### Plantilla: Diagrama de Flujo (Llamada de Ventas)

```xml
<mxfile host="Claude">
  <diagram name="Llamada de Ventas" id="diagram-ventas">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- INICIO -->
        <mxCell id="2" value="Inicio Llamada" style="ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="80" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- ETAPA 1: APERTURA -->
        <mxCell id="3" value="Apertura" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="80" y="200" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- ETAPA 2: DISCOVERY -->
        <mxCell id="4" value="Discovery" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="80" y="320" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- ETAPA 3: PITCH -->
        <mxCell id="5" value="Pitch / Propuesta" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="80" y="440" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- OBJECION (rama lateral) -->
        <mxCell id="6" value="¿Objeción?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="310" y="440" width="140" height="80" as="geometry" />
        </mxCell>
        <!-- MANEJO OBJECION -->
        <mxCell id="7" value="Manejo de Objeción" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;" vertex="1" parent="1">
          <mxGeometry x="520" y="450" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- CIERRE -->
        <mxCell id="8" value="Cierre" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="80" y="580" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- PROXIMOS PASOS -->
        <mxCell id="9" value="Próximos Pasos" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="700" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- CONEXIONES -->
        <mxCell id="10" edge="1" source="2" target="3" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="11" edge="1" source="3" target="4" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="12" edge="1" source="4" target="5" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="13" edge="1" source="5" target="6" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="14" value="Sí" edge="1" source="6" target="7" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="15" value="No" edge="1" source="6" target="8" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="16" edge="1" source="7" target="8" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="17" edge="1" source="8" target="9" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

### Plantilla: Mapa Mental (YouTube)

```xml
<mxfile host="Claude">
  <diagram name="Mapa Mental" id="diagram-youtube">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- CENTRO: TEMA PRINCIPAL -->
        <mxCell id="2" value="Tema Central" style="ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="450" y="350" width="200" height="80" as="geometry" />
        </mxCell>
        <!-- SUBTEMA 1 -->
        <mxCell id="3" value="Subtema 1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="180" y="200" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- SUBTEMA 2 -->
        <mxCell id="4" value="Subtema 2" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="180" y="400" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- SUBTEMA 3 -->
        <mxCell id="5" value="Subtema 3" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="760" y="200" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- SUBTEMA 4 -->
        <mxCell id="6" value="Subtema 4" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="760" y="400" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- INSIGHT bajo Subtema 1 -->
        <mxCell id="7" value="Insight clave" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="60" y="310" width="140" height="50" as="geometry" />
        </mxCell>
        <!-- CONEXIONES -->
        <mxCell id="8" edge="1" source="2" target="3" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="9" edge="1" source="2" target="4" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="10" edge="1" source="2" target="5" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="11" edge="1" source="2" target="6" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="12" edge="1" source="3" target="7" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

### Plantilla: Diagrama de Proceso (Reunión)

```xml
<mxfile host="Claude">
  <diagram name="Diagrama de Proceso" id="diagram-proceso">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- INICIO -->
        <mxCell id="2" value="Inicio" style="ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="360" width="100" height="60" as="geometry" />
        </mxCell>
        <!-- PASO 1 -->
        <mxCell id="3" value="Paso 1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="240" y="360" width="140" height="60" as="geometry" />
        </mxCell>
        <!-- PASO 2 -->
        <mxCell id="4" value="Paso 2" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="440" y="360" width="140" height="60" as="geometry" />
        </mxCell>
        <!-- DECISION -->
        <mxCell id="5" value="¿Decisión?" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="640" y="345" width="140" height="90" as="geometry" />
        </mxCell>
        <!-- RAMA SI -->
        <mxCell id="6" value="Paso 3A" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="840" y="280" width="140" height="60" as="geometry" />
        </mxCell>
        <!-- RAMA NO -->
        <mxCell id="7" value="Paso 3B" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;" vertex="1" parent="1">
          <mxGeometry x="840" y="420" width="140" height="60" as="geometry" />
        </mxCell>
        <!-- FIN -->
        <mxCell id="8" value="Fin" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="1050" y="360" width="100" height="60" as="geometry" />
        </mxCell>
        <!-- CONEXIONES -->
        <mxCell id="9" edge="1" source="2" target="3" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="10" edge="1" source="3" target="4" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="11" edge="1" source="4" target="5" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="12" value="Sí" edge="1" source="5" target="6" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="13" value="No" edge="1" source="5" target="7" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="14" edge="1" source="6" target="8" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="15" edge="1" source="7" target="8" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

### Plantilla: Mapa de Relaciones (Genérico)

```xml
<mxfile host="Claude">
  <diagram name="Mapa de Relaciones" id="diagram-generico">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- ENTIDAD CENTRAL -->
        <mxCell id="2" value="Entidad Central" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=13;" vertex="1" parent="1">
          <mxGeometry x="450" y="360" width="180" height="60" as="geometry" />
        </mxCell>
        <!-- ENTIDAD A -->
        <mxCell id="3" value="Entidad A" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="180" y="240" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- ENTIDAD B -->
        <mxCell id="4" value="Entidad B" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="180" y="460" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- ENTIDAD C -->
        <mxCell id="5" value="Entidad C" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="760" y="240" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- ENTIDAD D -->
        <mxCell id="6" value="Entidad D" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
          <mxGeometry x="760" y="460" width="160" height="60" as="geometry" />
        </mxCell>
        <!-- CONEXIONES CON LABELS -->
        <mxCell id="7" value="relación" edge="1" source="3" target="2" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="8" value="relación" edge="1" source="4" target="2" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="9" value="relación" edge="1" source="2" target="5" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
        <mxCell id="10" value="relación" edge="1" source="2" target="6" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

## Convenciones de Estilo

### Colores por Rol

| Tipo de Nodo | Color Fill | Color Stroke | Uso |
|---|---|---|---|
| Inicio / Fin | `#dae8fc` | `#6c8ebf` | Puntos de entrada y salida |
| Paso / Proceso | `#f5f5f5` | `#666666` | Acciones principales |
| Decisión | `#fff2cc` | `#d6b656` | Bifurcaciones y preguntas |
| Resultado Positivo | `#d5e8d4` | `#82b366` | Cierre exitoso, aprobación |
| Alerta / Objeción | `#ffe6cc` | `#d79b00` | Problemas, objeciones, rechazos |
| Insight / Nota | `#fff2cc` | `#d6b656` | Información secundaria |

### Reglas Generales

- **Máximo 15 nodos** por diagrama — priorizar claridad
- **Labels concisos** — máximo 4 palabras por nodo
- **IDs únicos** — usar números secuenciales (0, 1, 2, ...)
- **IDs 0 y 1** siempre reservados para `mxCell` raíz (no modificar)
- Flujo **top-down** para llamadas y procesos; **radial** para mapas mentales
- Conexiones con `source` y `target` apuntando a IDs de nodos existentes
