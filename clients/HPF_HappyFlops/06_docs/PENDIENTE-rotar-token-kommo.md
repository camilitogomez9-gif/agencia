# 🔴 Pendiente de seguridad — rotar el token de Kommo/amoCRM

**Detectado:** 2026-08-07, al escanear antes de pushear al remoto.

## Qué

El flujo de producción `[Happy Flops]` (`pYtiBlhOTr7HVPmr`) tiene un **JWT de larga
duración de Kommo/amoCRM hardcodeado en texto plano** dentro del nodo `All_Data`
(un Set node, campo `token`). Son 1.083 caracteres y **vence recién en 2030**.

Además hay **79 apariciones de `X-Auth-Token`** (UUIDs de amojo) repartidas entre el main
y los tres workflows de seguimiento.

## Dónde quedó copiado

- `03_workflows/happyflops-main-v3.json` — **ya estaba en `origin/main`** desde antes
  (pusheado el 2026-08-04 o antes).
- `03_workflows/base-2026-08-06/` — copia de agencia congelada en esta sesión.
- `03_workflows/base-prod-2026-08-06/` — fuente de verdad congelada en esta sesión.

El repo es **privado**, así que no hay exposición pública. Pero la credencial está viva
y en git, y con este push se agregan más copias.

## Qué hacer

1. **Rotar el token en Kommo** (revocar el actual, emitir uno nuevo).
2. Reemplazarlo en el nodo `All_Data` del flujo vivo — ⚠️ eso es tocar producción, va
   con la ventana y el cuidado que corresponda.
3. Idem los `X-Auth-Token` de amojo si siguen siendo válidos.
4. Recién después tiene sentido evaluar purgar el historial de git; hacerlo antes es
   inútil porque la credencial seguiría siendo válida.

## Por qué importa aunque el repo sea privado

Cualquiera con acceso de lectura al repo —hoy o en el futuro, incluido un handoff a otro
desarrollador— se lleva una credencial de producción de Kommo con 4 años de vigencia.
Y al migrar a GHL, Kommo se va a dar de baja: conviene rotar o revocar **antes** de que
la cuenta quede sin dueño operativo.
