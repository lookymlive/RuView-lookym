# Getting Started with RuView WiFi-DensePose

This guide walks you from clone to first pose detection.

## Prerequisites

- **Docker Desktop** (recommended for instant demo) OR
- **Rust 1.85+** (for local development)
- **PowerShell 7+** or Bash

## Option A: Docker Demo (Fastest)

1. Copy environment file:
   ```bash
   cp example.env .env
   ```

2. Start the stack:
   ```bash
   ./examples/getting-started/01_docker_demo.sh
   ```

3. Open http://localhost:4000/ui/index.html

## Option B: Local Rust Server

**Linux/macOS:**
```bash
./scripts/run-sensing-server.sh
```

**Windows (PowerShell):**
```powershell
.\scripts\start-sensing-server.ps1
```

Then open http://localhost:3000/ui/index.html

## Option C: Connect Real ESP32-S3

1. Flash `firmware/esp32-csi-node` with your WiFi SSID/password.
2. Set `CSI_SOURCE=esp32` in `.env`.
3. Restart the server.

## Next Steps

- See `docs/build-guide.md` for hardware verification.
- See `docs/USER_MANUAL.md` for full usage.
- See `docs/ESP32_CSI_VERIFICATION.md` for CSI validation.
