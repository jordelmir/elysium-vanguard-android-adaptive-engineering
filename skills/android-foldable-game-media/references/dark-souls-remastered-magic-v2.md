# Dark Souls Remastered en Magic V2: pantalla completa desde el presenter Vulkan

## Propósito y alcance

Este caso registra un ajuste por título para el port Android de *Dark Souls: Remastered* basado en nx2android. El objetivo fue llenar el panel interior desplegado del HONOR Magic V2 durante una escena de juego, manteniendo visible el cuadro completo y sin sustituir la instalación original. La evidencia corresponde a una compilación clon local y a una sesión concreta; no es una configuración universal para otros títulos ni otros ports.

La solución cambia el destino de presentación de Vulkan a toda la superficie. Es un modo `Stretch`: evita bandas y no recorta el cuadro fuente, pero deforma su relación de aspecto. Para mantener las proporciones sin bandas se necesita un viewport/FOV que el propio juego amplíe o una decisión explícita de recorte; estirar no crea campo de visión adicional.

## Identificación y evidencia

| Punto | Observación de esta sesión |
|---|---|
| Dispositivo y alcance | HONOR Magic V2, panel interior desplegado, juego en orientación horizontal |
| Port/base examinada | nx2android; fuente inspeccionada en el commit [`e9bd2b7`](https://github.com/shirai91/nx2android/tree/e9bd2b764608facf841e39292d868ee657eaf634) |
| Juego | *Dark Souls: Remastered*, title ID `01004AB00A260000` usado por el build del port |
| Base Android de prueba | Clon v1.0.3 (versionCode 5), ABI `arm64-v8a`; el original se dejó aparte |
| Cuadro reportado por el presenter | `1920×1080` |
| Log de la misma sesión | `full-window stretch enabled: source=1920x1080 target=2156x1983` |
| Captura final del display | `2344×2156`; la escena cubrió el panel sin bandas ni una segunda imagen de fondo |
| Ventana Android | Bounds observados de `2344×2156`; el área activa ya ocupaba el panel |
| Resultado | Clon actualizado e iniciado; el usuario confirmó que la pantalla completa ya funcionaba |

Las medidas de ventana, superficie Vulkan y captura pertenecen a capas diferentes y no deben tratarse como si fueran una única resolución. En particular, el target `2156×1983` procede del log del presenter y la captura final mide `2344×2156` después de la composición/orientación del display.

### Fuerza y límites de la evidencia

- El log `[display] full-window stretch enabled` salió del proceso del juego y reportó dimensiones de origen y destino. La captura del display activo mostró la escena ocupando el panel. Juntas demuestran que el modo compilado se ejecutó y que la escena observada no tenía bandas.
- El usuario confirmó el resultado visual. No se conservó la captura del juego dentro del repositorio porque contiene material protegido.
- El rectángulo que usa el presenter para dibujar también se publica para el transformador de entrada táctil. Esto hace que el cálculo de entrada siga el rectángulo completo; no se hizo una prueba física completa de controles en bordes después del cambio, así que no se afirma que todo el tacto quedara validado.
- La captura mostró una lectura cercana a 29 FPS. Es un valor instantáneo; no demuestra una tasa estable, un límite de 30 sostenido ni 60 FPS.
- El log del loader informó que no pudo cargar el driver Turnip personalizado y que continuó con el driver del sistema. La pantalla completa se verificó con ese fallback; este caso no demuestra el uso activo de V37/V38/Amaral.
- No se integró Lossless Scaling ni generación de cuadros. No se cambió la configuración de calidad o el límite de FPS como parte de este ajuste de presentación.
- Se actualizó el clon con su identidad/firma existente. El paquete original permaneció instalado y sin reemplazo; APK, key, datos del juego, capturas y logs se excluyeron del repositorio.

## Diagnóstico por capas

1. **Display y actividad.** Se identificó el display interior activo y se consultaron bounds de la ventana NativeActivity. La ventana Android ya cubría el rectángulo completo `2344×2156`; por ello, cambiar immersive flags, `wm size` o densidad del sistema no abordaba la franja observada.
2. **Superficie y cuadro del juego.** El presenter recibió un cuadro de juego `1920×1080` (16:9) y, en su modo normal, lo ajustaba uniformemente dentro de una superficie casi cuadrada. Esa operación centrada conserva proporción y deja bandas.
3. **Presentación.** La función `present_window()` de nx2android calcula un rectángulo centrado de tipo `Fit`. El arreglo sustituyó el rectángulo de destino por el rectángulo completo de la superficie para este title ID.
4. **Entrada.** El mismo rectángulo normalizado publicado por el presenter se consulta en `front_android.c` al transformar coordenadas. La modificación mantuvo este canal sincronizado con el rectángulo de imagen; aun así, el tacto se considera pendiente de prueba manual.
5. **Prueba visual.** Se volvió a cargar la escena de juego, se verificó el log del mismo proceso y se capturó explícitamente el display interior. La captura final no incluyó la duplicación de fondo que apareció en una iteración previa.

Android puede aplicar políticas de orientación y compatibilidad en pantallas grandes según la versión y el target SDK. En Android 16, los cambios para apps que apuntan a API 36 en displays de al menos `sw600dp` tienen una excepción para juegos identificados por `android:appCategory`; no atribuyas el layout de este port a una sola política sin verificar target, categoría y bounds efectivos. Un manifiesto con `screenOrientation` no sustituye la lectura de actividad, ventana y superficie. Consulta la [documentación de comportamiento de Android 16 en pantallas grandes](https://developer.android.com/about/versions/16/behavior-changes-16) y mide el caso real.

## Cambio de presentación

La compilación del clon añadió una definición específica para el title ID de Dark Souls. En el presenter, el modo normal calcula `Fit`; el modo de pantalla completa fuerza el origen de destino a `(0, 0)` y su ancho/alto a la superficie Vulkan. Después, `vk_pic_set()` publica ese mismo rectángulo normalizado, que es la referencia consumida por la transformación táctil de `front_android.c`.

Pseudocódigo del cambio conceptual:

```text
destination = centered_fit(source_frame, vulkan_surface)
if full_window_for_this_title:
    destination = entire_vulkan_surface
publish_normalized_picture_rect(destination)  # renderer y transformador táctil
blit_complete_frame(source_frame, destination)
```

El build activó `DM_GAME_FULL_WINDOW` únicamente cuando `build.py` compila el title ID `01004AB00A260000`. La variable de entorno `DM_VK_FULL_WINDOW` de esa fuente permite que el port tenga un override de runtime si su configuración lo expone. No cambies el valor global por defecto ni reutilices este ID/flag para otro juego sin leer su flujo de presentación.

La compilación de esta sesión usó NDK r29: 192 fuentes compilaron y ninguna falló; `libdmhost.so` quedó en aproximadamente 1.9 MB después de strip. Forma general del comando, ajustando las rutas al checkout local:

```bash
python3 nxnative/dm/android/build.py \
  --game 01004AB00A260000 --lib --release \
  --ndk "$ANDROID_NDK_DIR" --out "$DSR_BUILD_OUT" --jobs 10
```

Se reemplazó solo `lib/arm64-v8a/libdmhost.so` dentro del clon decodificado, se reconstruyó y alineó el APK, y se firmó con la misma clave del clon instalado. `apksigner verify --verbose` pasó y la firma coincidió con la app clon existente. Luego `adb install -r` devolvió éxito sin borrar los datos del clon. La clave y el artefacto firmado son locales y no se suben a GitHub.

### No apilar un fondo duplicado

Una iteración anterior ampliaba primero el cuadro para rellenar la superficie y luego dibujaba encima el cuadro original con aspecto conservado. La imagen repetida se percibía como contenido duplicado y no solucionaba el objetivo de mostrar una sola imagen a pantalla completa. En el resultado final se dejó desactivado ese modo de fondo y se presentó un único cuadro estirado. El relleno ambiental puede servir como opción estética cuando el cuadro original permanece en `Fit`, pero no debe dibujarse como una segunda copia sin una elección explícita y una prueba visual.

## Receta reproducible para otra IA

1. **Fija la build.** Identifica APK, paquete, firma, port, commit/tag, ABI, GPU, display, orientación y title ID. Conserva el original, sus saves y un clon aparte; no limpies datos para hacer el cambio.
2. **Obtén una línea base.** Captura una escena reproducible del display correcto. Registra bounds de actividad/ventana, superficie Vulkan, dimensiones del cuadro fuente, viewport y logs del proceso. Si hay varios displays, pide el ID explícito a `screencap` y verifica dimensiones/cabecera del PNG.
3. **Atribuye la franja.** Si ventana y superficie ya llenan el panel y el cuadro es menor o centrado, inspecciona el presenter final y su transformación de entrada. No cambies la resolución global ni atribuyas el problema al driver sin evidencia.
4. **Selecciona la política.** Elige `Fit` para proporción y cuadro completo con bandas; `Cover` para proporción sin bandas y con recorte; `Stretch` para mostrar todo el cuadro en toda la superficie con deformación; o viewport/FOV del motor si existe soporte real para el nuevo ratio.
5. **Aísla el cambio.** Hazlo por title ID o perfil de juego, nunca como default indiscriminado. Si escalas o recortas, sincroniza el rectángulo usado por input con la imagen que ve el jugador. No añadas simultáneamente un fondo duplicado.
6. **Construye y actualiza solo el clon.** Usa el NDK/toolchain y el método de empaquetado que requiere esa build. Conserva package ID y certificado del clon para una actualización en sitio; confirma `apksigner verify`, instala con `adb install -r` y no reemplaces ni desinstales el original.
7. **Verifica el mismo proceso.** Confirma actividad NativeActivity, log del presenter con source/destination, captura del display activo en una escena, y controles en centro y cerca de los bordes. Repite título/menú y gameplay antes de afirmar que ambos son adaptativos.
8. **Registra resultados separados.** Escribe qué modo de escala quedó activo, si se instaló, qué escena se renderizó, si el tacto se probó, lectura instantánea vs serie de FPS, renderer/driver activo y cualquier regresión. Si un driver personalizado falla, anota el fallback del sistema sin atribuirle la pantalla completa.
9. **Rollback.** Desactiva el override de pantalla completa en el clon o reinstala su APK anterior firmado con la misma clave. El original y sus datos quedan fuera del ciclo de rollback.

### Enlaces al código inspeccionado

- [Presenter Vulkan `gfx_vk_present.c` en nx2android](https://github.com/shirai91/nx2android/blob/e9bd2b764608facf841e39292d868ee657eaf634/nxnative/dm/android/gfx_vk_present.c): destino del blit, `DM_VK_FULL_WINDOW` y publicación del rectángulo.
- [Transformación Android en `front_android.c`](https://github.com/shirai91/nx2android/blob/e9bd2b764608facf841e39292d868ee657eaf634/nxnative/dm/android/front_android.c): consumo de `dm_picture_rect()` para coordenadas táctiles.
- [Build Android `build.py`](https://github.com/shirai91/nx2android/blob/e9bd2b764608facf841e39292d868ee657eaf634/nxnative/dm/android/build.py): lugar para mantener definiciones específicas del juego.

Las URLs apuntan a la versión inspeccionada para que otra persona pueda contrastar el diseño. Este repositorio solo enlaza el upstream: no contiene ni redistribuye su código, el APK, bibliotecas, assets, saves o datos del juego. Revisa la licencia upstream antes de reutilizar código.

## Fuentes adicionales

- [Android 16: cambios de comportamiento para pantallas grandes](https://developer.android.com/about/versions/16/behavior-changes-16).
- [Matriz de decisión de la skill](decision-matrix.md).
- [Informe de casos y límites de evidencia](case-study.md).
