"""Triaje por reglas sobre B1. Pre-especificado, semilla fija.

El clasificador NO fija el umbral de inclusion: produce una puntuacion continua y
cinco bandas. El umbral se estima despues, contra el cribado manual ciego de una
muestra estratificada, exigiendo sensibilidad >= 0.95.
"""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, numpy as np, re

SEED = 20261012
df = pd.read_csv('out/B1_normalizado.csv')
df['id_registro'] = ['B1-%04d' % i for i in range(1, len(df) + 1)]

def blob(r):
    parts = [r.get('Title'), r.get('Abstract'), r.get('Author Keywords'), r.get('Index Keywords')]
    return ' '.join('' if pd.isna(p) else str(p) for p in parts).lower()
df['blob'] = df.apply(blob, axis=1)

S1 = {  # lenguaje definicional / dimensional / de medicion
 'define':    r'\b(we define|is defined as|defined here as|definition of|conceptuali[sz](e|ed|ation)|operationali[sz](e|ed|ation)|theoriz(e|ed|ing))\b',
 'dimension': r'\b(dimension[s]?|facet[s]?|sub-?construct|typolog(y|ies)|taxonom(y|ies)|conceptual (model|framework)|continuum)\b',
 'measure':   r'\b(scale development|measurement (model|instrument|scale)|psychometric|validated (scale|instrument)|factor analys[ie]s|items were developed|index of|metric for)\b',
 'construct': r'\b(construct|notion of|concept of|re-?conceptuali[sz])\b',
}
S2 = {  # contexto decisional / de consumo / conductual
 'consumer':  r'\b(consumer[s]?|customer[s]?|shopper[s]?|marketing|e-?commerce|retail|advertis)\w*',
 'decision':  r'\b(decision[- ]making|choice[s]?|purchase|buying|preference[s]?|consideration set|willingness to (buy|pay))\b',
 'cognition': r'\b(cognitiv\w+|attention|memory|deliberat\w+|heuristic[s]?|bias(es)?|autonom\w+|agency|self-?determination)\b',
 'recsys':    r'\b(recommend\w+|personali[sz]ation|personali[sz]ed|ranking|curation|filter bubble|nudg\w+|choice architecture)\b',
}
S3 = {  # senales de exclusion
 'ml_tecnico':    r'\b(benchmark dataset|state-of-the-art model|neural (network|architecture)|transformer architecture|training corpus|latency|throughput|hyperparameter|federated learning|adversarial (attack|example)|convolutional|gradient descent)\b',
 'gobernanza':    r'\b(gdpr|data protection (law|regulation)|compliance framework|regulatory sandbox|data governance|cybersecurity)\b',
 'fuera_dominio': r'\b(clinical trial|cancer|radiolog|genomic|molecular|protein|agricultur|seismic|photovoltaic|battery|wastewater|traffic flow|crop yield)\b',
}

for name, D in (('d', S1), ('c', S2), ('x', S3)):
    for k, p in D.items():
        df[f'{name}_{k}'] = df['blob'].str.contains(p, regex=True, na=False)

df['s1_def'] = df[[f'd_{k}' for k in S1]].sum(axis=1)
df['s2_ctx'] = df[[f'c_{k}' for k in S2]].sum(axis=1)
df['s3_exc'] = df[[f'x_{k}' for k in S3]].sum(axis=1)
df['sin_resumen'] = df['Abstract'].astype(str).str.contains(r'\[No abstract available\]', case=False, na=False)

# puntuacion continua: la senal definicional pesa doble (es el criterio nuclear)
df['score'] = 2 * df['s1_def'] + df['s2_ctx'] - 2 * df['s3_exc']
df.loc[df['sin_resumen'], 'score'] = np.nan   # no cribables por resumen -> revision manual forzosa

bins = [-np.inf, 0, 2, 4, 6, np.inf]
labels = ['E1 (<=0)', 'E2 (1-2)', 'E3 (3-4)', 'E4 (5-6)', 'E5 (>=7)']
df['banda'] = pd.cut(df['score'], bins=bins, labels=labels)
df['banda'] = df['banda'].cat.add_categories(['E0 (sin resumen)'])
df.loc[df['sin_resumen'], 'banda'] = 'E0 (sin resumen)'

print('== PUNTUACION ==')
print(df['score'].describe().to_string())
print('\n== BANDAS ==')
print(df['banda'].value_counts().sort_index().to_string())
print('\n== s1_def x s2_ctx ==')
print(pd.crosstab(df['s1_def'], df['s2_ctx']).to_string())
print('\n== Banda x ano ==')
print(pd.crosstab(df['Year'], df['banda']).to_string())
print('\n== Banda x tipo documental ==')
print(pd.crosstab(df['Document Type'], df['banda']).to_string())

df.to_csv('out/B1_triaje.csv', index=False)

# --- muestra de validacion ciega: 20 por banda (E0 completa) ----------------
partes = []
for b in df['banda'].cat.categories:
    g = df[df['banda'] == b]
    if len(g) == 0:
        continue
    n = min(len(g), 20)
    partes.append(g.sample(n=n, random_state=SEED))
muestra = pd.concat(partes).sample(frac=1, random_state=SEED)

cols = ['id_registro', 'Title', 'Year', 'Source title', 'Document Type',
        'Author Keywords', 'Abstract', 'DOI']
val = muestra[cols].copy()
val['INCLUIR_SI_NO'] = ''
val['APORTA_DEFINICION_SI_NO'] = ''
val['MOTIVO_EXCLUSION'] = ''
val.to_csv('out/muestra_validacion.csv', index=False)
muestra[['id_registro', 'banda', 'score', 's1_def', 's2_ctx', 's3_exc']].to_csv(
    'out/muestra_validacion_CLAVE.csv', index=False)
print('\n== MUESTRA DE VALIDACION ==')
print('n =', len(val))
print(muestra['banda'].value_counts().sort_index().to_string())
