# Historial de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Este sistema usa [versionado semántico](https://semver.org/lang/es/).

---

## [2.0.1] · 2026-09-11

Corrección de seguridad en cómo se le pide a Claude que hable con Apify.

### Corregido

- **La clave de Apify viaja ahora en la cabecera `Authorization: Bearer`**, no como parámetro
  de la dirección. La documentación de Apify marca esa segunda forma como *"Less secure"*,
  porque una dirección queda escrita en los registros del servidor y del proxy; el RFC 6750
  §2.3 dice que no debe usarse cuando la cabecera es posible. Afecta las tres llamadas del
  procedimiento de análisis.
- **El README ya no promete que basta con abrir Claude Code dentro de la carpeta
  descomprimida.** No basta: Claude Code registra las skills desde `.claude/skills/`, así que
  hay que copiar la carpeta ahí. Comprobado en una instalación limpia.

### Por qué sube la versión y no solo se reemplaza el archivo

Claude Code solo entrega actualizaciones cuando cambia el campo `version` del manifiesto. Con
la 2.0.0 congelada, quien ya lo tuviera instalado no recibiría nunca esta corrección.

## [2.0.0] · 2026-09-10

Reestructuración completa contra el estándar de skills de Anthropic. **Si vienes de la 1.0,
lee "Cómo migrar" abajo: las rutas cambiaron.**

### Cambiado

- **Las dos skills son una.** `configurar` y `analizar` se fusionaron en
  `publicidad-competencia`, que mira el disco y decide sola cuál flujo corresponde. Antes
  había que elegir entre dos nombres parecidos sin saber cuál se necesitaba.
- **Una sola frase para todo.** "analiza la publicidad de mi competencia" sirve la primera vez
  y todas las siguientes. Si falta configuración, se hace primero, sin comando aparte.
- **Los archivos de apoyo viven dentro de la carpeta de la skill.** La calculadora, la
  plantilla del informe y el contrato de patrones estaban en la raíz del repositorio con rutas
  relativas a ella. Correcto para la vía del archivo comprimido, roto para un plugin: un plugin
  se instala en la carpeta de plugins mientras Claude sigue parado en el proyecto del usuario.
- **Las salidas van a `datos/` e `informes/`**, dentro de la carpeta de tu empresa, en vez de a
  `corridas/` colgando de la raíz. Eso permite además analizar varias empresas sin que una pise
  a la otra.
- **La configuración se llama `configuracion-competencia.json`** (antes `configuracion.json`) y
  vive en la carpeta de la empresa, no en la raíz.
- **La guía de instalación pasó de 6 pasos a 5**, con la instalación por plugin adelante.

### Agregado

- **Instalación en dos líneas** con `/plugin marketplace add` y `/plugin install`, gracias a
  `.claude-plugin/plugin.json` y `.claude-plugin/marketplace.json`.
- **Sección de seguridad en el README:** qué programas ejecuta el sistema, a qué sitios sale a
  internet, qué hace con tu clave y qué permisos pide.
- **Instrucciones de instalación en el README** para las tres vías: plugin, archivo comprimido
  y copia a `.claude/skills/`.
- **Validación continua** con `claude plugin validate --strict` en cada cambio.
- **Este historial de cambios.**

### Cómo migrar desde la 1.0

Tu trabajo anterior no se pierde, pero hay que moverlo de lugar:

1. Instala la versión nueva con las dos líneas del README.
2. Crea una carpeta para tu empresa y, dentro, una carpeta `datos/`.
3. Mueve ahí los archivos `.csv` que tenías en `corridas/`. **Son tu activo: la serie histórica
   no se puede reconstruir hacia atrás.**
4. Mueve `configuracion.json` a esa misma carpeta y renómbralo a
   `configuracion-competencia.json`. Agrégale una línea `"carpeta": "<ruta de esa carpeta>"`, o
   pídele a Claude que lo haga.
5. Tu clave de Apify sigue donde estaba y no hay que tocarla.

---

## [1.0] · 2026-08-11

Primera versión pública.

### Agregado

- Dos instructivos, `configurar` y `analizar`, para operar el sistema desde Claude Code.
- `huella.py`: agrupa los anuncios por creativo real (texto más destino), mide la antigüedad
  desde la primera vez que se vio cada uno, y compara corridas entre sí para detectar qué
  apareció y qué desapareció.
- `contrato-de-patrones.md`: categorías cerradas de clasificación, con desempates definidos.
- `plantilla-informe.html` y `renderizar_pdf.py`: el informe en PDF, con el navegador que ya
  tengas, en Mac, Windows o Linux.
- Dos corridas de ejemplo con datos inventados, para probar la calculadora sin gastar.
- Guía de instalación en PDF.
- Enlace de referido de Apify, declarado como tal en el README y en la guía.

[2.0.0]: https://github.com/franciscovalj/sistema-publicidad-competencia/releases/tag/v2.0.0
[1.0]: https://github.com/franciscovalj/sistema-publicidad-competencia/releases/tag/v1.0
