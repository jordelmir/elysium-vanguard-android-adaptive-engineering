# Aspect ratio en emuladores PS2 para Android

## Propósito y alcance

Este runbook localiza las franjas de un emulador PS2 Android y cambia el encuadre con una sola variable controlada. Distingue el tamaño del display, la ventana Android, la superficie de render y el cuadro producido por la GS del emulador. Se verificó el método en un wrapper ARMSX2 instalado como `com.catonix.gow2`; sus nombres de clave y valores no son universales.

Lee primero el [caso de God of War II en el Magic V2](../../../docs/god-of-war-ii-armsx2-magic-v2.md) y el [registro de casos](case-study.md#caso-18--god-of-war-ii-en-armsx2catonix-aspect-ratio-en-pantalla-interior). No supongas que un wrapper renombrado usa el mismo código o esquema que upstream.

## Pregunta y predicción

Pregunta: si la actividad y la superficie ya ocupan la pantalla interior, ¿las bandas provienen de que el emulador conserva el cuadro PS2 4:3?

- H1: cambiar el modo de aspecto del renderer de `Auto`/4:3 a `Stretch` llena el destino sin recortar el cuadro y deforma la imagen.
- H0: el ajuste no cambia el cuadro, la superficie sigue siendo menor, el cuadro se recorta o el valor no persiste tras reiniciar la app.

Mantén fijo el paquete/build, el disco del juego, postura, orientación, display y escena. La única variable independiente es el modo de aspecto. Mide por separado área de bandas, recorte, deformación, persistencia y entrada táctil.

## Protocolo reproducible

### 1. Identifica y congela el objetivo

1. Descubre el ADB actual; no reutilices un serial antiguo:

   ```sh
   adb devices -l
   SERIAL='serial-en-linea'
   PKG='paquete.observado'
   adb -s "$SERIAL" shell dumpsys package "$PKG" | grep -E 'versionName=|versionCode=|DEBUGGABLE'
   ```

2. Registra modelo/Android, paquete, versión, actividad, arquitectura del emulador, juego/ID de disco, postura desplegada y display activo. Omite el serial de la documentación pública.
3. Abre primero los ajustes de pantalla/aspecto del emulador. Si existe una opción visible, úsala y registra literalmente su etiqueta.
4. Si el valor no es visible, busca la clave y el enum en el código o esquema de la misma build. Una página upstream o el nombre ARMSX2 no prueba que el wrapper local sea idéntico.

### 2. Obtén la línea base

1. Desde un menú o estado seguro, reproduce una escena fija y captura el display interior correcto.
2. Registra bounds del display, actividad, `SurfaceView`/superficie y rectángulo visible del juego. `dumpsys window`, `dumpsys SurfaceFlinger` y las métricas del display sirven para localizar las capas; una resolución nominal no demuestra el tamaño de la superficie.
3. Anota si el cuadro 4:3 conserva proporción, dónde aparecen las bandas y si se pierde algún borde. Mantén sin cambios resolución de emulación, renderer, driver, HUD, FPS y escala táctil.
4. Guarda copia local de la preferencia original y captura; no publiques seriales, XML privado, saves, APK ni imágenes protegidas.

### 3. Elige el compromiso visual

Sea el cuadro `W×H` y el destino `A×B`:

```text
sx = A / W
sy = B / H
Fit     = min(sx, sy) aplicado uniformemente: conserva cuadro y aspecto, deja bandas
Cover   = max(sx, sy) aplicado uniformemente: llena, conserva aspecto, recorta
Stretch = aplica sx y sy por separado: llena y conserva el cuadro, deforma el aspecto
```

No llames a `Stretch` FOV adaptativo. Para preservar geometría, elige `Fit`. Para llenar cada píxel y mostrar todos los bordes, `Stretch` es el único de estos modos que satisface ambos objetivos a la vez, a costa de deformar. Una modificación real de viewport/FOV requiere soporte del juego/renderer y validación independiente.

### 4. Cambia una sola preferencia y conserva rollback

1. Prefiere el control de la interfaz. Si solo hay configuración privada, respalda el archivo antes de editar y confirma el nombre, formato, valores admitidos y ámbito global/por juego de esta build.
2. Usa `run-as` solo si la app es depurable. Si no lo es, no escales a root: usa el ajuste visible o un clon de prueba autorizado.
3. Detén la app solo en una pantalla segura. Edita un único campo con un parser XML/JSON, valida el resultado, conserva el archivo de reversión y reemplaza el archivo de forma atómica bajo el UID de la app. No uses `sed` sobre XML ni reemplaces toda la configuración con un perfil de otro emulador.
4. Registra valor anterior/nuevo, ruta, hash local redactado si aporta reproducción y alcance. No cambies a la vez renderer, driver, resolución ni FPS.

Ejemplo **solo para una build que ya se haya confirmado con este formato** (`config.global` es un nodo `<string>` cuyo texto es JSON). Primero lee la copia y guarda el respaldo en el Mac:

```sh
SERIAL='serial-en-linea'
PKG='paquete.observado'
adb -s "$SERIAL" exec-out run-as "$PKG" cat shared_prefs/ARMSX2.xml > ./ARMSX2.before.xml
```

Transforma el XML localmente con un parser y aserciones para impedir que un esquema distinto se modifique por accidente:

```sh
python3 - ./ARMSX2.before.xml ./ARMSX2.after.xml <<'PY'
import json
import sys
import xml.etree.ElementTree as ET

source, destination = sys.argv[1:]
tree = ET.parse(source)
node = tree.find("./string[@name='config.global']")
if node is None or not node.text:
    raise SystemExit("No existe config.global en el formato esperado")
settings = json.loads(node.text)
if settings.get("aspectRatio") != 1:
    raise SystemExit(f"Valor anterior inesperado: {settings.get('aspectRatio')!r}")
settings["aspectRatio"] = 0
node.text = json.dumps(settings, separators=(",", ":"))
tree.write(destination, encoding="utf-8", xml_declaration=True)
check = ET.parse(destination).find("./string[@name='config.global']")
if json.loads(check.text)["aspectRatio"] != 0:
    raise SystemExit("No se pudo verificar el valor nuevo")
PY
```

Con la app en un estado seguro, deténla y transmite solo el XML validado a un archivo temporal dentro de `shared_prefs`; el `mv` ocurre en el mismo directorio:

```sh
adb -s "$SERIAL" shell am force-stop "$PKG"
adb -s "$SERIAL" shell run-as "$PKG" sh -c \
  'cat > shared_prefs/ARMSX2.xml.new && mv shared_prefs/ARMSX2.xml.new shared_prefs/ARMSX2.xml' \
  < ./ARMSX2.after.xml
adb -s "$SERIAL" exec-out run-as "$PKG" cat shared_prefs/ARMSX2.xml
```

Si `run-as` falla, no intentes eludir el sandbox: vuelve a la UI o usa una build de prueba depurable. No borres datos para forzar una preferencia nueva; eso puede borrar saves.

Para la build estudiada, el dato era el JSON `config.global` dentro de `shared_prefs/ARMSX2.xml`: `aspectRatio=1` antes y `aspectRatio=0` después. La preferencia interna era la fuente primaria. Esa ruta y esos índices son una observación de `com.catonix.gow2`, no una receta para cualquier fork.

### 5. Verifica desde cero

1. Inicia la app en frío y vuelve a leer la preferencia efectiva. Que el control se haya tocado no demuestra que el renderer la haya aplicado.
2. Abre el mismo juego en el mismo display y reproduce la misma escena/cámara que en la línea base.
3. Captura explícitamente el panel interior. Comprueba visualmente barras y bordes; registra también tamaño de ventana/superficie y, si es posible, el rectángulo del cuadro.
4. Comprueba persistencia después de otro cierre completo. Prueba el táctil en el centro y cerca de los bordes por separado; una imagen completa no prueba el mapeo de entrada.
5. Si el resultado falla, restaura el respaldo y repite desde la línea base. No cambies varias capas para “compensar” una discrepancia.

## Cálculo de referencia del caso Magic V2

El display observado fue `2344×2156`, razón `2344/2156 ≈ 1.0872`; el cuadro PS2 4:3 tiene razón `1.3333`. Al ajustar `2344×1758` a lo ancho, `Fit` deja `2156−1758=398` píxeles verticales, unos `199` arriba y abajo si está centrado. Al estirar ese mismo cuadro hasta `2344×2156`, la escala horizontal es `1.0` y la vertical `2156/1758 ≈ 1.2264`; la deformación vertical relativa es aproximadamente `22.6 %`. Es geometría calculada a partir de las dimensiones, no una medición fotométrica de cada píxel.

## Estado de evidencia que debe reportarse

Separa estos hechos en el informe:

- **Configurado:** el archivo o control contiene el valor esperado.
- **Persistió en cold start:** el valor se leyó después de cerrar y volver a iniciar.
- **Reproducido visualmente:** captura del display correcto muestra el efecto.
- **Táctil probado:** entrada física confirmada en puntos declarados.
- **Reportado por usuario:** confirmación humana, etiquetada como tal.

Una captura de un solo cuadro no demuestra tacto, FOV, estabilidad, FPS ni ausencia de regresiones en otros juegos. La plantilla de evidencia incluye proporciones, modo, ámbito, recorte, deformación y persistencia.

## Rollback

Restaura el archivo respaldado bajo el UID de la app o elige de nuevo el modo anterior en la interfaz. Cierra la app de forma normal, arranca en frío y verifica tanto el valor como el encuadre. Si una restauración externa de preferencias puede ocurrir al faltar el archivo primario, inspecciona ese mecanismo antes de borrar datos; el fallback no debe confundirse con el valor efectivo actual.

## Fuentes de formato

El [caso técnico](../../../docs/god-of-war-ii-armsx2-magic-v2.md) describe la build y las limitaciones observadas. La referencia al [enum de ARMSX2](https://github.com/ARMSX2/ARMSX2/blob/c25493a20285dc126a950d2d61826987a566a306/platforms/android/app/src/main/java/com/armsx2/config/Settings.kt#L587-L596) y la [precedencia de su configuración](https://github.com/ARMSX2/ARMSX2/blob/c25493a20285dc126a950d2d61826987a566a306/platforms/android/app/src/main/java/com/armsx2/config/ConfigStore.kt#L326-L334) señalan el commit inspeccionado; no establecen que el APK Catonix derive exactamente de él.
