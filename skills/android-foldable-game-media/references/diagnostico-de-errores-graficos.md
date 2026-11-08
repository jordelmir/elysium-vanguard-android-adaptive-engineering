# Diagnóstico reproducible de errores gráficos en juegos Android

## Objetivo y límites

Esta guía ayuda a separar defectos del encuadre de fallas del renderer y a evaluar correcciones en ports Android, recompilaciones, emuladores y capas de compatibilidad. No propone un driver, flag Vulkan ni parche universal. Una versión de APK, GPU, API gráfica y escena forman una combinación concreta; cualquier ajuste debe probarse en un clon reversible.

No publiques APK, bibliotecas del juego, drivers, saves, llaves de firma, logs privados ni capturas con contenido protegido. Registra hashes y evidencia de forma local; en Git conserva el método y resultados redactados.

## Clasifica lo que se ve

| Síntoma | Capa inicial que conviene investigar | Indicios y límites |
|---|---|---|
| Franjas, imagen recortada o estirada | ventana, superficie, viewport, presentador o cámara/FOV | Compara sus rectángulos. No atribuyas una banda a Vulkan sin medir antes el cuadro. |
| Pantalla o escena completa negra | carga del juego, swapchain/superficie, renderer, shaders o crash | Distingue cuadro negro con proceso vivo de proceso terminado; conserva el log del instante. |
| Modelos concretos negros con el escenario visible | datos de vértices/skinning, shader, descriptor/buffer, material o ruta del driver | Comprueba si la silueta y animación siguen presentes; “negro” por sí solo no identifica la causa. |
| Geometría ausente, agujeros o triángulos que faltan | índices, culling, clipping, sincronización, buffers o shader | Busca si afecta a objetos/ángulos concretos y si cambia al rotar cámara. |
| Texturas negras, rosas o incorrectas | carga de recursos, formato, mipmaps, descriptor/sampler o shader | Separa un recurso no cargado de una textura cargada que se muestrea mal. |
| Parpadeo o imagen corrupta | sincronización, buffers, carrera CPU/GPU, shader, memoria o driver | Graba una secuencia breve y prueba otra escena; una captura aislada puede ocultar intermitencia. |
| Fallo al entrar a gameplay | transición, asignación de recursos, renderer/driver o datos | Guarda PID, `logcat` de crash/tombstone y log propio del port antes de cambiar opciones. |

La matriz y el flujo para distinguir ventana, superficie y cuadro están en la [matriz de decisión](decision-matrix.md).

## Flujo de trabajo

### 1. Fija un baseline que se pueda repetir

Anota fecha, dispositivo y GPU, Android/API, arquitectura ABI, paquete y versión exacta del APK, versión/tag/commit del port, backend gráfico, display/postura y escena. Registra cómo llegar al mismo punto sin avanzar o sobrescribir una partida. Captura localmente:

- la escena afectada con el mismo ángulo y ajustes;
- si el proceso sigue vivo y qué actividad está al frente;
- logs del juego y de la capa gráfica alrededor de esa escena;
- driver archivado, importado, seleccionado, cargado y renderer confirmado, cada uno por separado;
- hash SHA-256 del APK y de las bibliotecas locales que se van a comparar.

No cambies a la vez driver, resolución, calidad, shader y viewport. Conserva el APK/configuración anterior y los datos de juego.

### 2. Confirma la arquitectura y busca la evidencia de esa build

Lee el README, el código y el registro de cambios de la versión exacta. Distingue un port Android nativo de una recompilación, emulador, wrapper o juego que corre dentro de una capa Windows/Linux: cada uno tiene un límite distinto donde puede nacer el defecto. Busca la ruta concreta (shader, recurso, renderer, loader, superficie) antes de proponer una edición binaria.

Prefiere issues y commits primarios del proyecto con permalink inmutable. Una hipótesis de upstream es pista para un experimento, no una explicación confirmada para otro build o teléfono.

### 3. Valida el APK y el loader sin confundir presencia con uso

Para un port DOOM que use la integración AdrenoTools, el preflight local de esta skill inspecciona las bibliotecas del APK sin extraerlas:

```sh
python3 scripts/audit_android_renderer_apk.py /ruta/local/al-clon.apk
```

El informe revisa `libdm.so`, las cuatro bibliotecas hook esperadas, ABI/cabecera ELF y SHA-256. `--skip-hooks` omite la comprobación de esos hooks si el port no utiliza esa integración. La herramienta no instala el APK, no lee datos del juego y no prueba el renderer en ejecución. Si una biblioteca no está empaquetada donde el loader la busca, elegir “driver personalizado” en la UI no demuestra que ese driver se haya cargado.

Para afirmar uso activo, exige logs/estado del mismo proceso que identifiquen biblioteca, dispositivo Vulkan y resultado de inicialización. Consulta la [matriz de evidencia de drivers](decision-matrix.md#drivers-y-rendimiento-matriz-de-evidencia). Un APK puede contener un hook correcto y aun así caer al driver del sistema.

### 4. Haz A/B con una sola variable

Usa paquetes de prueba distintos cuando la firma o los datos privados del original deban quedar intactos. Mantén idénticos save/checkpoint, escena, cámara, calidad, superficie y duración; cambia solo el driver o el ajuste documentado bajo evaluación. Captura y compara en este orden:

1. Baseline con configuración actual conocida.
2. Una variante soportada por el port (renderer/driver o un flag de diagnóstico, no varios a la vez).
3. La misma escena tras reiniciar en frío, para detectar caché o estado transitorio.
4. Una segunda escena con otros materiales, geometría/animaciones y dirección de cámara para buscar regresiones.

Si la imagen mejora pero aparece flicker, objetos ausentes, armas oscuras, crasheos o errores nuevos, el experimento no es un arreglo general. Revierte esa variable y conserva el resultado como una observación delimitada.

### 5. Trata los flags de shader/Vulkan como hipótesis específicas

Un síntoma negro no autoriza a desactivar robustez, reemplazar UBO por SSBO, cambiar formato de textura o parchear SPIR-V a ciegas. Primero identifica la lectura o el estado que podría fallar. `robustBufferAccess` afecta accesos a buffers fuera de rango; no corrige automáticamente imágenes, formatos, carga de texturas ni todos los defectos de shader. Desactivarlo puede dejar accesos fuera de rango sin comportamiento definido y debe probarse solo como A/B en una build de diagnóstico reversible. Consulta la [guía Vulkan de robustez](https://docs.vulkan.org/guide/latest/robustness.html) y la especificación pertinente a la API usada.

Al editar SPIR-V, registra los módulos y bindings afectados, valida los binarios con el validador correspondiente y compara la misma escena. Un parche que arregla un modelo puede modificar otros draws que comparten shader o descriptor; inspecciona también suelo, puertas, armas, sombras, HUD y transiciones.

### 6. Define qué cuenta como resultado

| Estado | Evidencia | Qué permite afirmar |
|---|---|---|
| Configurado | opción/archivo cambiado | Se escribió una configuración, no que haya entrado en vigor. |
| Incluido/seleccionado | APK contiene biblioteca o UI nombra driver | El paquete/preferencia lo ofrece; no confirma carga. |
| Renderer cargado | log del mismo PID identifica biblioteca y dispositivo | El componente participó en esa sesión, sujeto a la precisión del log. |
| Reproducido antes/después | capturas comparables y escena identificada | El defecto cambió en esa comparación concreta. |
| Confirmado por el usuario | el usuario informa que la imagen mejoró | Es una confirmación válida reportada; no aísla por sí sola la causa técnica. |
| Verificado en runtime | capturas comparables más log/renderer del mismo proceso | La ruta y el resultado gráfico se relacionaron en esa sesión. |

No llames “reparado” a un juego que solo abre el menú. Reporta qué escenas se comprobaron, duración y regresiones observadas, si el driver activo quedó sin confirmar y qué falta para repetir el caso.

## Caso de estudio: DOOM Mobile y modelos animados negros

El registro upstream de DOOM v0.4.18-test1 describe cuerpos y enemigos negros en una ruta de driver Adreno 740, mientras otras partes de la escena seguían visibles. Investiga los detalles en el [registro de fallas fijado al commit `085d0cb0`](https://github.com/Desm0nt/doom-port/blob/085d0cb0b3796ddbfa33c64b6d00776387ad4eba/docs/doom/BUGS_AND_FIXES.md). El propio registro separa el arreglo de clipping de la hipótesis posterior de índices dinámicos en el UBO de huesos: corregir clipping no bastó para los modelos negros.

El mismo experimento upstream informa que `DM_GFX_BONES_SSBO=1` mostró cuerpos/enemigos normales en un dispositivo, pero introdujo suelo parpadeante, una puerta ausente y un arma oscura. Por eso ese cambio no debe publicarse como arreglo global. El siguiente ensayo registrado (`DM_VK_ROBUST=0`) era una hipótesis por comprobar, no un resultado demostrado por ese documento.

En el caso de Magic V2 registrado por este proyecto se preparó un clon de diagnóstico con cambios nativos y soporte de loader. La confirmación más reciente del usuario es que el defecto visual quedó resuelto. No se conservó en esta sesión una captura final comparable ni un log del proceso que aísle la opción responsable o demuestre qué driver llegó a cargar. El estado correcto es **resuelto según el usuario; causa exacta y renderer activo no confirmados independientemente**. Para repetir, empieza por el [informe de casos DOOM](case-study.md) y aplica este flujo; no copies los flags del caso a otros ports.

## Referencias

- [DOOM Mobile: adaptación y diagnóstico en Magic V2](doom-mobile-magic-v2.md)
- [Fuente upstream DOOM v0.4.18-test1, commit inmutable](https://github.com/Desm0nt/doom-port/tree/085d0cb0b3796ddbfa33c64b6d00776387ad4eba)
- [Vulkan Guide: robustez de memoria](https://docs.vulkan.org/guide/latest/robustness.html)
- [Skill principal para agentes](../SKILL.md)
- [Auditor estático del APK](../scripts/audit_android_renderer_apk.py)
