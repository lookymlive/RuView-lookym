# Protocolo de verificación CSI con ESP32-S3

Este documento es el **primer paso obligatorio** antes de comprar 4 ESP32. El objetivo es confirmar, con un solo ESP32, que realmente se puede capturar Channel State Information (CSI) de señales WiFi en el aire.

**Costo máximo de esta prueba:** ~$20 USD (1 ESP32-S3 DevKitC + cable USB-C con datos).

---

## 1. Hardware necesario (mínimo)`n`n> Nota incremental #70: verificación CSI revisada (2026-08-16).

| Componente | Cantidad | Precio aprox |
|------------|----------|--------------|
| ESP32-S3 DevKitC-1 (o similar) | 1 | $10-15 USD |
| Cable USB-C (debe tener datos, no solo carga) | 1 | $3-5 USD |
| **Total** | | **~$15-20 USD** |

> Importante: muchos cables USB-C económicos solo cargan. Si el ESP32 no aparece como dispositivo COM/serial, probá con otro cable.

---

## 2. Software necesario

- **Wireshark** — para capturar y analizar paquetes WiFi con CSI
- **Python 3.9+** — para correr el script de verificación
- **ESP-IDF v5.2+** — para compilar el firmware del ESP32
- **Docker Desktop** — alternativa para compilar el firmware sin instalar ESP-IDF

---

## 3. Paso 1: Obtener el ESP32

Comprar un ESP32-S3 DevKitC-1 en:
- AliExpress (buscar "ESP32-S3 DevKitC")
- Amazon
- Tiendas de electrónica locales

Modelo exacto recomendado: **ESP32-S3-DEVKITC-1** (fabricado por Espressif).

---

## 4. Paso 2: Conectar el ESP32 a la PC

1. Conectá el ESP32 a la PC con el cable USB-C.
2. Verificá que aparezca como puerto COM:
   - **Windows**: Abrir Device Manager → Ports (COM & LPT) → buscar "USB Serial" o similar.
   - Anotá el número de puerto (ej: `COM3`, `COM7`, etc.).

3. Si no aparece:
   - Probá otro cable USB-C.
   - Probá otro puerto USB.
   - Instalá los drivers CP210x o CH340 según el chip de la placa.

---

## 5. Paso 3: Compilar el firmware

### Opción A: Docker (recomendado, más fácil)

```powershell
cd C:\Users\usuario\Desktop\RuView-lookym

# Compilar el firmware de ESP32-CSI
MSYS_NO_PATHCONV=1 docker run --rm `
  -v "$(pwd)/firmware/esp32-csi-node:/project" -w /project `
  espressif/idf:v5.2 bash -c `
  "rm -rf build sdkconfig && idf.py set-target esp32s3 && idf.py build"
```

Esto genera los archivos binarios en `firmware/esp32-csi-node/build/`.

### Opción B: Instalar ESP-IDF localmente

```powershell
# Instalar ESP-IDF (requiere ~2 GB de espacio)
git clone -b v5.2 --recursive https://github.com/espressif/esp-idf.git C:\esp-idf
cd C:\esp-idf
.\install.bat
.\export.bat

# Compilar
cd C:\Users\usuario\Desktop\RuView-lookym\firmware\esp32-csi-node
idf.py set-target esp32s3
idf.py build
```

---

## 6. Paso 4: Flashear el firmware

```powershell
# Reemplazar COM7 por el puerto real de tu ESP32
python -m esptool --chip esp32s3 --port COM7 --baud 460800 `
  write_flash --flash_mode dio --flash_size 8MB `
  0x0 firmware/esp32-csi-node/build/bootloader/bootloader.bin `
  0x8000 firmware/esp32-csi-node/build/partition_table/partition-table.bin `
  0x10000 firmware/esp32-csi-node/build/esp32-csi-node.bin
```

Verificación:
- Deberías ver el LED del ESP32 parpadear durante el flasheo.
- Al finalizar, el ESP32 se reinicia automáticamente.

---

## 7. Paso 5: Verificar que el ESP32 está vivo

Abrí el monitor serial:

```powershell
python -m esptool --chip esp32s3 --port COM7 --baud 115200 monitor
```

Deberías ver mensajes como:
```
I (123) esp32-csi-node: WiFi CSI sender started
I (124) esp32-csi-node: Channel: 6
I (125) esp32-csi-node: Sending CSI to 192.168.1.20:5005
```

Si ves esto, el firmware está corriendo. Presioná `Ctrl+C` para salir.

---

## 8. Paso 6: Capturar paquetes WiFi con Wireshark (prueba DEFINITIVA)

Esta es la prueba más importante. Si ves paquetes con CSI en Wireshark, el ESP32 funciona de verdad.

### 8.1 Instalar Wireshark

Descargar de https://www.wireshark.org/download.html

### 8.2 Configurar la interfaz WiFi de la PC

**Importante:** Necesitás una tarjeta WiFi que soporte modo monitor y captura de CSI. No todas las tarjetas lo soportan.

Tarjetas conocidas que funcionan:
- Alfa AWUS036ACH (chipset Realtek RTL8812AU)
- Alfa AWUS036ACM (chipset Realtek RTL8814AU)
- Alfa AWUS036NH (chipset Realtek RTL8188LUS)

Si tu tarjeta WiFi integrada no soporta modo monitor, podés:
- Usar un adaptador USB WiFi compatible.
- Usar el ESP32 mismo como fuente de paquetes (ver opción alternativa abajo).

### 8.3 Capturar en modo monitor

1. Abrir Wireshark.
2. Seleccionar tu interfaz WiFi.
3. Click en "Capture Options".
4. Marcar "Monitor mode" (si está disponible).
5. Empezar captura.

### 8.4 Enviar paquetes desde el ESP32

Mientras Wireshark captura, forzá al ESP32 a enviar paquetes:
- Acercá el ESP32 a la PC (a menos de 1 metro).
- El ESP32 está en modo promiscuo capturando paquetes ajenos y enviando CSI por UDP a la IP configurada.

### 8.5 Filtrar en Wireshark

En el filtro de Wireshark escribí:
```
wlan.fc.type_subtype == 0x08 || wlan.fc.type_subtype == 0x05
```

Esto muestra Beacon frames (0x08) y CTS frames (0x05), que son los que el ESP32 está capturando.

### 8.6 Buscar CSI

Si tu tarjeta WiFi soporta CSI, en la información del paquete deberías ver una sección llamada:
```
Radio: CSI
```
o
```
CSI: ...
```

Si ves eso, **el ESP32 está capturando CSI real**. Confirmado.

---

## 9. Paso 6 alternativo: Usar el ESP32 como fuente de captura

Si tu tarjeta WiFi no soporta modo monitor, podés usar el ESP32 mismo para verificar que captura paquetes:

1. Configurar el ESP32 para que envíe paquetes de debug por serial.
2. O usar el ESP32 como sniffer pasivo y enviar los CSI por serial a la PC.
3. Analizar el stream serial para ver si hay datos de CSI válidos.

---

## 10. Paso 7: Probar detección de presencia básica

Una vez confirmado que hay CSI real, probá si el sistema detecta presencia:

### 10.1 Configurar el servidor en modo raw-capture

```powershell
cd C:\Users\usuario\Desktop\RuView-lookym\docker
$env:CSI_SOURCE="esp32"
$env:RUVIEW_API_TOKEN="test-token"
docker-compose up
```

### 10.2 Provisionar el ESP32

```powershell
python scripts/provision.py --port COM7 `
  --ssid "TuWiFi" --password "TuPass" --target-ip 192.168.1.20
```

### 10.3 Generar movimiento

1. Abrir el dashboard: http://localhost:4000/ui/index.html
2. Pararse frente al ESP32 (a 1-2 metros).
3. Mover las manos.
4. Observar si el banner cambia a "LIVE - ESP32" y si las métricas se actualizan.

### 10.4 Criterios de éxito

| Test | Resultado esperado | ¿Pasó? |
|------|-------------------|--------|
| ESP32 aparece en `/api/v1/nodes` | Sí, con IP y estado `online` | ☐ |
| RSSI cambia con movimiento | Sí, valores varían >3 dB | ☐ |
| `estimated_persons` cambia con gente | Sí, de 0 a 1 o más | ☐ |
| Vital signs detectadas (si hay movimiento) | BR o HR aparecen en la UI | ☐ |

**Si los 4 tests pasan:** el sistema funciona con hardware real. Podés comprar los 3 ESP32 restantes con confianza.

**Si fallan:** no pierdas más dinero. El proyecto tiene bases teóricas pero la implementación práctica requiere más ajuste del que parece.

---

## 11. Troubleshooting de la prueba

| Problema | Solución |
|----------|----------|
| ESP32 no aparece como COM | Probá otro cable, otro puerto, reinstalá drivers CP210x/CH340 |
| Firmware no compila | Usá Docker (Opción A), es más confiable |
| ESP32 se cuelga después de flashear | Alimentá con cargador de pared, no solo USB de la PC |
| Wireshark no ve paquetes | Probá con tarjeta WiFi USB compatible (Alfa AWUS036ACH) |
| No veo CSI en Wireshark | Algunas tarjetas muestran CSI pero Wireshark no lo decodifica. Confirmá con el script de Python |
| Dashboard no muestra datos | Verificá firewall (UDP 5005 abierto), verificá IP del servidor en provision |

---

## 12. Criterios de éxito final

**Antes de comprar 4 ESP32, necesitás confirmar:**

1. ✅ Firmware compila y flashea sin errores.
2. ✅ ESP32 se conecta a tu WiFi.
3. ✅ Wireshark captura paquetes con CSI (o el script Python confirma datos CSI válidos).
4. ✅ Dashboard muestra "LIVE - ESP32" y métricas cambian con movimiento.

**Si los 4 puntos se cumplen:** procedé a comprar 3 ESP32 más.

**Si alguno falla:** no compres más hardware hasta resolverlo.

---

## 13. Costo total del proyecto (si la prueba pasa)

| Componente | Cantidad | Precio aprox |
|------------|----------|--------------|
| ESP32-S3 DevKitC | 4 | $40-60 USD |
| Cables USB-C con datos | 4 | $15-20 USD |
| Cargadores de pared 5V/2A | 4 | $15-20 USD |
| Raspberry Pi 5 (4GB) | 1 | $40-50 USD |
| Tarjeta microSD 32GB | 1 | $5-8 USD |
| Switch Ethernet 5 puertos (opcional) | 1 | $10-15 USD |
| **Total** | | **~$125-173 USD** |

---

## 14. Próximos pasos después de la prueba

Si la prueba pasa:
1. Comprar 3 ESP32 restantes + accesorios.
2. Flash y provisionar los 4 nodos.
3. Configurar Raspberry Pi 5 como servidor.
4. Seguir `docs/DISTRIBUTED_SETUP.md` para la instalación completa.
5. Configurar Tailscale para acceso remoto (`docs/REMOTE_ACCESS.md`).

Si la prueba falla:
1. Documentar el error exacto.
2. Evaluar si requiere modificación del firmware.
3. Decidir si invertir tiempo en desarrollo o buscar alternativas.

---

## 15. Script de verificación rápida

Usar `scripts/verify_csi.py` para analizar si el ESP32 está enviando datos CSI válidos sin necesidad de Wireshark.

```powershell
# En una terminal, ejecutar el servidor en modo captura:
python scripts/verify_csi.py --port 5005 --duration 30
```

El script:
- Escucha en UDP puerto 5005 por 30 segundos.
- Analiza los paquetes recibidos.
- Reporta si contienen estructuras CSI válidas (longitud, formato, valores dentro de rangos esperados).
- Genera un veredicto: CSI_REAL o CSI_FAKE/SIMULATED.

**Veredicto esperado:** `CSI_REAL` con al menos 10 paquetes válidos en 30 segundos.


