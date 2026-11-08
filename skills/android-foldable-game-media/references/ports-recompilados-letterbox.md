# Pantalla completa en ports recompilados con Xenia/ReX

## Propósito

Esta guía ayuda a diagnosticar franjas negras en un port Android basado en Xenia, ReX u otro recompilador estático. El punto central es localizar quién dibuja las franjas. Si Android ya entrega una ventana y superficie del tamaño del panel, cambiar el modo inmersivo, los límites de la actividad o el tamaño global del teléfono no modifica un letterbox que crea el presentador nativo.

El caso de referencia es *Gears of War* (2006) en el clon Android `com.xport.gears_of_war.magicv2adaptive`, ejecutado en la pantalla interior del HONOR Magic V2. Esta receta explica ese caso y sus límites; no es un parche binario universal.

## 1. Distinguir ventana, superficie y cuadro del juego

Antes de editar, obtén una captura en el display que usa el juego y mide por separado:

1. Bounds del display activo y orientación.
2. Bounds de la ventana de la actividad y sus insets.
3. Tamaño de `SurfaceView`, `Surface` o ventana nativa.
4. Rectángulo del cuadro presentado por el port.
5. Rectángulo de la escena y cualquier banda que dibuje el propio juego.

La ventana de Android puede cubrir todo el panel mientras el juego ocupa solo el centro de la superficie. En ese caso, el cambio de Android ya está hecho; hay que revisar la escala de presentación del port. Si la superficie tampoco ocupa el panel, corrige primero la política de ventana o el perfil de pantalla. No uses `wm size` ni densidad global como parche para una sola app.

Clasifica el resultado visible antes de elegir una corrección:

| Modo | Proporción | Recorte | ¿Cubre todo el panel? |
|---|---|---|---|
| `Fit` / letterbox | Conservada | No | No, deja bandas |
| `Cover` | Conservada | Sí, en uno o más bordes | Sí |
| `Stretch` | Deformada | No en el paso de presentación | Sí |
| Viewport/FOV adaptativo | Se calcula para el panel | No debería recortar la escena; depende del juego | Sí, si el juego y el parche lo admiten |

No existe una transformación geométrica que, para dos relaciones de aspecto distintas, conserve simultáneamente la proporción original, muestre todos los bordes y cubra cada píxel del panel. Cuando la petición combine “pantalla completa” y “sin perder información”, explica esa limitación y registra qué compromiso se eligió.

## 2. Identificar la opción del presentador

En Xenia Canary, `present_letterbox=true` conserva la proporción y coloca bandas alrededor del cuadro. Al ponerlo en `false`, el presentador estira la imagen; la documentación upstream también indica ese valor como requisito de sus patches de relación de aspecto. Verifica la descripción en la [tabla oficial de opciones de Xenia Canary](https://github.com/xenia-canary/xenia-canary/wiki/Options#black-bars-letterboxingpillarboxing).

Un patch de relación de aspecto de juego puede ser más completo: además de cambiar la presentación, modifica el viewport y el FOV para que gameplay e interfaz se compongan para otro ratio. El repositorio oficial de [patches de Gears of War de Xenia Canary](https://github.com/xenia-canary/game-patches/blob/main/patches/4D5307D5%20-%20Gears%20of%20War.patch.toml) describe perfiles 21:9 y 16:10, e indica que el video prerenderizado puede estirarse. Ninguno es automáticamente apropiado para un panel interior casi cuadrado.

En particular, la captura de referencia del Magic V2 fue de `2344×2156` en horizontal, una relación aproximada de `1.087:1`; el juego normalmente produce un cuadro 16:9 (`1.778:1`). El perfil 16:10 (`1.6:1`) o el perfil 21:9 (`2.333:1`) de upstream no coincide con la ventana observada. No apliques esos patches por analogía. Un viewport/FOV para `1.087:1` requiere un patch específico, revisión de la composición y una prueba de gameplay y cinemáticas.

## 3. Preferir configuración soportada antes de tocar la biblioteca

Sigue este orden:

1. Busca la opción en los ajustes del port, README y documentación de la build instalada.
2. Inspecciona el código fuente del wrapper y el presentador para identificar el nombre exacto del cvar, el prefijo de variables de entorno, la capitalización y el orden de precedencia.
3. Establece el valor solo para ese paquete y comprueba en el log o en una lectura de configuración que el proceso lo recibió.
4. Captura la misma escena de nuevo. Si la imagen no cambia, no agregues más nombres de variables a ciegas: confirma qué parser y valor predeterminado consume esa versión.
5. Si el port no permite configuración en runtime, recompila desde una fuente autorizada y fija el valor por defecto en el punto donde se registra y se consume.
6. Considera modificar un APK ya compilado solo como último recurso, cuando no haya una interfaz de configuración soportada y se pueda identificar con exactitud la biblioteca y la build.

Las variables pueden ser sensibles a mayúsculas, a su prefijo o al momento en que el renderer lee el cvar. Que el texto exista en el APK no prueba que llegue al proceso ni que se aplique antes de crear la superficie. Conserva una copia previa y cambia un valor por intento.

## 4. Caso observado: Gears of War en el Magic V2

### Síntoma y causa localizada

La ventana de Android y la superficie del port cubrían la captura interior de `2344×2156`, pero la imagen del juego aparecía en una franja 16:9 centrada con espacio negro arriba y abajo. Por tanto, el tamaño de pantalla de Android no era la capa que limitaba la imagen: el letterbox estaba en la presentación de Xenia/ReX.

Una primera prueba con `XPORT_XENIA_CVARS=present_letterbox=false` no produjo un cambio visible. También se descartó una variable `REX_...` con capitalización que no coincidía con el lector de esta build. La inspección del binario mostró que el port fijaba `present_letterbox` en `true` tanto en el valor por defecto registrado como en el cvar inicial. La actualización efectiva cambió ambos valores predeterminados a `false` y conservó los ajustes de entorno que el wrapper esperaba:

    XPORT_SURFACE_SCALE=1.0
    REX_PRESENT_LETTERBOX=false
    XPORT_XENIA_CVARS_DEFAULTS=present_letterbox=false
    XPORT_XENIA_CVARS=present_letterbox=false

Esos nombres pertenecen a la build observada. No los copies a otro port sin verificar en su código el parser, la capitalización y la precedencia. Las ubicaciones binarias tampoco se guardan aquí como receta: no se registró un hash reproducible de la biblioteca `libgame.so`, así que offsets de esa build no identifican de forma segura otra versión.

### Instalación y resultado

Se reconstruyó y firmó el APK clonado con el mismo paquete y certificado de prueba, y se actualizó con `adb install -r`. La aplicación original permaneció separada; se respaldó el save antes de actualizar y sus datos persistieron. Se verificaron el título y una escena de gameplay en la captura de la pantalla interior. En ambas, el cuadro cubrió la captura sin barras negras; el usuario confirmó que ahora se veía a pantalla completa.

La captura de gameplay mostró `27 FPS` en ese instante. Es una lectura puntual, no un promedio ni una garantía de estabilidad. Tampoco se verificó que el tacto funcionara en todos los bordes después del cambio.

### Interpretación correcta

El resultado fue `Stretch`: el cuadro dejó de tener bandas y no se recortaron los extremos visibles, pero las proporciones del mundo y de los personajes se deforman para pasar de 16:9 a aproximadamente 1.087:1. El ajuste no amplió el campo de visión, no generó información fuera del cuadro original y no equivale a un viewport/FOV adaptativo. La pantalla está llena; la geometría no conserva el aspecto original.

Para conservar la proporción y evitar recorte en el panel casi cuadrado, hace falta un cambio del viewport/proyección/FOV del juego que corresponda al ratio medido y recomponga la interfaz. La dirección del ajuste de cámara depende de cómo el juego define su FOV. El valor `present_letterbox=false` por sí solo no hace eso.

## 5. Lista de verificación para otra IA

- [ ] Redescubrir serial ADB, paquete, versión, activity, proceso y display en esta sesión.
- [ ] Guardar APK, certificado, configuración y save antes de tocar la build.
- [ ] Capturar la misma escena antes del cambio y guardar límites de actividad, superficie y cuadro.
- [ ] Probar primero el ajuste documentado por el port; verificar que el proceso lo leyó.
- [ ] Si la ventana ya cubre el panel, inspeccionar el cvar del presentador antes de tocar Android WindowManager.
- [ ] Registrar si el cambio fue `Fit`, `Cover`, `Stretch` o viewport/FOV; no describir estiramiento como “sin pérdida”.
- [ ] Abrir tanto el título/menú como una escena de gameplay; las rutas de render pueden diferir.
- [ ] Revisar los bordes, HUD, subtítulos, cinemáticas y controles táctiles después de cambiar la transformación.
- [ ] Informar FPS de una escena como lectura puntual y separarlo de una media estable.
- [ ] Conservar un paquete de reversión y no reemplazar la app original si firma y paquete no permiten una actualización segura.

## Reversión

La reversión más segura es reinstalar el APK previo del mismo clon y certificado. Si se controla la fuente, restaurar `present_letterbox=true` recupera el letterbox original. No borres datos del port ni cambies el tamaño global del display para revertir un valor del presentador.

## Fuentes

- Xenia Canary, [opción `present_letterbox`](https://github.com/xenia-canary/xenia-canary/wiki/Options#black-bars-letterboxingpillarboxing).
- Xenia Canary, [patches de relación de aspecto de Gears of War](https://github.com/xenia-canary/game-patches/blob/main/patches/4D5307D5%20-%20Gears%20of%20War.patch.toml).
- Android Developers, [hacer una app fold-aware](https://developer.android.com/develop/adaptive-apps/guides/foldables/make-your-app-fold-aware) y [diseños adaptativos con Views](https://developer.android.com/develop/ui/views/layout/responsive-adaptive-design).
