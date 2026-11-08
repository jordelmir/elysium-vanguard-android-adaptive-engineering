# DOOM Mobile v0.4.9 en el panel interior del Magic V2

## Alcance

Este documento registra una adaptación del clon Android del port de DOOM (2016) sobre HONOR Magic V2. El origen consultado fue el tag [`v0.4.9`](https://github.com/Desm0nt/doom-port/tree/v0.4.9) del proyecto [Desm0nt/doom-port](https://github.com/Desm0nt/doom-port). El informe no distribuye APK, biblioteca nativa, driver ni archivos del juego.

La prueba se limitó al panel interior desplegado. El paquete original era `org.doom.port`; el clon se instaló con identificador `org.doom.port.magicv2adaptive` y nombre visible `DOOM Mobile Adaptive`, conservando el original separado.

## Problema observado

La ventana Android cubría el área interior en paisaje: `2344×2156` (`1.0872:1`). Las franjas negras estaban dentro de la imagen de juego. En el código de v0.4.9, la opción de aspecto `Auto` conserva una salida mínima de `960×720` (4:3) para pantallas estrechas. Para este panel, esa cota producía una imagen demasiado ancha y dejaba bandas arriba/abajo.

El parser nativo ya acepta `DM_DOOM_ASPECT` con `auto`, ratios explícitos (`a:b`) o ancho de salida. En modo Auto, el ancho se calcula desde el tamaño de pantalla comunicado al motor y se restringe a un mínimo de 960. Un ratio explícito puede bajar hasta 720 de ancho, que es el límite documentado por el código de esa versión.

## Cambio del clon

Se cambió solo el wrapper Java. Cuando la preferencia de aspecto permanece en Auto y el rectángulo actual de `WindowMetrics` es más estrecho que 4:3, el clon normaliza la orientación y envía ese ratio a la variable que el motor existente ya lee. En las demás proporciones y preferencias, sigue el comportamiento original de Auto/16:9/4:3.

Para el Magic V2 horizontal:

```text
ratio de ventana = 2344:2156 ≈ 1.0872:1
ancho a altura base 720 = round(720 × 2344 / 2156) = 783 px
alineación del renderer al múltiplo de 16 = 784×720
```

El renderer mantiene el aspecto de salida cerca del ratio del panel y la superficie lo escala al tamaño visible. La diferencia por alineación a 16 píxeles es de aproximadamente 0.16 %. Esto evita depender del mínimo 4:3 de Auto. La modificación no cambia `wm size`, densidad, orientación global ni el APK original.

La construcción usó fuente del tag v0.4.9 y la biblioteca nativa arm64 de la build instalada, de modo que la prueba aisló el cambio del wrapper sin volver a compilar/reemplazar el motor nativo. Se generó un APK de debug independiente con Gradle 9.6.0 y Android SDK 36. El código de adaptación del clon y los binarios resultantes no se publican aquí; esta receta describe el método, no afirma que el tag upstream incluya el cambio.

## Datos y lanzamiento

El port espera su carpeta `Download/DOOM Mobile` con los directorios `dm` y `romfs` documentados por el upstream. Conserva esa carpeta fuente; no la metas en el APK ni la subas a Git. En un clon, confirma cómo resuelve su `getExternalFilesDir`, almacenamiento compartido y permisos antes de lanzar. No copies saves privados del original como supuesto: los directorios internos y preferencias pueden quedar aislados por paquete.

Durante una apertura en frío, esta ejecución mostró los videos/logos de inicio y el proceso seguía vivo. Tras la secuencia apareció `Load from checkpoint`; el control A visible recibió un evento de entrada A enviado por ADB y el port cargó una escena de gameplay. Por tanto, en esa sesión no se confirmó el cierre que se percibía durante los videos. Si el PID desaparece en otra versión/sesión, guarda tombstone, `logcat -b crash` y logs del propio port antes de cambiar drivers o borrar datos.

## Resultado y estado de evidencia

- **Ventana:** actividad en el rectángulo interior `2344×2156` según Android.
- **Gameplay:** proceso del clon vivo y captura del juego cubriendo el panel interior; el usuario confirmó que ya lo veía a pantalla completa.
- **Entrada:** un evento A de ADB avanzó el menú de checkpoint. La prueba no cubrió toques físicos ni toda la distribución de controles.
- **FPS:** la captura mostraba 60 en el contador del port en ese instante. No hay serie de frametime o promedio; no equivale a 60 FPS sostenidos.
- **Driver:** `Turnip Amaral 26.3.0-devel v4.6.1.4` se importó y quedó seleccionado en preferencias del clon. No se capturó el estado del renderer del mismo proceso ni un log Vulkan; por eso driver activo queda **no confirmado**.
- **Original:** paquete original separado; el APK del clon se guardó localmente en Descargas del usuario. No se publicaron artefactos.
- **Reversión:** cerrar/desinstalar únicamente `org.doom.port.magicv2adaptive` elimina el clon. Mantén `org.doom.port` y los datos fuente del juego.

## Seguimiento gráfico: modelos animados negros en v0.4.18-test1

Este defecto es independiente del letterbox documentado arriba, que correspondía al tag v0.4.9. No reutilices el parche de aspecto como arreglo de materiales o geometría.

El registro del upstream para [`v0.4.18-test1` en el commit `085d0cb0`](https://github.com/Desm0nt/doom-port/blob/085d0cb0b3796ddbfa33c64b6d00776387ad4eba/docs/doom/BUGS_AND_FIXES.md) describe modelos animados negros en una ruta de Adreno 740. El cambio de clipping no resolvió por sí solo los cuerpos negros; el registro propone investigar índices dinámicos del UBO de huesos. Un ensayo con `DM_GFX_BONES_SSBO=1` mostró cuerpos/enemigos normales en un dispositivo, pero produjo flicker de suelo, una puerta ausente y un arma oscura. El registro deja `DM_VK_ROBUST=0` como el siguiente experimento, no como una reparación confirmada.

En este proyecto se preparó un clon separado para diagnóstico gráfico con una variante nativa de prueba y bibliotecas del loader. La confirmación más reciente del usuario es que los gráficos ya se ven corregidos. No se conservó en esta sesión una captura comparable final ni un log del mismo proceso que demuestre el driver activo o aísle qué cambio causó la mejora. Por tanto, el resultado queda como **confirmado por el usuario; causalidad técnica y renderer activo sin verificación independiente**. No presentes `robustBufferAccess=VK_FALSE`, SSBO, un driver específico ni la presencia de hooks como causa probada.

Al continuar el caso, conserva el APK original y prueba un solo cambio por clon; captura el mismo encuadre con el mismo checkpoint y compara una segunda escena que contenga suelo, puertas, armas, sombras y modelos animados. Consulta el [flujo completo de diagnóstico gráfico](diagnostico-de-errores-graficos.md) y usa el [auditor estático del APK](../scripts/audit_android_renderer_apk.py) solo para inspección de paquete. La auditoría no demuestra carga en runtime.

## Reproducción para otra IA

1. Reidentifica el teléfono, serial ADB, display interior, postura, bounds y versión del port.
2. Obtén el código de la misma versión exacta. Revisa `dm_doom_wide_w`, `auto_width`, los límites de `DM_DOOM_ASPECT`, el wrapper Java y el momento anterior a `System.loadLibrary`/`nativeStart`.
3. Reproduce el cuadro inicial en una escena conocida; registra PID/actividad y confirma que la ventana ya cubre el panel.
4. Calcula la dimensión desde `WindowMetrics` en el wrapper, solo para Auto bajo 4:3. Respeta el parser, sus clamps y su alineación. No edites offsets de `libdm.so` sin una necesidad medida.
5. Cambia package ID y etiqueta del clon. Valida manifiesto, ABI, firma y biblioteca incluida antes de instalarlo junto al original.
6. Confirma la ruta de juego y permisos que usa el clon sin mover/eliminar el origen ni pisar saves.
7. Espera la secuencia de inicio observando proceso y pantalla. Llega a gameplay; captura el ID de display interior explícito.
8. Repite el mismo tipo de escena y prueba input. Registra por separado aspecto, FPS instantáneo/serie, driver seleccionado/cargado y cualquier crash.
9. Conserva APK/screenshot/logs localmente. Publica solo el código/documentación original y resultados redactados.

## Fuentes

- [Código upstream v0.4.9](https://github.com/Desm0nt/doom-port/tree/v0.4.9)
- [Guía de instalación upstream](https://github.com/Desm0nt/doom-port/blob/v0.4.9/docs/INSTALL.md)
- [Android: hacer una app fold-aware](https://developer.android.com/develop/adaptive-apps/guides/foldables/make-your-app-fold-aware)
- [`SKILL.md` del proyecto](../SKILL.md)
