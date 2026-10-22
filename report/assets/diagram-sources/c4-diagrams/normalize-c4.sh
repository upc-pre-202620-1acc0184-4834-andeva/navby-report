#!/bin/sh
cd /app/report/assets/diagram-sources/c4-exported 2>/dev/null || exit 0
for file in structurizr-*.puml; do
    [ -f "$file" ] || continue
    base=$(basename "$file" .puml | sed 's/^structurizr-//' | tr '[:upper:]' '[:lower:]')
    mv -f "$file" "${base}.puml"
done
