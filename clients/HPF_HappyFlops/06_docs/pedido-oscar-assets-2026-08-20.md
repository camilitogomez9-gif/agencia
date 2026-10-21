# Pedido a Oscar — archivos que faltan · 2026-08-20

Dos partes: el **mensaje para mandarle** (corto, directo) y el **detalle interno** de por qué
se pide cada cosa y qué se rompe sin eso.

---

## 1. Mensaje para Oscar

> Hola Oscar, para terminar de dejar el bot nuevo igual al viejo me faltan unos archivos.
> Son cinco cosas.
>
> **1. La infografía de pantuflas de boda con el precio nuevo.** La que tengo dice $29 el par
> y el precio actual es $30. El número está dentro de la imagen, así que no lo puedo corregir
> por texto. Las de XV y las de sandalias ya están bien, es sólo esta.
>
> **2. La infografía de mandiles con las 5 frases.** El catálogo nuevo que me pasaste tiene 5
> diseños, pero la ficha de mandiles sigue diciendo "6 frases diferentes para escoger". Si no la
> cambiamos, el bot dice 5 y muestra una imagen que promete 6.
>
> **3. Confirmame cuál es el PDF de números de cuenta que está vigente.** Tengo dos versiones
> dando vueltas, una se llama "NUMEROS DE CUENTA" y la otra "NUMEROS DE CUENTA NUEVA". Quiero
> estar seguro de cuál mandarle al cliente antes de subirla, porque es con la que transfieren
> el anticipo.
>
> **4. Los tres archivos de cilindros de la categoría "Otros".** La ficha de bautizo, la grilla
> de graduación y la grilla de bautizo y primera comunión. Hoy el bot nuevo manda ahí el
> material de XV, que no corresponde.
>
> **5. El archivo textos_salesbots.txt** que armaste hace unos meses, si lo tenés a mano. Me
> sirve para no tener que ir a buscar textos uno por uno a Kommo antes de darla de baja.
>
> Con eso cierro lo que falta. Gracias!

---

## 2. Detalle interno

### 1. Infografía pantuflas Boda con $30

**Ficha:** `Boda::Boda::Pantuflas boda` · asset actual `INFOGRAFÍA final 2-11 (1).png`
(PNG 4500×4500, 2,24 MB).

El `$29` está **rasterizado** en el starburst amarillo (`¡PROMO! $29 PAR`). Verificado abriendo
el archivo el 2026-08-20. Es la **única** de las 5 fichas con precio mal donde la imagen también
está mal: XV Pantuflas, Otros Pantuflas, XV Comparativa y Otros Comparativa ya muestran el
precio correcto y sólo necesitan corrección de texto.

**Sin esto:** el texto va a decir $30 y la imagen $29, en el mismo mensaje.

### 2. Infografía mandiles con 5 frases

**Ficha:** `Boda::Boda::Mandiles` · asset `INFOGRAFIA final-04 (1).png` (PNG 4500×4500, **6,12 MB**).

Dice **"6 Frases diferentes para escoger"**. El catálogo se reemplazó por el de 5 el 17/8 y el
prompt ya se ajustó para que el lead elija entre 5.

⚠️ **Aparte, esta imagen tiene un problema propio:** con 6,12 MB supera el límite de 5 MB de
Telegram y **mata el turno entero** (es la causa raíz de R3). Si Oscar manda una versión nueva,
pedirla o exportarla por debajo de 5 MB. Si no llega pronto, **se recomprime la actual** a
2400 px / calidad alta (976 KB, medido) y se corrige el "6" cuando llegue el arte definitivo.

### 3. PDF de números de cuenta

- **Migrado:** `NUMEROS DE CUENTA.pdf`, 2.539.068 bytes, recuperado de Airtable el 2026-08-20.
  Abierto y verificado: 1 página, legible, Banamex + OXXO/HSBC + BBVA.
- **El que manda el viejo:** `NUMEROS DE CUENTA NUEVA`, ~2,0 MB. **Archivo distinto.**
- **La URL que hoy sirve el bot nuevo da 404** (`NoSuchKey`), así que el PDF no sale.

**Por qué se pregunta en vez de subir el de Airtable:** el del viejo se llama "NUEVA". Subir el
otro sin confirmar sería servir números de cuenta posiblemente viejos en el documento con el que
el lead transfiere el anticipo.

### 4. Tres assets de cilindros de "Otros"

Bots de Kommo `61918` (CILINDROS OTROS INFO), `61920` (CILINDROS CATALOGO 1 OTROS),
`61922` (CILINDROS CATÁLOGO 2 OTROS).

Las filas de cilindros de Otros **vinieron vacías del CSV de Airtable** (sin descripción, sin
archivo, sin URL, sin CURL) — igual que las de XV. Los archivos que hay hoy los aportó Oscar el
7/8 y se aplicaron a **los dos** eventos, así que Otros terminó mostrando material de XV.

⚠️ **`Cilindros Catálogo 1` y `Cilindros Catálogo 2` NO son un duplicado**: son dos catálogos
distintos (graduación vs bautizo/comunión) y el viejo manda los dos. **No deduplicar.**

### 5. `textos_salesbots.txt`

Oscar lo produjo una vez; el análisis de mayo lo cita por número de línea
(`00_migracion_ghl/02_logica_validada/01_decisiones.md:60`). **Nunca estuvo en git.**

Es la vía barata: el runner de captura de Kommo **no extrae texto** (sólo dispara bots y hay que
exportar la conversación a mano), no tiene esperas entre disparos, tiene la URL del PATCH partida
por un salto de línea, y correrlo entero manda ~292 mensajes reales de WhatsApp a un lead de
producción. Si el .txt aparece, se evita buena parte de eso.
