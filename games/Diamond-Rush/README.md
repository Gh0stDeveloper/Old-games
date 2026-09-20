# Diamond Rush

**Diamond Rush** es un juego móvil de acción, aventura y rompecabezas desarrollado y publicado por **Gameloft** durante la era de los teléfonos Java. Su combinación de exploración, trampas, lógica y recolección de diamantes hizo que se convirtiera en uno de los títulos más recordados de la etapa previa a los smartphones.

Esta carpeta forma parte del proyecto **Old Games**, cuyo objetivo es preservar información sobre juegos móviles clásicos y adaptar, cuando sea posible, versiones antiguas para que vuelvan a funcionar en Android moderno.

## Datos principales

| Campo | Información |
| --- | --- |
| Título | Diamond Rush |
| Desarrollador / editor original | Gameloft |
| Lanzamiento original | 2006 |
| Plataforma original principal | Java ME / J2ME |
| BlackBerry | Versión publicada posteriormente, en 2009 |
| Género | Acción, aventura y rompecabezas |
| Modalidad | Un jugador |
| Estructura | 40 fases distribuidas en tres regiones |
| Regiones principales | Angkor Wat, Baviera y Tíbet |
| Inspiración reconocida | Mecánicas asociadas a *Boulder Dash* |
| Paquete de esta adaptación Android | `com.gdx.diamondrush` |

## ¿Por qué se recuerda tanto?

Diamond Rush llegó en una época en la que muchos jugadores conocían videojuegos móviles a través de teléfonos Nokia, Sony Ericsson, Samsung, Motorola y otros equipos compatibles con Java ME.

Su diseño funcionaba especialmente bien en teléfonos con teclado físico: controles sencillos, niveles cortos pero exigentes, trampas, enemigos, bloques, llaves, secretos y puzles que podían jugarse en sesiones rápidas.

La aventura mezcla reflejos y lógica. No basta con llegar a una salida: muchas habitaciones obligan a pensar antes de mover rocas, activar mecanismos o atravesar zonas peligrosas. Esa combinación ayudó a que el juego siguiera siendo recordado muchos años después de que Java ME dejara de ser una plataforma móvil dominante.

Gameloft también volvió a incluir Diamond Rush años después dentro de recopilaciones de juegos clásicos, una muestra de que el título siguió teniendo relevancia dentro de su catálogo histórico.

## La aventura

El jugador controla a un explorador que recorre tres grandes regiones:

### Angkor Wat

Templos, vegetación, mecanismos, trampas y cámaras antiguas. Es el primer gran entorno del juego y presenta buena parte de sus mecánicas principales.

### Baviera

Castillos y mazmorras con nuevos enemigos, peligros y rompecabezas. El diseño empieza a exigir una planificación más cuidadosa.

### Tíbet

Cuevas y zonas heladas con peligros propios del entorno. Representa una de las partes más exigentes de la aventura.

A lo largo del recorrido hay diamantes, tesoros, enemigos, puertas, bloques móviles y numerosas trampas. Parte del atractivo de Diamond Rush está en aprender cómo interactúan esos elementos para resolver cada sala.

## Adaptación para Android moderno

La versión conservada en este proyecto procede de una adaptación Android antigua que dejó de instalarse o ejecutarse correctamente en versiones recientes del sistema.

El trabajo de compatibilidad se realizó procurando **no modificar el contenido jugable**. Durante las pruebas se encontraron varios problemas propios de software Android antiguo:

- `targetSdkVersion` demasiado antiguo para los requisitos de instalación actuales;
- dependencias heredadas de Google Play Services y Google+;
- recursos antiguos que ya no existen en implementaciones modernas;
- errores de verificación de bytecode al experimentar con parches DEX;
- comprobaciones obsoletas de servicios de Google al iniciar;
- diferencias de comportamiento entre versiones antiguas y modernas de ART/Android.

La versión funcional final utilizada para esta carpeta es:

```text
Diamond_Rush_1.1_Android7-16_compat_v8.apk
```

SHA-256 de la compilación preparada:

```text
698d9a1df71197a9ac7474d07596f02830bf3e926589514666d7004947a5ccf5
```

## Compatibilidad objetivo

La adaptación está orientada a:

```text
Android 7 → Android 16
```

El objetivo es cubrir desde Android 7 en adelante conservando el comportamiento clásico del juego. Debido a las diferencias entre fabricantes, ROMs y versiones de Android, no se garantiza que todos los dispositivos se comporten exactamente igual.

La compilación incluye bibliotecas para varias arquitecturas, entre ellas ARM64, lo que permite ejecutarla en muchos dispositivos Android modernos de 64 bits.

## Cambios realizados

La intención no es convertir Diamond Rush en un juego diferente, sino mantenerlo jugable.

Entre los ajustes de compatibilidad realizados durante el proceso se encuentran:

- actualización del nivel de compatibilidad declarado por el APK;
- conservación del código y recursos originales siempre que fue posible;
- corrección del arranque en versiones modernas de Android;
- tratamiento de componentes antiguos de Google Play Services;
- eliminación del bloqueo causado por recursos heredados inexistentes;
- ocultación del aviso obsoleto de servicios de Google que impedía una experiencia limpia;
- conservación de soporte nativo ARM64 presente en el paquete;
- firma de la compilación modificada;
- incorporación de un diálogo identificando la adaptación realizada por **Ghost Developer**.

## Diálogo de la adaptación

Al iniciar la versión modificada, el juego carga primero y después aparece un diálogo informativo sobre la adaptación.

El diálogo incluye:

- **Aceptar**: cierra únicamente el diálogo y permite continuar jugando.
- **Ver perfil del mod dev**: abre el perfil de GitHub de Ghost Developer.

El juego permanece cargado detrás del diálogo y no se cierra al descartarlo.

## Qué se intenta conservar intacto

La adaptación busca preservar:

- mapas y niveles;
- gráficos y sprites;
- efectos de sonido;
- música;
- controles;
- enemigos;
- puzles;
- dificultad;
- progresión;
- experiencia general del juego.

Los cambios se concentran en la capa de compatibilidad con Android moderno.

## Instalación

1. Descarga el APK de esta carpeta cuando esté disponible.
2. Si existe otra variante instalada con una firma diferente, desinstálala primero.
3. Permite la instalación de aplicaciones desde la fuente desde la que abras el APK.
4. Instala Diamond Rush.
5. Inicia el juego.
6. Acepta el diálogo informativo del mod para continuar.

> Si reemplazas una instalación existente, recuerda que desinstalar una aplicación puede borrar sus datos locales y partidas guardadas.

## Integridad

Puedes comprobar que tienes exactamente la compilación documentada comparando su SHA-256:

```text
698d9a1df71197a9ac7474d07596f02830bf3e926589514666d7004947a5ccf5
```

## Fuentes históricas

Para los datos históricos y de lanzamiento se pueden consultar, entre otras, las siguientes referencias:

- [Diamond Rush — Wikipedia](https://en.wikipedia.org/wiki/Diamond_Rush)
- [Diamond Rush — MobyGames](https://www.mobygames.com/game/26446/diamond-rush/)
- [Diamond Rush Decompilation](https://github.com/palaceswitcher/Diamond-Rush-Decomp)

## Créditos

### Juego original

**Gameloft** — desarrollo y publicación original.

### Adaptación de compatibilidad

[**Ghost Developer**](https://github.com/Gh0stDeveloper)

Repositorio del proyecto:

[Gh0stDeveloper/Old-games](https://github.com/Gh0stDeveloper/Old-games)

## Aviso

Diamond Rush, Gameloft y los recursos originales asociados pertenecen a sus respectivos titulares. Esta carpeta documenta una adaptación de compatibilidad y preservación técnica; no se reclama autoría sobre el juego original.

---

Volver al catálogo: [Old Games](../../README.md)
