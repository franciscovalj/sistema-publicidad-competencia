# El sistema operativo de la publicidad de tu competencia

Te dice qué están pagando tus competidores en Facebook e Instagram: qué anuncio lleva meses
corriendo, cuál está en testeo, cuál acaba de aparecer o morir, y qué ángulo no usa nadie.

**[⬇ Descargar la última versión (ZIP)](https://github.com/franciscovalj/sistema-publicidad-competencia/releases/latest/download/sistema-publicidad-competencia.zip)** · gratis, licencia MIT

No es un prompt. Son dos instructivos y una calculadora que corren en orden: uno configura
(tu empresa, tus competidores confirmados, tu acceso a los datos), el otro captura, clasifica
con criterio fijo, calcula y arma el informe.

**No hace falta saber programar.** Le pasas los instructivos a Claude y él opera el resto.

---

## Cómo se usa

Necesitas **Claude Code** (el agente de Anthropic que puede leer archivos y ejecutar
programas en tu computador), Python 3 (viene instalado en Mac y Linux; en Windows se
instala gratis desde python.org, y Claude te acompaña si hace falta) y un navegador
(Chrome, Edge o Chromium: el que ya tienes sirve; se usa en silencio para producir el PDF
del informe, sin tocar tus ventanas).

1. Deja esta carpeta completa en tu computador.
2. Abre Claude Code en la carpeta y dile: **"configura el análisis de mi competencia"**
   (sigue `skills/configurar/SKILL.md`). Se hace una sola vez.
3. Después, cada 2-4 semanas: **"analiza la publicidad de mi competencia"**
   (sigue `skills/analizar/SKILL.md`).

### Pruébalo en 10 segundos, sin configurar nada

La carpeta `corridas-ejemplo/` trae dos corridas con **datos inventados**. Esto muestra el
sistema completo funcionando, incluido el radar de cambios entre corridas:

```bash
python3 scripts/huella.py corridas-ejemplo/*.csv
```

(En Windows el comando suele ser `python` en vez de `python3`; Claude lo ajusta solo.)

Y `informe-ejemplo.md` muestra cómo se ve el informe final. Todo lo de ahí es inventado y
está rotulado como tal: el destino a la vista antes de partir.

---

## Qué hay adentro

| Archivo | Qué es |
|---|---|
| `skills/configurar/SKILL.md` | El instructivo de la primera vez: tu empresa, tus competidores, tu acceso. |
| `skills/analizar/SKILL.md` | El instructivo de cada corrida: capturar, clasificar, calcular, informar. |
| `scripts/huella.py` | La calculadora. Agrupa por creativo real y mide contra tu propia serie. |
| `plantilla-informe.html` | El diseño del informe, congelado. Claude lo rellena con tus datos; portada, gráficas, anexo y paginación ya vienen resueltos. |
| `scripts/renderizar_pdf.py` | Convierte el informe en PDF con el navegador que ya tienes, en cualquier sistema. |
| `contrato-de-patrones.md` | Las categorías con las que se clasifica, cerradas y con desempates. |
| `informe-ejemplo.md` | El contenido de un informe, con **datos inventados**, para ver el destino antes de partir. El diseño final lo pone la plantilla. |
| `corridas-ejemplo/` | Dos corridas inventadas para probar la calculadora sin gastar. |
| `.gitignore` | Impide publicar por accidente tu configuración, tu clave y tus corridas. |

## Lo que cuesta, dicho de frente

Los anuncios salen de la Biblioteca de Anuncios de Meta (pública) capturados vía
[Apify](https://www.apify.com?fpr=kr27nl): cuenta **gratis, sin tarjeta, con US$5 de
crédito al mes**. (Ese es un enlace de referido: a ti no te cambia el precio y al autor le
deja una comisión si algún día pasas a un plan pagado.) La captura cuesta cerca de
US$0,50 por mil anuncios. **Nuestra corrida real de 120 anuncios costó US$0,074** — siete
centavos. El crédito gratis alcanza para 5-8 competidores todos los meses.

## Las dos ideas que lo sostienen

> **1 · Se cuentan creativos, no anuncios.** Los anunciantes duplican sus anuncios para
> escalar, y cada duplicado sale con fecha nueva: contar anuncios infla todo y hace que los
> ganadores más escalados parezcan recién nacidos. El sistema agrupa por huella (el texto
> más el destino) y mide cada creativo una vez. En nuestra corrida real, el 47% de los
> anuncios eran duplicados.

> **2 · La señal más valiosa se construye, no se consulta.** La Biblioteca de Anuncios no
> dice cuánto lleva corriendo un anuncio de verdad. La única forma de saber qué sobrevive es
> guardar cada corrida y comparar contra la anterior. Por eso cada corrida se guarda con su
> fecha desde el día uno: estás construyendo un registro que no se puede comprar hacia atrás.

## Lo que este sistema no hace

- **No dice qué anuncio convierte.** Meta no publica el rendimiento de los anuncios
  comerciales; nadie que mire datos públicos lo sabe, diga lo que diga. La antigüedad
  prioriza qué mirar primero, nada más.
- **No estima presupuestos.** Contar anuncios como proxy de gasto engaña.
- **No decide por ti.** Dice qué está pagando tu competencia y hace cuánto. La decisión
  sigue siendo tuya.
- **No trae datos ni conclusiones de ningún rubro.** Trae el método. Las conclusiones salen
  cuando lo corres sobre TUS competidores.

## Tu información

Tu configuración, tu clave de Apify y tus corridas se quedan en tu computador. El
`.gitignore` incluido impide que se publiquen por accidente si subes la carpeta a un
repositorio. Las corridas guardadas (`corridas/`) son tu activo: **respáldalas** como
respaldas cualquier archivo importante.

## Licencia

MIT. Úsalo, modifícalo y véndelo si quieres. Si te sirve, me gusta saberlo — y una
estrella en este repositorio ayuda a que le llegue a más dueños de negocio.

El informe sale de fábrica con la firma de quien construyó el sistema y su LinkedIn. La
licencia te deja cambiarla; se agradece dejarla.

Hecho por Francisco Val.
