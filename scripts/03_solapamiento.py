"""Deduplicacion y solapamiento entre B1, B1b, B2, B3."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, re

def load(p):
    d = pd.read_csv(p)
    d['doi_norm'] = d['DOI'].apply(lambda x: None if pd.isna(x) else re.sub(r'^https?://(dx\.)?doi\.org/', '', str(x).strip().lower()))
    d['key'] = d['EID'].astype(str)
    return d

B = {k: load(f'data/{k}_scopus_20261012.csv') for k in ['B1', 'B1b', 'B2', 'B3']}
for k, d in B.items():
    print(f'{k}: {len(d)} registros, {d["key"].nunique()} EID unicos')

s = {k: set(d['key']) for k, d in B.items()}
print('\n== SOLAPAMIENTO (EID) ==')
for a in ['B1', 'B1b', 'B2', 'B3']:
    print(' ', a, {b: len(s[a] & s[b]) for b in ['B1', 'B1b', 'B2', 'B3'] if b != a})

print('\nB1 contenido en B1b:', len(s['B1'] - s['B1b']) == 0, '| B1b anade:', len(s['B1b'] - s['B1']))
union = set().union(*s.values())
print('Union de las cuatro busquedas:', len(union))

# nucleo tematico: lo que esta en B1 y ademas en B2 (constructo + consumidor)
core = s['B1'] & s['B2']
print('\n== NUCLEO B1 n B2 (constructo Y vocabulario de consumidor):', len(core))
print('B1 n B3 (constructo Y sostenible):', len(s['B1'] & s['B3']))
print('B2 n B3:', len(s['B2'] & s['B3']))

b3 = B['B3']
print('\n== B3 por ano ==');  print(b3['Year'].value_counts().sort_index().to_string())
print('\n== B3 fuentes top ==');  print(b3['Source title'].value_counts().head(12).to_string())

b2 = B['B2']
print('\n== B2 por ano ==');  print(b2['Year'].value_counts().sort_index().to_string())

# que terminos del bloque A' traen B2 y B3 (aproximado por presencia en texto)
A_core = ['algorithmic agency','consumer autonomy','algorithmic manipulation','algorithmic curation',
          'illusion of autonomy','algorithmic bounded rationality','algorithmic consumer culture','algorithmic authority']
A_ext  = ['choice architecture','recommender system','hyper-personalization','hyperpersonalization','filter bubble']
for name, d in (('B2', b2), ('B3', b3)):
    txt = (d['Title'].fillna('') + ' ' + d['Abstract'].fillna('') + ' ' +
           d['Author Keywords'].fillna('') + ' ' + d['Index Keywords'].fillna('')).str.lower()
    print(f'\n== {name}: de que termino del bloque A viene ==')
    for t in A_core + A_ext:
        n = txt.str.contains(re.escape(t)).sum()
        if n: print(f'  {t:35s} {n:4d}')
    nucleo = txt.str.contains('|'.join(re.escape(t) for t in A_core))
    print(f'  --> con al menos un termino NUCLEAR (bloque A estricto): {nucleo.sum()} de {len(d)}')
