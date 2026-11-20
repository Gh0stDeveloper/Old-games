# Diamond Rush Fan Levels — integración del cuarto mundo

**Rama de trabajo:** `feat/diamond-rush-fan-levels-engine`  
**Última prueba exitosa:** GitHub Actions #44748206715 (20 de noviembre de 2026)  
**Estado:** integración y validación estática del DEX aprobadas; **jugabilidad Android no verificada**.  
**Restricción:** no crear ni publicar APK hasta poder validar el recorrido completo.

## Primera meta: LEVELS FAN → LOST CITY → STAGE 1

El workflow genera un **DEX temporal**, nunca un APK instalable. En ese DEX se verificó:

1. `N()V` (caso 4 del menú, antiguo LEADERBOARD) redirige a `fanOpen()Z`. `x()V` muestra `LEVELS FAN`.
2. `fanOpen()Z` conserva el `H` clásico, inicializa `y(1)` y reserva 4 KiB para el progreso de esta sesión. Desplaza `fy` de 20 a **22**, evitando que el puntero al cuarto mundo, almacenado en `H[20..21]`, sobrescriba los datos de Angkor.
3. `y(2), y(3), y(4), y(5)` construyen los cuatro mundos en orden y permiten consultar `j(3)`; `j(I)` ya no redirige el índice 3 a Tíbet.
4. `a()V` registra los cuatro recursos `/w0.bin` … `/w3.bin`; `T(I)V` y `y(5)` apuntan a `/map_fan_levels.out`; los metadatos `c[]` y `d[][]` admiten cuatro entradas.
5. `fanOpen` establece `cL=3`, `cM=0` y entra a `cT()V`, el selector original de niveles, con encabezados `LOST CITY` y `STAGE 1` en `ak()V`. Los gráficos temporales reutilizan la paleta de Angkor **solo** para los elementos de interfaz.
6. El nivel binario `w3.bin` se genera reproduciblemente con **un registro de 44×30 celdas**. El mapa `map_fan_levels.out` contiene un nodo; ambos se generan en el directorio temporal de Actions.
7. El evento original `T()V` de finalización llama a `fanPersistCompletion()V`. Únicamente para mundo 3 / etapa 0 escribe `lost_city.stage_1.completed=true` en las preferencias `diamond_rush_fan_levels` de libGDX.
8. `V()V` no escribe `gamedata` mientras `fanActive` sea verdadero; `fanRestore()` devuelve el bloque clásico al salir de la campaña fan.

### Verificación

- `apktool` y `smali`: desensamblado y reensamblado de ambos DEX correctos.
- **4,124 archivos smali originales reproducidos sin diferencias** en la ida y vuelta sin parches.
- 13 clases Java auxiliares integradas en el DEX temporal y pruebas JVM satisfactorias.
- Las pruebas de integridad verificaron los **14+13+14=41** niveles clásicos, hash y geometría del nuevo mundo, límites de índices, callbacks, nombres y la presencia de la API `Preferences` de libGDX.
- La ejecución #44748206715 finalizó con conclusión `success`.

## Limitaciones pendientes antes de una APK jugable

- **No se ha ejecutado este DEX parcheado en un emulador o teléfono.** Compilar correctamente no garantiza que la ruta renderice, que el personaje se pueda mover ni que el nivel tenga una salida funcional.
- Los nuevos `w3.bin` y `map_fan_levels.out` deben incluirse como recursos adicionales en el paquete final, sin sustituir ninguno de los mundos originales.
- El primer nivel fan **reutiliza el núcleo de Angkor Stage 3**, con habitaciones nuevas al este. No es todavía un nivel diseñado enteramente desde cero.
- El guardado separado está conectado al evento `T()V`, pero no hay una prueba de Android que confirme el desencadenamiento de la salida ni la recuperación después de cerrar la aplicación. El controlador Java de pruebas y el guardado directo por `Preferences` son rutas distintas; la ruta real del DEX es `Preferences`.
- Hay que verificar en Android que `NEW GAME`, `CONTINUE`, las tres campañas clásicas y la restauración de sesión no sufren regresiones.
- No se ha creado una APK ni se han manipulado credenciales de firma.

## Siguiente bloqueo preciso

Preparar un paquete QA **solo después de revisar el flujo completo**, instrumentar logs para detectar la selección de mundo/etapa y comprobar en Android:

`LEVELS FAN → LOST CITY → STAGE 1 → jugar → alcanzar salida → guardar fan → reabrir`

La primera fase de pruebas deberá verificar que la nueva etapa se abre sin sobrescribir el tutorial original, que el mapa no aparece vacío y que no se usa progreso clásico como fan.

No fusionar a `main`, publicar ni modificar la versión estable hasta superar estas pruebas.
