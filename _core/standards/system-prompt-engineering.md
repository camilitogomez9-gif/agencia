# Guía de System Prompt Engineering — la agencia

Principios y patrones para diseñar system prompts de agentes conversacionales en n8n.

---

## 1. Principios Fundamentales

### 1.1 Especificidad sobre generalidad
Un prompt vago produce un agente vago. Cada instrucción debe ser observable y testeable.

❌ **Malo:** "Respondé de forma amable"  
✅ **Bueno:** "Mensajes de máximo 200 caracteres. Nunca uses frases como 'Espero que te encuentres bien'. Tuteo rioplatense siempre."

### 1.2 Una sola pregunta a la vez
Regla universal para agentes conversacionales en mensajería. Múltiples preguntas en un mensaje generan respuestas parciales o confusión.

### 1.3 Jerarquía de objetivos clara
El modelo necesita saber qué priorizar cuando hay conflicto. Orden típico:
1. Seguridad / no revelar info sensible
2. Objetivo principal del agente (calificar, vender, informar)
3. Satisfacción del usuario
4. Eficiencia de la conversación

### 1.4 Separar información de comportamiento
- **Base de conocimiento** = qué sabe el agente (precios, servicios, horarios)
- **Instrucciones** = cómo se comporta el agente (flujo, tono, herramientas)
Mezclarlos genera prompts difíciles de mantener.

### 1.5 Reglas críticas explícitas, no implícitas
Si algo nunca debe pasar, decilo explícitamente con "NUNCA". No confíes en que el modelo infiera prohibiciones.

---

## 2. Estructura Recomendada

Las secciones van en este orden por una razón: el modelo "lee" el prompt de arriba a abajo y las instrucciones anteriores anclan la interpretación de las siguientes.

```
1. ROL E IDENTIDAD          ← quién es el agente
2. PERSONALIDAD Y TONO      ← cómo habla
3. OBJETIVO PRINCIPAL       ← para qué existe
4. FLUJO DE CONVERSACIÓN    ← cómo avanza la conversación
5. INSTRUCCIONES OPERATIVAS ← comportamientos específicos
6. HERRAMIENTAS             ← cuándo y cómo usar tools
7. BASE DE CONOCIMIENTO     ← qué sabe
8. REGLAS CRÍTICAS          ← qué nunca debe hacer
9. ESCALADA A HUMANO        ← cuándo ceder el control
```

---

## 3. Patrones Efectivos

### 3.1 El patrón "Admitidor, no Vendedor"
En agentes de calificación, el agente no vende — evalúa si hay fit. Esto reduce la resistencia del usuario y aumenta la tasa de agendamiento.

```
"Nosotros también tenemos que evaluar si este programa es para vos. 
¿Querés que hablemos 20 minutos para ver si tiene sentido?"
```

### 3.2 Etapas explícitas de conversación
Nombrar las etapas le da al modelo contexto sobre "en qué momento está" y qué debe hacer a continuación. Sin etapas, el modelo puede saltar al pitch antes de entender el problema.

```
ETAPA 1 — Apertura: presentarse y hacer la primera pregunta de calificación
ETAPA 2 — Diagnóstico: entender la situación actual (2-4 mensajes)
ETAPA 3 — Conexión: relacionar el problema con la solución (brevemente)
ETAPA 4 — CTA: proponer el siguiente paso
```

### 3.3 Ejemplos de tono correcto e incorrecto
Los ejemplos concretos son más efectivos que las descripciones abstractas.

```
Correcto: "che, ¿hoy cómo estás consiguiendo clientes?"
Incorrecto: "Estimado usuario, me gustaría saber cuál es su método actual de adquisición de clientes"
```

### 3.4 Triggers explícitos para herramientas
Nunca: "activá la herramienta cuando sea necesario"  
Siempre: "activá 'notificar' cuando (a) el usuario pida hablar con un humano, (b) el usuario proponga un horario específico, o (c) la pregunta requiere información que no está en estas instrucciones"

### 3.5 Respuestas verbatim para momentos clave
Para momentos críticos de la conversación (envío del link, mensaje de cierre, bienvenida), incluir el texto exacto que debe enviar el agente. Elimina variabilidad indeseada.

```
Al enviar el link de agendamiento, mandá exactamente este mensaje:
"[texto exacto]"
```

---

## 4. Errores Comunes

| Error | Consecuencia | Solución |
|-------|-------------|----------|
| Instrucciones contradictorias | El modelo elige arbitrariamente | Revisar coherencia antes de deployar |
| Demasiadas reglas (>15) | El modelo ignora las últimas | Priorizar y eliminar las redundantes |
| Base de conocimiento desactualizada | Respuestas incorrectas sobre precios/servicios | Versionar el prompt con fecha |
| No definir casos de escalada | El agente intenta responder todo | Siempre incluir criterios de derivación a humano |
| Reglas implícitas ("sé profesional") | Interpretación inconsistente | Hacer todo explícito y testeable |
| Flujo sin etapas | El agente va directo al pitch | Siempre definir etapas con criterios de avance |

---

## 5. Calibración Post-Lanzamiento

Revisar después de las primeras 20-50 conversaciones reales:

1. **Tasa de llegada a la CTA**: ¿el agente logra proponer el siguiente paso en la mayoría de las conversaciones?
2. **Naturalidad del tono**: pedirle a alguien que lea 5 conversaciones sin saber que son automáticas
3. **Preguntas sin respuesta**: ¿hay preguntas frecuentes que el agente no sabe manejar? → agregar a la base de conocimiento
4. **Falsos positivos en herramientas**: ¿activa tools en momentos incorrectos? → hacer el trigger más específico
5. **Mensajes muy largos**: ¿el agente responde con párrafos? → agregar regla de longitud máxima

---

## 6. Variables Dinámicas en n8n

Para personalizar prompts con datos del contexto (nombre del usuario, historial, etc.), usar doble llave como convención:

```
{{NOMBRE_USUARIO}}     ← nombre del lead/cliente
{{HISTORIAL}}          ← historial de conversación formateado
{{NICHO}}              ← categoría del prospecto
{{FECHA_HOY}}          ← fecha actual (útil para confirmaciones)
```

El nodo Code en n8n reemplaza estas variables antes de enviar el prompt al modelo.

---

## 7. Checklist Antes de Deployar

- [ ] ¿Está definido claramente quién es el agente y qué empresa representa?
- [ ] ¿El objetivo principal está en una sola oración?
- [ ] ¿El flujo tiene etapas nombradas con criterios de avance?
- [ ] ¿Cada herramienta tiene un trigger explícito y datos requeridos?
- [ ] ¿Las reglas críticas usan "NUNCA" / "SIEMPRE"?
- [ ] ¿Hay criterios de escalada a humano?
- [ ] ¿La base de conocimiento está actualizada con precios y servicios vigentes?
- [ ] ¿El prompt fue testeado manualmente con al menos 5 escenarios distintos?
- [ ] ¿Se registró la versión y la fecha?
