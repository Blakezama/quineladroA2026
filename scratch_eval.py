"""
DIAGNÓSTICO ENFOCADO - FARMACIA TENERIFE + TOP RANKING
=======================================================
"""
import os, sys, re
from datetime import datetime

try:
    import psycopg2, psycopg2.extras
except ImportError:
    os.system(f"{sys.executable} -m pip install psycopg2-binary -q")
    import psycopg2, psycopg2.extras

DATABASE_URL = "postgresql://postgres.uktaufrmiowqssixllkr:MBCfxEZFvCoPWEKj@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

def ganador_real(ga, gb):
    if ga is None or gb is None: return "?"
    return "A" if ga > gb else ("B" if gb > ga else "E")

def calcular_pts(voto_g, ga_pred, gb_pred, res_g, res_ga, res_gb):
    acierto_g = (voto_g == res_g)
    acierto_m = (res_ga is not None and ga_pred == res_ga and gb_pred == res_gb)
    if acierto_m:   return 5, "EXACTO"
    elif acierto_g: return 3, "GANADOR"
    return 0, "FALLO"

print("Conectando a Supabase...")
conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor, connect_timeout=10)
cur  = conn.cursor()
print("OK!\n")

# ─── ESTADÍSTICAS GENERALES ────────────────────────────────────────────────
cur.execute("SELECT COUNT(*) AS c FROM usuario");              total_u  = cur.fetchone()['c']
cur.execute("SELECT COUNT(*) AS c FROM partido");              total_p  = cur.fetchone()['c']
cur.execute("SELECT COUNT(*) AS c FROM partido WHERE estado='finished'"); fin = cur.fetchone()['c']
cur.execute("SELECT COUNT(*) AS c FROM voto");                 total_v  = cur.fetchone()['c']
cur.execute("SELECT COUNT(*) AS c FROM partido WHERE estado='finished' AND (goles_a IS NULL OR goles_b IS NULL)"); sg = cur.fetchone()['c']

print("=" * 60)
print("  ESTADO GENERAL (Produccion Supabase)")
print("=" * 60)
print(f"  Usuarios totales        : {total_u}")
print(f"  Partidos en BD          : {total_p}")
print(f"  Partidos FINALIZADOS    : {fin}   <-- CRITICO")
print(f"  Finalizados sin goles   : {sg}")
print(f"  Total votos registrados : {total_v}")

# ─── PARTIDOS FINALIZADOS ──────────────────────────────────────────────────
cur.execute("SELECT id, equipo_a, equipo_b, goles_a, goles_b FROM partido WHERE estado='finished' ORDER BY id")
partidos_fin = cur.fetchall()

print("\n" + "-" * 60)
print("  PARTIDOS FINALIZADOS (que generan puntos)")
print("-" * 60)
resultados_reales = {}
if not partidos_fin:
    print("  ** NINGUNO -> TODOS TIENEN 0 PUNTOS **")
else:
    for p in partidos_fin:
        gr = ganador_real(p['goles_a'], p['goles_b'])
        resultados_reales[p['id']] = {'ganador_real': gr, 'goles_a': p['goles_a'], 'goles_b': p['goles_b']}
        gstr = f"{p['goles_a']}-{p['goles_b']}" if p['goles_a'] is not None else "??-??"
        print(f"  [P{p['id']:02d}] {p['equipo_a']:<18} vs {p['equipo_b']:<18}  {gstr}  Ganador={gr}")

# ─── BUSCAR FARMACIA TENERIFE (nombre exacto o parcial) ───────────────────
print("\n" + "=" * 60)
print("  BUSQUEDA DE FARMACIA TENERIFE")
print("=" * 60)

cur.execute("SELECT * FROM usuario WHERE LOWER(nombre) LIKE '%tenerife%' OR LOWER(email) LIKE '%tenerife%'")
candidatos = cur.fetchall()

if not candidatos:
    print("  NO encontrado por nombre/email.")
    # Buscar por otras palabras clave que podría usar
    print("  Buscando con otras palabras clave...")
    cur.execute("SELECT id, nombre, email FROM usuario ORDER BY id LIMIT 700")
    todos = cur.fetchall()
    print(f"  Mostrando usuarios con 'tener' o 'ten' en nombre:")
    for u in todos:
        if 'ten' in u['nombre'].lower() or 'ten' in u['email'].lower():
            print(f"    ID {u['id']:>4}: {u['nombre']:<35} {u['email']}")
else:
    for fcia in candidatos:
        print(f"\n  ENCONTRADO -> ID {fcia['id']}: {fcia['nombre']}  ({fcia['email']})")

        cur.execute("""
            SELECT v.id, v.voto_ganador, v.goles_a_prediccion, v.goles_b_prediccion,
                   v.fecha_voto, v.partido_id,
                   p.equipo_a, p.equipo_b, p.goles_a, p.goles_b, p.estado
            FROM voto v JOIN partido p ON v.partido_id = p.id
            WHERE v.usuario_id = %s ORDER BY v.partido_id
        """, (fcia['id'],))
        votos = cur.fetchall()

        print(f"  Votos registrados: {len(votos)}\n")
        if votos:
            print(f"  {'Partido':<33} {'Mi voto':^9} {'Real':^9} {'Estado':^12} {'Pts':>4}  Tipo")
            print(f"  {'-'*33} {'-'*9} {'-'*9} {'-'*12} {'-'*4}  {'-'*8}")

            pts_total = 0; exactos = 0; gana = 0; fallos = 0; pend = 0
            for v in votos:
                pstr  = f"{v['equipo_a']} vs {v['equipo_b']}"
                pred  = f"{v['voto_ganador']}({v['goles_a_prediccion']}-{v['goles_b_prediccion']})"
                if v['estado'] == 'finished':
                    gr = ganador_real(v['goles_a'], v['goles_b'])
                    pts, tipo = calcular_pts(v['voto_ganador'], v['goles_a_prediccion'], v['goles_b_prediccion'],
                                             gr, v['goles_a'], v['goles_b'])
                    real = f"{gr}({v['goles_a']}-{v['goles_b']})"
                    pts_total += pts
                    if tipo == "EXACTO": exactos += 1
                    elif tipo == "GANADOR": gana += 1
                    else: fallos += 1
                else:
                    pts, tipo, real = "-", "PENDIENTE", v['estado']
                    pend += 1
                print(f"  {pstr:<33} {pred:^9} {real:^9} {v['estado']:^12} {str(pts):>4}  {tipo}")

            print(f"\n  RESUMEN:")
            print(f"    Exactos  (+5): {exactos}  -> {exactos*5} pts")
            print(f"    Ganadores(+3): {gana}  -> {gana*3} pts")
            print(f"    Fallos   ( 0): {fallos}")
            print(f"    Pendientes   : {pend}  (aun no finalizados)")
            print(f"    >>> PUNTOS TOTALES ACTUALES = {pts_total} <<<")
        else:
            print("  ** Sin votos registrados **")

# ─── TOP 25 DEL RANKING ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  TOP 25 RANKING + POSICION FARMACIA TENERIFE")
print("=" * 60)

cur.execute("SELECT id, nombre FROM usuario")
todos_u = cur.fetchall()

ranking = []
for u in todos_u:
    cur.execute("SELECT * FROM voto WHERE usuario_id = %s", (u['id'],))
    votos_u = cur.fetchall()
    pts = 0; exac = 0; diff = 0; ult = None
    for v in votos_u:
        if v['fecha_voto']:
            fv = v['fecha_voto'] if isinstance(v['fecha_voto'], datetime) else datetime.fromisoformat(str(v['fecha_voto']))
            if ult is None or fv > ult: ult = fv
        if v['partido_id'] in resultados_reales:
            res = resultados_reales[v['partido_id']]
            p2, t2 = calcular_pts(v['voto_ganador'], v['goles_a_prediccion'], v['goles_b_prediccion'],
                                   res['ganador_real'], res['goles_a'], res['goles_b'])
            pts += p2
            if t2 == "EXACTO": exac += 1
            elif t2 == "GANADOR": diff += 1
    ranking.append({'id': u['id'], 'nombre': u['nombre'], 'puntos': pts,
                    'exactos': exac, 'diffs': diff, 'votos': len(votos_u), 'ultima': ult})

ranking.sort(key=lambda x: (-x['puntos'], -x['exactos'], -x['diffs'],
                             x['ultima'] if x['ultima'] else datetime.max))

# Asignar posición
pos = 1
for i, r in enumerate(ranking):
    if i > 0 and (r['puntos'] != ranking[i-1]['puntos'] or r['exactos'] != ranking[i-1]['exactos']):
        pos = i + 1
    r['posicion'] = pos

es_farmacia = lambda n: 'tenerife' in n.lower() or 'farmacia' in n.lower()

print(f"\n  {'Pos':>3}  {'Nombre':<28} {'Pts':>5}  {'Exactos':>7}  {'Gana':>5}  {'Votos':>5}")
print(f"  {'-'*3}  {'-'*28} {'-'*5}  {'-'*7}  {'-'*5}  {'-'*5}")
for r in ranking[:25]:
    marca = " <<" if es_farmacia(r['nombre']) else ""
    print(f"  {r['posicion']:>3}  {r['nombre']:<28} {r['puntos']:>5}  {r['exactos']:>7}  {r['diffs']:>5}  {r['votos']:>5}{marca}")

# Posición de Farmacia Tenerife
farm_entries = [r for r in ranking if es_farmacia(r['nombre']) or 'tenerife' in r['nombre'].lower()]
if farm_entries:
    print(f"\n  [FARMACIA TENERIFE en el ranking]")
    for r in farm_entries:
        print(f"    Posicion {r['posicion']:>3} de {len(ranking)} -> {r['nombre']} | {r['puntos']} pts | {r['exactos']} exactos | {r['votos']} votos")

print("\n" + "=" * 60 + "\n")
cur.close(); conn.close()
