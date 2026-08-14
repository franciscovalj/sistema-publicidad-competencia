---
name: configurar-publicidad-competencia
description: >
  Configuración inicial del sistema operativo de la publicidad de tu competencia.
  Corre UNA vez: entiende tu empresa desde tu web, encuentra y confirma competidores
  contigo, deja guardado el acceso a los datos y escribe la configuración. Úsala la
  primera vez, o cuando cambien tus competidores.
license: MIT
author: Francisco Val
---

# Configurar el sistema — la primera vez

Este archivo es el instructivo de la configuración inicial. Claude lo sigue conversando
contigo. **No hace falta que sepas programar**: tú respondes preguntas sobre tu negocio,
Claude hace el resto.

Al terminar quedan dos cosas guardadas: `configuracion.json` (tu empresa y tus competidores
confirmados) y tu clave de acceso a los datos (aparte, ver el paso 4). Con eso, la skill
`analizar` puede correr todas las veces que quieras.

Todas las rutas de este instructivo son relativas a la carpeta del paquete: Claude trabaja
parado en ella.

**Antes de partir, Claude revisa si ya existe `configuracion.json` en esta carpeta.** Si
existe, no se parte de cero: se muestra lo que hay y se pregunta qué cambiar.

---

## Paso 1 · Entender tu empresa desde tu web

Claude pide la dirección de tu sitio web y lo lee. En orden: primero el `sitemap.xml` (el
índice del sitio, para no adivinar), después la portada, precios, servicios, quiénes somos,
casos y contacto.

### ⛔ Guardia obligatoria: ¿se pudo leer de verdad?

Más de dos tercios de los sitios modernos se arman con programas que un lector automático no
siempre puede ejecutar. El síntoma es traicionero: el sitio responde "todo bien" pero entrega
una página vacía.

**Por eso Claude cuenta las palabras útiles que extrajo. Si son menos de 200, dice
exactamente esto: "no pude leer tu sitio"** y pasa a preguntarte directamente:

1. ¿Qué vendes, en tus palabras?
2. ¿A quién? ¿Empresas o personas? ¿De qué tamaño?
3. ¿En qué país o ciudad?
4. ¿En qué rango de precios te mueves?

**Prohibido concluir "empresa sin propuesta clara" cuando el problema fue no poder leer.**
Son dos cosas distintas y confundirlas arruina todo lo que viene después.

### Señales que Claude busca (y en este orden de confianza)

Para ubicar tu país y mercado: la moneda y el formato de los precios → el prefijo telefónico
(+56, +52, +34, +57...) → la dirección física → el identificador tributario (RUT, RFC, CIF,
CUIT) → la terminación del dominio (.cl, .mx, .es) → el idioma.

⛔ Lo que NO se usa: la ubicación del servidor. Hoy todo está alojado en granjas de servidores
de otro país; ese dato es ruido puro.

## Paso 2 · Mostrarte el perfil, con la fuente de cada dato

Claude te muestra lo que entendió, y cada dato lleva su origen marcado:

- **[verificado]** — con la cita textual de tu web de donde salió
- **[inferido]** — con el razonamiento ("los precios están en UF, así que asumo Chile")
- **[desconocido]** — no se encontró y no se inventa

Y cierra con UNA pregunta: **"¿corrijo algo antes de buscar competidores?"** No es un
interrogatorio; es un borrador que tú corriges.

## Paso 3 · Encontrar y confirmar tus competidores

### ⛔ La regla más importante de todo el sistema

**Claude GENERA candidatos a competidor. JAMÁS los confirma solo.** Los modelos de lenguaje
inventan nombres de empresas con una frecuencia alta, y el problema es peor justamente con
empresas medianas de mercados hispanos, donde el modelo sabe poco y rellena con inventos
plausibles o con marcas grandes que no compiten contigo.

Por eso cada candidato pasa dos filtros antes de entrar a la lista:

1. **Una URL viva.** Claude visita el sitio del candidato y verifica que exista, que sea del
   mismo rubro, del mismo mercado geográfico y de un nivel de precios comparable. Sin URL
   viva verificada, el candidato se descarta sin excepción.
2. **Tu confirmación.** Claude te muestra la lista con la evidencia de cada uno y tú dices
   cuáles sí y cuáles no. Tú conoces tu mercado; el sistema no.

### Cómo busca Claude

- Búsquedas en la web con las palabras de tu rubro y tu país, en varias formulaciones
  distintas. **La señal es la repetición**: el nombre que aparece en varias búsquedas
  independientes pesa más que el que aparece en una.
- Búsquedas tipo "alternativas a [tu empresa]" y "mejores [tu categoría] en [tu país]".
- Si tu negocio es local (atiende en una ciudad), búsquedas de mapa: quién aparece cuando un
  cliente busca tu categoría en tu ciudad.

### Las dos preguntas que ninguna búsqueda reemplaza

1. **"¿Con quién te comparan tus clientes? ¿Qué usaban antes de contratarte?"** — la
   respuesta vale más que cualquier búsqueda.
2. **"¿Cuál línea de tu negocio quieres analizar?"** — si vendes varias cosas, se elige una.
   Mezclar líneas produce un análisis que no sirve para ninguna.

Y una verdad incómoda que el sistema registra aunque no tenga anuncios: para muchos negocios
el competidor real no es otra empresa, es **"lo sigue haciendo a mano / en Excel"**. Si es tu
caso, queda anotado en el perfil, porque cambia contra qué compites en tus propios anuncios.

### El dato clave por competidor: su página de Facebook

Para cada confirmado, Claude busca **la dirección de su página de Facebook** (por ejemplo
`https://www.facebook.com/nombredelapagina`) y te la muestra para que valides que es la
correcta y no un homónimo. La captura se hace buscando el nombre de la marca, y esta página
es lo que permite después separar sus anuncios de los de cualquier otro que se llame
parecido.

Dos avisos que se dan aquí y no después:

- **Si el nombre del competidor es una palabra común** (un animal, un objeto, una palabra
  en inglés), la búsqueda de anuncios va a traer ruido de homónimos, a veces masivo. Queda
  anotado en la configuración para que la captura lo maneje aparte.
- Si no se encuentra página de Facebook verificable, el competidor queda igual, con la
  advertencia de que su captura puede no ser posible y el chequeo será manual.

Entre 3 y 8 competidores es el rango sano para partir.

## Paso 4 · El acceso a los datos, y lo que cuesta (dicho de frente)

Los anuncios salen de la Biblioteca de Anuncios de Meta, que es pública. Para capturarlos de
forma ordenada se usa un servicio llamado Apify. Lo que cuesta, con números:

- **Crear la cuenta es gratis y no pide tarjeta.** Trae US$5 de crédito cada mes.
- La captura cuesta alrededor de **US$0,50 por cada mil anuncios**. Nuestra corrida real de
  120 anuncios costó **US$0,074** — siete centavos de dólar.
- Con el crédito gratis alcanza para analizar 5-8 competidores todos los meses, de sobra.

**Pasos** (Claude te acompaña):

1. Crea tu cuenta entrando por este enlace: `https://www.apify.com?fpr=kr27nl` (correo y
   contraseña, sin tarjeta). Transparencia: es un enlace de referido del autor del sistema;
   a ti no te cambia el precio y a él le deja una comisión si algún día pasas a un plan
   pagado.
2. **Fija el tope de gasto ANTES de correr nada:** en la configuración de facturación de tu
   cuenta de Apify hay un límite mensual de uso. Ponlo en el monto que estés dispuesto a
   gastar (con el crédito gratis, US$5 basta). Sin tope, un error de configuración puede
   correr mil veces.
3. Copia tu **token** en `console.apify.com/settings/integrations` (la clave empieza con
   `apify_api_`). Esa clave es tuya: quien la tenga puede gastar tu crédito.
4. Guárdala **fuera** del archivo de configuración, de una de estas dos formas:
   - **La normal (cualquier sistema):** un archivo `.env` dentro de esta carpeta, con la
     línea `APIFY_TOKEN=tu_clave`. Puedes pegarle la clave a Claude para que lo escriba, o
     — si prefieres que la clave no pase por la conversación — crear tú el archivo con
     cualquier editor de texto y avisarle a Claude que ya está. El `.gitignore` del paquete
     impide que ese archivo se publique por accidente.
   - **La de Mac (opcional, más segura):** el Llavero del sistema, bajo el nombre exacto
     `apify-competencia`. Claude lo guarda con
     `security add-generic-password -s apify-competencia -a apify -w TU_CLAVE`
     y lo lee después sin mostrarlo. En Windows y Linux esta opción no existe: se usa el
     `.env`.

⛔ **La clave jamás se escribe en `configuracion.json`** ni en ningún archivo que pueda
terminar compartido. Y Claude jamás la muestra en pantalla: la usa por sustitución en el
momento de llamar a la API.

## Paso 5 · Dejar todo guardado

Claude escribe `configuracion.json` en esta carpeta, con esta forma:

```json
{
  "empresa": {
    "nombre": "Mi Empresa",
    "url": "https://miempresa.cl",
    "que_vende": "mantención de maquinaria para minería",
    "pais": "CL",
    "linea_analizada": "mantención preventiva"
  },
  "competidores": [
    {
      "nombre": "Competidor Uno",
      "url": "https://competidoruno.cl",
      "facebook": "https://www.facebook.com/competidoruno",
      "confirmado": "2026-08-09"
    }
  ],
  "que_vende_valores": ["mantencion", "repuestos", "arriendo", "otro"]
}
```

(`que_vende_valores` son las categorías de TU rubro para clasificar los anuncios; se definen
aquí, de una vez, siguiendo `contrato-de-patrones.md`.)

Y te dice, textual, con qué seguir:

> Listo. La configuración quedó en `configuracion.json` y tu clave quedó guardada aparte.
> Ahora pídeme "analiza la publicidad de mi competencia" y corre la skill `analizar`.

---

## Cuándo volver a correr esta skill

- Cuando agregues o saques un competidor.
- Cuando cambies la línea de negocio que analizas.
- Si cambias de computador (la clave de Apify hay que guardarla de nuevo).

Licencia MIT · Francisco Val
