#!/bin/bash
# Fetch snapshot completo (schema + records paginados) de una base Airtable.
# Genérico para cualquier cliente — usado por el skill auditoria-airtable-cliente.
#
# Uso:
#   AIRTABLE_TOKEN=pat... AIRTABLE_BASE_ID=app... ./fetch-airtable-snapshot.sh /ruta/output
#
# Requiere: curl, python3 (jq es opcional pero no se usa para parsear — python3
# es más tolerante a control chars que rompen jq en campos de texto largo).

set -euo pipefail

if [ -z "${AIRTABLE_TOKEN:-}" ] || [ -z "${AIRTABLE_BASE_ID:-}" ]; then
  echo "ERROR: seteá AIRTABLE_TOKEN y AIRTABLE_BASE_ID antes de correr este script." >&2
  exit 1
fi

OUT_DIR="${1:?Uso: fetch-airtable-snapshot.sh /ruta/output}"
mkdir -p "$OUT_DIR"

echo "→ Fetching schema completo..."
curl -s -H "Authorization: Bearer $AIRTABLE_TOKEN" \
  "https://api.airtable.com/v0/meta/bases/$AIRTABLE_BASE_ID/tables" \
  > "$OUT_DIR/00-schema.json"

TABLE_COUNT=$(python3 -c "import json; print(len(json.load(open('$OUT_DIR/00-schema.json'))['tables']))")
echo "  $TABLE_COUNT tablas encontradas."

# Extraer pares (nombre-sanitizado, tableId) del schema
python3 - "$OUT_DIR" <<'PYEOF'
import json, re, sys
out_dir = sys.argv[1]
schema = json.load(open(f"{out_dir}/00-schema.json"))
pairs = []
for t in schema["tables"]:
    safe_name = re.sub(r"[^A-Za-z0-9]", "", t["name"])
    pairs.append((safe_name, t["id"], t["name"]))
with open(f"{out_dir}/.table-index.tsv", "w") as f:
    for safe, tid, real in pairs:
        f.write(f"{safe}\t{tid}\t{real}\n")
PYEOF

echo "→ Fetching records por tabla (paginado completo)..."
TOTAL=0
while IFS=$'\t' read -r SAFE_NAME TABLE_ID REAL_NAME; do
  python3 - "$AIRTABLE_TOKEN" "$AIRTABLE_BASE_ID" "$TABLE_ID" "$OUT_DIR/$SAFE_NAME.json" "$REAL_NAME" <<'PYEOF'
import json, sys, urllib.request, urllib.parse

token, base_id, table_id, out_path, real_name = sys.argv[1:6]
records = []
offset = None
pages = 0
while True:
    params = {"pageSize": 100}
    if offset:
        params["offset"] = offset
    url = f"https://api.airtable.com/v0/{base_id}/{urllib.parse.quote(table_id)}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    records.extend(data.get("records", []))
    offset = data.get("offset")
    pages += 1
    if not offset or pages > 50:
        break

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2, ensure_ascii=False)

print(f"  {real_name:30s} {len(records):4d} records")
PYEOF
  COUNT=$(python3 -c "import json; print(len(json.load(open('$OUT_DIR/$SAFE_NAME.json'))))")
  TOTAL=$((TOTAL + COUNT))
done < "$OUT_DIR/.table-index.tsv"

rm -f "$OUT_DIR/.table-index.tsv"

echo ""
echo "✅ Snapshot completo: $TABLE_COUNT tablas, $TOTAL records totales."
echo "   Output: $OUT_DIR/"
