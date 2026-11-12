# God of War II / ARMSX2-Catonix en HONOR Magic V2

## Resumen

Se corrigieron las franjas de *God of War II* cambiando el aspecto del cuadro del emulador en el paquete instalado `com.catonix.gow2`. La actividad y el área de pantalla ya ocupaban el panel interior completo; el cuadro del juego estaba en Auto/4:3. Se respaldó la preferencia interna de la app y se cambió solo `aspectRatio`, de `1` a `0`. Después de un arranque en frío, el valor permaneció y una captura local de `2344×2156` mostró el juego ocupando el panel; el usuario confirmó el resultado.

La modalidad es **Stretch**. No se recortó el cuadro, pero sí se deformó su geometría para llenar el panel casi cuadrado. No se alteraron el APK, los datos del juego, la ISO ni la partida. No se probó el tacto.

## Pregunta e hipótesis

**Pregunta:** ¿la franja venía de una ventana Android reducida o del modo de aspecto de la GS del emulador?

**H1:** la ventana ya ocupa el display; el emulador mantiene el cuadro PS2 4:3 en modo Auto, por eso `Fit` agrega bandas. Al elegir `Stretch`, el cuadro cubrirá la superficie completa sin recortarlo, a costa de deformación.

**H0:** la ventana/superficie es menor, `Stretch` no cambia el cuadro, se pierden bordes o la preferencia no persiste al volver a iniciar.

## Entorno y materiales

| Variable | Valor observado |
|---|---|
| Dispositivo | HONOR Magic V2, código de modelo `VER-N49` |
| Sistema | Android 16 |
| Postura | Panel interior desplegado, horizontal |
| Display activo | `2344×2156` píxeles, razón `1.0872` |
| Paquete instalado | `com.catonix.gow2` |
| Actividad observada | `com.armsx2.Main` |
| Paquete | `versionName=1.0.0`, `versionCode=1088`, `targetSdk=37`, marcado `DEBUGGABLE` |
| Juego / disco | *God of War II*, `SCUS-97481 NTSC-U` |
| Preferencia interna | `shared_prefs/ARMSX2.xml`, string `config.global` con JSON |
| Campo cambiado | `aspectRatio`: `1` → `0` |
| Ámbito observado | Global para la app; no había perfil específico del juego en la ruta revisada |

No se registran serial ADB, identificador único del display, hash privado del APK, XML de preferencias, partida o captura protegida. El paquete es un wrapper con nombre propio; no quedó demostrada su procedencia binaria exacta desde una revisión concreta de ARMSX2 upstream.

## Método

El procedimiento operativo reutilizable está en [Aspect ratio en emuladores PS2 para Android](../skills/android-foldable-game-media/references/ps2-emulator-aspect-ratio.md). Esta sección distingue lo que se ejecutó de una receta para repetirlo.

1. **Identificar el objetivo.** Se confirmó el paquete, actividad, versión, título/ID de disco y pantalla interior. Esto impidió tratar la franja interna como una ventana del sistema reducida.
2. **Ubicar la capa.** La ventana Android ya cubría `2344×2156`; el cuadro era de aspecto 4:3 y aparecía con bandas. No se cambió `wm size`, densidad, modo inmersivo, renderer, driver ni resolución de emulación.
3. **Verificar esquema antes de editar.** Se inspeccionó la preferencia efectiva de la app. La clave `config.global` contenía `aspectRatio=1`; la configuración específica del juego no estaba presente. El código upstream inspeccionado en commit `c25493a20285dc126a950d2d61826987a566a306` define `0` como Stretch y `1` como Auto. Como no se estableció la procedencia exacta del wrapper, se consideró ese código orientación y el resultado del APK instalado se verificó empíricamente.
4. **Crear rollback.** Se conservó una copia de `ARMSX2.xml` antes del cambio dentro del espacio privado de la app (`files/ARMSX2.before-stretch.xml`). No se cambió ningún archivo de juego o save.
5. **Cambiar una variable.** Con la app en estado seguro, `config.global.aspectRatio` cambió de `1` a `0`. La intervención se limitó a la preferencia privada de la app.
6. **Arranque frío.** Se cerró por completo y se volvió a abrir el emulador. La preferencia interna volvió a leerse como `0`; la pantalla de juego volvió a abrir.
7. **Verificar salida y comunicar el trade-off.** Se capturó el panel interior explícitamente; la captura local de `2344×2156` mostró el juego llenando el cuadro visible. El usuario confirmó: “bien ya quedó”. El táctil no se comprobó.

## Cálculo geométrico

Para una fuente 4:3 ajustada a un destino de `2344×2156`:

```text
aspecto_destino = 2344 / 2156 = 1.0872
fit_por_ancho = 2344 × (3/4) = 1758 px de alto
espacio_vertical = 2156 - 1758 = 398 px ≈ 199 px por borde
stretch_y = 2156 / 1758 = 1.2264
deformación vertical respecto a fit = (1.2264 - 1) × 100 ≈ 22.6 %
```

El cálculo predice el letterbox de `Fit` centrado y la deformación anisotrópica de `Stretch`. No mide el color/posición de cada píxel ni indica que el juego haya generado una cámara/FOV más ancha. `Stretch` llena el destino completo, conserva el cuadro sin recorte visible y alarga verticalmente el contenido respecto a la presentación ajustada a 4:3.

## Resultados y evidencia

| Comprobación | Resultado | Clase de evidencia |
|---|---|---|
| Bounds de la ventana | Ya ocupaba el panel interior `2344×2156` | Lectura del dispositivo durante la sesión |
| Valor antes/después | `aspectRatio=1` → `0` | Preferencia interna leída antes y después |
| Persistencia | El valor `0` permaneció tras cold start | Verificación de configuración después del reinicio de proceso |
| Imagen final | Captura local del display interior a `2344×2156`, contenido extendido a pantalla completa | Captura revisada localmente; no se publica porque contiene juego protegido |
| Aceptación | El usuario confirmó que quedó bien | Reporte explícito del usuario |
| Recorte | No se observó recorte del cuadro en la captura final | Inspección visual de una captura |
| Distorsión | Esperada por geometría; escala vertical calculada ~1.226× frente a Fit | Cálculo, no medición de landmark dentro del juego |
| Táctil | No probado | Sin evidencia |
| FPS, driver, estabilidad | No evaluados en esta tarea | Fuera de alcance |

La captura final y la baseline no fueron la misma escena exacta tras el reinicio del launcher. Por ello, el resultado demuestra el estado final de pantalla completa en una escena, pero no es una comparación fotométrica A/B de píxeles idénticos. El cálculo geométrico es reproducible; la aceptación final también fue reportada por el usuario.

## Detalle de precedencia y limitación de persistencia

La preferencia primaria interna estaba en `shared_prefs/ARMSX2.xml`. Se observó además un espejo externo en `/storage/emulated/0/Android/data/com.catonix.gow2/files/armsx2-settings.json` cuyo `aspectRatio` seguía en `1`. La fuente upstream consultada indica que el JSON externo es un fallback al faltar la preferencia primaria; el cold start normal conservó el valor interno `0`. No se probó limpiar datos, perder la preferencia primaria, restaurar desde el espejo ni reinstalar. Esos escenarios podrían volver a introducir Auto/4:3 y requieren una prueba separada antes de afirmar recuperación persistente.

La documentación de ARMSX2 consultada incluye [el enum de aspecto en `Settings.kt`](https://github.com/ARMSX2/ARMSX2/blob/c25493a20285dc126a950d2d61826987a566a306/platforms/android/app/src/main/java/com/armsx2/config/Settings.kt#L587-L596) y [la precedencia de configuración en `ConfigStore.kt`](https://github.com/ARMSX2/ARMSX2/blob/c25493a20285dc126a950d2d61826987a566a306/platforms/android/app/src/main/java/com/armsx2/config/ConfigStore.kt#L326-L334). Son referencias de una revisión upstream fijada; no prueban que el APK observado sea idéntico.

## Reproducción independiente

1. Usa una copia legítima del juego y una build cuya configuración hayas identificado; registra versión, paquete, actividad e ID de disco.
2. Confirma que el panel interior, actividad y superficie estén a tamaño completo. Si no lo están, este caso no localiza la misma capa.
3. Guarda una captura de una escena fija en Auto/4:3 y respalda las preferencias.
4. Usa la UI de la build para seleccionar Stretch. Si la UI no ofrece el modo, comprueba el esquema de esa build antes de editar. En una build con esquema equivalente al observado, revisa `config.global.aspectRatio`; no copies este índice ciegamente.
5. Cambia solo ese campo, conserva rollback y cierra la app desde un estado seguro.
6. Arranca en frío, confirma el valor, reproduce la misma escena y captura el display interior correcto.
7. Anota barra, recorte, deformación y tacto por separado. Revierte si el encuadre o los controles no son aceptables.

Para verificarlo con rigor, repite A/B en la misma escena y postura, con el mismo build, partida, cámara y display; toma varias capturas y conserva originales localmente. Reporta proporciones observadas y calculadas por separado.

## Amenazas a la validez y límites

- La etiqueta “Auto” y el valor enum pueden variar por fork, versión o personalización del wrapper.
- La observación proviene de una sola app, título, pantalla y estado de configuración.
- No se ejecutó una prueba física de botones; el llenado visual no valida coordenadas táctiles.
- No se midió FOV, geometría de landmark, frametime, FPS, rendimiento ni calentamiento.
- El cold start normal se verificó; fallback después de borrar preferencias, recuperación y actualización no.
- No se conserva una baseline/final de la misma escena; el resultado final se complementa con la confirmación del usuario.
- Las capturas, APK, ISO, saves y XML se mantienen fuera de Git.

**Conclusión acotada:** en esta build concreta, cambiar `config.global.aspectRatio` de `1` a `0` llenó visualmente el panel interior después de un cold start. El costo esperado es deformación vertical de aproximadamente 22.6 % respecto a Fit 4:3; no se probó tacto. El procedimiento y el valor solo se deben reutilizar tras verificar el esquema, ámbito y resultado de otra build.
