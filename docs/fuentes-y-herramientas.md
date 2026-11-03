# Fuentes y herramientas

## Herramientas observadas en el caso

- Apktool 3.0.3 local: decodificación y reconstrucción del APK.
- ADB: consulta del paquete, configuración privada del contenedor, procesos, actividad, logs y capturas.
- REA CLI 6.5.0: soporte para inspección y evidencia de APK/dispositivo; depende del ADB que ya tenga el operador.
- FFmpeg: conversión puntual de recursos cuyo sufijo decía .png pero cuya firma no era PNG.
- Android SDK Build Tools: necesarios para alinear y firmar una reconstrucción local.
- `aapt` y `apksigner`: comprobar identificador de paquete, versión y certificado antes de instalar un clon.
- Android NDK 28.2.13676358 y GLES/EGL: cargador nativo experimental del caso PES 6; su ejecución no quedó confirmada por logs después del último update.
- Morphe Desktop y el bundle de patches Anddea/ReVanced Extended: receta del clon de YouTube registrada en el informe de casos. Verifica versiones nuevas antes de repetirla.

REA complementa ADB; no reemplaza ni administra el transporte del dispositivo. Sus operaciones de captura y lectura pueden ser de solo lectura, mientras que instalar, iniciar, detener y desinstalar una app cambian estado. Revisa la documentación de cada operación.

## Referencias externas

- [REA: análisis de dispositivos Android por ADB](https://github.com/morluto/rea/blob/main/docs/adb-device-analysis.md)
- [REA: inspección estática de APK Android](https://github.com/morluto/rea/blob/main/docs/android-analysis.md)
- [Apktool: documentación oficial](https://apktool.org/docs/)
- [LSFG-Android: release 0.1.2](https://github.com/FrankBarretta/LSFG-Android/releases/tag/0.1.2)
- [LSFG-Android: repositorio y README](https://github.com/FrankBarretta/LSFG-Android)
- [Morphe Desktop: documentación CLI](https://github.com/MorpheApp/morphe-desktop/blob/main/docs/documentation.md)
- [Anddea/ReVanced Extended: patches](https://github.com/anddea/revanced-patches)
- [Halo 2 Android port indicado por el usuario](https://github.com/Ayanokoji989/Halo-2)
- [zFitness: port gow3_android](https://github.com/zFitness/gow3_android)
- [Xenia Canary: opciones de presentación](https://github.com/xenia-canary/xenia-canary/wiki/Options#black-bars-letterboxingpillarboxing)
- [Xenia Canary: patches de Gears of War](https://github.com/xenia-canary/game-patches/blob/main/patches/4D5307D5%20-%20Gears%20of%20War.patch.toml)
- [Android: MediaProjection](https://developer.android.com/media/grow/media-projection)
- [Android: hacer una app fold-aware](https://developer.android.com/develop/adaptive-apps/guides/foldables/make-your-app-fold-aware)

## Usar REA con criterio

Antes de una sesión, vuelve a descubrir serial, modelo, versión Android, actividad, display y paquetes. Guarda la salida como evidencia local fuera del repo. No publiques seriales ADB, logs completos, dumps del dispositivo, rutas privadas, listas de archivos personales o identificadores de cuenta.
