# Distributed Setup Guide — 4-Node Home WiFi Sensing with RuView

> Daily maintenance note: distributed setup guide reviewed 2026-08-18

This guide explains how to deploy **4 ESP32-S3 nodes** in a home to enable WiFi-based sensing with RuView. You can aggregate data via a **Raspberry Pi 5** or a laptop.

---

## 1. Hardware List

| Item | Qty | Notes |
|------|-----|-------|
| ESP32-S3 development board | 4 | Built-in WiFi 2.4/5 GHz, USB-C |
| USB-C cable (data + power) | 4+1 | For flashing and powering each ESP32 |
| 5V USB-C power adapter | 4 | 2–3 A per adapter |
| **Optional:** PoE splitter (5V/2.4 A output) | 4 | 802.3af compatible |
| **Optional:** Ethernet cable (Cat5e/Cat6) | 4 | If using PoE or wired backhaul |
| **Optional:** PoE switch (4–8 port) | 1 | Centralized power and networking |
| **Optional:** Raspberry Pi 5 (4 GB+) | 1 | Aggregator / local server instead of laptop |
| **Optional:** Raspberry Pi USB-C power supply | 1 | Official 27 W USB-C PSU recommended |
| **Optional:** USB 3.0 Ethernet adapter | 1 | If using wired backhaul to Pi 5 |
| **Optional:** MicroSD card (32 GB) | 1 | For Raspberry Pi OS |
| **Optional:** Small enclosure / 3D-printed mount | 4 | To mount nodes in each room |

---

## 2. Power Options

Choose one of the following per node:

### A. Wall Adapter (Recommended)
- Plug each ESP32 into a wall outlet using a 5V USB-C adapter.
- Simplest and most reliable.
- Recommended for permanent installations.

### B. USB-C Power Bank
- Use a high-quality 5V/3 A power bank.
- Good for temporary or mobile setups.
- Monitor battery levels if used long-term.

### C. PoE + Ethernet (Advanced)
1. Connect ESP32 to a **PoE splitter** via Ethernet cable.
2. The splitter outputs 5V DC to the ESP32 USB-C port.
3. Connect all Ethernet cables to a **PoE switch**.
4. The switch powers the nodes *and* provides network connectivity.

### D. Raspberry Pi USB Hub
- If the Pi 5 acts as the aggregator, connect all 4 ESP32s via USB-C to the Pi’s USB 3.0 ports.
- Use a powered USB 3.0 hub if power draw exceeds Pi’s budget.

---

## 3. Physical Placement Strategy

Place one node in each major zone of the home to maximize coverage overlap and person-counting accuracy.

### Recommended Rooms
| Node | Location | Purpose |
|------|----------|---------|
| `ruview-node-01` | Living Room | Primary occupancy, main movement |
| `ruview-node-02` | Bedroom | Sleep/wake tracking |
| `ruview-node-03` | Hallway | Transit detection between rooms |
| `ruview-node-04` | Kitchen | Secondary occupancy, meal times |

### Coverage Overlap Diagram

```
          Bedroom (02)
           |
Hallway --[02]--[03]-- Kitchen (04)
  (03)     |      |      |
           |      |      |
        [01]----[03]----[04]
           |
       Living Room (01)

Legend: [0X] = Node placement
        --- = WiFi sensing coverage overlap
```

**Placement tips:**
- Mount nodes **high on a wall** or on a shelf (1.5–2 m elevation).
- Keep **line-of-sight** to the center of the room.
- Avoid placing directly behind large metal objects, mirrors, or inside metal cabinets.
- Maintain at least **1–2 meters** between nodes to reduce interference.
- USB-C port should face **outward** for easy access during flashing.

---

## 4. Wiring / Connection Diagram

### Option A: Raspberry Pi 5 Aggregator (Ethernet Switch)

```
                 +------------------+
                 |   PoE Switch     |
                 |  (or any switch) |
                 +----+------+------+
                      |      |
              Cat5e/Cat6   Cat5e/Cat6
                   |           |
            +------+---+   +---+------+
            | ESP32 01  |   | ESP32 02  |
            +-----------+   +-----------+
            | ESP32 03  |   | ESP32 04  |
            +-----------+   +-----------+
                      |      |
                 USB-C hub (optional)
                      |
                 +---------+
                 | Pi 5     |
                 | (Server) |
                 +---------+
```

### Option B: Laptop Aggregator (USB-C)

```
        +-----------+   +-----------+
        | ESP32 01  |   | ESP32 02  |
        +-----+-----+   +-----+-----+
        | ESP32 03  |   | ESP32 04  |
        +-----+-----+   +-----+-----+
                \         /
                 \       /
              USB-C hub (powered)
                       |
                   Laptop (Server)
```

---

## 5. Network Setup

### IP Addressing
- **Option 1 — Static IPs (recommended):**
  - `192.168.1.101` — `ruview-node-01`
  - `192.168.1.102` — `ruview-node-02`
  - `192.168.1.103` — `ruview-node-03`
  - `192.168.1.104` — `ruview-node-04`
  - `192.168.1.10`  — Aggregator (Pi 5 or Laptop)

- **Option 2 — DHCP with Reservations:**
  - Configure your router to reserve the above IPs based on each ESP32’s MAC address.

### Subnet
- Use your existing home LAN (e.g., `192.168.1.0/24`).
- All nodes and the aggregator must be on the **same subnet** and able to ping each other.

### Ports and Firewall Rules
- **UDP 5005** — ESP32 nodes send CSI/sensing data to the aggregator.
- **TCP 8080** (or as configured) — Dashboard/API access.

On the aggregator, ensure the firewall allows inbound UDP 5005:

```bash
# Linux (Pi 5)
sudo ufw allow 5005/udp

# Windows Defender Firewall
New-NetFirewallRule -DisplayName "RuView UDP 5005" -Direction Inbound -Protocol UDP -LocalPort 5005 -Action Allow
```

---

## 6. Software Installation on Raspberry Pi

### Option A: Rust Server (Recommended for Performance)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

# Clone repository
git clone https://github.com/your-org/ruview.git
cd ruview

# Build release binary
cargo build --release

# Run server in multistatic mode
./target/release/ruview-server --mode multistatic --nodes 192.168.1.101:5005,192.168.1.102:5005,192.168.1.103:5005,192.168.1.104:5005
```

### Option B: Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Run server container
docker run -d \
  --name ruview-server \
  --network=host \
  -e RUV_NODES="192.168.1.101:5005,192.168.1.102:5005,192.168.1.103:5005,192.168.1.104:5005" \
  -e RUV_MODE=multistatic \
  your-org/ruview-server:latest
```

### Option C: Python Backend

```bash
# Install Python dependencies
sudo apt install -y python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run server
python server.py --mode multistatic --nodes 192.168.1.101,192.168.1.102,192.168.1.103,192.168.1.104 --port 5005
```

---

## 7. Step-by-Step Provisioning

### Step 1: Build Firmware
```bash
git clone https://github.com/your-org/ruview-firmware.git
cd ruview-firmware

# Install ESP-IDF (if not already installed)
# Follow: https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/

# Configure for multistatic mode
cp sdkconfig.defaults.multistatic sdkconfig.local

# Build
idf.py build
```

### Step 2: Flash Each Node
```bash
# Flash Node 01
idf.py -p /dev/ttyUSB0 flash monitor

# Flash Node 02
idf.py -p /dev/ttyUSB1 flash monitor

# Flash Node 03
idf.py -p /dev/ttyUSB2 flash monitor

# Flash Node 04
idf.py -p /dev/ttyUSB3 flash monitor
```

### Step 3: Provision WiFi Credentials
Use the RuView provisioning tool or serial console:

```bash
# Using ruview-cli
ruview-cli provision --port /dev/ttyUSB0 --name ruview-node-01 --wifi-ssid "MyHomeWiFi" --wifi-pass "MyPassword"

ruview-cli provision --port /dev/ttyUSB1 --name ruview-node-02 --wifi-ssid "MyHomeWiFi" --wifi-pass "MyPassword"

ruview-cli provision --port /dev/ttyUSB2 --name ruview-node-03 --wifi-ssid "MyHomeWiFi" --wifi-pass "MyPassword"

ruview-cli provision --port /dev/ttyUSB3 --name ruview-node-04 --wifi-ssid "MyHomeWiFi" --wifi-pass "MyPassword"
```

Alternatively, use the serial monitor:
```bash
idf.py -p /dev/ttyUSB0 monitor
# In the monitor, type:
wifi ssid MyHomeWiFi
wifi pass MyPassword
name ruview-node-01
save
reboot
```

### Step 4: Verify Nodes Are Online
```bash
# Ping each node
ping 192.168.1.101
ping 192.168.1.102
ping 192.168.1.103
ping 192.168.1.104

# Or use ruview-cli to scan
ruview-cli scan
```

---

## 8. Starting the Server in Multistatic Mode

The **multistatic** mode aggregates data from multiple static ESP32 nodes into a unified sensing layer.

### Command
```bash
ruview-server --mode multistatic \
  --nodes 192.168.1.101:5005,192.168.1.102:5005,192.168.1.103:5005,192.168.1.104:5005 \
  --port 5005 \
  --bind 0.0.0.0
```

### As a Systemd Service (Pi 5)
```ini
# /etc/systemd/system/ruview.service
[Unit]
Description=RuView WiFi Sensing Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ruview
ExecStart=/home/pi/ruview/target/release/ruview-server --mode multistatic --nodes 192.168.1.101:5005,192.168.1.102:5005,192.168.1.103:5005,192.168.1.104:5005
Restart=always
Environment=RUST_LOG=info

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable ruview
sudo systemctl start ruview
sudo systemctl status ruview
```

---

## 9. Expected Behavior

### Dashboard
- The web dashboard displays a **floor plan** or room list with real-time occupancy.
- Each node contributes data; the server fuses detections to infer person count.
- Color-coded zones: green (empty), yellow (occupied), red (high density).

### Latency
- **End-to-end latency:** < 500 ms from movement to dashboard update.
- **Node-to-server latency:** < 100 ms over local WiFi.
- **Person count accuracy:** 80–95% in ideal conditions (clear paths, minimal interference).
- Accuracy improves with **node overlap** — zones where two nodes see the same area.

### Person Counting
- Single-room: ~90% accuracy with one node.
- Multi-room with 4 nodes: ~95% accuracy when fusing detections across the hallway.
- The system handles **occlusion** better when multiple viewpoints exist.

---

## 10. Troubleshooting

### Node Not Appearing
1. Verify the node is powered (LED on).
2. Check WiFi connection: `ruview-cli status --name ruview-node-01`
3. Ensure static IP / DHCP reservation is correct.
4. Ping the node from the aggregator: `ping 192.168.1.101`
5. Check that the node is sending to the correct server IP and port.

### UDP Blocked
- Confirm firewall on the aggregator allows UDP 5005.
- Verify no router-level firewall or AP isolation is blocking intra-LAN traffic.
- Disable “AP Isolation” or “Client Isolation” on your WiFi router/AP.

### IP Conflicts
- Use static IPs or DHCP reservations to avoid conflicts.
- Check for IP conflicts: `arp -a` on the aggregator.
- Reboot the router if nodes receive duplicate IPs.

### Low Accuracy / False Positives
- Reduce WiFi interference: switch to a less congested 2.4 GHz or 5 GHz channel.
- Re-position nodes for better room coverage.
- Increase **smoothing window** in server config if detections flicker.

### Server Crashing
- Check logs: `journalctl -u ruview -f` (systemd) or console output.
- Ensure all node IPs are reachable before starting the server.
- Update firmware and server to the latest versions.

---

## 11. Privacy and Legal Considerations

- **Only capture your own space.** Do not point ESP32 antennas at windows or shared walls where neighbor WiFi traffic is present.
- **Obtain consent** before sensing any space you do not own or control.
- **Local processing only.** All CSI/sensing data should be processed locally on your Pi 5 or laptop. Do not stream raw data to external cloud services unless explicitly intended.
- **Data retention:** Implement short retention policies if storing historical data.
- **Compliance:** Check local regulations regarding wireless sensing and privacy (e.g., GDPR in the EU, CCPA in California).

---

## Quick Start Checklist

- [ ] Purchase 4x ESP32-S3 boards and power supplies
- [ ] Choose aggregation method: Pi 5 (Ethernet switch) or Laptop (USB hub)
- [ ] Flash firmware to all 4 nodes
- [ ] Provision WiFi credentials and unique node names
- [ ] Configure static IPs / DHCP reservations
- [ ] Open firewall port UDP 5005 on aggregator
- [ ] Install and start RuView server in `multistatic` mode
- [ ] Open dashboard and verify all 4 nodes appear
- [ ] Test person counting in each room
- [ ] Review privacy settings and data retention policy
