"""NIVEL 1: caracterizacion bibliometrica de B1 (642) + intersecciones. Solo metadatos."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, numpy as np, re, json

OUT = 'out'
B = {k: pd.read_csv(f'data/{k}_scopus_20261012.csv')
     for k in ['B1', 'B1b', 'B2', 'B3']}
b1 = B['B1']; N = len(b1)
s = {k: set(d['EID']) for k, d in B.items()}

tabla = {}

# ---- T1a: evolucion temporal ----------------------------------------------
t1a = b1['Year'].value_counts().sort_index().rename('n').to_frame()
t1a['%'] = (t1a['n'] / N * 100).round(1)
t1a['acum_%'] = t1a['%'].cumsum().round(1)
tabla['T1a_anio'] = t1a

# ---- T1b: tipo documental y estatus editorial ------------------------------
t1b = pd.crosstab(b1['Document Type'], b1['Publication Stage'], margins=True, margins_name='Total')
tabla['T1b_tipo_estatus'] = t1b

# ---- T1c: acceso abierto ---------------------------------------------------
oa = b1['Open Access'].notna()
t1c = pd.DataFrame({'n': [oa.sum(), (~oa).sum()], '%': [oa.mean()*100, (~oa).mean()*100]},
                   index=['Acceso abierto', 'Acceso restringido']).round(1)
tabla['T1c_acceso'] = t1c

# ---- T1d: dispersion por fuente (ley de Bradford simplificada) -------------
fs = b1['Source title'].value_counts()
t1d = pd.DataFrame({
    'Fuentes distintas': [fs.size],
    'Fuente mas frecuente (n)': [fs.iloc[0]],
    '% del corpus en la fuente mas frecuente': [round(fs.iloc[0]/N*100, 1)],
    '% del corpus en las 10 fuentes mayores': [round(fs.head(10).sum()/N*100, 1)],
    'Fuentes con un solo documento': [int((fs == 1).sum())],
    '% del corpus en fuentes con un solo documento': [round((fs == 1).sum()/N*100, 1)],
    'Indice de concentracion (Herfindahl)': [round(float(((fs/N)**2).sum()), 4)],
}).T.rename(columns={0: 'valor'})
tabla['T1d_dispersion'] = t1d

# ---- T1e: campo disciplinar (INFERIDO del titulo de la fuente) -------------
DISC = [
 ('Marketing y consumo',      r'market|consum|retail|advertis|brand|commerce|business|manageri|macromarket'),
 ('Comunicacion y medios',    r'communicat|media|journalis|press|broadcast'),
 ('Computacion, IS y HCI',    r'comput|informat|human-?comput|hci|chi\b|intellig|data|system|software|ceur|acm|ieee|lecture notes|machine learning'),
 ('Etica, derecho y politica', r'ethic|law|legal|polic|right|justice|regulat|govern|philos|topoi'),
 ('Psicologia y conducta',    r'psycholog|behavio|cognit|mind|personality'),
 ('Sostenibilidad y ambiente', r'sustainab|environment|clean|energ|climate|green'),
 ('Educacion',                r'educat|learning|teach|pedago|curricul'),
 ('Salud',                    r'health|medic|nurs|clinic|psychiatr'),
]
def disc(x):
    t = str(x).lower()
    for nombre, pat in DISC:
        if re.search(pat, t):
            return nombre
    return 'Otros / no clasificado'
b1['campo_inferido'] = b1['Source title'].apply(disc)
t1e = b1['campo_inferido'].value_counts().rename('n').to_frame()
t1e['%'] = (t1e['n']/N*100).round(1)
tabla['T1e_campo_INFERIDO'] = t1e

# ---- T2: intersecciones entre literaturas (OE3) ----------------------------
t2 = pd.DataFrame([
 ['B1  Constructo (bloque A)',                      len(s['B1']), '100.0', 'Corpus de caracterizacion'],
 ['B1b Constructo ampliado (sensibilidad)',         len(s['B1b']), f"{len(s['B1b'])/len(s['B1'])*100-100:+.1f} vs B1", 'Anade "consumer agency" y "algorithmic nudg*"'],
 ['B2  Arquitectura algoritmica x consumidor',      len(s['B2']), '-', 'Bloque A ampliado AND bloque B'],
 ['B3  Arquitectura algoritmica x sostenible',      len(s['B3']), '-', 'Bloque A ampliado AND bloque C'],
 ['B1 ∩ B2',                                        len(s['B1'] & s['B2']), f"{len(s['B1']&s['B2'])/len(s['B1'])*100:.1f}% de B1", 'Constructo con vocabulario de consumidor'],
 ['B1 ∩ B3',                                        len(s['B1'] & s['B3']), f"{len(s['B1']&s['B3'])/len(s['B1'])*100:.1f}% de B1", 'Constructo con vocabulario sostenible'],
 ['B2 ∩ B3',                                        len(s['B2'] & s['B3']), f"{len(s['B2']&s['B3'])/len(s['B2'])*100:.1f}% de B2", 'Consumidor y sostenible'],
 ['B1 ∩ (B2 ∪ B3)  = nucleo de codificacion',       len(s['B1'] & (s['B2'] | s['B3'])), f"{len(s['B1']&(s['B2']|s['B3']))/len(s['B1'])*100:.1f}% de B1", 'Corpus del Nivel 2'],
 ['Union de las cuatro busquedas',                  len(set().union(*s.values())), '-', 'Registros unicos recuperados'],
], columns=['Conjunto', 'n', 'Proporcion', 'Nota'])
tabla['T2_intersecciones'] = t2

# ---- cuanto del bloque A aporta cada termino en B1 -------------------------
A = ['algorithmic agency','consumer autonomy','algorithmic manipulation','algorithmic curation',
     'illusion of autonomy','algorithmic bounded rationality','algorithmic consumer culture','algorithmic authority']
txt = (b1['Title'].fillna('')+' '+b1['Abstract'].fillna('')+' '+
       b1['Author Keywords'].fillna('')+' '+b1['Index Keywords'].fillna('')).str.lower()
t3 = pd.DataFrame({'termino': A,
                   'n': [int(txt.str.contains(re.escape(t)).sum()) for t in A]})
t3['%'] = (t3['n']/N*100).round(1)
t3 = t3.sort_values('n', ascending=False)
tabla['T3_terminos'] = t3

for k, v in tabla.items():
    print('\n' + '='*70); print(k); print('='*70)
    print(v.to_string())
    v.to_csv(f'{OUT}/{k}.csv')

# ---- PRISMA preliminar -----------------------------------------------------
prisma = {
 'identificacion_B1': len(s['B1']), 'identificacion_B1b_adicionales': len(s['B1b']-s['B1']),
 'identificacion_B2': len(s['B2']), 'identificacion_B3': len(s['B3']),
 'identificacion_total_registros': sum(len(v) for v in s.values()),
 'duplicados_eliminados': sum(len(v) for v in s.values()) - len(set().union(*s.values())),
 'registros_unicos': len(set().union(*s.values())),
 'nivel1_corpus_caracterizacion': len(s['B1']),
 'nivel2_nucleo_cribado_texto_completo': len(s['B1'] & (s['B2'] | s['B3'])),
}
print('\n== PRISMA (conteos disponibles) =='); print(json.dumps(prisma, indent=2, ensure_ascii=False))
json.dump(prisma, open(f'{OUT}/prisma_counts.json', 'w'), indent=2, ensure_ascii=False)
