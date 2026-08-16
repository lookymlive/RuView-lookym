# Monitoreo remoto — Acceso desde fuera de la casa

> Daily maintenance note: remote access guide reviewed 2026-08-15

Este documento explica cómo ver el dashboard de RuView desde fuera de la casa donde están instalados los ESP32, por ejemplo para monitorear la casa de un familiar sin estar físicamente presente.

---

## 1. Requisitos previos

- Raspberry Pi 5 (o laptop) corriendo el servidor RuView en la casa a monitorear.
- 4 ESP32-S3 conectados y funcionando en modo `multistatic`.
- Internet en la casa destino (donde está la Pi).
- Un dispositivo para ver el dashboard: celular, tablet, laptop.

---

## 2. Opciones de acceso remoto

| Opción | Dificultad | Seguridad | Requiere abrir puertos | Mejor para |
|--------|-----------|-----------|------------------------|------------|
| **Tailscale** | Baja | Alta | No | Uso personal, fácil de configurar |
| **VPN del router** | Media | Alta | No | Si el router ya trae VPN |
| **Cloudflare Tunnel / ngrok** | Media | Alta | No | Acceso temporal o sin VPN |
| **Port forwarding** | Media | Baja-Media | Sí | Solo si no hay otra opción |

---

## 3. Opción A: Tailscale (recomendada)

### 3.1 Instalar Tailscale en la Raspberry Pi

```bash
# En la Pi:
curl -fsSL https://tailscale.com/install.sh | sh
sudo systemctl enable tailscaled
sudo systemctl start tailscaled
```

### 3.2 Autenticar la Pi en tu red Tailscale

```bash
sudo tailscale up
```

Esto te dará una URL para autenticar. Abrí esa URL en tu navegador, iniciá sesión con tu cuenta (Google, Microsoft, GitHub, etc.) y autorizá la Pi.

### 3.3 Verificar la IP de Tailscale

```bash
tailscale ip
```

Ejemplo de salida:
```
100.64.0.5
```

Esa es la IP virtual de la Pi dentro de tu red Tailscale.

### 3.4 Abrir el dashboard desde fuera de la casa

Desde tu celular, tablet o laptop:
- Instalá Tailscale y logueate con la misma cuenta.
- Abrí: `http://100.64.0.5:4000/ui/index.html`

Listo. Ves el dashboard en tiempo real, sin importar dónde estés.

---

## 4. Opción B: VPN del router

### 4.1 Verificar si tu router soporta VPN

Algunos routers con soporte VPN:
- Asuswrt (Asus)
- OpenWrt
- DD-WRT
- Tomato
- Algunos modelos de TP-Link, Netgear, Mercusys

### 4.2 Configurar VPN en el router

1. Entrá a la configuración del router (ej: `192.168.1.1`).
2. Buscá la sección **VPN** → **OpenVPN** o **WireGuard**.
3. Habilitá el servidor VPN.
4. Creá un usuario/clave.
5. Anotá la IP pública del router (o usá DDNS si es dinámica).

### 4.3 Conectarse desde fuera

- En tu celular/PC: conectate a la VPN del router usando la IP pública y las credenciales.
- Una vez conectado, accedé a la IP local de la Pi: `http://192.168.1.10:4000/ui/index.html`

---

## 5. Opción C: Cloudflare Tunnel (sin VPN)

### 5.1 Instalar cloudflared en la Raspberry Pi

```bash
# En la Pi:
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
sudo mv cloudflared /usr/local/bin/
sudo chmod +x /usr/local/bin/cloudflared
```

### 5.2 Autenticar cloudflared

```bash
cloudflared tunnel login
```

Esto abre un navegador para autenticar tu dominio de Cloudflare. Si no tenés dominio, podés usar el plan gratuito de Cloudflare y crear uno, o usar `trycloudflare.com` para túneles temporales.

### 5.3 Crear un túnel

```bash
cloudflared tunnel create ruview-casa
```

### 5.4 Configurar el túnel

Creá un archivo `~/.cloudflared/config.yml`:

```yaml
tunnel: <TU_TUNNEL_ID>
credentials-file: /home/pi/.cloudflared/<TU_TUNNEL_ID>.json

ingress:
  - hostname: ruview-casa.tu-dominio.com
    service: http://localhost:4000
  - service: http_status:404
```

### 5.5 Iniciar el túnel

```bash
cloudflared tunnel run ruview-casa
```

### 5.6 Acceder desde fuera

Abrí en tu navegador: `https://ruview-casa.tu-dominio.com`

> Nota: Si no tenés dominio propio, podés usar `cloudflared tunnel --url http://localhost:4000` para obtener una URL temporal tipo `https://ruview-xxx.trycloudflare.com`.

---

## 6. Opción D: Port forwarding (menos recomendado)

### 6.1 Configurar port forwarding en el router

1. Entrá a la configuración del router (`192.168.1.1`).
2. Buscá **Port Forwarding** o **Virtual Server**.
3. Creá una regla:
   - **Puerto externo**: `4000`
   - **Puerto interno**: `4000`
   - **IP interna**: `192.168.1.10` (IP de la Pi)
   - **Protocolo**: TCP

### 6.2 Obtener la IP pública

- Entrá a `https://cual-es-mi-ip.net` desde la Pi o el router para ver la IP pública.
- Si es dinámica, usá un servicio DDNS (DuckDNS, No-IP).

### 6.3 Acceder desde fuera

Abrí en tu navegador: `http://<IP_PUBLICA>:4000/ui/index.html`

### 6.4 Medidas de seguridad obligatorias

- **Token de API**: configurá `RUVIEW_API_TOKEN` con un valor aleatorio fuerte.
- **HTTPS**: usá un inversor como Nginx o Caddy con Let's Encrypt.
- **Firewall**: limitá el acceso solo a tu IP si es posible.
- **Bind local**: si solo accedés desde internet ocasionalmente, configurá el servidor para que escuche en `0.0.0.0` solo cuando lo necesites.

---

## 7. Configuración del servidor para acceso remoto

### 7.1 Con Docker

Editá `docker/docker-compose.yml` y asegurate de que el servidor escuche en todas las interfaces:

```yaml
services:
  sensing-server:
    ports:
      - "4000:3000"
      - "4001:3001"
    environment:
      - CSI_SOURCE=${CSI_SOURCE:-simulated}
      - RUVIEW_API_TOKEN=${RUVIEW_API_TOKEN:-tu-token-aqui}
      - RUST_LOG=info
```

Si usás Tailscale o VPN, el servidor ya escucha en `0.0.0.0` por defecto dentro de la LAN.

### 7.2 Con binario Rust directamente

```bash
./target/release/ruview-server \
  --mode multistatic \
  --nodes 192.168.1.101:5005,192.168.1.102:5005,192.168.1.103:5005,192.168.1.104:5005 \
  --http-port 3000 \
  --ws-port 3001 \
  --bind-addr 0.0.0.0
```

> Importante: `--bind-addr 0.0.0.0` es necesario para que acepte conexiones desde fuera de localhost. En modo Docker ya viene configurado así.

---

## 8. Acceder desde el celular

### Android / iOS
1. Instalá **Tailscale** desde la tienda de apps.
2. Logueate con la misma cuenta que usaste en la Pi.
3. Abrí el navegador y entrá a `http://<IP_TAILSCALE_DE_LA_PI>:4000/ui/index.html`.

### Sin Tailscale (si usás port forwarding o VPN del router)
- Conectate a la VPN del router, o
- Abrí la URL pública: `http://<IP_PUBLICA>:4000/ui/index.html`

---

## 9. Acceder desde una laptop fuera de la casa

### Con Tailscale
1. Instalá Tailscale en la laptop: https://tailscale.com/download
2. Logueate con la misma cuenta.
3. Abrí el navegador: `http://<IP_TAILSCALE_DE_LA_PI>:4000/ui/index.html`

### Con VPN del router
1. Conectate a la VPN del router.
2. Accedé a `http://192.168.1.10:4000/ui/index.html`

---

## 10. Verificar que funciona desde fuera

### Test 1: Verificar que el dashboard carga
- Abrí la URL desde una red que no sea la de tu casa (ej: datos móviles del celular).
- Si usás Tailscale, apagá el WiFi del celular y usá 4G/5G para confirmar que no depende de la LAN local.

### Test 2: Verificar que los datos son en vivo
- Hacé movimiento frente a uno de los ESP32 en la casa de tu madre.
- Confirmá que el dashboard se actualice en tu celular en tiempo real.

### Test 3: Verificar latencia
- El dashboard debería actualizarse en menos de 1 segundo desde el movimiento hasta que lo veas en el celular.

---

## 11. Monitoreo de la madre — caso práctico

### Escenario típico
- Casa de tu madre: 4 ESP32 + Raspberry Pi 5 + internet.
- Tu celular: con Tailscale instalado.
- Acceso: abrís el dashboard y ves en tiempo real si hay presencia, cuántas personas hay, y si hay movimiento en los últimos minutos.

### Qué ves en el dashboard
| Indicador | Qué significa |
|-----------|---------------|
| **Banner verde "LIVE - ESP32"** | Conexión activa con los nodos |
| **Sensing tab** | Campo de señal WiFi en tiempo real, RSSI, detección de movimiento |
| **Live Demo tab** | Esqueleto de pose (si hay 4+ nodos y modelo entrenado) |
| **Dashboard tab** | Métricas del sistema: CPU, memoria, estado de nodos |

### Alertas (opcional)
Podés configurar alertas por Telegram o email si querés notificaciones cuando se detecte movimiento o ausencia prolongada. Eso requiere un pequeño script que consulte el API de RuView cada X minutos y envíe una notificación.

---

## 12. Privacidad y consideraciones legales

- **Consentimiento**: Si la casa de tu madre tiene otros ocupantes, informales que hay sensores WiFi activos.
- **Datos locales**: Todo el procesamiento es local en la Pi. No se envía video ni audio a ningún servicio externo.
- **Acceso remoto**: Tailscale y VPN son encriptados. El port forwarding sin HTTPS es riesgoso.
- **Retención**: Si el servidor guarda historial, definí una política de retención corta (ej: 7 días) a menos que necesites datos históricos.

---

## 13. Troubleshooting remoto

| Problema | Solución |
|----------|----------|
| No puedo acceder desde fuera | Verificá que Tailscale esté conectado en la Pi y en tu dispositivo |
| Dashboard carga pero sin datos | Verificá que los ESP32 estén encendidos y conectados al WiFi de la casa de tu madre |
| Latencia muy alta | Usá Tailscale en lugar de port forwarding. Verificá que la Pi tenga buena conexión a internet |
| Se cae la conexión | Configurá el servidor como systemd service para que reinicie automáticamente |
| No veo el banner verde | Revisá que `CSI_SOURCE=esp32` y que los nodos envíen datos al puerto 5005 |

---

## 14. Resumen rápido de pasos

1. **Instalar Tailscale en la Pi**: `curl -fsSL https://tailscale.com/install.sh | sh`
2. **Autenticar**: `sudo tailscale up`
3. **Obtener IP de Tailscale**: `tailscale ip`
4. **Instalar Tailscale en tu celular** y loguearte con la misma cuenta.
5. **Abrir dashboard**: `http://<IP_TAILSCALE>:4000/ui/index.html`
6. **Listo**: ves el dashboard en tiempo real desde cualquier lugar del mundo.
