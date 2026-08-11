---
name: analizar-publicidad-competencia
description: >
  El sistema operativo de la publicidad de tu competencia. Captura los anuncios que tus
  competidores están pagando en Facebook e Instagram, los agrupa por creativo real, los
  clasifica con criterio fijo y arma un informe: qué lleva meses corriendo, qué está en
  test, qué acaba de aparecer o morir, y qué ángulo no usa nadie. Úsala cada 2-4 semanas.
license: MIT
author: Francisco Val
---

# Analizar la publicidad de tu competencia

Este archivo es el instructivo de la corrida. Claude lo sigue completo, en orden. **No hace
falta que sepas programar**: Claude opera y tú decides.

## Paso 0 · ¿Está todo listo para correr?

Todas las rutas de este instructivo son relativas a la carpeta del paquete: Claude trabaja
parado en ella. Y revisa dos cosas antes de partir:

1. Que exista `configuracion.json` con al menos un competidor confirmado.
2. Que exista la clave de Apify: el archivo `.env` (línea `APIFY_TOKEN=`) o, en Mac, la
   entrada `apify-competencia` del Llavero
   (`security find-generic-password -s apify-competencia -w`, usada por sustitución, jamás
   mostrada en pantalla).

**Si falta cualquiera de las dos, Claude no improvisa: deriva a la skill `configurar` y
recién después vuelve aquí.** Correr sin configuración produce análisis de competidores no
confirmados, que es peor que no correr.

## Paso 1 · De dónde salen los datos (y la trampa a evitar)

Los anuncios salen de la **Biblioteca de Anuncios de Meta**, el registro público donde
aparece todo lo que se paga en Facebook e Instagram. Se capturan con un servicio de
extracción (Apify), que lee esa biblioteca pública.

### ⛔ La trampa que arruina el análisis sin avisar

Meta ofrece también una vía oficial gratuita (su API), pero **solo devuelve anuncios
comerciales de países de la Unión Europea**. Para Chile, México, Colombia o cualquier país
fuera de la UE, esa vía **no da error: devuelve una lista vacía**, idéntica a la de un
competidor que no hace publicidad.

Reglas duras que Claude respeta siempre:

- Para mercados fuera de la UE se usa **únicamente** el extractor, jamás la API oficial.
- **Una lista vacía nunca se interpreta sola.** Antes de escribir "este competidor no hace
  publicidad", Claude abre la Biblioteca de Anuncios en la web
  (`facebook.com/ads/library`), busca la página del competidor a mano y verifica. Si ahí
  tampoco hay nada, la conclusión es legítima y se anota con fecha. Si ahí sí hay anuncios,
  el problema fue la captura y se reintenta.

## Paso 2 · Declarar el costo ANTES de correr

La captura cuesta alrededor de **US$0,005 por corrida más US$0,0005 por anuncio** (medio
dólar por cada mil anuncios). Referencia real: nuestra corrida de 120 anuncios costó
**US$0,074**.

Claude calcula el estimado con la fórmula, lo dice, y espera tu ok:

> Voy a capturar hasta 100 anuncios por cada uno de tus 6 competidores. Costo máximo
> estimado: US$0,33 de tu crédito gratis de Apify. ¿Corro?

## Paso 3 · Capturar

Claude llama al extractor `automation-lab/facebook-ads-library` con la API de Apify. Dos
decisiones de diseño que salen de pruebas reales, no de la documentación:

- **Se captura por BÚSQUEDA del nombre** (`searchQueries`), no por página (`pageUrls`). En
  nuestras pruebas la captura por página devolvió 0 anuncios por fallos de extracción del
  actor; la búsqueda funcionó de forma estable. La página de Facebook guardada en la
  configuración se usa después, para filtrar homónimos.
- **La corrida se lanza asíncrona.** La vía síncrona corta a los ~300 segundos y una corrida
  de varios competidores no alcanza.

```
1. Lanzar:
POST https://api.apify.com/v2/acts/automation-lab~facebook-ads-library/runs?timeout=1500&token=TU_CLAVE
{ "searchQueries": ["Nombre Uno", "Nombre Dos"], "country": "CL",
  "activeStatus": "active", "maxAds": 50 }
   → anotar del resultado el `id` de la corrida y el `defaultDatasetId`.

2. Esperar: consultar cada 30 segundos
GET https://api.apify.com/v2/actor-runs/ID?token=TU_CLAVE
   hasta que `status` deje de ser RUNNING/READY.

3. Descargar:
GET https://api.apify.com/v2/datasets/DATASET_ID/items?format=json&token=TU_CLAVE
```

- `country` sale de la configuración (el país de TU mercado, no el de la casa matriz del
  competidor).
- La clave se lee del `.env` o del Llavero **en el momento de usarla**; nunca queda escrita
  en el comando guardado ni en ningún archivo del historial.

### ⛔ Las tres guardias sobre lo que vuelve

1. **`SUCCEEDED` con 0 anuncios NO significa "no hacen publicidad".** Antes de concluir,
   Claude lee el log de la corrida (`GET .../actor-runs/ID/log`): si dice "Failed to
   scrape", fue fallo de captura y se reintenta por otra vía. El veredicto "este competidor
   no tiene anuncios" solo puede darlo el chequeo manual: **tú**, en tu navegador, en
   `facebook.com/ads/library`, con tu país seleccionado, buscando la marca.
2. **Filtrar homónimos, leyendo.** La búsqueda por nombre trae todo lo que se llame
   parecido. Se conservan solo los anuncios cuya página (`pageUrl` o `pageName`) coincide
   con la página confirmada en la configuración; el resto se lee, se descarta y **se
   declara cuántos se fueron**. El riesgo es real: en nuestra prueba, buscar una marca de
   nombre genérico devolvió 100 de 100 anuncios de juegos móviles homónimos.
3. **Nombre genérico = capturar aparte o declarar no capturable.** Si un competidor se
   llama con una palabra común, su búsqueda puede devorar el presupuesto de la corrida en
   puro ruido. Va en corrida separada con tope bajo, o queda documentado en el informe como
   "no capturable por búsqueda", con el chequeo manual como vía.

### Guardar la corrida: el paso que construye el activo

El resultado se convierte a un archivo `corridas/AAAA-MM-DD.csv` (la fecha de hoy), una fila
por anuncio, con estas columnas exactas:

| Columna del CSV | Del resultado del extractor |
|---|---|
| `fecha_captura` | la fecha de hoy, AAAA-MM-DD |
| `anunciante` | `pageName` |
| `texto` | `bodyText` |
| `titulo` | `title` |
| `destino_url` | `linkUrl` |
| `formato` | `displayFormat` |
| `plataformas` | `platforms`, unidos con `\|` |
| `cta` | `ctaType` |
| `fecha_inicio` | `startDate` |
| `activo` | `isActive` como `si`/`no` |
| `variantes` | `collationCount` (0 si viene vacío) |
| `media_ia` | `containsAiMedia` como `si`/`no` |
| `url_biblioteca` | `adLibraryUrl` |

**Este archivo no se borra nunca y cada corrida crea uno nuevo.** La razón: la Biblioteca de
Anuncios no dice cuánto tiempo lleva corriendo un anuncio de verdad (la fecha que muestra se
reinicia cuando el anunciante lo duplica, y duplicar es lo que hacen los buenos anunciantes
para escalar). La única forma de saber qué sobrevive es **tu propia serie**: comparar tus
corridas entre sí. Cada corrida que guardas es señal que nadie más tiene; cada corrida que
no guardas es señal que no existirá nunca.

## Paso 4 · Clasificar

1. Claude corre `python3 scripts/huella.py corridas/*.csv --listar-creativos` para
   obtener las creativos únicos (los duplicados ya vienen agrupados).
2. Clasifica cada una siguiendo **`contrato-de-patrones.md`**, que es la ley: categorías
   cerradas, desempates definidos, y la regla cero — **cada etiqueta viene de haber leído
   ese anuncio; jamás se deduce ni se completa "por consistencia"**. Lo que no se pudo
   leer se marca `error` y queda fuera.
3. La primera vez, antes de clasificar todo: la prueba de estabilidad del contrato
   (20 creativos, dos veces, con una hora de separación).
4. Las etiquetas se escriben en el CSV de la corrida, en las columnas `angulo`,
   `protagonista`, `cifra_concreta` y `que_vende`. Los duplicados de una misma huella llevan
   la misma etiqueta (es el mismo texto).

## Paso 5 · Calcular y armar el informe en PDF

El informe final es **un PDF diseñado**, no un texto en el chat. El diseño ya viene resuelto
en el paquete; Claude solo lo rellena con los datos de la corrida. El flujo, en orden:

1. **Calcular:**
   ```bash
   python3 scripts/huella.py corridas/*.csv
   ```
2. **Copiar la plantilla** (`plantilla-informe.html`, que no se toca) a un archivo nuevo:
   `corridas/informe-AAAA-MM-DD.html`.
3. **Rellenar la copia.** Las instrucciones de llenado viven DENTRO de la plantilla, en los
   comentarios: qué va en cada marcador `{{...}}`, cuánto cabe en cada página (una página es
   un bloque cerrado: si algo no cabe, se crea otra página, jamás se deja que se corte), y
   qué bloques se duplican (las fichas del anexo, máximo 4 por página). El texto de cada
   anuncio va completo en el anexo, con su enlace real a la Biblioteca. La firma y la marca
   del autor no se editan: son parte del sistema.
4. **Renderizar:**
   ```bash
   python3 scripts/renderizar_pdf.py corridas/informe-AAAA-MM-DD.html corridas/informe-AAAA-MM-DD.pdf
   ```
   El programa encuentra solo el navegador instalado (Chrome, Edge o Chromium, en Mac,
   Windows o Linux) y lo usa en modo silencioso con un perfil temporal, sin tocar las
   ventanas abiertas. **Si no hay navegador compatible, el programa mismo da las dos
   salidas:** instalar Chrome (gratis) o abrir el HTML y usar Imprimir → Guardar como PDF
   con márgenes en "Ninguno" y "Gráficos de fondo" activado. Las tipografías del informe
   se descargan de internet al renderizar; sin conexión, salen las de respaldo (el informe
   se ve bien igual).
5. **⛔ Verificación obligatoria antes de entregarlo:** Claude ABRE el PDF generado y lo
   revisa página por página, mirándolo de verdad:
   - Nada pegado al borde superior; ninguna sección ni tabla cortada entre páginas.
   - Ningún marcador `{{...}}` vivo.
   - Los enlaces del anexo apuntan al anuncio correcto y el pie aparece en todas las páginas.
   - Las cifras del PDF coinciden con la salida de la calculadora.
   Lo que falle se corrige en el HTML y se vuelve a renderizar. **Un informe que no pasó
   esta revisión no se entrega.**

### Las reglas del informe (las que separan esto de una impresión)

1. **Jamás se promete rendimiento.** Meta no publica qué anuncio comercial convierte. La
   antigüedad **prioriza qué mirar primero**; no dice "esto funciona". Un anuncio malo con
   tope de costo puede seguir "activo" gastando casi nada, y el informe lo recuerda.
2. **Toda tasa lleva su n y su control.** "El 23% lleva promoción" obliga a decir cuántos
   son y cuántos días lleva el resto. Un 0% con 4 casos es "no hay datos", no "nadie lo
   hace".
3. **Los huecos se presentan como huecos, no como oportunidades probadas.** Que nadie use un
   ángulo puede significar que nadie lo probó o que alguien lo probó y no le resultó. El
   informe dice cuál de las dos no se puede saber.
4. **Desde la segunda corrida, el radar manda.** Qué apareció y qué murió desde la última
   corrida es la sección más accionable del informe, y solo existe porque guardaste la
   anterior.

## Paso 6 · Decir cuándo volver

El informe cierra con la fecha sugerida de la próxima corrida: **entre 2 y 4 semanas**. Antes
de 2 semanas no alcanza a cambiar nada; después de 4 se pierden anuncios que nacieron y
murieron sin que los vieras.

---

## Lo que este sistema NO hace (y por qué)

- **No estima cuánto gasta tu competencia.** Ese dato no es público fuera de la UE, y
  contar anuncios como proxy engaña: los presupuestos chicos publican muchas piezas
  segmentadas y los grandes pocas piezas masivas.
- **No rankea anuncios por efectividad.** No existe el dato público que haría honesto ese
  ranking.
- **No mide interacciones** (reacciones, comentarios). La biblioteca no las entrega y
  rasparlas de otro lado produce una foto sesgada.
- **No decide por ti.** Te dice qué está pagando tu competencia y hace cuánto. La decisión
  de qué hacer con eso sigue siendo tuya.

Licencia MIT · Francisco Val
