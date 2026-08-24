param(
    [string]$CsiSource = "simulated",
    [string]$LogFormat = "text",
    [int]$HttpPort = 3000,
    [int]$WsPort = 3001,
    [string]$BindAddr = "0.0.0.0"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path "$ScriptDir/.."

Set-Location $RepoRoot

if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Rust/cargo not found. Install from https://rustup.rs/"
    exit 1
}

$env:CSI_SOURCE = $CsiSource
$env:RUST_LOG = "info"
$env:LOG_FORMAT = $LogFormat
$env:HTTP_PORT = $HttpPort
$env:WS_PORT = $WsPort
$env:BIND_ADDR = $BindAddr
$env:UI_PATH = "$RepoRoot/ui"

Write-Host ""
Write-Host "Starting WiFi-DensePose Sensing Server..."
Write-Host "  UI:    http://localhost:${HttpPort}/ui/index.html"
Write-Host "  API:   http://localhost:${HttpPort}/api/v1/info"
Write-Host "  WS:    ws://localhost:${WsPort}/ws/sensing"
Write-Host "  Source: ${CsiSource}"
Write-Host "  Logs:   ${LogFormat} format"
Write-Host ""

Push-Location "$RepoRoot/v2"
cargo run --release -p wifi-densepose-sensing-server -- `
    --source $CsiSource `
    --tick-ms 100 `
    --ui-path "$RepoRoot/ui" `
    --http-port $HttpPort `
    --ws-port $WsPort `
    --bind-addr $BindAddr `
    --log-format $LogFormat
Pop-Location
