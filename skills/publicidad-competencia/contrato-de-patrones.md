# Contrato de patrones — cómo se clasifica cada anuncio

Este archivo define **con qué categorías** se clasifica la publicidad de tu competencia.
Existe por una razón concreta: sin categorías cerradas, la clasificación deriva. Se empieza
etiquetando con un criterio y a los 200 anuncios se está usando otro, sin darse cuenta.

Cuando eso pasa, el análisis mide el cambio de criterio, no la publicidad.

---

## Primero: se clasifica el CREATIVO, no el anuncio

Los anunciantes duplican sus anuncios (es la práctica normal para escalar), así que el mismo
texto aparece varias veces con distinta fecha. Antes de clasificar, la calculadora agrupa por
**huella del creativo** (el texto más el enlace de destino) y deja una fila por creativo
único. En nuestra experiencia, cerca de la mitad de los anuncios capturados son duplicados.

**Se clasifica cada creativo único una sola vez.** Clasificar los duplicados por separado
infla los conteos y duplica el trabajo.

---

## ⛔ Regla cero — nunca inventes una etiqueta

**Cada etiqueta viene de haber leído ese anuncio.** Está prohibido:

- deducirla de otro anuncio parecido, aunque sea del mismo anunciante
- deducirla del título o de las primeras palabras sin leer el resto
- completar "por consistencia" con las anteriores
- rellenar las últimas de una tanda para cuadrar el conteo

Si un anuncio no se pudo leer (texto vacío o ilegible), se marca `error` y se deja fuera.

> Una etiqueta faltante es un dato que se recupera. Una inventada corrompe el análisis
> y **no se puede detectar después**.

---

## Las dos familias de dimensiones

Hay dimensiones que **calcula el programa** (nadie las etiqueta a mano, y por eso no derivan
jamás) y dimensiones que **etiqueta Claude leyendo cada creativo**. No las mezcles: si una
dimensión es del programa, no se corrige a mano.

---

## Dimensiones del programa (las calcula `huella.py`)

| Dimensión | Valores | De dónde sale |
|---|---|---|
| `formato` | `video` · `imagen` · `carrusel` · `dco` · `catalogo` · `otro` | el campo de formato del anuncio |
| `destino` | `web_propia` · `whatsapp` · `facebook` · `instagram` · `sin_enlace` | el dominio del enlace de destino |
| `promocion` | `si` · `no` | lista cerrada de señales en el texto |
| `variantes` | `con_variantes` · `sin_variantes` | si el anuncio corre junto a variantes de sí mismo |
| `media_ia` | `si` · `no` | lo que el propio anunciante declara |
| `dias_visto` | número | cuánto lleva corriendo ese creativo |

Notas que importan al leerlas:

- **`dco`** es el contenido dinámico: Meta arma combinaciones automáticas de piezas. Es la
  firma de un anunciante en testeo masivo.
- **`catalogo`** (DPA) es el anuncio dinámico de productos: retargeting sobre el catálogo de
  la tienda. Su texto suele ser genérico ("vuelve por lo que viste"); lo que informa es su
  presencia y cuánto lleva corriendo, no su texto.
- **`promocion`** se detecta con esta lista cerrada, y solo con ella: porcentajes de descuento,
  "gratis", "descuento", "oferta", "cupón", "2x1", "envío gratis", "rebaja", "promoción",
  "liquidación". Si tu rubro usa otra palabra de promoción, agrégala al programa ANTES de la
  primera corrida, nunca a la mitad.
- **`sin_variantes`** NO significa "ganador". Significa que no está en testeo. Ganador probable es
  otra cosa: sin variantes Y con más de 45 días corriendo, y eso lo marca la calculadora.
- **`media_ia`** es autodeclarado por el anunciante. Que diga `no` no prueba que no haya IA.

---

## Dimensiones manuales (las etiqueta Claude, leyendo)

### Dimensión 1 · `angulo` — con qué abre el anuncio

Deciden **las dos primeras líneas** del texto (lo que se ve antes del "Ver más"), no el resto.

| Valor | Cuándo |
|---|---|
| `promesa_de_resultado` | promete un resultado concreto al lector ("vende más", "ahorra 10 horas") |
| `dolor` | abre nombrando el problema, el error o la frustración del lector |
| `caso_de_tercero` | abre con lo que logró o vivió alguien concreto que no es el anunciante |
| `oferta_directa` | abre con el precio, el descuento o la oferta misma |
| `novedad` | abre anunciando algo nuevo ("ya llegó", "lanzamos", "nuevo") |
| `autoridad` | abre con credenciales: años, premios, cantidad de clientes |
| `curiosidad` | abre con intriga, sin promesa ni dolor explícito |
| `otro` | no cabe en ninguno |

**Desempates, en este orden:**

1. Si en las dos primeras líneas hay precio o descuento, es `oferta_directa`, aunque además
   prometa.
2. Si hay un tercero concreto Y una promesa, gana `caso_de_tercero` (lo específico le gana a
   lo genérico).
3. Una pregunta que promete resultado ("¿imaginas vender 40 pedidos diarios?") es
   `promesa_de_resultado`. Una que nombra el problema es `dolor`. Una que solo intriga es
   `curiosidad`.

### Dimensión 2 · `protagonista` — quién está en la primera línea

| Valor | Cuándo |
|---|---|
| `tu` | la primera línea le habla al lector o describe su situación |
| `un_tercero` | una persona o negocio concreto que no es el anunciante ni el lector |
| `la_marca` | el anunciante o su producto ("en X llevamos...", "Y hace todo por ti") |
| `nadie` | un tema, una idea o un grupo genérico ("muchos negocios", "la gente") |

**Desempate:** decide la primera línea, no el resto. El tercero tiene que ser concreto: "una
tienda de ropa en Antofagasta" es `un_tercero`; "las tiendas de ropa" es `nadie`.

### Dimensión 3 · `cifra_concreta` — ¿hay un número de resultado?

`si` cuando el texto trae una cifra verificable de resultado, escala o uso: pedidos, horas
ahorradas, clientes, porcentaje de mejora.

**Desempates:** el precio, las cuotas y el descuento NO cuentan (ya los captura `promocion`).
La fecha o la hora de un evento tampoco. "Más de 500 clientes" sí cuenta (es autoridad, pero es
cifra). En la duda, `no`.

### Dimensión 4 · `que_vende` — qué ofrece de verdad el anuncio

Esta dimensión **la defines tú**, con las palabras de tu rubro. Entre 4 y 8 valores, cerrados,
decididos ANTES de empezar a clasificar. Ejemplo para un rubro de equipamiento (inventado):

`producto_nuevo` · `usado` · `arriendo` · `servicio_tecnico` · `repuestos` · `otro`

⚠️ Si tienes más de 8 valores, no tienes categorías: tienes títulos. Agrupa.

---

## Prueba de que el contrato funciona

Antes de clasificar todo, **clasifica 20 creativos dos veces, sin mirar la primera tanda**.
Si clasifica una persona, con una hora de separación basta; si clasifica Claude, la segunda
pasada se hace en una conversación nueva (sin la primera a la vista, o se copia sin querer).
Si más de 2 de las 20 salen distintas, el contrato no está lo bastante cerrado: hay que
precisar los desempates antes de seguir.

Es media hora que ahorra tener que reclasificar 200.

---

## Una honestidad sobre el método

Estas categorías describen **la forma** de los anuncios: con qué abren, a quién le hablan, qué
ofrecen. La forma es lo que se puede clasificar de manera consistente; la intención del
anunciante, casi nunca.

Y ninguna dimensión mide rendimiento. Nadie fuera del anunciante sabe qué anuncio le convierte:
Meta no publica ese dato para anuncios comerciales. Lo que este contrato permite es contar qué
hace tu competencia y cuánto tiempo lo sostiene, que es la mejor señal pública disponible, no
una medición de resultados.

Licencia MIT.
