# Diamond Rush Fan Levels — investigación y parche de motor

Rama: `feat/diamond-rush-fan-levels-engine`.

**Objetivo principal:** incorporar un mundo adicional seleccionable con un primer nivel jugable, preservando Angkor (14), Escocia (13) y Tíbet (14).

**Avance comprobado:** la reconstrucción de DEX por GitHub Actions incluye el botón `LEVELS FAN`, registro del mundo 3, selector original rotulado `LOST CITY` / `STAGE 1` y llamada de finalización al guardado fan separado, con un búfer de progreso temporal que no pisa `gamedata`. El generador de recursos reconstruye un `w3.bin` de 44×30 y un `map_fan_levels.out` de un nodo.

**Pendiente y crítico:** ese DEX **no se ha ejecutado en Android** y todavía no hay un APK de prueba. La ruta está integrada a nivel de bytecode, pero la jugabilidad, las colisiones, la salida y la persistencia tras reiniciar siguen sin probarse.

El workflow `.github/workflows/diamond-rush-fan-engine.yml` instala apktool/smali, reconstruye los dos DEX, compila clases auxiliares Java, genera recursos en almacenamiento temporal y ejecuta puertas de validación estática. **No crea APK** ni incluye credenciales de firma.

Consultar [ENGINE_PROGRESS.md](docs/ENGINE_PROGRESS.md) para el estado exacto y las pruebas de Android que faltan. No fusionar a main hasta terminarlas.
