#!/usr/bin/env python3
"""
verify_csi.py — Verificación rápida de CSI real desde ESP32-S3

Escucha en UDP puerto 5005 y analiza si los paquetes recibidos
contienen Channel State Information (CSI) válida del ESP32.

Uso:
    python scripts/verify_csi.py --port 5005 --duration 30

Salida:
    - Cantidad de paquetes recibidos
    - Tamaño promedio de paquetes
    - Análisis de estructura CSI
    - Veredicto: CSI_REAL, CSI_FAKE, o SIN_DATOS

Requisitos:
    - Python 3.9+
    - Ninguna dependencia externa (solo stdlib)
"""

import argparse
import socket
import struct
import time
import sys
from collections import defaultdict


def parse_csi_packet(data: bytes) -> dict:
    """
    Intenta parsear un paquete CSI del formato de RuView/ESP32.
    El formato esperado (basado en el firmware) es:
        - Header: 'R', 'U', 'V', 'C', 'S', 'I' (6 bytes magic)
        - Seq: uint16 (2 bytes)
        - N_sub: uint8 (1 byte) — cantidad de subportadoras
        - N_rx: uint8 (1 byte) — cantidad de antenas RX
        - N_tx: uint8 (1 byte) — cantidad de antenas TX
        - CSI data: int16 complex values (2 bytes por subportadora × N_rx × N_tx)
        - RSSI: int8 (1 byte)
        - Rate: uint8 (1 byte)
        - Footer: checksum uint16 (2 bytes)
    """
    result = {
        "valid": False,
        "magic": None,
        "seq": None,
        "n_sub": None,
        "n_rx": None,
        "n_tx": None,
        "csi_len": None,
        "rssi": None,
        "rate": None,
        "raw_len": len(data),
    }

    if len(data) < 14:
        return result

    # Verificar magic bytes
    magic = data[:6]
    if magic != b"RUVCSI":
        return result

    result["magic"] = magic.decode("ascii", errors="replace")

    try:
        offset = 6
        result["seq"] = struct.unpack_from("<H", data, offset)[0]
        offset += 2
        result["n_sub"] = struct.unpack_from("<B", data, offset)[0]
        offset += 1
        result["n_rx"] = struct.unpack_from("<B", data, offset)[0]
        offset += 1
        result["n_tx"] = struct.unpack_from("<B", data, offset)[0]
        offset += 1

        # Validar rangos
        if not (1 <= result["n_sub"] <= 128):
            return result
        if not (1 <= result["n_rx"] <= 8):
            return result
        if not (1 <= result["n_tx"] <= 4):
            return result

        expected_csi_bytes = result["n_sub"] * result["n_rx"] * result["n_tx"] * 2
        result["csi_len"] = expected_csi_bytes

        if offset + expected_csi_bytes + 3 > len(data):
            return result

        offset += expected_csi_bytes
        result["rssi"] = struct.unpack_from("<b", data, offset)[0]
        offset += 1
        result["rate"] = struct.unpack_from("<B", data, offset)[0]
        offset += 1
        result["checksum"] = struct.unpack_from("<H", data, offset)[0]

        result["valid"] = True

    except struct.error:
        return result

    return result


def analyze_packets(packets: list) -> dict:
    """Analiza una lista de paquetes parseados y devuelve estadísticas."""
    stats = {
        "total_packets": len(packets),
        "valid_packets": sum(1 for p in packets if p["valid"]),
        "invalid_packets": sum(1 for p in packets if not p["valid"]),
        "avg_raw_len": 0,
        "avg_csi_len": 0,
        "seq_numbers": [],
        "rssi_values": [],
        "rates": set(),
        "n_sub_values": set(),
        "n_rx_values": set(),
        "n_tx_values": set(),
        "invalid_reasons": defaultdict(int),
    }

    if stats["total_packets"] == 0:
        return stats

    valid_packets = [p for p in packets if p["valid"]]
    stats["avg_raw_len"] = sum(p["raw_len"] for p in packets) / len(packets)
    stats["avg_csi_len"] = (
        sum(p["csi_len"] for p in valid_packets) / len(valid_packets)
        if valid_packets
        else 0
    )

    for p in packets:
        if p["valid"]:
            stats["seq_numbers"].append(p["seq"])
            stats["rssi_values"].append(p["rssi"])
            stats["rates"].add(p["rate"])
            stats["n_sub_values"].add(p["n_sub"])
            stats["n_rx_values"].add(p["n_rx"])
            stats["n_tx_values"].add(p["n_tx"])
        else:
            if p["raw_len"] < 14:
                stats["invalid_reasons"]["too_short"] += 1
            elif p["magic"] is None:
                stats["invalid_reasons"]["bad_magic"] += 1
            elif p["n_sub"] is not None and not (1 <= p["n_sub"] <= 128):
                stats["invalid_reasons"]["invalid_n_sub"] += 1
            elif p["n_rx"] is not None and not (1 <= p["n_rx"] <= 8):
                stats["invalid_reasons"]["invalid_n_rx"] += 1
            elif p["n_tx"] is not None and not (1 <= p["n_tx"] <= 4):
                stats["invalid_reasons"]["invalid_n_tx"] += 1
            else:
                stats["invalid_reasons"]["truncated"] += 1

    return stats


def print_results(stats: dict):
    """Imprime el reporte de verificación."""
    print("\n" + "=" * 60)
    print("REPORTE DE VERIFICACIÓN CSI — ESP32-S3")
    print("=" * 60)

    print(f"\n📊 Paquetes recibidos:")
    print(f"   Total:       {stats['total_packets']}")
    print(f"   Válidos:     {stats['valid_packets']}")
    print(f"   Inválidos:   {stats['invalid_packets']}")

    if stats["total_packets"] == 0:
        print("\n❌ SIN_DATOS — No se recibió ningún paquete.")
        print("   Verificá que:")
        print("   - El ESP32 esté encendido y conectado al WiFi")
        print("   - El puerto UDP 5005 esté abierto en el firewall")
        print("   - El ESP32 esté enviando a la IP correcta")
        return

    valid_ratio = stats["valid_packets"] / stats["total_packets"]
    print(f"\n📈 Ratio válidos/total: {valid_ratio:.1%}")

    if stats["valid_packets"] > 0:
        print(f"\n🔍 Estructura CSI detectada:")
        print(f"   Tamaño promedio paquete: {stats['avg_raw_len']:.0f} bytes")
        print(f"   Tamaño promedio CSI:     {stats['avg_csi_len']:.0f} bytes")
        print(f"   RSSI rango:              {min(stats['rssi_values'])} a {max(stats['rssi_values'])} dBm")
        print(f"   Rates detectados:        {sorted(stats['rates'])}")
        print(f"   Subportadoras:           {sorted(stats['n_sub_values'])}")
        print(f"   Antenas RX:              {sorted(stats['n_rx_values'])}")
        print(f"   Antenas TX:              {sorted(stats['n_tx_values'])}")

        # Verificar secuencias
        if len(stats["seq_numbers"]) > 1:
            seq_diffs = [
                stats["seq_numbers"][i + 1] - stats["seq_numbers"][i]
                for i in range(len(stats["seq_numbers"]) - 1)
            ]
            avg_diff = sum(seq_diffs) / len(seq_diffs)
            print(f"   Secuencia promedio diff: {avg_diff:.1f}")

    if stats["invalid_packets"] > 0:
        print(f"\n⚠️  Paquetes inválidos:")
        for reason, count in stats["invalid_reasons"].items():
            print(f"   {reason}: {count}")

    # Veredicto
    print("\n" + "=" * 60)
    if valid_ratio >= 0.8 and stats["valid_packets"] >= 10:
        print("✅ Veredicto: CSI_REAL")
        print("   El ESP32 está enviando Channel State Information válida.")
        print("   Podés proceder a comprar los 3 ESP32 restantes.")
    elif stats["valid_packets"] > 0 and valid_ratio >= 0.3:
        print("⚠️  Veredicto: CSI_PARCIAL")
        print("   Hay CSI válida pero también mucho ruido.")
        print("   Verificá la conexión WiFi y la configuración del ESP32.")
    else:
        print("❌ Veredicto: SIN_CSI_REAL")
        print("   No se detectó CSI válida del ESP32.")
        print("   Posibles causas:")
        print("   - El ESP32 no está en modo promiscuo")
        print("   - Firmware incorrecto o corrupto")
        print("   - Paquetes provenientes de otra fuente")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Verificación rápida de CSI real desde ESP32-S3"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5005,
        help="Puerto UDP para escuchar (default: 5005)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Duración de la captura en segundos (default: 30)",
    )
    parser.add_argument(
        "--bind-addr",
        default="0.0.0.0",
        help="Dirección IP para escuchar (default: 0.0.0.0)",
    )
    args = parser.parse_args()

    print(f"🎯 Escuchando CSI en UDP {args.bind_addr}:{args.port} por {args.duration} segundos...")
    print("   Asegurate de que el ESP32 esté encendido y provisionado.")
    print("   Presioná Ctrl+C para cancelar.\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((args.bind_addr, args.port))
    except OSError as e:
        print(f"❌ Error al bindear puerto {args.port}: {e}")
        print("   Verificá que no haya otro proceso usando ese puerto.")
        sys.exit(1)

    sock.settimeout(1.0)

    packets = []
    start_time = time.time()
    last_print = start_time

    try:
        while True:
            elapsed = time.time() - start_time
            if elapsed >= args.duration:
                break

            try:
                data, addr = sock.recvfrom(4096)
                parsed = parse_csi_packet(data)
                parsed["src_ip"] = addr[0]
                packets.append(parsed)

                # Mostrar progreso cada 5 segundos
                if time.time() - last_print >= 5:
                    valid_count = sum(1 for p in packets if p["valid"])
                    print(
                        f"   📦 {len(packets)} paquetes recibidos, "
                        f"{valid_count} válidos ({elapsed:.0f}s)"
                    )
                    last_print = time.time()

            except socket.timeout:
                continue

    except KeyboardInterrupt:
        print("\n\n⚠️  Captura interrumpida por usuario.")

    finally:
        sock.close()

    stats = analyze_packets(packets)
    print_results(stats)


if __name__ == "__main__":
    main()
