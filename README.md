# Elysium Vanguard Android Adaptive Engineering

Métodos reproducibles para diagnosticar y adaptar juegos, ports y reproductores de video en Android plegables. El equipo de referencia es el HONOR Magic V2, con prioridad en el panel interior desplegado.

El repositorio reúne casos de *Resident Evil 7*, *Halo 2*, *Sekiro*, *Left 4 Dead 2*, *Need for Speed: Most Wanted* (2012), *Just Cause 2*, *PES 6*, *Gears of War* en un port Android derivado de Xenia, *God of War III*, *Zelda: Breath of the Wild Recompiled*, clones de YouTube y tareas relacionadas con USB y almacenamiento. Distingue entre cambios configurados, APKs instalados, comportamiento medido y resultados reportados por el usuario.

## Qué contiene

- Un método de diagnóstico por capas para actividad, ventana, superficie, viewport, controles y contenido.
- Una guía específica para puertos recompilados que colocan el letterbox dentro del presentador nativo, incluido el significado real de `present_letterbox=false`.
- Procedimientos para crear clones Android firmados por separado, importar datos propios y preservar la app original.
- Guías para mapear entrada táctil después de un cambio de escala o recorte.
- Separación entre FPS del juego, límite configurado, refresco del panel y cuadros generados.
- Casos de estudio en formato técnico con resultados, límites y evidencia disponible.
- Un parche Smali acotado para el caso concreto de RE7; no es un adaptador universal.

## Alcance y derechos

Este repositorio publica documentación y herramientas originales. **No contiene APKs, ISOs, ejecutables de juegos, saves, drivers, `Lossless.dll`, claves de firma ni capturas con contenido protegido.** Cada persona debe usar copias que tenga derecho a modificar y respetar las licencias del juego, el port y las herramientas.

La adaptación de escala siempre tiene un costo cuando la imagen y el panel tienen relaciones distintas: `Fit` conserva el cuadro completo y deja espacio libre; `Cover` ocupa el área pero recorta; `Stretch` ocupa el área y deforma. El método registra cuál se usó y verifica la entrada táctil por separado.

## Documentación

- [Informe técnico de casos y método reproducible](skills/android-foldable-game-media/references/case-study.md)
- [Skill para agentes de IA](skills/android-foldable-game-media/SKILL.md)
- [Guía de letterbox en ports Xenia/ReX](docs/ports-recompilados-letterbox.md)
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
