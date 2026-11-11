#!/usr/bin/env bash
# Une videos .webm del historial en un solo archivo para la entrega (2–3 min).
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
SALIDA="${1:-$RAIZ/entregables/video-laboratorio.webm}"
LISTA="$(mktemp)"
CONCAT_LIST="$(mktemp)"
trap 'rm -f "$LISTA" "$CONCAT_LIST"' EXIT

find "$RAIZ/resultados" -path '*/historial/*.webm' -type f 2>/dev/null | sort >"$LISTA" || true
if [[ ! -s "$LISTA" ]]; then
  echo "No hay .webm en resultados/*/historial/. Corre demos 2–5 desde la interfaz primero." >&2
  exit 1
fi

mkdir -p "$(dirname "$SALIDA")"
: >"$CONCAT_LIST"
while IFS= read -r f; do
  printf "file '%s'\n" "$f" >>"$CONCAT_LIST"
done <"$LISTA"

ffmpeg -y -f concat -safe 0 -i "$CONCAT_LIST" -c copy "$SALIDA"
echo "Listo: $SALIDA"
