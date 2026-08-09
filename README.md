# RuView – WiFi-DensePose Spatial Intelligence Platform

**Built by Studio Lookym | 2026**

> Daily maintenance: keeping GitHub updated with incremental improvements.

![Status](https://img.shields.io/badge/status-production-green?style=flat-square)
![Rust](https://img.shields.io/badge/Rust-1.85%2B-CE422B?style=flat-square&logo=rust)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT%2FApache%202.0-blue?style=flat-square)

> **Security Notice (2026-08-09):** Kilo Code / Anaconda notified users of a Metabase BI security incident on 2026-08-06. If you use Kilo Code with shared credentials, review your session history, audit API tokens, rotate any reused passwords, and monitor for phishing. See the [Anaconda blog](https://www.anaconda.com/blog) for updates.

---

## 🎯 What is RuView?

**RuView** is a cutting-edge spatial intelligence platform that transforms WiFi signals into actionable human presence, pose, and vital sign data. Using Channel State Information (CSI) from low-cost ESP32 sensors, it enables:

- **Through-wall detection** – Presence sensing without cameras
- **Pose estimation** – 17-point COCO keypoint detection via radio signals
- **Vital signs** – Heart rate (40-120 BPM) and breathing rate (0.1-0.5 Hz) extraction
- **Occupancy monitoring** – Real-time room and activity tracking
- **Privacy-first** – No cameras, no audio, fully edge-based
- **Multi-modal fusion** – Optional integration with depth cameras and mmWave radar

Perfect for disaster response, elderly care, smart buildings, and research.

---

## ⚡ Quick Features

| Feature | Capability | Latency | Hardware |
|---------|-----------|---------|----------|
| **Presence Detection** | Through 3 walls | <15ms | ESP32-S3 ($9) |
| **Pose Estimation** | 17 keypoints @ 30 FPS | <50ms | ESP32-S3 cluster |
| **Breathing Rate** | ±2 BPM accuracy | <5s | Single ESP32 |
| **Heart Rate** | 40-120 BPM ±5 | <10s | Dual ESP32 |
| **Multistatic Mesh** | 3x bandwidth fusion | <100ms | 3× ESP32 nodes |
| **Edge AI** | Inference @ <30ms | N/A | Onboard (no GPU) |

---

## 🏗️ Architecture

### Dual Codebase Strategy

| Component | Python (v1) | Rust (v2) |
|-----------|-----------|----------|
| **Status** | Legacy/Reference | Production ✓ |
| **Framework** | FastAPI | Axum |
| **Signal Proc** | NumPy/SciPy | RuvSense (14 modules) |
| **AI Runtime** | PyTorch 2.0 | ONNX/Candle |
| **Database** | PostgreSQL/SQLite | Postgres/SQLite/Redis |
| **Performance** | ~5ms per frame | <1ms per frame |

### Core Modules

**Signal Processing (RuvSense):**
- Multi-band CSI fusion & phase alignment
- Multistatic array coordination (attention-weighted)
- Coherence scoring & drift detection
- RF tomography (ISTA solver)
- Gesture & intention recognition
- Adversarial signal filtering

**Cross-Viewpoint Fusion (RuVector v2.0.4):**
- Geometric diversity indexing
- Antenna attention mechanisms
- Phase coherence with hysteresis gates
- Fisher Information matrix scaling

**Neural Inference:**
- ONNX Runtime backend (GPU/CPU)
- Candle (WASM + native)
- PyTorch (training only)

---

## 🚀 Getting Started

### Prerequisites

- **Rust 1.85+** — `rustup update`
- **Python 3.9+** — For v1 reference or proof validation
- **ESP-IDF v5.4** — For firmware builds
- **Docker** — Optional, for containerized deployment

### Option 1: Docker (Quickest)

```bash
docker run -p 3000:3000 \
  -e SIMULATE_CSI=true \
  studioolookym/ruviews:latest
```

### Option 2: Live Sensing with ESP32-S3 hardware ($9)

- Flash firmware, provision WiFi, and start sensing:
  ```bash
  python -m esptool --chip esp32s3 --port COM9 --baud 460800 \
    write_flash 0x0 bootloader.bin 0x8000 partition-table.bin \
    0xf000 ota_data_initial.bin 0x20000 esp32-csi-node.bin
  ```
  ```bash
  python firmware/esp32-csi-node/provision.py --port COM9 \
    --ssid "YourWiFi" --password "secret" --target-ip 192.168.1.20
  ```

### Option 3: Full system with Cognitum Seed ($140)

- ESP32 streams CSI → bridge forwards to Seed for persistent storage + kNN + witness chain
  ```bash
  node scripts/rf-scan.js --port 5006           # Live RF room scan
  node scripts/snn-csi-processor.js --port 5006  # SNN real-time learning
  node scripts/mincut-person-counter.js --port 5006  # Correct person counting
  ```

---

## 🧩 Claude Code & Codex Plugin

RuView ships a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin (and Codex prompt mirror) that wraps the whole workflow — onboarding, ESP32 setup, configuration, sensing apps, model training, advanced multistatic sensing, CLI/API/WASM, mmWave radar, and witness verification — as 9 skills, 7 `/ruview-*` commands, and 3 agents. It lives in [`plugins/ruview/`](plugins/ruview/README.md); the marketplace manifest is [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) at the repo root.

```bash
# In Claude Code — add this repo as a plugin marketplace, then install:
/plugin marketplace add ruvnet/RuView
/plugin install ruview@ruview

# Or try it for one session without installing (from a local clone of the repo):
claude --plugin-dir ./plugins/ruview

# Then, in Claude Code:
#   /ruview-start      → onboarding (Docker demo / repo build / live ESP32)
#   /ruview-flash      → build + flash ESP32 firmware
#   /ruview-provision  → provision WiFi creds, sink IP, channel/MAC, mesh slots
#   /ruview-app        → run a sensing application (presence / vitals / pose / sleep / MAT / point cloud)
#   /ruview-train      → train / evaluate / publish a model (incl. GPU on GCloud)
#   /ruview-advanced   → multistatic / tomography / cross-viewpoint / mesh-security
#   /ruview-verify     → tests + deterministic proof + witness bundle
```

**Codex (OpenAI CLI):** `cp plugins/ruview/codex/prompts/*.md ~/.codex/prompts/` — the seven `/ruview-*` commands are mirrored as Codex prompts; [`plugins/ruview/codex/AGENTS.md`](plugins/ruview/codex/AGENTS.md) carries the project rules. See [`plugins/ruview/codex/README.md`](plugins/ruview/codex/README.md).

Verify the plugin structure: `bash plugins/ruview/scripts/smoke.sh`. Full details: [`plugins/ruview/README.md`](plugins/ruview/README.md).

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/user-guide.md) | Step-by-step guide: installation, first run, API usage, hardware setup, training |
| [Build Guide](docs/build-guide.md) | Building from source (Rust and Python) |
| [Claude Code / Codex Plugin](plugins/ruview/README.md) | The `ruview` plugin + marketplace — skills, `/ruview-*` commands, agents, and the Codex prompt mirror |
| [Architecture Decisions](docs/adr/README.md) | 96 ADRs — why each technical choice was made, organized by domain (hardware, signal processing, ML, platform, infrastructure) |
| [Domain Models](docs/ddd/README.md) | 8 DDD models (RuvSense, Signal Processing, Training Pipeline, Hardware Platform, Sensing Server, WiFi-Mat, CHCI, rvCSI) — bounded contexts, aggregates, domain events, and ubiquitous language |
| [rvCSI — edge RF sensing runtime](https://github.com/ruvnet/rvcsi) | Rust-first / TypeScript-accessible / hardware-abstracted CSI runtime: multi-source ingestion (incl. real nexmon_csi `.pcap` from a **Raspberry Pi 5** / Pi 4 / Pi 3B+ — CYW43455 / BCM43455c0) → validation → DSP → typed events → RuVector RF memory ([ADR-095](docs/adr/ADR-095-rvcsi-edge-rf-sensing-platform.md), [ADR-096](docs/adr/ADR-096-rvcsi-ffi-crate-layout.md), [domain model](docs/ddd/rvcsi-domain-model.md)). Now its own repo — [`ruvnet/rvcsi`](https://github.com/ruvnet/rvcsi) — vendored here under `vendor/rvcsi`; 9 `rvcsi-*` crates on crates.io, `@ruv/rvcsi` on npm, plus a Claude Code plugin. |
| [Desktop App](v2/crates/wifi-densepose-desktop/README.md) | **WIP** — Tauri v2 desktop app for node management, OTA updates, WASM deployment, and mesh visualization |
| [Medical Examples](examples/medical/README.md) | Contactless blood pressure, heart rate, breathing rate via 60 GHz mmWave radar — $15 hardware, no wearable |
| [Extended Documentation](docs/readme-details.md) | Latest additions, key features, installation, quick start, signal processing, training, CLI, testing, deployment, and changelog |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 📞 Support

[GitHub Issues](https://github.com/ruvnet/RuView/issues) | [Discussions](https://github.com/ruvnet/RuView/discussions) | [PyPI](https://pypi.org/project/wifi-densepose/)

---

**WiFi DensePose** — Privacy-preserving human pose estimation through WiFi signals.
