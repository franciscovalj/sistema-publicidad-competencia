#!/usr/bin/env python3
"""
huella.py — el motor de cálculo del sistema operativo de la publicidad de tu competencia.

Responde UNA pregunta: de todo lo que tu competencia está pagando en Facebook e Instagram,
¿qué lleva tiempo corriendo, qué está en testeo, qué acaba de aparecer y qué acaba de morir?

LA IDEA CENTRAL
---------------
No se cuentan anuncios: se cuentan CREATIVOS. Los anunciantes duplican sus anuncios para
escalar (es la práctica normal), y cada duplicado sale con fecha nueva. Contar anuncios infla
todo y hace que los ganadores más escalados parezcan recién nacidos. Este programa agrupa por
HUELLA — el texto más el enlace de destino — y mide cada creativo una sola vez, desde la
fecha más antigua en que se vio.

Y el techo honesto, impreso al final de cada corrida: la antigüedad sirve para PRIORIZAR qué
mirar, no para rankear efectividad. Meta no publica el rendimiento de los anuncios comerciales,
y un anuncio malo con tope de costo puede seguir "activo" gastando casi nada.

USO
---
    python3 huella.py corridas/2026-08-09.csv
    python3 huella.py corridas/*.csv              (2+ corridas activan el radar de cambios)
    python3 huella.py corridas/*.csv --listar-creativos
    python3 huella.py corridas/*.csv --evergreen-dias 60

El CSV necesita al menos estas columnas (una fila por anuncio, ver el instructivo):
    fecha_captura, anunciante, texto, fecha_inicio
y acepta además: titulo, destino_url, formato, plataformas, cta, activo, variantes,
media_ia, url_biblioteca, y las columnas manuales del contrato de patrones
(angulo, protagonista, cifra_concreta, que_vende).

Licencia MIT · Francisco Val
"""

import argparse
import csv
import hashlib
import re
import sys
from collections import Counter, defaultdict
from datetime import date

EVERGREEN_DIAS = 45   # activo y sin variantes desde hace tanto = candidato a ganador probado
MIN_REPORTE = 10      # bajo esto, un patrón ni se reporta
MIN_SOLIDO = 30       # entre MIN_REPORTE y esto, es indicio y se dice en voz alta

COLS_MANUALES = ["angulo", "protagonista", "cifra_concreta", "que_vende"]

# La misma lista cerrada del contrato de patrones. Si tu rubro usa otra palabra de
# promoción, agrégala aquí ANTES de la primera corrida, nunca a la mitad.
PROMO_RX = re.compile(
    r"(\d+\s?%|gratis|descuento|oferta|cup[oó]n|2x1|env[ií]o gratis|rebaja|"
    r"promoci[oó]n|liquidaci[oó]n)",
    re.IGNORECASE,
)

FORMATOS = {"VIDEO": "video", "IMAGE": "imagen", "CAROUSEL": "carrusel",
            "MULTI_IMAGES": "carrusel", "DCO": "dco", "DPA": "catalogo",
            "video": "video", "imagen": "imagen", "carrusel": "carrusel",
            "dco": "dco", "catalogo": "catalogo"}


def fecha(s):
    try:
        return date.fromisoformat((s or "").strip()[:10])
    except ValueError:
        return None


def es_si(s):
    return (s or "").strip().lower() in {"true", "si", "sí", "1", "yes", "activo"}


def esta_activo(fila):
    """Si el CSV no trae la columna 'activo', se asume activo (la captura
    normal trae solo anuncios activos)."""
    valor = fila.get("activo")
    return True if valor is None else es_si(valor)


def huella_de(fila):
    clave = (fila.get("texto") or "").strip() + "|" + (fila.get("destino_url") or "").strip()
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()[:12]


def destino_de(url):
    u = (url or "").strip().lower()
    if not u:
        return "sin_enlace"
    dominio = re.sub(r"^https?://", "", u).split("/")[0]
    if "wa.me" in dominio or "whatsapp" in dominio:
        return "whatsapp"
    if "fb.me" in dominio or "facebook.com" in dominio or "fb.com" in dominio:
        return "facebook"
    if "instagram.com" in dominio:
        return "instagram"
    return "web_propia"


def cargar(rutas):
    filas = []
    for ruta in rutas:
        with open(ruta, encoding="utf-8-sig", newline="") as f:
            nuevas = list(csv.DictReader(f))
        if not nuevas:
            print(f"⚠️  {ruta} está vacío, se salta.")
            continue
        faltan = {"fecha_captura", "anunciante", "texto", "fecha_inicio"} - set(nuevas[0])
        if faltan:
            sys.exit(f"A {ruta} le faltan columnas obligatorias: {', '.join(sorted(faltan))}.\n"
                     f"Cada fila necesita al menos: fecha_captura, anunciante, texto, fecha_inicio.")
        filas.extend(nuevas)
    if not filas:
        sys.exit("No hay datos en ningún archivo.")
    for r in filas:
        r["_captura"] = fecha(r.get("fecha_captura"))
        r["_inicio"] = fecha(r.get("fecha_inicio"))
        if r["_captura"] is None:
            sys.exit("Hay filas sin fecha_captura válida (formato AAAA-MM-DD). "
                     "Es la fecha del día en que corriste la captura.")
    return filas


def mas_comun(valores):
    limpios = [v.strip() for v in valores if (v or "").strip()]
    return Counter(limpios).most_common(1)[0][0] if limpios else ""


def agrupar(filas):
    """Agrupa los anuncios por huella y arma un creativo por grupo."""
    grupos = defaultdict(list)
    for r in filas:
        grupos[huella_de(r)].append(r)

    ultima_corrida = max(r["_captura"] for r in filas)
    creativos = []
    for h, rs in grupos.items():
        inicios = [r["_inicio"] for r in rs if r["_inicio"]]
        capturas = [r["_captura"] for r in rs]
        primera_vez = min(inicios) if inicios else min(capturas)
        activa_hoy = any(esta_activo(r) and r["_captura"] == ultima_corrida for r in rs)
        capturas_activa = [r["_captura"] for r in rs if esta_activo(r)]
        ultima_activa = max(capturas_activa) if capturas_activa else max(capturas)

        texto = mas_comun([r.get("texto") or "" for r in rs]) or (rs[0].get("texto") or "")
        c = {
            "huella": h,
            "anunciante": mas_comun([r.get("anunciante") or "" for r in rs]),
            "texto": texto,
            "destino_url": (rs[0].get("destino_url") or "").strip(),
            "n_anuncios": len(rs),
            "primera_vez": primera_vez,
            "dias_visto": (ultima_activa - primera_vez).days,
            "activa": activa_hoy,
            "corridas": sorted({r["_captura"] for r in rs}),
            "formato": FORMATOS.get(mas_comun([r.get("formato") or "" for r in rs]), "otro"),
            "destino": destino_de(rs[0].get("destino_url")),
            "promocion": "si" if PROMO_RX.search(texto + " " + (rs[0].get("titulo") or "")) else "no",
            "variantes": "con_variantes"
                         if any(int(r.get("variantes") or 0) > 1 for r in rs) else "sin_variantes",
            "media_ia": "si" if any(es_si(r.get("media_ia")) for r in rs) else "no",
        }
        for col in COLS_MANUALES:
            etiquetas = {(r.get(col) or "").strip() for r in rs} - {""}
            if len(etiquetas) > 1:
                print(f"⚠️  El creativo {h} ({c['anunciante']}) tiene etiquetas distintas en "
                      f"'{col}': {sorted(etiquetas)}. Se usa la más frecuente; revisa el CSV.")
            c[col] = mas_comun([r.get(col) or "" for r in rs])
        creativos.append(c)
    return creativos, ultima_corrida


def mediana(nums):
    ns = sorted(nums)
    return ns[len(ns) // 2] if ns else None


def recorte(texto, largo=64):
    plano = " ".join((texto or "").split())
    return plano[:largo] + ("…" if len(plano) > largo else "")


def nombre(c, largo=28):
    return recorte(c["anunciante"] if isinstance(c, dict) else c, largo).ljust(largo + 1)


def seccion(titulo):
    print("\n" + ("─" * 96))
    print(titulo)
    print("─" * 96)


def listar_creativos(creas):
    """Modo para clasificar: una línea por creativo único, lista para etiquetar."""
    print("huella,anunciante,dias_visto,texto")
    for c in sorted(creas, key=lambda c: (c["anunciante"], -c["dias_visto"])):
        texto = (c["texto"] or "").replace('"', '""')
        print(f'{c["huella"]},"{c["anunciante"]}",{c["dias_visto"]},"{texto}"')


def imprimir_radar(creas, filas):
    corridas = sorted({r["_captura"] for r in filas})
    if len(corridas) < 2:
        print("\n⚠️  PRIMERA CORRIDA: la antigüedad de hoy sale de la fecha de inicio que")
        print("   reporta Meta, y esa fecha se resetea cada vez que el anunciante duplica.")
        print("   Desde la segunda corrida el sistema mide con su propia serie, que nadie")
        print("   puede resetear. Guarda este archivo: es el activo que se está construyendo.")
        return
    actual, anterior = corridas[-1], corridas[-2]
    en_actual = {c["huella"] for c in creas if actual in c["corridas"]}
    en_anterior = {c["huella"] for c in creas if anterior in c["corridas"]}
    altas = [c for c in creas if c["huella"] in en_actual - en_anterior]
    bajas = [c for c in creas if c["huella"] in en_anterior - en_actual]

    seccion(f"RADAR DE CAMBIOS · {anterior} → {actual}")
    print(f"Creativos nuevos: {len(altas)}   ·   desaparecidos: {len(bajas)}")
    for titulo, lote in (("── Nuevos (lo que acaban de lanzar):", altas),
                         ("── Desaparecidos (lo que apagaron o murió):", bajas)):
        if lote:
            print(f"\n{titulo}")
            for c in sorted(lote, key=lambda c: c["anunciante"])[:15]:
                print(f'   {nombre(c)} {recorte(c["texto"])}')
            if len(lote) > 15:
                print(f"   … y {len(lote) - 15} más.")


def imprimir_evergreen(creas, umbral):
    ganadores = sorted((c for c in creas
                        if c["activa"] and c["dias_visto"] >= umbral
                        and c["variantes"] == "sin_variantes"),
                       key=lambda c: -c["dias_visto"])
    seccion(f"PARA MIRAR PRIMERO · activos hace {umbral}+ días y sin variantes en testeo ({len(ganadores)})")
    print("Si alguien sostiene el gasto en el mismo creativo por meses, algo está viendo.")
    print("Eso PRIORIZA qué estudiar; no prueba que funcione (ese dato no es público).\n")
    print(f'{"días":>5}  {"anunciante":29} {"destino":10} texto')
    for c in ganadores[:20]:
        print(f'{c["dias_visto"]:>5}  {nombre(c)} {c["destino"]:10} {recorte(c["texto"], 44)}')
    if len(ganadores) > 20:
        print(f"       … y {len(ganadores) - 20} más.")


def imprimir_anunciantes(creas):
    seccion("QUIÉN TESTEA Y QUIÉN ESCALA · por anunciante")
    print("Muchos creativos nuevos = está buscando. Pocos y viejos = ya encontró.\n")
    por_marca = defaultdict(list)
    for c in creas:
        por_marca[c["anunciante"]].append(c)
    print(f'{"anunciante":29} {"creat.":>7} {"anuncios":>9} {"en testeo":>9} {"med. días":>10}')
    orden = sorted(por_marca.items(), key=lambda kv: -len(kv[1]))
    for marca, cs in orden[:15]:
        en_test = sum(1 for c in cs if c["variantes"] == "con_variantes")
        print(f'{nombre(marca)} {len(cs):>7} {sum(c["n_anuncios"] for c in cs):>9} '
              f'{en_test:>8} {mediana([c["dias_visto"] for c in cs]):>10}')
    if len(orden) > 15:
        print(f"… y {len(orden) - 15} anunciantes más.")


def imprimir_mezcla(creas):
    seccion("LA MEZCLA DEL MERCADO · sobre creativos únicos")
    n = len(creas)
    for col, titulo in (("formato", "Formato"), ("destino", "A dónde mandan el clic"),
                        ("promocion", "Con promoción en el texto"), ("media_ia", "Declaran media con IA")):
        cuenta = Counter(c[col] for c in creas)
        partes = " · ".join(f"{v} {k*100//n}% ({k})"
                            for v, k in cuenta.most_common())
        print(f"{titulo:26} {partes}")
    print("\n('dco' = contenido dinámico: Meta combina piezas automáticamente, firma de testeo masivo."
          " 'media_ia' es autodeclarado.)")


def imprimir_patrones(creas):
    presentes = [col for col in COLS_MANUALES
                 if sum(1 for c in creas if c.get(col)) > 0]
    columnas = ["formato", "destino", "promocion", "variantes"] + presentes
    seccion("PATRONES · frecuencia y cuánto les dura")
    print("Se lee así: qué tan común es el patrón, y si las creativos que lo usan llevan")
    print("más o menos días corriendo que las que no. Días de vida, NO efectividad.\n")
    for col in columnas:
        valores = sorted({c.get(col) or "" for c in creas} - {""})
        if not 1 < len(valores) <= 12:
            continue
        print(f"── {col} ".ljust(96, "─"))
        for v in valores:
            con = [c for c in creas if (c.get(col) or "") == v]
            sin = [c for c in creas if (c.get(col) or "") and (c.get(col) or "") != v]
            if len(con) < MIN_REPORTE:
                print(f"   {v:26} n={len(con):<4} — bajo {MIN_REPORTE} casos, no se reporta "
                      f"(no es 'no funciona': es 'no hay datos')")
                continue
            m_con, m_sin = mediana([c["dias_visto"] for c in con]), mediana([c["dias_visto"] for c in sin])
            aviso = f"  ⚠️ indicio (n bajo {MIN_SOLIDO})" if len(con) < MIN_SOLIDO else ""
            print(f"   {v:26} n={len(con):<4} mediana {m_con:>4}d   resto {m_sin:>4}d   "
                  f"Δ{m_con - m_sin:+5}d{aviso}")
        print()


def main():
    ap = argparse.ArgumentParser(
        description="Mide qué está pagando tu competencia en Meta, por creativo único.")
    ap.add_argument("csv", nargs="+", help="una o más corridas (corridas/*.csv)")
    ap.add_argument("--evergreen-dias", type=int, default=EVERGREEN_DIAS,
                    help=f"umbral de días para la tabla de veteranos (por defecto {EVERGREEN_DIAS})")
    ap.add_argument("--listar-creativos", action="store_true",
                    help="imprime las creativos únicos en CSV, listas para clasificar")
    args = ap.parse_args()

    filas = cargar(args.csv)
    creas, ultima = agrupar(filas)

    if args.listar_creativos:
        listar_creativos(creas)
        return

    print("=" * 96)
    print("QUÉ ESTÁ PAGANDO TU COMPETENCIA")
    print("=" * 96)
    dup = (1 - len(creas) / len(filas)) * 100
    print(f"Anuncios leídos: {len(filas)}  →  creativos únicos: {len(creas)} "
          f"({dup:.0f}% eran duplicados)   ·   anunciantes: {len({c['anunciante'] for c in creas})}")
    print(f"Corridas: {len({r['_captura'] for r in filas})}   ·   última captura: {ultima}   ·   "
          f"activos hoy: {sum(1 for c in creas if c['activa'])}")

    imprimir_radar(creas, filas)
    imprimir_evergreen(creas, args.evergreen_dias)
    imprimir_anunciantes(creas)
    imprimir_mezcla(creas)
    imprimir_patrones(creas)

    print("=" * 96)
    print("CÓMO LEER TODO ESTO")
    print("=" * 96)
    print("· Los días de vida PRIORIZAN qué mirar. No rankean efectividad: Meta no publica el")
    print("  rendimiento de anuncios comerciales, y un anuncio malo con tope de costo puede")
    print("  seguir 'activo' gastando casi nada.")
    print("· 'sin variantes' + meses corriendo = alguien sostiene el gasto ahí. Es la mejor")
    print("  señal pública disponible, y sigue siendo una señal, no una prueba.")
    print("· Un patrón con n chica no se concluye. 0 casos no es 'nadie lo hace': puede ser")
    print("  que la captura no lo trajo.")
    print("· La señal más valiosa (qué aparece y qué muere) solo existe si guardas cada")
    print("  corrida. Este análisis mejora solo con repetirlo: misma carpeta, cada 2-4 semanas.")


if __name__ == "__main__":
    main()
