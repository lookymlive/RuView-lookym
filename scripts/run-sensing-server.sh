#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}/.."

cd "${REPO_ROOT}"

# ── Environment defaults ──────────────────────────────────────────────────────
export CSI_SOURCE="${CSI_SOURCE:-simulated}"
export RUST_LOG="${RUST_LOG:-info}"
export LOG_FORMAT="${LOG_FORMAT:-text}"
export HTTP_PORT="${HTTP_PORT:-3000}"
export WS_PORT="${WS_PORT:-3001}"
export BIND_ADDR="${BIND_ADDR:-0.0.0.0}"
export UI_PATH="${UI_PATH:-${REPO_ROOT}/ui}"

# ── Pre-flight checks ────────────────────────────────────────────────────────
if ! command -v cargo &>/dev/null; then
    echo "ERROR: Rust/cargo not found. Install from https://rustup.rs/"
    exit 1
fi

echo "Starting WiFi-DensePose Sensing Server..."
echo "  UI:    http://localhost:${HTTP_PORT}/ui/index.html"
echo "  API:   http://localhost:${HTTP_PORT}/api/v1/info"
echo "  WS:    ws://localhost:${WS_PORT}/ws/sensing"
echo "  Source: ${CSI_SOURCE}"
echo "  Logs:   ${LOG_FORMAT} format"
echo ""

cargo run --release -p wifi-densepose-sensing-server -- \
    --source "${CSI_SOURCE}" \
    --tick-ms 100 \
    --ui-path "${UI_PATH}" \
    --http-port "${HTTP_PORT}" \
    --ws-port "${WS_PORT}" \
    --bind-addr "${BIND_ADDR}" \
    --log-format "${LOG_FORMAT}"
