#!/usr/bin/env bash
# verify — все проверки DPprofile одной командой (CLAUDE.md, «Проверки»; D-08).
#
#   tools/verify/run.sh [--quick]   перед каждым коммитом: документы, ссылки, этапы, шлюз книги,
#                                   история фактов (если клон полный)
#   tools/verify/run.sh --full      перед вливанием в main: всё из --quick, плюс история фактов строго,
#                                   сверка ссылок с клонами источников (tools/verify/fetch_sources.sh)
#                                   и самопроверка; пропуск в полном режиме — ошибка
#
# Код возврата: 0 — всё прошло; 1 — хотя бы один шаг упал; 2 — неверный вызов.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 2

MODE=quick
case "${1:-}" in
  ""|--quick) ;;
  --full) MODE=full ;;
  -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
  *) echo "неизвестный параметр: $1 (есть --quick, --full)"; exit 2 ;;
esac

PY="${PYTHON:-python3}"
V=tools/verify
LOG_DIR="build/verify"
mkdir -p "$LOG_DIR"
FAILED=0
declare -a RESULTS=()

step() { # step <имя> <команда…>: итог — строкой, при отказе — журнал на экран
  local name="$1"; shift
  local log="$LOG_DIR/$(echo "$name" | tr ' /' '__').log"
  if "$@" >"$log" 2>&1; then
    RESULTS+=("$(grep -E '^✓' "$log" | tail -1)")
    grep -E '^  · ' "$log" || true
  else
    RESULTS+=("✗ $name (журнал: $log)")
    FAILED=1
    tail -40 "$log"
  fi
}

step "схема фактов"             "$PY" "$V/check_facts.py"
step "реестр источников"        "$PY" "$V/check_registry.py"
step "ссылки выводов"           "$PY" "$V/check_insights.py"
step "хронология"               "$PY" "$V/check_timeline.py"
step "внутренние ссылки"        "$PY" "$V/check_links.py"
step "запрещённые формулировки" "$PY" "$V/check_forbidden.py"
if [ "$MODE" = full ]; then
  step "этапы и критерии"       "$PY" "$V/check_stages.py" --strict
else
  step "этапы и критерии"       "$PY" "$V/check_stages.py"
fi
step "согласие документов"      "$PY" "$V/check_consistency.py"
step "шлюз книги"               "$PY" "$V/check_book_gate.py"
step "блок состояния README"    "$PY" "$V/readme_status.py"
if [ "$MODE" = full ]; then
  step "история фактов и решений" "$PY" "$V/check_history.py" --strict
  step "сверка ссылок с клонами"  "$PY" "$V/check_refs.py"
  step "самопроверка"             "$PY" "$V/selftest.py"
else
  step "история фактов и решений" "$PY" "$V/check_history.py"
fi

echo
echo "verify ($MODE):"
printf '  %s\n' "${RESULTS[@]}"
if [ "$FAILED" -ne 0 ]; then echo "✗ есть ошибки"; exit 1; fi
echo "✓ всё прошло"
