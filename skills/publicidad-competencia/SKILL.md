---
name: publicidad-competencia
description: >
  Analiza la publicidad que tu competencia está pagando en Facebook e Instagram y arma un
  informe en PDF: qué anuncio lleva meses corriendo, cuál está en testeo, cuál acaba de
  aparecer o morir, y qué ángulo no usa nadie. Úsala cuando el usuario diga "analiza la
  publicidad de mi competencia", "qué están pagando mis competidores", "configura el análisis
  de competencia", "quiero ver los anuncios de la competencia", o cuando haya que actualizar
  la lista de competidores de una empresa ya configurada. Detecta sola si la empresa ya está
  configurada y, si no lo está, configura primero. Captura anuncios con Apify, que cuesta
  centavos: declara el costo estimado y espera autorización antes de gastar.
---

# El sistema operativo de la publicidad de tu competencia

**No hace falta que sepas programar.** Tú respondes preguntas sobre tu negocio y decides; Claude
opera el resto.

## Cómo funciona

Una sola skill hace las dos cosas. **El primer paso siempre es averiguar en qué estado está la
empresa**, y de ahí sale a cuál de los dos procedimientos ir:

```
¿Qué empresa?  ──▶  ¿ya existe configuracion-competencia.json?
                          │
                    NO ───┴──▶ SÍ
                     │          │
              configurar.md    analizar.md
```

Nunca se le pregunta al usuario "¿quieres configurar o analizar?". Esa pregunta es del sistema:
se responde sola mirando el disco.

⛔ **Este archivo no contiene los procedimientos, solo decide cuál toca.** El detalle vive en
`configurar.md` y `analizar.md`, y se lee **el que corresponda, entero**, cuando corresponda.

---

## Paso 0 · Ubicar los archivos de la skill

Antes de nada, Claude localiza la carpeta de esta skill, porque de ahí salen la calculadora, la
plantilla del informe y el contrato de clasificación. **Hay dos formas de tener este sistema y
las rutas cambian entre una y otra**, así que se resuelve una vez y se recuerda:

- **Instalado como plugin:** la carpeta es `${CLAUDE_PLUGIN_ROOT}/skills/publicidad-competencia/`.
- **Descargado como ZIP** y con Claude Code abierto dentro: la carpeta es
  `skills/publicidad-competencia/` desde donde estás parado.

Si ninguna de las dos aparece, búscala antes de seguir:

```bash
find . -name "huella.py" -path "*publicidad-competencia*" 2>/dev/null
```

En este archivo esa carpeta se llama `<SKILL>`. Todo lo que diga `<SKILL>/algo` se reemplaza por
la ruta real que encontraste.

## Paso 1 · Ubicar la empresa y su estado

### 1.1 · Dónde van las cosas de esta empresa

Todo lo que produce el sistema vive junto, en la carpeta de la empresa:

```
<carpeta de tu empresa>/
├── configuracion-competencia.json   <- tu empresa y tus competidores confirmados
├── datos/                           <- una corrida por archivo: AAAA-MM-DD.csv
└── informes/                        <- informe-AAAA-MM-DD.html y .pdf
```

Si el usuario analiza una sola empresa, esa carpeta puede ser donde está parado. Si maneja
varias, cada una tiene la suya. **La ruta se pregunta una vez, se guarda en el campo `carpeta` de
la configuración, y no se vuelve a adivinar.** Si `datos/` o `informes/` no existen, se crean.

### 1.2 · El estado, y a dónde lleva

Se busca la configuración:

```bash
ls -1 configuracion-competencia.json */configuracion-competencia.json 2>/dev/null
```

| Lo que hay | Qué se lee y se hace |
|---|---|
| No hay `configuracion-competencia.json` | **`<SKILL>/configurar.md` entero**, y al terminar se ofrece seguir con el análisis |
| Hay configuración con competidores confirmados | **`<SKILL>/analizar.md` entero**. Antes de capturar, una línea: "tienes N competidores confirmados desde &lt;fecha&gt;; ¿los dejamos así?" |
| Hay configuración, pero sin competidores confirmados | **`<SKILL>/configurar.md`, desde el paso 3**, sin repetir el perfil de empresa |
| El usuario pide cambiar competidores | **`<SKILL>/configurar.md`, solo el paso 3**, sobre la configuración que ya existe |

---

## Las tres reglas que valen en los dos caminos

Estas rigen siempre, sin importar cuál procedimiento se lea.

1. **⛔ El costo se declara ANTES y se espera el sí.** Capturar anuncios gasta el crédito de la
   cuenta de Apify del usuario. Se calcula el estimado, se dice el número y se espera respuesta.
   Nunca se captura "para ver qué sale".

2. **⛔ La clave nunca se muestra ni se guarda en la configuración.** Vive en un archivo `.env`
   (línea `APIFY_TOKEN=...`) o, en Mac, en el Llavero bajo el nombre `apify-competencia`. Se usa
   por sustitución en el momento de llamar a la API. Jamás va en
   `configuracion-competencia.json` ni en ningún archivo que pueda terminar compartido.

3. **⛔ Claude propone competidores, nunca los confirma solo.** Los modelos de lenguaje inventan
   nombres de empresas, y el problema es peor con empresas medianas de mercados hispanos, donde
   el modelo sabe poco y rellena con inventos plausibles. Cada candidato necesita **una URL viva
   verificada** y **la confirmación del usuario**. Sin las dos cosas, se descarta.

---

## Lo que este sistema NO hace (y por qué)

- **No estima cuánto gasta tu competencia.** Ese dato no es público fuera de la Unión Europea, y
  contar anuncios como proxy engaña: los presupuestos chicos publican muchas piezas segmentadas y
  los grandes pocas piezas masivas.
- **No rankea anuncios por efectividad.** No existe el dato público que haría honesto ese
  ranking, diga lo que diga quien lo ofrezca.
- **No mide interacciones** (reacciones, comentarios). La biblioteca no las entrega y rasparlas
  de otro lado produce una foto sesgada.
- **No decide por ti.** Te dice qué está pagando tu competencia y hace cuánto. La decisión de qué
  hacer con eso sigue siendo tuya.

---

## Archivos de esta skill

| Archivo | Qué es | Cuándo se lee |
|---|---|---|
| `configurar.md` | La primera vez: tu empresa, tus competidores, tu acceso a los datos | Solo si falta la configuración, o al cambiar competidores |
| `analizar.md` | La corrida: capturar, clasificar, calcular, informar | En cada análisis |
| `contrato-de-patrones.md` | Las categorías de clasificación, cerradas y con desempates | En el paso de clasificar |
| `plantilla-informe.html` | El diseño del informe, congelado. Se copia y se rellena; el original no se edita | Al armar el informe |
| `scripts/huella.py` | La calculadora. Agrupa por creativo real y mide contra tu propia serie | Se **ejecuta**, no se lee |
| `scripts/renderizar_pdf.py` | Convierte el informe en PDF con el navegador que ya tienes | Se **ejecuta**, no se lee |

Licencia MIT · Francisco Val
