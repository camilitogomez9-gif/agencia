# Clientify: qué respaldar antes de apagarlo

**Para:** Venttur (Mauricio / Max) · **De:** el equipo de migración

Antes de apagar Clientify queremos ser transparentes sobre qué se pasa a GoHighLevel (GHL) y qué no, para que respalden por su cuenta lo que no viaja. Así nadie pierde información.

## Lo que pasamos nosotros a GHL (ya está o lo hacemos por API) ✅

- **Contactos** (los ~7.000 de Clientify, unificados con Airtable)
- **Oportunidades / deals** en sus pipelines (2.338)
- **Empresas** (266)
- **Campos personalizados** de contacto (datos de la encuesta, GDPR, etc.)
- **Asesores dueños** de cada contacto/deal (por email)

Todo eso lo migramos nosotros. No tienen que hacer nada con eso.

## Lo que NO migra a GHL, respalden ustedes 👇

Estas tres cosas no tienen forma de pasarse a GHL. Si las quieren conservar, tienen que respaldarlas desde Clientify antes de apagarlo:

1. **El historial de conversaciones / chat** (el inbox de Clientify). Los mensajes viejos con cada contacto no viajan.
2. **Los adjuntos** (archivos subidos en contactos y en deals).
3. **Las automatizaciones de Clientify** que quieran conservar como referencia. Las que estén vigentes las reconstruimos nosotros en GHL/n8n; el resto conviene guardarlas como respaldo.

## La regla, simple 🤝

**No apagamos Clientify hasta que:**
1. Ustedes respalden esas 3 cosas de arriba, y
2. Nosotros confirmemos que el traspaso de contactos y deals quedó completo y verificado.

Cuando esos dos pasos estén listos, recién ahí se apaga Clientify tranquilo, sin pérdida de nada.

---

## Nota interna (no para el cliente)

- El **segundo número** (el de recordatorios de Clientify) muere en el cutover y **no se avisa** a quien le escriba (decisión cerrada, `portabilidad §8`).
- Fuente: `00_migracion_ghl/05_ejecucion/auditoria-migrabilidad-clientify.md`. Es un **gate del cutover** (`12 §12.6`): cerrar esta brecha de expectativa (el cliente había entendido que "migra todo") antes de apagar Clientify.
