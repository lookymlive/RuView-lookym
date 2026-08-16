# Manual de Usuario — RuView WiFi-DensePose

Guía paso a paso para instalar, configurar y usar RuView sin hardware especializado, además de notas para cuando tengas ESP32.

---

## 1. Requisitos previos`n`n> Nota incremental #51: documentación de usuario actualizada (2026-08-15).

- Docker Desktop instalado y corriendo en Windows
- PowerShell 7+ o terminal compatible
- Navegador moderno (Chrome, Edge, Firefox)
- No necesitás ESP32 para probar la versión simulada

---

## 2. Instalación rápida (sin hardware)

```powershell
cd C:\Users\usuario\Desktop\RuView-lookym\docker
$env:CSI_SOURCE="simulated"
docker-compose up
```

- UI: http://localhost:4000/ui/index.html
- API: http://localhost:4000
- WebSocket: ws://localhost:4001/ws/sensing

El modo simulado genera datos sintéticos de CSI. El banner de la UI dirá "SIMULATED DATA" en rojo.

---

## 3. Prueba con hardware real (ESP32-S3)

### 3.1 Hardware necesario

| Componente | Especificación | Notas |
|------------|---------------|-------|
| ESP32-S3 | DevKitC o similar | ~$7-15 USD |
| Flash | 8 MB | Necesario para firmware |
| USB-C | Para flasheo y alimentación | Usar el puerto izquierdo |

### 3.2 Compilar firmware

```powershell
cd C:\Users\usuario\Desktop\RuView-lookym
MSYS_NO_PATHCONV=1 docker run --rm `
  -v "$(pwd)/firmware/esp32-csi-node:/project" -w /project `
  espressif/idf:v5.2 bash -c `
  "rm -rf build sdkconfig && idf.py set-target esp32s3 && idf.py build"
```

### 3.3 Flashear

```powershell
python -m esptool --chip esp32s3 --port COM7 --baud 460800 `
  write_flash --flash_mode dio --flash_size 8MB `
  0x0 firmware/esp32-csi-node/build/bootloader/bootloader.bin `
  0x8000 firmware/esp32-csi-node/build/partition_table/partition-table.bin `
  0x10000 firmware/esp32-csi-node/build/esp32-csi-node.bin
```

> Nota: Cambiar `COM7` por el puerto real del ESP32 en tu máquina.

### 3.4 Provisionar WiFi

```powershell
python scripts/provision.py --port COM7 `
  --ssid "TuSSID" --password "TuPass" --target-ip 192.168.1.20
```

### 3.5 Iniciar servidor en modo real

```powershell
cd C:\Users\usuario\Desktop\RuView-lookym\docker
$env:CSI_SOURCE="esp32"
docker-compose up
```

Abrir http://localhost:4000/ui/index.html. El banner debe decir "LIVE - ESP32" en verde.

---

## 4. Detectar personas en la casa del vecino

### 4.1 Concepto básico

No necesitás el WiFi del vecino ni su contraseña. El ESP32 captura señales WiFi que ya están en el aire (2.4 GHz). Esas señales rebotan en las personas, y el ESP32 detecta esos cambios en el CSI.

### 4.2 Condiciones para que funcione

- El ESP32 debe estar cerca de la pared compartida (mejor en tu casa, apuntando hacia la casa vecina)
- La señal WiFi del vecino debe llegar a tu ESP32 (depende de potencia, pared, material)
- Cuanto más fuerte sea la señal que llega del vecino, mejor la detección

### 4.3 Limitaciones

- Paredes gruesas de concreto reducen mucho la señal
- Si la señal del vecino es débil, la detección será menos confiable
- La privacidad del vecino está protegida: solo se detecta presencia/movimiento, no se captura contenido de su red

---

## 5. Uso de la interfaz web

### 5.1 Pestañas principales

| Pestaña | Función |
|---------|---------|
| Dashboard | Métricas del sistema: CPU, memoria, estado de nodos |
| Sensing | Visualización 3D del campo de señal WiFi, RSSI, detección de movimiento y respiración |
| Live Demo | Esqueleto de pose en tiempo real (17 keypoints COCO) |
| Hardware | Configuración de ESP32 |
| Settings | Ajustes de conexión y parámetros |

### 5.2 Indicadores de estado

- **Verde "LIVE - ESP32"**: conectado a hardware real
- **Amarillo "RECONNECTING..."**: perdió conexión, reintentando
- **Rojo "SIMULATED DATA"**: modo simulado sin hardware

### 5.3 Pasos para probar sin ESP32

1. Levantar Docker con `CSI_SOURCE=simulated`
2. Abrir http://localhost:4000/ui/index.html
3. Ir a la pestaña "Sensing" y ver las métricas actualizándose
4. Ir a "Live Demo" y ver el esqueleto animado

---

## 6. Comandos útiles

```powershell
# Levantar en modo simulado
cd docker
$env:CSI_SOURCE="simulated"
docker-compose up

# Levantar en modo real (requiere ESP32)
$env:CSI_SOURCE="esp32"
docker-compose up

# Ver logs
docker-compose logs -f sensing-server

# Detener
docker-compose down
```

---

## 7. Solución de problemas comunes

| Problema | Solución |
|----------|----------|
| No veo la UI | Verificar que Docker esté corriendo y que el puerto 4000 esté libre |
| Banner rojo "SIMULATED DATA" pero quiero real | Cambiar `CSI_SOURCE=esp32` y verificar que el ESP32 esté en la misma red |
| No aparecen métricas | Refrescar la página, verificar que el WebSocket esté conectado |
| Error de puerto ocupado | Cambiar los puertos en `docker/docker-compose.yml` |

---

## 8. Seguridad y privacidad

- RuView no usa cámaras ni micrófonos
- Todo el procesamiento es local en el ESP32 o en tu servidor
- No se envían datos a la nube
- Para entornos compartidos, usar `RUVIEW_API_TOKEN` y `--bind-addr 127.0.0.1`


