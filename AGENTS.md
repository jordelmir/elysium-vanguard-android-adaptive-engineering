# Instrucciones para agentes de IA

Este repositorio es una guía operativa de ingeniería para juegos, ports y apps multimedia en Android plegables. Cuando una tarea trate sobre instalación/lanzamiento de juegos, datos ISO/PKG/OBB, franjas negras, pantalla adaptativa, APK clon, controles táctiles, drivers Vulkan, FPS/frametime, Lossless/frame generation, reproducción de video o limpieza de almacenamiento:

1. Lee [`skills/android-foldable-game-media/SKILL.md`](skills/android-foldable-game-media/SKILL.md) antes de proponer o modificar una solución.
2. Lee [`skills/android-foldable-game-media/references/decision-matrix.md`](skills/android-foldable-game-media/references/decision-matrix.md) para seleccionar la capa y arquitectura.
3. Consulta el caso relevante en [`skills/android-foldable-game-media/references/case-study.md`](skills/android-foldable-game-media/references/case-study.md). Los valores de un juego/build no se trasladan a otro sin revisar fuente y runtime.
4. Si el caso coincide con un documento especializado, úsalo junto a la skill: por ejemplo [`docs/doom-mobile-magic-v2.md`](docs/doom-mobile-magic-v2.md) o [`docs/ports-recompilados-letterbox.md`](docs/ports-recompilados-letterbox.md).
5. Separa configuración, instalación, proceso iniciado, escena reproducida, función confirmada en runtime, lectura puntual y resultado sostenido. No infieras un crash, driver activo, FPS estable o pantalla completa a partir de un único indicador.
6. Conserva originales, saves, datos y trabajo ajeno. No pongas APKs, bibliotecas de juego, datos, drivers, claves, logs privados ni capturas con contenido protegido en Git.
7. Usa las plantillas en [`templates/`](templates/) para reportar resultados y límites.

Para cambios documentales, actualiza los enlaces cruzados y conserva la cronología/evidencia de los casos. Declara explícitamente si un caso no fue reproducido o si el usuario fue quien confirmó el resultado.
