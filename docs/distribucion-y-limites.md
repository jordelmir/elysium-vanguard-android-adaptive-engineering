# Distribución, derechos y límites

Este repositorio contiene documentación original, un script acotado que modifica dos anclajes de Smali después de decodificar un APK y un auditor estático que inventaría bibliotecas renderer/hooks, ABI ELF y hashes en un APK sin extraerlo. También documenta cambios de configuración de presentación para ports recompilados, pero no distribuye APK ni bibliotecas nativas de esos ports. No incluye el juego ni su ejecutable, archivos de licencia o emulación, APK original o modificado, archivos OBB/PCK, partidas, driver Turnip, `Lossless.dll`, shaders, claves de firma, código cargador del clon PES 6, logs completos ni capturas del juego.

Los juegos, ports y sus marcas pertenecen a sus respectivos titulares. Este repositorio no afirma afiliación ni autorización comercial. Cada usuario es responsable de usar un APK y datos que tenga derecho a modificar, y de cumplir las licencias del port, del juego, de las herramientas y del generador de cuadros. La licencia de este repositorio cubre únicamente los documentos, diagramas y scripts originales aquí publicados.

La app LSFG-Android y su release mantienen sus propios términos. Lossless.dll es un componente de terceros que debe obtenerse legítimamente; no se copia a este proyecto. El driver V38 parcheado también permanece fuera del repo.

Al encuadrar una imagen en una pantalla con otra proporción hay tres opciones: conservar proporción y aceptar bandas (`Fit`), conservar proporción y recortar (`Cover`), o llenar sin recortar deformando (`Stretch`). Un viewport y FOV adaptados pueden mostrar otra porción del mundo si el motor lo admite, pero requieren un patch específico y verificación del juego. No describas un estiramiento como adaptación sin pérdida.

La publicación describe casos de un dispositivo y versiones concretas de ports y aplicaciones. No garantiza compatibilidad con otras versiones de APK, GPU, pantallas plegables, drivers, firmantes ni capas de compatibilidad. Los valores de entorno y cvars del caso Xenia/ReX dependen de su wrapper; los valores binarios no se deben trasladar sin el hash exacto de la biblioteca. Los resultados reportados por el usuario no se convierten en mediciones hasta contar con capturas/logs de runtime comparables.

El auditor de APK no ejecuta el contenido y su resultado no prueba selección, carga ni uso de un driver; esa evidencia debe proceder del mismo proceso del juego.

La skill importable mantiene copias portables de la guía gráfica, el auditor, plantillas y guías relevantes dentro de `skills/android-foldable-game-media/`. Al modificar sus fuentes canónicas en `docs/`, `tools/` o `templates/`, actualiza también esas copias antes de publicar una versión nueva del paquete.
