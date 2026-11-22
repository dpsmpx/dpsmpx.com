#!/usr/bin/env bash
# fetch_sources — клоны репозиториев-источников для полного прогона (check_refs.py).
#
#   tools/verify/fetch_sources.sh
#
# Берёт источники вида repo из docs/sources/REGISTRY.md и кладёт голые
# частичные клоны (без содержимого файлов: коммиты и деревья) в
# build/sources/<клон>.git — или в каталог из DPPROFILE_SOURCES. Уже
# склонированное обновляется. Закрытые репозитории требуют доступа.
#
# Код возврата: 0 — все клоны на месте; 1 — хотя бы один не получен.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEST="${DPPROFILE_SOURCES:-$ROOT/build/sources}"
mkdir -p "$DEST"

LIST="$(python3 "$ROOT/tools/verify/docmodel.py" clones)" || exit 1
FAILED=0
while read -r name url; do
  [ -n "$name" ] || continue
  dir="$DEST/$name.git"
  if [ -d "$dir" ]; then
    printf '… обновление %s\n' "$name"
    git -C "$dir" fetch -q --prune --tags origin '+refs/heads/*:refs/heads/*' || { echo "✗ $name: fetch"; FAILED=1; }
  else
    printf '… клон %s (%s)\n' "$name" "$url"
    git clone -q --bare --filter=blob:none "$url" "$dir" || { echo "✗ $name: clone"; FAILED=1; }
  fi
done <<< "$LIST"

if [ "$FAILED" -eq 0 ]; then echo "✓ клоны источников: $DEST"; fi
exit "$FAILED"
