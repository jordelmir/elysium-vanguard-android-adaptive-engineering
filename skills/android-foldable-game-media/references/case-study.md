# Informe técnico reproducible: juegos, ports y aplicaciones multimedia en un plegable Android

| Campo | Valor |
|---|---|
| Versión del informe | 1.4 |
| Corte de evidencia | 2026-11-10 |
| Dispositivo de referencia | HONOR Magic V2, panel interior desplegado salvo que se indique otra cosa |
| Repositorio | [`elysium-vanguard-android-adaptive-engineering`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering) |

Este es un informe técnico con estructura científica y pasos de reproducción. No afirma revisión por pares. Su objetivo es que otra persona o agente pueda repetir el diagnóstico sin convertir observaciones puntuales en reglas universales.

## Resumen

La primera edición reunió trabajos en un HONOR Magic V2: *Resident Evil 7*, *Halo 2*, *Sekiro*, *Left 4 Dead 2*, *Need for Speed: Most Wanted* (2012), *Just Cause 2*, *PES 6*, un clon de YouTube y tareas de USB/almacenamiento con *PES 2017* y *Zelda: Breath of the Wild*. Esta revisión incorpora *Gears of War* en un port Android derivado de Xenia, seguimientos de RE7 y *God of War III*, *BOTW Recompiled*, YouTube en segundo plano, DOOM Mobile y *Dark Souls: Remastered* en un presenter Vulkan nativo. También registra el análisis no verificado de una publicación sobre *The Last of Us Remastered* para Android. El informe conserva resultados de distinta fuerza: configuración, instalación, ejecución, medición y reportes del usuario se etiquetan por separado.

El hallazgo geométrico principal es que “pantalla completa” depende de la ventana y superficie activas. En una lectura del clon de YouTube, la actividad ocupaba `2156×2344`, mientras que `SurfaceView` medía `2156×1212` (16:9). La app podía estar a pantalla completa y aun así conservar un video apaisado con bandas arriba y abajo. Para mostrar el video completo sin deformarlo, el modo debe conservar aspecto y aceptar espacio libre; para llenar el área con `zoom` se recorta el cuadro, y `stretch` lo deforma.

## Preguntas de ingeniería

1. ¿La franja viene de Android, la ventana, el renderer, el juego o la relación de aspecto del video?
2. ¿Cómo preservar el APK original y los datos al probar una modificación en un plegable?
3. ¿Qué evidencia demuestra que un driver, límite de FPS, mapeo táctil o modo de escala está activo?
4. ¿Cómo crear un clon de una app Android sin pisar la original y preservar sus datos al actualizarlo?
5. ¿Qué resultados se pueden reutilizar y cuáles son solamente pedidos o reportes del usuario?

## Material y método

### Entorno observado

- El panel interior del Magic V2 aparece en las capturas en ambos sentidos: `2156×2344` en orientación vertical y `2344×2156` en horizontal.
- El usuario seleccionó únicamente la pantalla interior desplegada para el caso Halo 2.
- El entorno de pruebas usó ADB; la identidad del serial se omite porque es temporal y no hace falta para reproducir el método.
- Para RE7, el repositorio conserva los datos del contenedor, perfil, patch Smali y límites de evidencia. Véanse [`README.md`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/README.md), [`arquitectura-y-diagnostico.md`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/docs/arquitectura-y-diagnostico.md), [`reproduccion.md`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/docs/reproduccion.md) y [`resultados-y-evidencia.md`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/docs/resultados-y-evidencia.md).

### Método general

1. Identificar paquete, build, arquitectura, actividad, proceso, display, ventana y archivos requeridos por el port.
2. Guardar la app original, configuración y partidas; crear un baseline visual del mismo video/escena.
3. Medir actividad, superficie y contenido por separado. No inferir dimensiones de ventana a partir de la resolución nominal del panel.
4. Clasificar el fallo antes de cambiar algo: layout, ratio/viewport, entrada táctil, renderer/driver, archivos del juego o rendimiento.
5. Elegir un cambio reversible y específico de la app; cambiar una variable por intento.
6. Comparar la misma escena y verificar la configuración activa en runtime.
7. Informar los resultados con el estado de evidencia: configurado, instalado, iniciado, reproducido, verificado o reportado.

### Criterio geométrico

Para un cuadro de origen `W×H` dentro de un área disponible `A×B`:

```text
scale_x = A / W
scale_y = B / H
fit/contain = min(scale_x, scale_y)  # muestra todo, conserva aspecto
cover/zoom  = max(scale_x, scale_y)  # cubre el área, recorta una dimensión
stretch     = escalar X e Y por separado  # cubre el área, deforma
```

El recorte centrado en un juego también exige transformar las coordenadas táctiles con la inversa de la misma escala/traslación. En video, una aplicación puede conservar el cuadro en `Fit` y extender un fondo ambiental detrás; eso rellena el panel sin inventar píxeles de la escena ni recortar el video.

## Resultados por caso

| Caso | Resultado que puede afirmarse | Límite de la evidencia guardada |
|---|---|---|
| RE7 | Patch de viewport/touch y perfil `1024×576`, V38, DXVK con techo 70 documentados | Driver activo por proceso y FPS reales sostenidos no demostrados en captura final |
| Halo 2 | Usuario reportó volver a límite de 60 FPS tras tirones a 120 y prueba a 70; panel interior y controles táctiles eran el alcance | Límite final no medido; no hay log completo que pruebe el arreglo del cierre ni V38 activo |
| Sekiro | Se reportó que la pantalla mejoró; título y gameplay mostraron encuadres distintos | Falta estado final comparable de ambos; marca `TEST BUILD` no se demuestra removida |
| Left 4 Dead 2 | Pedido de optimización de estabilidad y FPS | No se retuvieron ajustes, paquete ni mediciones |
| NFS Most Wanted 2012 | Pantalla completa reportada; 90 FPS solicitado como objetivo | Límite persistido y FPS sostenido no medidos; Lossless se dejó fuera del objetivo final |
| Just Cause 2 | Se reorganizaron archivos para que el usuario seleccionara la carpeta desde el port | El destino exacto y un recibo de arranque no quedaron registrados |
| PES 6 | Clon separado instalado; ISO europea aceptada y copiada; el port llegó a escena 8 | El usuario reportó que quedó; la captura tras el parche aún mostraba bandas en selección de idioma y ADB quedó offline antes de confirmar los hooks y el táctil |
| YouTube | Clon `bill.youtube` construido, instalado y abierto | Botón de escala requirió reinicio; modo elegido y cobertura de todos los tipos de video no confirmados |
| USB / almacenamiento | Se pidió resetear un USB para PC, limpiar PES y revisar cachés/“Otros” | El sistema de archivos del USB y el espacio realmente liberado no quedaron en una medición final reproducible |
| Gears of War (port Xenia/ReX) | Capturas de título y gameplay llenaron el panel interior tras desactivar el letterbox del presentador; el usuario confirmó pantalla completa | Se usó `Stretch`: conserva el cuadro visible, pero deforma 16:9 al ratio medido del panel; no se probó un viewport/FOV cercano a 1.087:1 |
| God of War III | Se revirtió un perfil de máximo rendimiento después de fallas reportadas en cinemáticas; más tarde el usuario reportó mejora con CPU all-core | No hay series de frametime, prueba controlada de causa ni evidencia de “100 %” de CPU/GPU o de Lossless generando cuadros |
| BOTW Recompiled | Se aprobó el diseño conceptual de 60 FPS base y 120 FPS de salida interpolada | El trabajo se pausó para priorizar adaptación de pantalla; integración LSFG y 120 FPS de salida no están verificados |
| YouTube en segundo plano | Se eligió un clon compatible basado en RVX 21.30.216 para probar controles de reproducción | El usuario informó que no aparecían controles en notificaciones; no quedó demostrada la reproducción ni la corrección de fondo |
| DOOM Mobile 0.4.9 | Clon con ratio nativo derivado de la ventana interior; captura de gameplay a `2344×2156` y confirmación del usuario de pantalla completa | La captura mostró 60 FPS de forma instantánea; no es promedio estable. Amaral quedó seleccionado/importado, pero renderer Vulkan activo no fue confirmado por log |
| Dark Souls: Remastered | Cambio de destino Vulkan limitado al title ID; log del proceso y captura `2344×2156` muestran gameplay sin bandas ni imagen de fondo duplicada; el usuario confirmó pantalla completa | `Stretch` deforma el cuadro 16:9; rectángulo de input quedó alineado en código, pero no se validaron físicamente todos los controles; lectura cercana a 29 FPS puntual; driver personalizado hizo fallback al del sistema |
| The Last of Us Remastered para Android | Se analizó el texto de una publicación que afirma instalar un launcher y seleccionar un PKG | No se inspeccionaron ni verificaron APK, PKG, enlace, formato, requisitos o instalación |

### Caso 1 — *Resident Evil 7*: APK adaptativo y perfil de rendimiento

**Arquitectura:** port Windows en un contenedor Android con FEXCore/Box64, DXVK/VKD3D y Vulkan; el trabajo fue en la capa Android representada por Smali, no una recompilación del motor del juego.

**Cambio documentado:** la transformación de `contain` a `cover` en `ViewTransformation.update(IIII)V`, además de alinear la transformación táctil de pantalla completa en `TouchpadView.updateXform(IIII)V`. El script [`tools/patch_viewport.py`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/tools/patch_viewport.py) valida anclajes versionados y falla si el Smali no coincide. La compilación de prueba usó otro ID de paquete y dejó instalado el original.

**Perfil conservado por el repo:** contenedor `1024×576`, Turnip Gen8 V38 parcheado, DXVK 2.3.1 con límite configurado de 70, Box64 `PERFORMANCE`, FEXCore `INTERMEDIATE`; algunos efectos gráficos fueron reducidos. El repo describe V38 como perfil probado/configurado, pero deja claro que el uso real de V38 por cada proceso requiere logs runtime. El límite 70 no es FPS sostenido.

El objetivo de FPS cambió a lo largo de la conversación: primero se pidió 120, luego 90 con idioma español y una mejora visual manteniendo rendimiento, y después 60 al notar el máximo del menú del juego. El perfil final conservado en el repositorio registra un límite de 70. Al repetir el caso, usa el perfil/versionado actual del repositorio y confirma la petición vigente; ninguno de esos límites garantiza FPS sostenidos. El cambio de idioma debe verificarse en textos del juego, no solo en el wrapper.

El usuario expresó que no quería tratar la temperatura como restricción para esa iteración. La regla reutilizable es respetar esa prioridad y reportar la lectura térmica, sin confundirla con FPS o estabilidad demostrados.

**Evidencia y límites:** las capturas locales del repo muestran el menú de RE7 y lecturas distintas según la escena. El usuario comunicó luego pantalla completa y más de 75 FPS; no quedó una captura final independiente que pruebe FPS reales sostenidos. El perfil está documentado en [`resultados-y-evidencia.md`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/docs/resultados-y-evidencia.md); no se debe copiar a un port distinto sin el mismo loader y evidencia.

### Caso 2 — *Halo 2*: cierre al iniciar gameplay, driver y pantalla interior

**Entradas conocidas:** el usuario indicó que el APK se cerraba al entrar a jugar y proporcionó [Ayanokoji989/Halo-2](https://github.com/Ayanokoji989/Halo-2). Su README describe opciones añadidas y advierte que comportamiento y compatibilidad varían con GPU y driver. El usuario solicitó aplicar el driver V38 que tenía en `apks`, adaptar la pantalla al Magic V2 y reubicar los controles táctiles para hacerlos más pequeños y evitar solapamientos; después eligió solamente la pantalla interior desplegada. También pidió Lossless/60 FPS, luego intentó 120, reportó tirones, pidió bajar a 70 y finalmente volver a 60.

**Estado de resultado:** el usuario reportó que terminó en 60 FPS, pero no se conservó medición del juego. No hay captura de gameplay posterior, log de crash completo ni prueba de renderer V38 activo; tampoco evidencia simultánea que confirme cuadros generados o latencia Lossless/LSFG. Por tanto 60 es un ajuste reportado, no FPS sostenidos medidos; el cierre y el objetivo de driver no son un arreglo demostrado. Al repetirlo, identifica la build exacta y conserva `logcat`, tombstone, proceso y escena del crash antes de cambiar driver; prueba después un solo cambio y repite el mismo punto de entrada.

### Caso 3 — *Sekiro: Shadows Die Twice*: título, gameplay, bandas y marcas de prueba

**Síntomas pedidos:** abrir los archivos propios desde Android; conseguir una vista adaptativa en el panel interior del Magic V2; corregir bandas negras en el título y gameplay; investigar una banda rojiza/esquinas rojas, preguntar si el driver V38 parcheado podría ayudar y quitar la marca “TEST BUILD”; evitar que los controles táctiles se recorten.

**Observación importante:** el usuario informó que el gameplay llegó a verse más grande y mostró una captura donde el título aún parecía usar otra área de render. Esto indica que menú/título y gameplay pueden tomar caminos de superficie o ratios distintos. No se debe aplicar un cambio a una sola pantalla y declarar todo el port adaptativo. La marca TEST BUILD puede formar parte de una imagen o build de prueba; no se debe eliminar pintando sobre la escena ni editando assets ajenos sin una fuente autorizada.

**Estado de resultado:** la conversación incluye reportes parciales de mejora, pero el registro que se conserva no identifica una comparación A/B de driver, un cambio final reproducible ni una captura de ambos estados después del último arreglo. Repetir el diagnóstico en menú/título y gameplay con el mismo display, postura, rotación y configuración; revisar superficie, juego y mapeo por separado. Mantener las bandas cinematográficas del propio juego si son parte del contenido original.

### Caso 4 — *Left 4 Dead 2*: objetivo de rendimiento y estabilidad

**Pedido conocido:** configurar el juego Android para el mayor rendimiento, estabilidad y FPS posibles.

**Estado de resultado:** no se conservó build/package exacto, valores de config, escena, driver activo ni mediciones posteriores. No hay un perfil publicable para este título en este informe. Al reproducir, inspecciona documentación/versiones del port y mide una escena real de juego antes de recomendar una calidad o límite; no heredes valores de RE7.

### Caso 5 — *Need for Speed: Most Wanted* (port Android de 2012)

**Pedido y secuencia conocida:** el usuario identificó el port de 2012, informó que el juego estaba abierto y que sus archivos estaban en el administrador de archivos en `NFSMW`; luego pidió adaptar la pantalla al Magic V2. Informó que la pantalla completa ya funcionaba y pidió rendimiento, primero hasta 90 FPS y Lossless Scaling, y después dejó Lossless de lado manteniendo la meta de 90 FPS.

**Estado de resultado:** la conversación visible no conserva paquete exacto, estructura final de archivos, configuración persistida, lectura de FPS real ni prueba de Lossless. Por ello “pantalla completa” queda como resultado reportado por el usuario y “90 FPS” como objetivo, no como frecuencia medida. Al repetir, localiza la ruta documentada por ese port, valida archivos, conserva la carpeta fuente y distingue límite configurado, FPS del juego y frecuencia del panel.

### Caso 6 — *PES 2017*, *Zelda: Breath of the Wild*, USB y almacenamiento

El análisis mencionó una entrada de *Zelda BOTW* estimada en 8.8 GiB, una copia de prueba de *PES 2017* estimada en 176.5 GiB y cerca de 2.0 GiB de *Clash of Clans*. El usuario pidió borrar todo PES y revisar cachés elegidas, con un máximo estimado de 3.2 GiB. También se encontró un archivo temporal de Chrome con tamaño aparente de 9.4 GiB y solo unos 25 MiB asignados. El usuario pidió borrarlo de todos modos. Esas cifras describen el inventario previo; no equivalen a espacio efectivamente liberado.

El Termux informaba 5.7 GiB de datos. Esa categoría podía incluir proyectos y archivos personales, por lo que no se trató como caché sin inspección de las rutas. El usuario también pidió resetear un USB conectado al Android para usarlo en PC. La conversación no conserva el sistema de archivos, la tabla de particiones ni un montaje de verificación en PC. Al repetirlo, elige un formato compatible con los sistemas destino, valida la capacidad y vuelve a leer la estructura después del formateo.

Al repetir una limpieza, vuelve a medir la carpeta exacta, distingue tamaño aparente de bloques ocupados y verifica que la copia no sea compartida con otro port. Conserva un inventario del objetivo; elimina solo lo que el usuario nombró explícitamente. No deduzcas que “Otros” es contenido temporal ni borres datos de apps para liberar almacenamiento cuando la instrucción solo dice caché. Informa los bytes realmente recuperados después de la operación.

### Caso 7 — *Just Cause 2*: ubicar archivos para el port

El usuario indicó que el port estaba abierto y que el juego residía en una carpeta `JustCause2` del almacenamiento. Pidió organizar los archivos y recibir la ruta para seleccionarla manualmente en el port. La conversación no conserva la ruta final ni una validación de ejecutable/datos o recibo de arranque; no la inventes a partir del nombre de la carpeta. Al repetir, inspecciona primero la estructura que exige esa versión del port, conserva la carpeta fuente y entrega la ruta exacta que queda en el dispositivo.

### Caso 8 — Clon de YouTube para escala del video en el Magic V2

**Objetivo:** responder a las franjas superior/inferior de la aplicación mod, ofreciendo un clon separado con un control de escala que pueda usarse con los videos a pantalla completa. El requisito de no perder información se trata como preservación del cuadro en `Default/Fit`; `Zoom` y `Stretch` se exponen como decisiones con costos explícitos.

**Entradas/build registradas:**

- App original observada: paquete `app.rvx.android.youtube`, versión `20.14.43`; quedó instalada.
- Un intento de volver a parchear ese APK ya modificado no encontró patches compatibles y no se instaló.
- Base limpia usada para el clon: YouTube `21.13.164`, obtenida de [esta entrada de APKMirror](https://www.apkmirror.com/apk/google-inc/youtube/youtube-21-13-164-release/youtube-21-13-164-4-android-apk-download/), SHA-256 `c193daf879d36e04886c34dcc44580b1c98c20534165d306c2a04b8025fc3f46`. APKMirror es un mirror de terceros; la cadena de firma de la base se verificó antes de parchear. Para repetir, usa una copia autorizada de la misma versión y verifica su firma/hash.
- Morphe Desktop CLI `1.20.0`, SHA-256 `679f579b3ad743ac0ca697ef71e57430d00be59411b04494afd1845c43fb79f`; bundle Anddea `4.3.0`, SHA-256 `deb9dbe2fe1d70300d3fe4b6c99c0042a6f3095dfb932e5d79ca40eaeb59f454`.
- Patches: `Fullscreen video scale`, `GmsCore support`, `Settings for YouTube`, `Ambient mode control`, `Custom branding for YouTube`.
- Ajustes de patch usados: paquete del clon `bill.youtube`, vendor group `app.revanced`, comprobación de GmsCore activa, patch de manifest, etiqueta de ajustes `RVX`, marca visible `YouTube Adaptive` y el icono original.
- Resultado: APK firmado por separado, paquete verificado como `bill.youtube`, versión `21.13.164`, target SDK 36, tamaño `195,462,047` bytes y SHA-256 de salida `fd46b8fff078a33ba0dbb062f3d775a67f7814579e66d465837621bdb3e506ce`. El reporte de Morphe describía el package base `com.google.android.youtube`; por eso se verificó el ID final directamente desde el manifiesto.

**Instalación/runtime:** `adb install` terminó en `Success`; se confirmó que el original y el clon aparecen como paquetes distintos; el clon abrió la actividad principal sin crash inmediato. GmsCore mostró un selector de cuentas; no se eligió cuenta. Se denegó la solicitud de notificaciones. La verificación de arranque no equivale a comprobar que todos los tipos de video usan la escala.

**Lectura geométrica del player:** la jerarquía UI informó actividad/player de `2156×2344` y `SurfaceView` de `[0,566][2156,1778]`, esto es `2156×1212` con relación `16:9`. La ventana ocupa el panel interior, pero el cuadro de video conserva 16:9; la franja visible no prueba por sí sola que falte una configuración global de pantalla.

**Ajuste in-app:** se encontró `YouTube → Settings → RVX → Player → Player buttons → Overlay buttons → Show video scale button`. Al intentar activarlo, la UIAutomation reportó “Restart required”. El estado final de ese reinicio y el ciclo `Default/Stretch/Zoom` no quedaron verificados tras la interrupción del trabajo. El clon sí incluye el patch en el binario, pero no se afirma que el usuario ya tenga Zoom persistido ni que la vista llene el panel en todos los videos.

**Trade-off:** en una pantalla casi cuadrada, ampliar una imagen 16:9 hasta ocupar la altura recorta una fracción grande de sus bordes horizontales. `Stretch` conserva todos los extremos, pero altera figuras y texto. Para mantener toda la información, usa `Default/Fit`; si el usuario prioriza cobertura total, habilita Zoom y comprueba que entiende el recorte. Una alternativa visual es ambient/background fill detrás de un video en Fit.

La petición posterior de quitar el 100 % de los anuncios no forma parte del trabajo de escala descrito aquí; este registro no confirma que se haya aplicado un cambio de anuncios.

### Caso 9 — *PES 6*: clon limpio, ISO europea, pantalla completa y tacto

**Base y datos:** el APK original identificado en el dispositivo era `com.pes6port.iso`; el usuario confirmó que estaba limpio y pidió un clon separado. Se copió el APK instalado, se cambió el identificador a `com.pes6port.iso.touchfix`, se le dio una etiqueta distinta y se firmó con una llave local de prueba. La instalación del clon y una actualización posterior conservaron separado el original. La llave y los APK permanecen en el Mac; no se publican.

La ISO seleccionada fue *Pro Evolution Soccer 6 (Europe) (En,Fr,De,Es,It)*, de 1,248,329,728 bytes. El log del clon indicó `ISO correcta` y confirmó que la copia terminó en los datos de esa app. En la misma ejecución, el renderer detectó Adreno 740, preparó una resolución interna de 1440×816 y llegó a la escena 8 con lecturas cercanas a 30 FPS. Esas lecturas se refieren al juego antes del parche de escala y no prueban 60 FPS.

**Parche de prueba:** se dividió el `libpes6.so` incluido en el APK de prueba en una biblioteca núcleo y un cargador pequeño. El cargador intercepta las llamadas `glBlitFramebuffer` que copian el FBO del juego a la superficie EGL y escala el cuadro a las dimensiones de la superficie. También redirige `pes6_launcher_window_point` a coordenadas normalizadas por el ancho y alto completos, para que los toques del menú correspondan a la imagen extendida. Esto aplica `Stretch`: cubre la superficie sin recorte, pero deforma la relación original. Requiere comprobar los controles por separado.

El APK actualizado se verificó con `apksigner`, mantuvo el mismo paquete/llave del clon, se instaló correctamente y abrió `NativeActivity`. El archivo `pes6.iso` persistió después de la actualización. Una captura tomada en la selección de idioma todavía mostraba bandas arriba y abajo. El usuario indicó luego “ya quedó”; ADB pasó a `offline` antes de leer los logs específicos del cargador o verificar el toque físico. Estado de evidencia: **actualización instalada y éxito reportado por el usuario; hook activo, pantalla 100 % y tacto final no verificados independientemente**. Para cerrar la reproducción se necesita una captura posterior en la misma escena y una prueba táctil en menú y gameplay.

## Seguimientos y casos nuevos al 2026-11-07

### Caso 10 — *Gears of War* (2006): letterbox del presentador nativo

**Arquitectura y alcance:** clon Android `com.xport.gears_of_war.magicv2adaptive`, con un presentador Xenia/ReX dentro de `libgame.so`. El objetivo de la última sesión fue la pantalla interior desplegada del Magic V2. No se tocó el APK original.

**Diagnóstico:** la actividad Android y la superficie ya cubrían la captura horizontal `2344×2156`, mientras el cuadro del juego 16:9 quedaba centrado con franjas negras arriba y abajo. Eso localizó el problema en el cvar de presentación, no en el modo inmersivo o en `wm size`. Una variable de entorno añadida sola no cambió la captura; el parser de este wrapper tenía prefijos/capitalización propios y la biblioteca inicializaba `present_letterbox` como activo en más de un valor predeterminado.

**Cambio aplicado en esa build:** se cambiaron a falso los valores predeterminados de `present_letterbox` que usaba el binario y se mantuvieron los overrides específicos que el wrapper esperaba: `XPORT_SURFACE_SCALE=1.0`, `REX_PRESENT_LETTERBOX=false`, `XPORT_XENIA_CVARS_DEFAULTS=present_letterbox=false` y `XPORT_XENIA_CVARS=present_letterbox=false`. Las posiciones binarias no se publican como receta porque el hash exacto de `libgame.so` no se guardó. La reproducción debe buscar primero el cvar soportado o reconstruir desde fuente; los offsets de otro APK no son reutilizables.

**Resultado:** el APK del clon se actualizó en sitio con la misma identidad de paquete y firma. Se capturó el título y después una escena real de gameplay; ambos llenaron la captura sin letterbox. El usuario confirmó que ya veía pantalla completa. Los saves se conservaron y se habían respaldado antes de actualizar.

**Interpretación y límites:** el método efectivo fue `Stretch`. No se vieron bandas ni se recortaron los extremos del cuadro en esas capturas, pero la imagen 16:9 se deformó al ratio aproximado 1.087:1 del panel. No se amplió la cámara ni se generó contenido nuevo fuera del cuadro. Una captura mostró 27 FPS en un instante; no mide rendimiento estable. El tacto de todos los bordes tampoco quedó medido. La [guía específica](ports-recompilados-letterbox.md) separa este ajuste de un patch real de viewport/FOV.

La documentación oficial de Xenia Canary confirma que `present_letterbox=false` estira el cuadro. Sus patches públicos para *Gears of War* ofrecen perfiles 16:10 y 21:9 con cambios de viewport/FOV; esos ratios no coinciden con el panel casi cuadrado de esta prueba. No deben aplicarse sin un patch calculado para la proporción medida y una verificación de menú, gameplay, HUD y cinemáticas.

### Caso 11 — *God of War III* en Android: Lossless, estabilidad y CPU

**Proyecto de referencia:** el usuario indicó el port [zFitness/gow3_android](https://github.com/zFitness/gow3_android) y pidió reparar su integración Lossless, compilar para el Magic V2 y medir el resultado. También pidió 1080p nativo, corrección persistente de texturas y más rendimiento.

**Secuencia relevante:** después de un perfil de máximo rendimiento, el usuario informó errores en cinemáticas de acciones y pidió volver a la primera versión que solo incorporaba ajustes de Lossless. Más adelante pidió activar todos los núcleos de CPU y dijo que el rendimiento mejoró. Son reportes útiles para orientar experimentos, pero no demuestran que el perfil agresivo causara las fallas ni que el sistema llegara a 100 % de CPU/GPU. No se conservó una medición A/B, telemetría por núcleo, perfil binario final ni prueba concluyente de cuadros interpolados.

**Regla aprendida:** conserva un perfil conocido como baseline antes de optimizar. Prueba las cinemáticas que fallaron además de un punto de gameplay interactivo. Añade un cambio cada vez (resolución, CPU scheduling, driver, cache de texturas o generación de cuadros), y revierte la última variable si reaparece el fallo. “Todos los núcleos disponibles” no implica que el juego pueda paralelizar todo el trabajo ni que la CPU deba informar 100 % de uso; un uso menor puede significar espera de GPU, sincronización o límites de un hilo.

### Caso 12 — *Zelda: Breath of the Wild Recompiled*: meta 60→120

El usuario describió una meta de 60 FPS renderizados por el juego y 120 FPS de salida con interpolación. Se revisó y aprobó un diseño, pero el usuario pausó esa línea para corregir pantalla completa en una app abierta. El registro no confirma que la integración de LSFG se implementara, compilara o funcionara dentro del APK. El usuario había visto momentos cercanos a 60, lo que no equivale a 60 FPS estables.

**Regla aprendida:** documenta por separado FPS base del juego, tasa de salida interpolada, refresco activo del panel, lectura del HUD y límite configurado. La aprobación de diseño no es prueba de implementación; una sesión de captura no prueba que se generen cuadros válidos ni que la entrada responda como a 120 FPS nativos.

### Caso 13 — YouTube RVX: reproducción en segundo plano

Después del clon adaptativo anterior, el usuario eligió una base compatible RVX 21.30.216 para probar reproducción de fondo y controles de notificación. El usuario informó que no aparecieron controles de reproducir/pausar. El registro no demuestra que MediaSession, reproducción con la app cerrada, canal de notificación o permisos estuvieran configurados ni que se aplicara una corrección. Al repetir, verifica por separado patch de background playback, servicio/media session, permiso de notificaciones en Android, canal y aparición de controles después de salir del player. No infieras que el parche de escala de pantalla añade playback en segundo plano.

### Caso 14 — DOOM Mobile v0.4.9: ratio dinámico para el panel interior

**Dispositivo y base:** HONOR Magic V2, Android 16, panel interior desplegado en horizontal. El port instalado era `org.doom.port` v0.4.9. El código de referencia fue el tag [`v0.4.9` de Desm0nt/doom-port](https://github.com/Desm0nt/doom-port/tree/v0.4.9), un port nativo ARM64 con un parser propio de aspecto. Los datos del usuario permanecieron en `Download/DOOM Mobile/{dm,romfs}`; no se incluyó contenido del juego en el repo.

**Diagnóstico:** `dumpsys window` mostraba la actividad clonada en el rectángulo interior completo `2344×2156`; el letterbox inicial estaba en el tamaño/aspecto que elegía el renderer, no fuera de la ventana Android. En el tag consultado, `DM_DOOM_ASPECT=auto` calculaba un ancho pero imponía un mínimo de `960×720` (4:3). Ese mínimo dejaba bandas arriba y abajo en la pantalla interior, cuya relación es aproximadamente `1.087:1`.

**Cambio del clon:** se creó `org.doom.port.magicv2adaptive` con etiqueta propia y se dejó instalado junto al paquete original. Se modificó únicamente el wrapper Java: al estar la preferencia en Auto y la ventana ser más estrecha que 4:3, el clon obtiene las dimensiones actuales de `WindowMetrics` y pasa la relación `ancho:alto` a la variable de aspecto que el motor v0.4.9 ya reconoce. El parser nativo calcula un cuadro base de unos `783×720` y alinea el ancho a bloques de 16 píxeles (`784×720`); el presenter lo escala a la superficie completa. Se reutilizó la biblioteca nativa de la build instalada para no mezclar una recompilación del motor con el cambio de wrapper. El APK original, sus preferencias y datos no se reemplazaron.

**Arranque y resultado:** al iniciar en frío se vieron logotipos/videos y después el menú `Load from checkpoint`; el proceso permaneció vivo. Esto no fue un crash confirmado. Una activación del control A cargó el checkpoint y llegó a gameplay. La captura local del display interior era `2344×2156`, con escena y controles visibles hasta los bordes; el usuario confirmó que ya veía pantalla completa. La imagen de prueba se omitió del repositorio por contener el juego.

**Driver y rendimiento:** el paquete Turnip Amaral 26.3.0-devel v4.6.1.4 se importó al clon y quedó seleccionado en la preferencia de driver. La telemetría del port mostró una lectura instantánea de 60 FPS en esa captura; no hay serie temporal ni frametime agregado para llamarlo 60 FPS estable. El logcat de este firmware no entregó mensajes útiles del port y no se obtuvo la lectura de renderer de `nativeDriverStatus`; por tanto, la selección/importación de Amaral está observada, pero no se afirma que fuera el renderer Vulkan activo ni que causara el arranque correcto. El intento previo con Gen8 V37 también se limitó a ser una selección; sus metadatos indicaban paquete Gen8/A8xx y no se demostró que el cierre percibido fuera un fallo de ese driver.

**Límites:** se probó que un control A alcanzó el checkpoint, no toda el área táctil ni cada botón físico. La captura confirma pantalla completa en gameplay; no se conservó captura comparable del título tras el último cambio. La lectura de 60 FPS es puntual y el estado térmico, refresco del panel y renderer activo no se midieron en esa escena. No copies el override `DM_DOOM_ASPECT` a otros ports ni tomes el umbral Auto de esta versión como una norma de Android. Sigue la [guía reproducible del caso](doom-mobile-magic-v2.md) y el [código upstream v0.4.9](https://github.com/Desm0nt/doom-port/tree/v0.4.9).

### Caso 15 — *The Last of Us Remastered* para Android: análisis de publicación

El usuario compartió una publicación de redes sociales que afirma que el port requiere Android 11+, 12 GB de RAM y 15 GB libres, y que se instala con un launcher APK y datos PKG seleccionados desde el menú. Se describió un enlace de descarga truncado y otro hospedado por un tercero. Esta sesión solo analizó el texto pegado; no se descargó ni inspeccionó ningún archivo, no se verificó la procedencia del launcher o del PKG y no se probó la instalación. Los requisitos y la guía son afirmaciones de esa publicación, no hechos técnicos establecidos.

**Al repetir:** identificar paquete, firma, versión, ABI y documentación del launcher; determinar mediante contenido/firma el tipo real de archivo “PKG” y la ruta requerida; confirmar espacio temporal suficiente antes de copiar; y no asumir que un enlace abreviado o “sitio seguro” es confiable. No renombres el archivo para forzar importación y no borres los datos fuente antes de que el port valide la preparación y llegue a gameplay.

### Caso 16 — DOOM Mobile v0.4.18-test1: modelos animados negros

**Síntoma y base:** el upstream registra modelos/cuerpos animados negros con una ruta Adreno 740. Es una falla dentro del cuadro, no una variante del letterbox del caso v0.4.9. El análisis está fijado a [BUGS_AND_FIXES.md en el commit `085d0cb0`](https://github.com/Desm0nt/doom-port/blob/085d0cb0b3796ddbfa33c64b6d00776387ad4eba/docs/doom/BUGS_AND_FIXES.md), donde clipping/culling, skinning y lecturas de buffers se separan como hipótesis.

**Experimentos upstream y regresiones:** el workaround de clipping no resolvió el render negro. El modo `DM_GFX_BONES_SSBO=1` hizo aparecer cuerpos y enemigos en una prueba, pero el mismo registro encontró flicker de suelo, una puerta ausente y un arma oscura. `DM_VK_ROBUST=0` quedó anotado como el siguiente test; eso no prueba por sí solo la causa ni el resultado en el Magic V2. No conviertas ninguna de esas variables en predeterminado universal.

**Estado del caso local:** se generó un APK de clon de diagnóstico con una variante nativa experimental y archivos del loader; el usuario confirmó después que el aspecto gráfico ya quedó arreglado. No se conservó una captura final comparable, una sesión A/B ni un log del renderer del mismo proceso. No se puede asignar la mejora a un flag, al driver personalizado o a los hooks ni confirmar cuál renderer estuvo activo. Estado: **resultado reportado por el usuario; causa y driver activo sin verificación independiente**.

**Cómo repetir:** conserva original y saves; identifica APK, ABI, GPU, versión del port y escena exactos; usa [`diagnostico-de-errores-graficos.md`](diagnostico-de-errores-graficos.md); inspecciona estáticamente hooks y ABI antes de instalar; valida el driver por log del mismo proceso; cambia una sola variable en el clon; compara la misma escena y otra escena con suelo, puertas, armas y animaciones. El script local es preflight de paquete, no verificador de runtime. No publiques APK, driver, assets ni capturas protegidas.

### Caso 17 — *Dark Souls: Remastered*: presenter Vulkan a pantalla completa

**Arquitectura y alcance:** port Android nx2android, title ID `01004AB00A260000`, clon actualizado por separado en HONOR Magic V2 con el panel interior desplegado. La ventana activa de NativeActivity ya tenía bounds de `2344×2156`; el problema se encontraba en cómo el presenter Vulkan ajustaba el cuadro, no en una ventana Android reducida.

**Diagnóstico y cambio:** el presenter recibía un cuadro de `1920×1080` y el modo normal lo centraba en la superficie, conservando el 16:9 y dejando barras. Se hizo que la build para este title ID estableciera el destino de blit al tamaño completo de la superficie. El mismo rectángulo se publicó mediante `vk_pic_set()` y lo consume el transformador táctil de `front_android.c`. La implementación conceptual y referencias al código upstream están en [`la guía especializada`](dark-souls-remastered-magic-v2.md). Una primera variante dibujaba además una copia ampliada debajo del cuadro original y se veía duplicada; se desactivó para la build final.

**Resultado y evidencia:** el clon fue recompilado, firmado con la misma clave local del clon, actualizado en sitio y arrancó sin tocar el paquete original. El log del proceso dijo `full-window stretch enabled: source=1920x1080 target=2156x1983`; una captura explícita del display interior midió `2344×2156` y mostró la escena sin franjas ni fondo duplicado. El usuario confirmó que la pantalla completa funcionaba. No se guardaron capturas con el juego en Git.

**Límites:** el resultado es `Stretch`, por lo que la imagen 16:9 se deforma al ratio casi cuadrado del panel; el cambio no amplía FOV ni genera contenido fuera del cuadro. Aunque el rectángulo de toque sigue el rectángulo de imagen en el código, no se hizo una prueba física de todos los botones después de la actualización. La lectura cercana a 29 FPS fue instantánea, no una serie sostenida. El log indicó que Turnip personalizado no cargó y que el port usó el driver del sistema; no se atribuye el éxito visual a V37/V38/Amaral. No se integró Lossless ni se cambió la meta de FPS/calidad en esta tarea.

### Seguimiento de *Resident Evil 7*: hangs, driver y límites

El perfil histórico RE7 de este informe registraba V38 y un límite configurado de 70. Después se reportaron nuevos estados colgados; el usuario pidió probar el driver Adreno 27 R1, limitar a 120 FPS y mantener una configuración de pantalla de 120 Hz mediante un script de inicio de Termux. También solicitó acceso a todos los núcleos de CPU. El registro del proyecto no contiene el script final, una lectura posterior de `dumpsys display`, el log del renderer asociado al proceso ni una sesión comparativa que demuestre 120 FPS sostenidos o estabilidad. Por ello, conserva el caso V38/70 como histórico y trata 27 R1/120/core policy como experimento posterior que debe volver a identificarse y verificarse antes de reutilizarlo.

La lectura de refresco del panel, el tope del renderer, el FPS real de gameplay y cualquier salida de LSFG son valores distintos. Reiniciar Termux o guardar un valor persistente en el sistema tampoco prueba que la app del juego lo reciba. Para un hang, conserva tombstone/logcat antes de cambiar renderer; no asignes causalidad a la temperatura o al driver sin evidencia del proceso.

### Investigación propuesta de DLSS 5 en Android

Se discutieron runtime binaries de Hugging Face y repositorios de terceros, pero el registro no contiene una descarga ni integración en RE7. No se debe describirlo como portado o probado. Para una futura investigación se necesitan licencia y procedencia verificables, arquitectura/ABI compatible con Android, API gráfica soportada por el driver del teléfono, una ruta real de inferencia e integración en el renderer, y medición en el mismo proceso. Cambiar hashes o copiar DLLs al APK no establece compatibilidad ni sustituye una implementación Android/ARM64. No añadas DLLs, pesos, binarios ni archivos de juego al repositorio.

### Limpieza del Mac y almacenamiento

El trabajo de almacenamiento pidió priorizar cachés y compilaciones antiguas. El método reutilizable es medir bytes realmente asignados, identificar qué herramienta generó cada artefacto y comprobar que haya una fuente reproducible antes de borrar. Un tamaño aparente muy grande puede ocupar pocos bloques; el tamaño del Finder no basta. No elimines proyectos, datos privados de apps, saves o la categoría “Otros” sin identificar los archivos concretos. El informe no registra una lista completa de rutas eliminadas ni un delta final de almacenamiento del Mac, por lo que no ofrece una receta de borrado específica.

## Receta reproducible del clon de YouTube

Los comandos son una plantilla para una nueva copia autorizada; no redistribuyas el APK base, el clon firmado ni la llave. Fija las versiones y hashes para poder comparar. Revisa compatibilidad nuevamente antes de repetir porque los patches y builds cambian.

```bash
java -jar "$MORPHE_JAR" list-versions \
  --patches "$PATCH_BUNDLE" \
  --filter-package-names com.google.android.youtube

java -jar "$MORPHE_JAR" list-patches \
  --patches "$PATCH_BUNDLE" --with-options

java -jar "$MORPHE_JAR" patch \
  --patches "$PATCH_BUNDLE" --exclusive \
  --enable "Fullscreen video scale" \
  --enable "GmsCore support" \
  --enable "Settings for YouTube" \
  --enable "Ambient mode control" \
  --enable "Custom branding for YouTube" \
  --options 'packageNameYouTube=bill.youtube' \
  --options 'gmsCoreVendorGroupId=app.revanced' \
  --options 'checkGmsCore=true' \
  --options 'disableCoreServices=false' \
  --options 'patchAllManifest=true' \
  --options 'rvxSettingsLabel=RVX' \
  --options 'customName=YouTube Adaptive' \
  --options 'appIcon=original' \
  --out youtube-adaptive-clone.apk \
  --result-file patch-result.json \
  "$BASE_YOUTUBE_APK"

aapt dump badging youtube-adaptive-clone.apk | head
apksigner verify --verbose youtube-adaptive-clone.apk
unzip -t youtube-adaptive-clone.apk

adb devices -l
adb -s "$SERIAL" shell pm list packages
adb -s "$SERIAL" install youtube-adaptive-clone.apk
adb -s "$SERIAL" shell monkey -p bill.youtube 1
```

Use Java 21 for the recorded Morphe Desktop 1.20.0 setup. The patch CLI supports multiple named patches and typed options; use `--exclusive` so unlisted patches are not silently added. Never put a signing keystore/password, ADB serial, account state, downloaded APK, game data or private capture in this repo.

## Cómo repetir la medición de pantalla

1. Identifica el display interior y toma una captura explícita de ese display.
2. Guarda jerarquía UI, ventana y listado de superficies mientras reproduces un video conocido.
3. Registra bounds de la actividad y del `SurfaceView`/surface, y calcula su relación de aspecto.
4. En el clon, activa el botón de escala, reinicia si el diálogo lo solicita y abre el mismo video en modo de pantalla completa.
5. Cicla `Default`, `Stretch`, `Zoom`; en cada estado guarda captura y bounds. Confirma si la preferencia persiste al cambiar de video y después de cerrar/abrir la app.
6. Repite al menos con video estándar, Shorts, feed/miniplayer e incrustado. La afirmación “todos los videos” requiere resultados para cada clase probada y una lista explícita de lo que quedó fuera.
7. Confirma que el paquete activo sigue siendo `bill.youtube`, que el original no cambió, y que no se seleccionó una cuenta durante la verificación.

## Límite de inferencia y validez

Los resultados son de un solo dispositivo y aplicaciones/builds específicos. No se controlaron todas las codificaciones, relaciones de aspecto, contenidos servidos por servidor, posturas, orientaciones, escenas ni versiones. El usuario reportó algunas mejoras; el informe conserva ese dato como reporte cuando falta una captura verificable. Los ajustes de driver y rendimiento no son portables entre juegos solo por compartir el mismo hardware. El clon es un artefacto de prueba local y el modo de escala requiere comprobación por tipo de reproducción.

## Referencias

1. Repo y perfil RE7: [`README`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/README.md), [`diagnóstico`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/docs/arquitectura-y-diagnostico.md), [`método APK`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/docs/reproduccion.md), [`evidencia`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/docs/resultados-y-evidencia.md), [`LSFG`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/docs/generacion-de-cuadros.md).
2. Android Developers, [Make your app fold aware](https://developer.android.com/develop/adaptive-apps/guides/foldables/make-your-app-fold-aware) y [Use window size classes](https://developer.android.com/develop/adaptive-apps/guides/use-window-size-classes).
3. Morphe Desktop, [CLI documentation](https://github.com/MorpheApp/morphe-desktop/blob/main/docs/documentation.md).
4. Anddea, [patch list and compatible YouTube versions](https://github.com/anddea/revanced-patches), incluido `Fullscreen video scale`.
5. Repo Halo proporcionado por el usuario, [Ayanokoji989/Halo-2](https://github.com/Ayanokoji989/Halo-2).
6. Xenia Canary, [opciones de presentación](https://github.com/xenia-canary/xenia-canary/wiki/Options#black-bars-letterboxingpillarboxing) y [patches oficiales de relación de aspecto para Gears of War](https://github.com/xenia-canary/game-patches/blob/main/patches/4D5307D5%20-%20Gears%20of%20War.patch.toml).
7. zFitness, [gow3_android](https://github.com/zFitness/gow3_android), proyecto upstream indicado por el usuario para el port de *God of War III*.
8. Desm0nt, [port Android de DOOM](https://github.com/Desm0nt/doom-port), [fuente v0.4.9](https://github.com/Desm0nt/doom-port/tree/v0.4.9) y [guía de instalación de ese tag](https://github.com/Desm0nt/doom-port/blob/v0.4.9/docs/INSTALL.md).
9. Shirai91, [nx2android presenter Vulkan en el commit examinado](https://github.com/shirai91/nx2android/tree/e9bd2b764608facf841e39292d868ee657eaf634), enlazado solo como referencia externa; revisa la licencia upstream antes de reutilizar código.
10. Android Developers, [cambios de comportamiento de Android 16 en pantallas grandes](https://developer.android.com/about/versions/16/behavior-changes-16).
