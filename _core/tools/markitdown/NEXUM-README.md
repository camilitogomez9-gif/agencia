# MarkItDown (clon local)

Clon de [microsoft/markitdown](https://github.com/microsoft/markitdown) — MIT License.

**Pinned commit:** `e144e0a2be95b34df17433bac904e635f2c5e551` (clonado el 2026-06-27).

El `.git` interno fue eliminado para que esta carpeta no quede como nested repo dentro del workspace. Para actualizar:

```bash
cd /tmp && rm -rf markitdown-update && git clone --depth 1 https://github.com/microsoft/markitdown.git markitdown-update
rsync -a --delete --exclude='LA AGENCIA-README.md' /tmp/markitdown-update/ /Users/camilo/Downloads/camilo-workspace/_core/tools/markitdown/
rm -rf /tmp/markitdown-update
```

## Instalación local (ya hecha)

El binario `markitdown` está disponible globalmente vía pipx:

```bash
pipx install --python /opt/homebrew/bin/python3.12 'markitdown[all]'
```

Si pipx se rompe por el bug de `pyexpat` en macOS Tahoe (`Symbol not found: _XML_SetAllocTrackerActivationThreshold`), recompilar el Python afectado:

```bash
brew install expat
brew reinstall --build-from-source python@3.12
```

## Uso canónico en este workspace

Ver la sección **"Conversión automática de archivos pesados (MarkItDown)"** en el [CLAUDE.md](../../../CLAUDE.md) raíz.

## Limitaciones conocidas — qué NO convertir con MarkItDown

- **`.xlsx` / `.xls`** — se pierden las fórmulas (solo quedan valores calculados) y los headers se rompen cuando hay celdas mergeadas en la fila 1. La compresión además es pobre (~2× vs ~50-70× típico en PDF) porque XLSX ya es texto comprimido. Usar la skill `anthropic-skills:xlsx` o un script con `openpyxl` que preserve las fórmulas.
- **`.csv`** — ya es texto plano y tabular. Leer directo con `Read` (chicos) o herramientas tabulares (grandes).

Para todo el resto (PDF, DOCX, PPTX, HTML, EPUB, imágenes, audio, JSON/XML grandes, ZIP) MarkItDown es la primera opción.
