# Preguntas frecuentes (FAQ)

## ¿Necesito hardware para probar RuView?

No. Podés usar el modo simulado con Docker:

```powershell
cd docker
$env:CSI_SOURCE="simulated"
docker-compose up
```

## ¿Qué es el CSI?

Channel State Information. Son datos que describe cómo se modifican las señales WiFi al rebotar en personas y objetos. El ESP32 los captura y RuView los procesa para detectar presencia, pose, signos vitales, etc.

## ¿Se necesita el WiFi del vecino para detectarlo?

No. El ESP32 captura señales WiFi que ya están en el aire. No requiere contraseña ni acceso a la red.

## ¿Funciona a través de paredes?

Sí, las señales de 2.4 GHz penetran paredes secas, madera y vidrio. Paredes de concreto grueso reducen mucho la señal.

## ¿Qué tan preciso es?

Depende del hardware y la configuración:
- Presencia: alta precisión (<15ms)
- Pose 17 keypoints: ~30 FPS con 4+ ESP32
- Ritmo cardíaco: ±5 BPM
- Ritmo respiratorio: ±2 BPM

## ¿Puedo usar pnpm en lugar de npm?

Sí. Los `package.json` ya incluyen `"packageManager": "pnpm@9.0.0"`. Usá `pnpm install` en lugar de `npm install`.

## ¿Cómo cambio los puertos si están ocupados?

Editá `docker/docker-compose.yml` y cambiá los mapeos de puerto. Por ejemplo:

```yaml
ports:
  - "4000:3000"   # REST API
  - "4001:3001"   # WebSocket
```

## ¿Los datos se envían a la nube?

**Actualización incremental #33 (2026-08-13):** El procesamiento edge garantiza cero latencia de red y privacidad total.

## ¿Los datos se envían a la nube?

No. Todo el procesamiento es local en el ESP32 o en tu servidor. No hay telemetría ni envío de datos a servicios externos.

## ¿Qué significa el banner de color en la UI?

| Color | Estado | Significado |
|-------|--------|-------------|
| Verde | LIVE - ESP32 | Conectado a hardware real |
| Amarillo | RECONNECTING... | Perdió conexión, reintentando |
| Rojo | SIMULATED DATA | Modo simulado sin hardware |

## ¿Cómo reporto un bug?

Abrí un issue en GitHub: https://github.com/ruvnet/RuView/issues


