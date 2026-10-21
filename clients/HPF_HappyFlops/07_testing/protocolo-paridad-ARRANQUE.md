# Arranque para la sesión de Camilo

la agencia: pasale a Camilo el bloque de abajo tal cual. Es lo que él pega en su Claude Code, parado en la raíz del workspace.

---

```
Vas a ejecutar el protocolo de paridad de Happy Flops. Trabajás sobre este repo.

Antes de hacer NADA, leé completo:
  clients/HPF_HappyFlops/07_testing/protocolo-paridad-hpf-v1.md

Ese documento manda. Si algo de lo que yo te diga después lo contradice, gana el
documento, y me avisás.

CONTEXTO QUE NECESITÁS TENER EN LA CABEZA

El bot nuevo de Happy Flops no se comporta como el original y el cliente (Oscar) ya
se quejó varias veces. Hubo tres intentos previos de arreglarlo que se declararon
listos y no lo estaban. No fallaron por falta de esfuerzo: fallaron porque se
verificó a un nivel que no es el que le falla al cliente, y porque los casos de
prueba se eligieron a ojo en vez de derivarse.

Tu trabajo no es "hacer que ande". Es producir EVIDENCIA de que anda, o evidencia
precisa de qué no anda.

CÓMO QUIERO QUE TRABAJES

1. Arrancá por el pre-flight (Parte 1 del protocolo). Es bloqueante. Si un acceso
   falla, me lo decís en el momento — no seguís y me lo contás al final.

2. El estado del trabajo vive en archivos, no en tu contexto. Después de CADA caso
   escribís a MATRIZ.md y ESTADO.md. Si esta sesión se compacta o se corta, tengo
   que poder retomar leyendo esos archivos.

3. No me digas "funciona", "listo" o "quedó andando" sin una ruta a un archivo de
   evidencia en la misma oración. Si no tenés artefacto, la frase correcta es
   "no verificado".

4. Distinguí siempre estas tres cosas y usá las palabras exactas:
   VERIFICADO (con ruta) / INFERIDO / NO VERIFICADO.
   Nunca me reportes un inferido como si fuera un hecho.

5. Observar y arreglar son fases separadas. En la Fase 2 corrés todo y solo anotás.
   No empieces a arreglar el primer caso que falla.

6. Cuando encuentres una ambigüedad, NO frenes ni elijas en silencio: aplicá el
   default que dice el protocolo, marcala PROVISIONAL-EJECUTOR, y seguí. Se me
   consulta al final, todas juntas.

7. Alcance cerrado: 25 casos P0. No lo amplíes. Si te parece que falta cobertura,
   anotalo en PARKING.md y seguí.

EL TRIPWIRE

Corridos los primeros 20 casos, si el pase está por debajo del 60%, PARÁS y me
mandás el número crudo antes de escribir un solo fix. Renegociar el alcance es
decisión mía, no tuya.

LO QUE NO PODÉS HACER

- Tocar el bot viejo de Kommo (happyflops-main-v3.json ni los sub-workflows de
  seguimiento). Está en producción vendiendo. Cero leads de prueba ahí.
- Re-importar el JSON completo del workflow nuevo. Nodos sueltos, siempre.
- Escribirle a Oscar. El canal es Juanpi.
- Refactorizar de paso.

Empezá por el pre-flight y contame qué encontraste antes de seguir a la Fase 1.
```

---

## Lo que la agencia tiene que saber antes de mandarlo

**Tres cosas van por Juanpi, no por Camilo, y salen a primera hora:**

1. **El pedido de assets a Oscar** — el PDF de números de cuenta, los videos de producto y los catálogos PDF. Solo viven dentro de Kommo y esa cuenta se va a dar de baja. Sin el PDF de cuentas el bot no puede cerrar el Paso 5 solo. El texto está en el protocolo, Parte 1 §P4.

2. **El aviso de deltas a Oscar, antes de la demo.** Diez líneas: "estas N conductas del bot viejo no las replicamos a propósito", cada una con quién la pidió. Sin eso, Oscar prueba, ve una de las mejoras que él mismo firmó hace dos meses y dice "sigue sin andar igual que antes".

3. **Aprobar la matriz congelada antes de que Camilo ejecute.** Diez minutos. Es el único control de calidad que no depende de que el ejecutor se autoevalúe.

**Y una expectativa a calibrar:** el sistema nuevo no tiene reactivadores. El original dedica 41 de sus 146 salesbots a reenganchar leads que se enfrían, más 4 sub-workflows de seguimiento. El nuevo tiene cero. Es el 28% de la superficie de conducta del original y no se arregla con este protocolo — pero puede ser la razón principal si Oscar dice que el bot nuevo vende menos.
