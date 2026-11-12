# Elysium Vanguard Android Adaptive Engineering

Métodos reproducibles para diagnosticar y adaptar juegos, ports y reproductores de video en Android plegables. El equipo de referencia es el HONOR Magic V2, con prioridad en el panel interior desplegado.

El repositorio reúne casos de *Resident Evil 7*, *Halo 2*, *Sekiro*, *Left 4 Dead 2*, *Need for Speed: Most Wanted* (2012), *Just Cause 2*, *PES 6*, *Gears of War* en un port Android derivado de Xenia, *God of War II* en un wrapper ARMSX2/Catonix, *God of War III*, *Zelda: Breath of the Wild Recompiled*, DOOM Mobile, *Dark Souls: Remastered* en un presenter Vulkan nativo, clones de YouTube, un análisis no verificado de una publicación sobre *The Last of Us Remastered* para Android y tareas de USB/almacenamiento. Distingue entre cambios configurados, APKs instalados, comportamiento medido y resultados reportados por el usuario.

## Qué contiene

- Un método de diagnóstico por capas para actividad, ventana, superficie, viewport, controles y contenido.
- Un enrutador para agentes de IA que selecciona el flujo correcto según arquitectura y síntoma, con un registro estructurado de evidencia y puertas explícitas para considerar un caso terminado.
- Una guía específica para puertos recompilados que colocan el letterbox dentro del presentador nativo, incluido el significado real de `present_letterbox=false`.
- Un procedimiento versionado para diagnosticar barras en emuladores PS2 Android y elegir el ajuste de aspecto con su alcance, persistencia y costo geométrico.
- Un caso de presenter Vulkan nativo que limita `Stretch` a un title ID, sincroniza el rectángulo táctil con el blit y distingue la pantalla completa de FOV, driver activo y FPS sostenidos.
- Procedimientos para crear clones Android firmados por separado, importar datos propios y preservar la app original.
- Guías para mapear entrada táctil después de un cambio de escala o recorte.
- Separación entre FPS del juego, límite configurado, refresco del panel y cuadros generados.
- Una guía de diagnóstico gráfico reproducible para modelos negros, geometría ausente, texturas erróneas, flicker y fallos de renderer; incluye evidencia A/B y límites para comprobar drivers.
- Un auditor estático en Python estándar para revisar renderer/hooks, ABI ELF y SHA-256 dentro de APKs sin extraerlos. La salida no afirma que un driver se haya cargado.
- Casos de estudio en formato técnico con resultados, límites y evidencia disponible.
- Una receta específica de DOOM Mobile v0.4.9: ratio dinámico desde `WindowMetrics` para quitar el letterbox 4:3 en el panel interior, con límite de prueba del driver y de FPS.
- Un parche Smali acotado para el caso concreto de RE7; no es un adaptador universal.

Los agentes que trabajen en este checkout deben comenzar por [AGENTS.md](AGENTS.md), que enruta automáticamente a la skill y a la matriz apropiadas.

La carpeta [`skills/android-foldable-game-media/`](skills/android-foldable-game-media/) también es un paquete importable de skill: incluye su `SKILL.md`, referencias, guía de errores gráficos, plantillas y auditor APK dentro de la misma carpeta. Sus referencias externas usan enlaces públicos al repo.

## Alcance y derechos

Este repositorio publica documentación y herramientas originales. **No contiene APKs, ISOs, ejecutables de juegos, saves, drivers, `Lossless.dll`, claves de firma ni capturas con contenido protegido.** Cada persona debe usar copias que tenga derecho a modificar y respetar las licencias del juego, el port y las herramientas.

La adaptación de escala siempre tiene un costo cuando la imagen y el panel tienen relaciones distintas: `Fit` conserva el cuadro completo y deja espacio libre; `Cover` ocupa el área pero recorta; `Stretch` ocupa el área y deforma. El método registra cuál se usó y verifica la entrada táctil por separado.

## Documentación

- [Informe técnico de casos y método reproducible](skills/android-foldable-game-media/references/case-study.md)
- [Skill para agentes de IA](skills/android-foldable-game-media/SKILL.md)
- [Matriz de decisión por arquitectura](skills/android-foldable-game-media/references/decision-matrix.md)
- [Registro YAML de evidencia](templates/evidence-record.yaml)
- [Plantilla de informe de sesión](templates/run-report.md)
- [Guía de letterbox en ports Xenia/ReX](docs/ports-recompilados-letterbox.md)
- [Caso de Dark Souls Remastered en el presenter Vulkan del Magic V2](docs/dark-souls-remastered-magic-v2.md)
- [Caso de God of War II en ARMSX2/Catonix](docs/god-of-war-ii-armsx2-magic-v2.md)
- [Runbook de aspecto para emuladores PS2 Android](skills/android-foldable-game-media/references/ps2-emulator-aspect-ratio.md)
- [Caso técnico DOOM Mobile en Magic V2](docs/doom-mobile-magic-v2.md)
- [Diagnóstico reproducible de errores gráficos](docs/diagnostico-de-errores-graficos.md)
- [Auditor estático de renderer/hooks en APK](tools/audit_android_renderer_apk.py)
- [Arquitectura y diagnóstico de RE7](docs/arquitectura-y-diagnostico.md)
- [Reproducción desde un APK propio](docs/reproduccion.md)
- [Experimentos y evidencia de RE7](docs/resultados-y-evidencia.md)
- [Evaluación de LSFG-Android](docs/generacion-de-cuadros.md)
- [Fuentes y herramientas](docs/fuentes-y-herramientas.md)
- [Distribución y límites](docs/distribucion-y-limites.md)

## Caso de RE7

El parche de RE7 cambia una transformación de vista de `contain` a `cover` y alinea el mapeo táctil de esa versión del port. El script [tools/patch_viewport.py](tools/patch_viewport.py) comprueba sus anclajes y se detiene si no encuentra la estructura esperada.

~~~mermaid
flowchart LR
    A[APK autorizado] --> B[Identificar actividad, superficie y viewport]
    B --> C[Elegir Fit, Cover o Stretch]
    C --> D[Aplicar cambio aislado en un clon]
    D --> E[Transformar entrada táctil de forma coherente]
    E --> F[Comparar la misma escena y revisar logs]
    F --> G[Registrar evidencia y límites]
~~~

Para reproducir el caso RE7, sigue [la guía específica](docs/reproduccion.md). Para los demás títulos, primero lee el informe de casos: sus loaders, datos, drivers y límites no son intercambiables.
