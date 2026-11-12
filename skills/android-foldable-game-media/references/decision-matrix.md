# Matriz de decisión para ports y multimedia Android

Esta referencia permite que un agente elija la capa de inspección antes de modificar un APK. Empieza por identificar la actividad y el paquete instalados; el nombre comercial del juego no basta para saber qué renderer o formato de datos utiliza.

## Árbol corto

1. **¿La actividad Android no cubre el área visible?** Corrige orientación, modo inmersivo, política de ventana, resizability o insets del clon. No cambies la resolución global del dispositivo.
2. **¿La actividad cubre el panel, pero la superficie no?** Inspecciona `SurfaceView`, `TextureView`, `ANativeWindow`, EGL/Vulkan swapchain y el tamaño que recibe el renderer.
3. **¿La superficie cubre el panel, pero el contenido no?** Localiza letterbox en el presenter, ratio cvar, viewport/FOV, escala de video, ajuste de aspecto del emulador o barras dibujadas por el propio juego.
4. **¿La imagen llena el panel y los toques caen en otro sitio?** Mide el mapeo táctil antes de tocar más escala; aplica la inversa geométrica del mismo recorte/estiramiento y prueba menú y gameplay.
5. **¿La app aparenta cerrarse al arrancar?** Lee PID/actividad a lo largo de la transición, observa si son videos/logos o un menú, y adquiere el crash/log antes de cambiar driver. Solo modifica datos después de validar formato y ruta.
6. **¿El objetivo es FPS o interpolación?** Registra por separado tope configurado, FPS del motor, frecuencia del panel, FPS generados, frametime, input/latencia y escena.
7. **¿Se ve un defecto dentro del cuadro?** Separa escena completa negra, modelos/materiales negros, geometría ausente, texturas corruptas y flicker. Compara renderer, driver cargado, shaders/datos y logs en la misma escena; no trates el viewport como causa por defecto.

## Matriz por arquitectura

| Tipo de app/port | Qué revisar primero | Ajuste típico que sí corresponde | Evidencia para afirmar éxito | Error común |
|---|---|---|---|---|
| Juego Android nativo con código | `Activity`, `WindowMetrics`, `SurfaceView`, parser de ratio, renderer y coordenadas de input | Preferencia de ratio/viewport derivada de la ventana activa | Gameplay renderiza al ratio solicitado; HUD y controles probados | Fijar `wm size` del sistema o modificar flags sin medir superficie |
| Recompilación estática / HLE | README y tag de fuente, tamaño de ventana comunicado a HLE, cvars/aspect parser, FOV virtual y escala de HUD | Ratio de salida soportado por esa build; rebuild del wrapper si Auto tiene límites inadecuados | Log del parser más captura de inicio y gameplay en el display correcto | Suponer que la resolución interna 720p es la resolución física final |
| Presenter Vulkan nativo con letterbox | Bounds de ventana/superficie, rectángulo del blit final, cálculo de aspecto y rectángulo consumido por input | Preferencia por título entre `Fit`, `Cover`, `Stretch` o viewport del motor | Log del mismo proceso, captura del display activo y prueba táctil tras el cambio | Cambiar immersive flags aunque la ventana ya esté completa; estirar y llamarlo FOV adaptado; apilar una copia de fondo |
| Presenter Xenia/ReX | Defaults del cvar, parser exacto del wrapper, presenter y configuración efectiva | Opción/cvar del presenter; patch de viewport/FOV separado si existe | Cuadro ocupa el destino; clasificación explícita como Fit/Cover/Stretch/FOV; input probado | Copiar variables `XPORT_*` o offsets de otra build |
| Port Windows/Linux en contenedor | Resolución del contenedor, `ANativeWindow`, Surface, escalador del contenedor, DXVK/VKD3D y mapa táctil | Cambio de viewport/transformación por versión del contenedor | Misma escena, menú y gameplay; logs DXVK/renderer y entrada coincidente | Llamar “Android nativo” al binario Windows o asumir que subir la resolución da más FPS |
| Emulador PS2 Android (ARMSX2/fork) | Bounds Android, `SurfaceView`, cuadro GS, build exacta, opción de aspecto y ámbito global/por juego | UI del emulador; si no basta, formato de configuración de esa build con rollback; ver [runbook](ps2-emulator-aspect-ratio.md) | Preferencia tras cold start, captura del mismo display y escena, recorte/deformación y tacto por separado | Copiar enums/rutas upstream sin validar el fork; llamar FOV a `Stretch`; asumir que la ventana completa implica cuadro completo |
| Otros emuladores | Bounds Android y `SurfaceView`, cuadro GS, backend, ajuste del core y ámbito global/por juego | Preferencia de aspecto del emulador; preferir ajuste por título si existe, mantener `Fit` o elegir `Stretch` según el costo aceptado | Captura del mismo display/escena más lectura de la preferencia después de cold start; tacto probado por separado | Cambiar tamaño global Android, asumir que la ventana completa implica cuadro completo, o copiar un enum/perfil de otra versión |
| Player de video/mod de YouTube | Parche/versionado, modo fullscreen, player view, selector de escala, `MediaSession`, servicio y notificaciones | Mantener Fit como default; habilitar explícitamente Zoom/Stretch/background si el patch los implementa | Probar video normal, Shorts, feed, miniplayer, incrustado, fullscreen y salida al background | Suponer que fullscreen scale habilita background playback o funciona en todos los players |

## Captura y comandos de referencia

Primero redescubre el serial y úsalo explícitamente:

```bash
adb devices -l
adb -s "$SERIAL" shell dumpsys display
adb -s "$SERIAL" shell dumpsys activity activities
adb -s "$SERIAL" shell dumpsys window windows
adb -s "$SERIAL" shell dumpsys SurfaceFlinger --list
adb -s "$SERIAL" shell dumpsys SurfaceFlinger --display-id
adb -s "$SERIAL" exec-out screencap -d "$DISPLAY_ID" -p > /tmp/app-screen.png
adb -s "$SERIAL" shell pidof "$PACKAGE"
adb -s "$SERIAL" logcat -d -t 3000 -v threadtime
```

En Android 16 de HONOR se encontraron varios displays lógicos aunque solo el interior estuviera visible. La captura predeterminada de `screencap` pudo salir mezclada con advertencias; toma el ID de `dumpsys SurfaceFlinger --display-id` y verifica el encabezado/dimensiones del PNG. Los tamaños `2344×2156` y `2156×2344` son orientaciones del panel interior de Magic V2 observadas en este caso, no valores que deban fijarse globalmente.

Si logcat no muestra mensajes de la app:

1. Guarda PID, actividad y captura antes de volver a lanzar.
2. Prueba buffer `crash` y tags del port acotados por proceso; no imprimas DropBox completo sin filtros.
3. Busca logs/documentación del port en almacenamiento app-specific o su runtime. Android puede impedir leer una ruta de `Android/data` desde `shell`; que `adb pull` falle no demuestra que el archivo no exista.
4. Revisa si el renderer muestra un estado/contador dentro del propio juego. Regístralo como lectura visual, no como sustituto automático del log de driver.
5. Declara el límite de observabilidad. Nunca conviertas la ausencia de líneas en confirmación de driver, FPS o estabilidad.

## Semántica del encuadre

| Resultado | Geometría | Qué conservar | Qué sacrifica |
|---|---|---|---|
| Fit / contain | escala uniforme dentro del destino | toda la imagen y proporción | deja bandas o fondo |
| Cover / zoom | escala uniforme hasta cubrir destino | proporción | recorta bordes |
| Stretch | escala X/Y independiente | todo el cuadro de origen | deforma geometría |
| Viewport/FOV adaptado | el motor genera el cuadro para el ratio destino | puede conservar el contenido relevante y el HUD | requiere soporte del juego, validación y a veces cambios de cámara |
| Fondo ambiental | cuadro completo más fondo derivado | todo el cuadro original | el relleno es decorativo, no nuevo campo de visión |

No prometas a la vez píxeles completos del destino, geometría no deformada y ningún recorte para ratios distintos, salvo que el juego amplíe su viewport/FOV o exista contenido de fondo.

## Arranque: espera, crash o carga infinita

Registra una pequeña línea temporal (por ejemplo, 0/5/15/30 segundos) con PID, actividad, pantalla y mensajes del port. Esta pausa acotada evita confundir logos/video legal con un cierre. Si el PID desaparece, adquiere `logcat -b crash`, tombstone/DropBox filtrado por nombre de paquete y el último boot log antes de cambiar variables. Si el PID continúa en primer plano y la imagen avanza, sigue el flujo del juego; si se mantiene la misma imagen, distingue vídeo bloqueado, proceso vivo sin render, ANR y cierre según los datos disponibles.

Después de crear un clon, no supongas que comparte saves, preferencias o estado de pantalla del original. Los datos privados del paquete son separados salvo que el port use archivos compartidos. Usa el checkpoint o un inicio nuevo de forma controlada; no borres datos para “arreglar” un arranque sin haber respaldado primero.

## Drivers y rendimiento: matriz de evidencia

| Nivel | Evidencia | Afirmación permitida |
|---|---|---|
| Driver archivado | ZIP presente en una carpeta | El paquete existe |
| Driver importado | Biblioteca y `meta.json` dentro del storage que usa el port | El port lo puede enumerar |
| Driver seleccionado | Preferencia UI/config apunta al nombre | Quedó seleccionado para el próximo inicio |
| Driver cargado | Log del mismo proceso, ruta/nombre de biblioteca y resultado de inicialización | El loader intentó/cargó esa biblioteca |
| Renderer confirmado | Dispositivo Vulkan, vendor/driver/API reportados por la instancia del juego | Ese renderer participó en esa sesión |
| FPS instantáneo | HUD/overlay de un frame o ventana corta | Lectura puntual, no estabilidad |
| FPS sostenido | Serie temporal del mismo gameplay más frametimes | Rendimiento observado en esa escena/duración |
| FPS generados | Contador real de salida de frame generation sincronizado con FPS base | Salida interpolada observada; no cambia por sí sola el tick ni el input base |

Un driver nombrado “Gen8”, “patched” o “Adreno” no determina compatibilidad por sí solo. Compara metadata, ABI, API, GPU, loader y runtime. El V38 debe evaluarse con la evidencia de su loader concreto; un ZIP compartido no se vuelve un driver global. No persigas 100 % de CPU/GPU: mide el cuello de botella, carga por núcleo, esperas y frametime.

## Defectos de imagen y render

| Síntoma reproducido | Primeras capas a inspeccionar | Evita concluir |
|---|---|---|
| Solo algunos modelos aparecen negros | skinning/índices, shader, buffers/descriptores, material y ruta del renderer | Que sea una textura faltante o un driver incompatible sin inspección |
| Geometría falta o deja agujeros | culling/clipping, buffers de índices, sincronización y cámara | Que una mejora de encuadre haya arreglado el render |
| Textura errónea, negra o rosa | recurso y formato/mip, descriptor/sampler, shader, loader de datos | Que un cambio de viewport pueda reparar recursos |
| Flicker o corrupción temporal | carreras CPU/GPU, barreras, memoria, driver y shader | Que una única captura estable demuestre resolución |
| Cuadro entero negro/crash | PID, transición de escena, swapchain, renderer, inicialización y logs/tombstone | Que “driver seleccionado” signifique inicializado o activo |

Procedimiento, preflight estático del APK y límites del caso DOOM están en la [guía de diagnóstico gráfico](diagnostico-de-errores-graficos.md). La presencia de una biblioteca en el APK solo verifica el paquete; para una afirmación de carga, usa estado/log del mismo proceso. Compara una sola variable en un clon y conserva el driver/configuración que funcionaba. Una variante que arregla un modelo pero rompe suelo, puerta, arma u otra escena es una regresión, no una solución general.

## Formatos de datos e instalación

- La ruta y estructura las decide el launcher/port. Sigue su README y valida una muestra de archivos antes de copiar varios GiB.
- Verifica firma/formato, número de volúmenes, región, hash/tamaño y espacio temporal requerido. No cambies extensión para fingir compatibilidad.
- No ejecutes archivos descargados. No distribuyas juegos o assets protegidos en el repo.
- Para copias grandes, calcula origen, destino, espacio libre y método de reanudación. Conserva el origen hasta que el launcher valide los datos.
- APK, ISO, PKG, OBB, carpetas `romfs` y paquetes de importación no son formatos intercambiables. Un post en redes no es documentación técnica del instalador.

## Casos que deben abrirse antes de repetir

- [Informe técnico y evidencia por título](case-study.md)
- [Letterbox de Gears of War/Xenia-ReX](ports-recompilados-letterbox.md)
- [Presenter Vulkan nativo de Dark Souls Remastered](dark-souls-remastered-magic-v2.md)
- [Implementación de viewport en RE7](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering/blob/main/docs/arquitectura-y-diagnostico.md)
- [Fuentes del port DOOM v0.4.9](https://github.com/Desm0nt/doom-port/tree/v0.4.9)
