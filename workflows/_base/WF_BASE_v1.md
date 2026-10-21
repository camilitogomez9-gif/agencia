# WORKFLOW TEMPLATE — BASE

## Metadata
- ID: WF_[NICHE]_[FUNCION]_v1
- Trigger: webhook | schedule | manual | event
- Niche: 
- Última modificación:

## Descripción funcional
**Input:** 
**Output:** 
**Propósito:**

## Flujo de nodos
```
[Trigger] 
  → [Validación de input]
  → [Transformación de datos]
  → [Condición/Router]
    ├─ Rama A: [acción]
    └─ Rama B: [acción]
  → [Integración externa]
  → [Confirmación / Log]
  → [Error Handler]
```

## Integraciones usadas
| Servicio | Credencial requerida | Endpoint |
|----------|---------------------|---------|
| | | |

## Variables de entorno
```
VAR_NAME=  # descripción
```

## Manejo de errores
- Error de credencial: [acción]
- Timeout: [acción]
- Datos malformados: [acción]
- Notificación de error a: [canal]

## JSON del workflow
[Pegar JSON exportado de n8n aquí]

## Historial de versiones
| Versión | Cambio | Fecha |
|---------|--------|-------|
| v1 | Versión inicial | |
