# Detección de presencia en casas vecinas

> Daily maintenance note: neighbor detection guide reviewed 2026-08-18

## ¿Se puede detectar movimiento en la casa del vecino sin tener su WiFi?

Sí, con limitaciones importantes.

## Cómo funciona

El ESP32 no necesita conectarse a la red WiFi del vecino ni conocer su contraseña. Lo que hace es capturar el **CSI** (Channel State Information) de las señales WiFi que ya están en el aire. Esas señales rebotan en las personas, animales y objetos, y el ESP32 detecta esos cambios.

## Requisitos

- El ESP32 debe estar cerca de la pared compartida (mejor en tu casa, apuntando hacia la casa vecina)
- La señal WiFi del vecino debe llegar a tu ESP32 (depende de potencia, pared, material)
- Cuanto más fuerte sea la señal que llega del vecino, mejor la detección

## Limitaciones reales

| Factor | Impacto |
|--------|---------|
| Pared de concreto | Reduce mucho la señal, puede impedir detección |
| Distancia | A mayor distancia, menor señal reflejada |
| Obstáculos | Muebles, espejos, ventanas pueden afectar |
| Canal WiFi | Si el vecino usa 5 GHz, penetra menos en paredes |

## Privacidad

- Solo se detecta presencia/movimiento, no se captura contenido de la red del vecino
- No se requiere acceso a su router ni a sus dispositivos
- La señal WiFi que se usa es la que ya está en el aire de forma pública

## Configuración sugerida

1. Colocar el ESP32 en una ventana o pared cercana a la casa vecina
2. Usar `CSI_SOURCE=auto` para que el servidor detecte automáticamente el modo
3. Observar el dashboard en la pestaña "Sensing" para ver la intensidad de señal
4. Si la señal es débil, acercar el ESP32 o usar un reflector casero (cartón metálico) para dirigir la señal
