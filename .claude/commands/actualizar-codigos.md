# Actualizar Códigos — Sonrisas | Reporte Facturación

El usuario adjuntó o indicó la ruta de un archivo Excel con el Listado de Precios.

## Pasos

1. Identificar la ruta del archivo Excel adjunto o mencionado en el mensaje.

2. Correr el script:
```bash
python3 scripts/utilities/update-sonrisas-nodes.py "<ruta_al_excel>"
```

3. Mostrar la salida completa con los tres bloques de código JS listos para pegar en n8n:
   - **NODO: Filtro** → pegar en `Filtro1` del Reporte + `Filtro` y `Filtro3` del Correo
   - **NODO: Categoria** → pegar en `Categoria` del Reporte + `Categoria` y `Categoria1` del Correo
   - **NODO: Clase** → pegar en `Clase1` del Reporte + `Clase` y `Clase1` del Correo

4. Mostrar el resumen de totales al final para verificación rápida (códigos válidos, categorías, clases, ambiguos).

Si el script falla por dependencias faltantes, correr primero:
```bash
pip3 install pandas openpyxl
```
