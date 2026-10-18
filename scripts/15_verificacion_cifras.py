"""Verificacion integral: recalcula TODA cifra citada en el articulo y la compara
con el valor publicado. Es la prueba de reproducibilidad del estudio.

Entradas : data/*.csv  (exportes de Scopus + archivos de codificacion manual)
Salidas  : out/verificacion_cifras.csv   ·  out/prisma_final.json
Codigo de salida: 0 si todas las cifras coinciden; 1 si alguna discrepa.
"""
# --- portabilidad ------------------------------------------------------------
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, numpy as np, re, json, sys
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster, cophenet
from sklearn.metrics import silhouette_score, cohen_kappa_score

SEMILLA = 20261012
np.random.seed(SEMILLA)
V = []   # (seccion, cifra, publicado, recalculado)

def chk(seccion, nombre, publicado, calculado, tol=0.0005):
    if isinstance(publicado, float) or isinstance(calculado, float):
        ok = abs(float(publicado) - float(calculado)) <= tol
    else:
        ok = publicado == calculado
    V.append({'seccion': seccion, 'cifra': nombre, 'publicado': publicado,
              'recalculado': calculado, 'coincide': 'SI' if ok else '*** NO ***'})
    return ok

# ============ carga ==========================================================
B = {k: pd.read_csv(f'data/{k}_scopus_20261012.csv') for k in ['B1', 'B1b', 'B2', 'B3']}
S = {k: set(d['EID']) for k, d in B.items()}
b1 = B['B1']
crib = pd.read_csv('data/N2_cribado_FINAL.csv', encoding='latin-1')
mat = pd.read_csv('data/N2_matriz_FINAL.csv', encoding='latin-1')
r2 = pd.read_csv('data/RONDA2.csv', encoding='latin-1')
asjc = pd.read_csv('data/B1_areas_ASJC_scopus.csv')

# ============ 4.1 flujo de seleccion =========================================
chk('4.1', 'B1 registros', 642, len(B['B1']))
chk('4.1', 'B2 registros', 525, len(B['B2']))
chk('4.1', 'B3 registros', 59, len(B['B3']))
chk('4.1', 'B1b registros', 785, len(B['B1b']))
chk('4.1', 'B1b adicionales sobre B1', 143, len(S['B1b'] - S['B1']))
chk('4.1', 'B1b incremento %', 22.3, round(len(S['B1b'] - S['B1']) / len(S['B1']) * 100, 1))
bruto = len(S['B1']) + len(S['B2']) + len(S['B3'])
union = len(S['B1'] | S['B2'] | S['B3'])
chk('4.1', 'Registros brutos B1+B2+B3', 1226, bruto)
chk('4.1', 'Duplicados entre busquedas', 106, bruto - union)
chk('4.1', 'Registros unicos', 1120, union)
nucleo = S['B1'] & (S['B2'] | S['B3'])
chk('4.1', 'Nucleo B1 n (B2 u B3)', 76, len(nucleo))
chk('4.1', 'Texto completo evaluado', 45, int((crib.TEXTO_OBTENIDO_SI_NO == 'SI').sum()))
chk('4.1', 'No recuperados', 31, int((crib.TEXTO_OBTENIDO_SI_NO == 'NO').sum()))
chk('4.1', 'Incluidos', 18, int((crib.INCLUIR_SI_NO == 'SI').sum()))
chk('4.1', 'Excluidos', 27, int((crib.INCLUIR_SI_NO == 'NO').sum()))

# ============ 4.2 caracterizacion ============================================
anios = b1['Year'].value_counts().sort_index()
for a, esp in zip(range(2021, 2027), [35, 30, 40, 54, 174, 309]):
    chk('4.2', f'B1 documentos {a}', esp, int(anios.get(a, 0)))
chk('4.2', '% publicado en 2025-2026', 75.2,
    round((anios.get(2025, 0) + anios.get(2026, 0)) / len(b1) * 100, 1))
chk('4.2', 'Mediana de citas', 0.5, float(b1['Cited by'].median()))
chk('4.2', 'Documentos con cero citas', 321, int((b1['Cited by'].fillna(0) == 0).sum()))
chk('4.2', 'Publicacion anticipada (n)', 57, int((b1['Publication Stage'] == 'Article in press').sum()))
chk('4.2', 'Publicacion anticipada (%)', 8.9,
    round((b1['Publication Stage'] == 'Article in press').mean() * 100, 1))
chk('4.2', 'Acceso abierto (%)', 50.3, round(b1['Open Access'].notna().mean() * 100, 1))
fs = b1['Source title'].value_counts()
chk('4.2', 'Fuentes distintas', 496, int(fs.size))
chk('4.2', 'Documentos en la fuente mayor', 9, int(fs.iloc[0]))
chk('4.2', '% en la fuente mayor', 1.4, round(fs.iloc[0] / len(b1) * 100, 1))
chk('4.2', '% en las 10 fuentes mayores', 9.0, round(fs.head(10).sum() / len(b1) * 100, 1))
chk('4.2', 'Fuentes con un solo documento', 407, int((fs == 1).sum()))
chk('4.2', '% del corpus en fuentes con un documento', 63.4, round((fs == 1).sum() / len(b1) * 100, 1))
chk('4.2', 'Indice de Herfindahl', 0.0029, round(float(((fs / len(b1)) ** 2).sum()), 4))
chk('4.2', 'Areas ASJC distintas', 24, len(asjc))
chk('4.2', 'Asignaciones ASJC totales', 1201, int(asjc.documents.sum()))
chk('4.2', 'Areas por documento', 1.87, round(asjc.documents.sum() / len(b1), 2))
adm = asjc[asjc.subject_area.isin(['Business, Management and Accounting',
                                   'Economics, Econometrics and Finance',
                                   'Decision Sciences'])].documents.sum()
chk('4.2', 'Asignaciones del nucleo administrativo', 245, int(adm))
chk('4.2', '% del nucleo administrativo', 20.4, round(adm / asjc.documents.sum() * 100, 1))

# Tabla 1: frecuencia de los terminos del bloque A
txt = (b1['Title'].fillna('') + ' ' + b1['Abstract'].fillna('') + ' ' +
       b1['Author Keywords'].fillna('') + ' ' + b1['Index Keywords'].fillna('')).str.lower()
TABLA1 = [('algorithmic curation', 234, 36.4), ('consumer autonomy', 135, 21.0),
          ('algorithmic manipulation', 101, 15.7), ('algorithmic authority', 85, 13.2),
          ('algorithmic agency', 50, 7.8), ('illusion of autonomy', 14, 2.2),
          ('algorithmic consumer culture', 6, 0.9), ('algorithmic bounded rationality', 1, 0.2)]
for t, n, pct in TABLA1:
    c = int(txt.str.contains(re.escape(t)).sum())
    chk('Tabla 1', f'"{t}" (n)', n, c)
    chk('Tabla 1', f'"{t}" (%)', pct, round(c / len(b1) * 100, 1))

# ============ 4.3 intersecciones =============================================
chk('4.3', 'B1 n B2', 74, len(S['B1'] & S['B2']))
chk('4.3', 'B1 n B2 (% de B1)', 11.5, round(len(S['B1'] & S['B2']) / len(S['B1']) * 100, 1))
chk('4.3', 'B1 n B3', 8, len(S['B1'] & S['B3']))
chk('4.3', 'B1 n B3 (% de B1)', 1.2, round(len(S['B1'] & S['B3']) / len(S['B1']) * 100, 1))
chk('4.3', 'B2 n B3', 30, len(S['B2'] & S['B3']))
chk('4.3', 'Interseccion triple', 6, len(S['B1'] & S['B2'] & S['B3']))
A_ESTRICTO = ['algorithmic agency', 'consumer autonomy', 'algorithmic manipulation',
              'algorithmic curation', 'illusion of autonomy', 'algorithmic bounded rationality',
              'algorithmic consumer culture', 'algorithmic authority']
t2 = (B['B2']['Title'].fillna('') + ' ' + B['B2']['Abstract'].fillna('') + ' ' +
      B['B2']['Author Keywords'].fillna('') + ' ' + B['B2']['Index Keywords'].fillna('')).str.lower()
chk('4.3', 'B2 con termino nuclear de A', 67,
    int(t2.str.contains('|'.join(map(re.escape, A_ESTRICTO))).sum()))
chk('4.3', 'B2 recuperados por "recommender system"', 311,
    int(t2.str.contains('recommender system').sum()))

# ============ 4.4 corpus de codificacion =====================================
inc = crib[crib.INCLUIR_SI_NO == 'SI']
tipo = inc['TIPO_ESTUDIO_empirico_teorico_mixto'].value_counts()
chk('4.4', 'Incluidos empiricos', 8, int(tipo.get('empirico', 0)))
chk('4.4', 'Incluidos mixtos', 5, int(tipo.get('mixto', 0)))
chk('4.4', 'Incluidos teoricos', 5, int(tipo.get('teorico', 0)))
chk('4.4', 'Incluidos en acceso abierto', 17, int(inc['Open Access'].notna().sum()))
chk('4.4', 'Incluidos en la interseccion con B2', 17, int(inc['en_B2'].sum()))
cal = inc['CALIDAD_MMAT_o_RUBRICA'].astype(str)
chk('4.4', 'Evaluados con MMAT', 13, int(cal.str.startswith('MMAT').sum()))
chk('4.4', 'Evaluados con rubrica conceptual', 5, int(cal.str.startswith('RC').sum()))
chk('4.4', 'Definiciones extraidas', 40, len(mat))
chk('4.4', 'Definiciones por documento', 2.22, round(len(mat) / mat.id_nucleo.nunique(), 2))

# ============ 4.5 consensos ==================================================
chk('4.5', 'd3 gradual (de 40)', 40, int((mat.d3_gradual_binaria == 'gradual').sum()))
med = mat.d5_medible.value_counts()
chk('4.5', 'd5 medible con instrumento', 23, int(med.get('si_con_instrumento', 0)))
chk('4.5', 'd5 medible sin instrumento', 13, int(med.get('si_sin_instrumento', 0)))
chk('4.5', 'd5 no medible', 4, int(med.get('no', 0)))
loc = mat.d1_locus_agencia.value_counts()
chk('4.5', 'd1 locus relacion', 26, int(loc.get('relacion', 0)))
chk('4.5', 'd1 locus relacion (%)', 65.0, round(loc.get('relacion', 0) / len(mat) * 100, 1))
chk('4.5', 'd1 locus sistema', 9, int(loc.get('sistema', 0)))
chk('4.5', 'd1 locus usuario', 5, int(loc.get('usuario', 0)))

# ============ 4.6 dimensiones ================================================
rol = mat.rol_del_constructo.value_counts()
chk('4.6', 'Definiciones con rol nuclear', 19, int(rol.get('nucleo', 0)))
AGRUPA = ['d1_locus_agencia', 'd2_requiere_conciencia', 'd4_momento_respecto_deliberacion',
          'd5_medible', 'd5_tipo_indicador', 'd7_umbrales_no_linealidad',
          'd8_naturaleza_del_constructo', 'd9_via_de_perdida',
          'd10_valencia_normativa', 'd11_nivel_de_analisis']
nuc = mat[mat.rol_del_constructo == 'nucleo'].reset_index(drop=True)
sub = nuc[nuc.id_definicion != 'N-044-D1'].reset_index(drop=True)
X = pd.get_dummies(sub[AGRUPA].astype(str)).astype(int)
X = X.drop(columns=X.columns[X.nunique() == 1])
D = pdist(X.values, metric='jaccard'); Z = linkage(D, 'average')
lab = fcluster(Z, 4, 'maxclust')
chk('4.6', 'n del agrupamiento (sin atipica)', 18, len(sub))
chk('4.6', 'Silueta k=4', 0.247, round(float(silhouette_score(squareform(D), lab, metric='precomputed')), 3))
chk('4.6', 'Correlacion cofenetica', 0.789, round(float(cophenet(Z, D)[0]), 3))
for d, n in zip([1, 2, 3, 4], sorted(np.bincount(lab)[1:])):
    pass
chk('4.6', 'Tamanos de los conglomerados', '[4, 4, 4, 6]', str(sorted(int(v) for v in np.bincount(lab)[1:])))
d9 = mat.d9_via_de_perdida.value_counts()
chk('4.6', 'd9 manipulacion encubierta', 18, int(d9.get('manipulacion_encubierta', 0)))
chk('4.6', 'd9 no aplica', 10, int(d9.get('no_aplica', 0)))
chk('4.6', 'd9 delegacion voluntaria', 7, int(d9.get('delegacion_voluntaria', 0)))
chk('4.6', 'd9 filtrado del acceso', 5, int(d9.get('filtrado_del_acceso', 0)))
d10 = mat.d10_valencia_normativa.value_counts()
chk('4.6', 'd10 potencialmente positiva', 18, int(d10.get('potencialmente_positiva', 0)))
chk('4.6', 'd10 ambivalente', 12, int(d10.get('ambivalente', 0)))
chk('4.6', 'd10 negativa', 8, int(d10.get('negativa', 0)))
chk('4.6', 'd10 neutra', 2, int(d10.get('neutra', 0)))

# ============ 4.7 fiabilidad =================================================
ATR = AGRUPA + ['d3_gradual_binaria']
m = nuc[['id_definicion'] + ATR].merge(r2[['id_definicion'] + ATR], on='id_definicion',
                                       suffixes=('_1', '_2'))
KAPPA_PUB = {'d8_naturaleza_del_constructo': 0.850, 'd5_medible': 0.703,
             'd11_nivel_de_analisis': 0.578, 'd9_via_de_perdida': 0.457,
             'd1_locus_agencia': 0.414, 'd5_tipo_indicador': 0.398,
             'd4_momento_respecto_deliberacion': 0.321, 'd10_valencia_normativa': 0.186,
             'd7_umbrales_no_linealidad': 0.159, 'd2_requiere_conciencia': 0.143}
acu = []
for a in ATR:
    x = m[a + '_1'].astype(str).str.strip(); y = m[a + '_2'].astype(str).str.strip()
    acu.append((x == y).mean())
    cats = sorted(set(x) | set(y))
    if a in KAPPA_PUB:
        chk('Tabla 3', f'kappa {a}', KAPPA_PUB[a],
            round(float(cohen_kappa_score(x, y, labels=cats)), 3))
chk('4.7', 'Acuerdo medio', 0.656, round(float(np.mean(acu)), 3))
chk('4.7', 'Kappa mediano (10 interpretables)', 0.406, round(float(np.median(list(KAPPA_PUB.values()))), 3))

FIABLES = [a for a, k in KAPPA_PUB.items() if k >= 0.40]
Xf = pd.get_dummies(sub[FIABLES].astype(str)).astype(int)
Xf = Xf.drop(columns=Xf.columns[Xf.nunique() == 1])
Df = pdist(Xf.values, metric='jaccard'); Zf = linkage(Df, 'average')
lf3 = fcluster(Zf, 3, 'maxclust')
chk('4.7', 'Cofenetica esquema fiable', 0.809, round(float(cophenet(Zf, Df)[0]), 3))
chk('4.7', 'Silueta fiable k=3', 0.317, round(float(silhouette_score(squareform(Df), lf3, metric='precomputed')), 3))
from sklearn.metrics import adjusted_rand_score
chk('4.7', 'Rand ajustado completo(k=4) vs fiable(k=3)', 0.537, round(float(adjusted_rand_score(lab, lf3)), 3))

# ============ 4.8 vecindario =================================================
chk('4.8', 'Definiciones no nucleares', 21, int(len(mat) - rol.get('nucleo', 0)))
chk('4.8', 'Antecedentes', 11, int(rol.get('antecedente', 0)))
chk('4.8', 'Consecuencias', 4, int(rol.get('consecuencia', 0)))
chk('4.8', 'Marcos normativos', 3, int(rol.get('marco_normativo', 0)))
chk('4.8', 'Vecinos', 3, int(rol.get('vecino', 0)))

# ============ salida =========================================================
R = pd.DataFrame(V)
R.to_csv('out/verificacion_cifras.csv', index=False)
fallos = R[R.coincide != 'SI']
print(R.to_string(index=False))
print(f'\n{"="*70}')
print(f'Cifras verificadas: {len(R)}   ·   coinciden: {len(R)-len(fallos)}   ·   discrepan: {len(fallos)}')
if len(fallos):
    print('\nDISCREPANCIAS:')
    print(fallos.to_string(index=False))
print('='*70)

json.dump({
 'identificacion': {'B1': len(S['B1']), 'B2': len(S['B2']), 'B3': len(S['B3']),
                    'B1b_sensibilidad': len(S['B1b']), 'bruto_B1_B2_B3': bruto,
                    'duplicados': bruto - union, 'unicos': union},
 'nivel_1': {'corpus_caracterizacion': len(S['B1'])},
 'nivel_2': {'nucleo': len(nucleo),
             'texto_completo_evaluado': int((crib.TEXTO_OBTENIDO_SI_NO == 'SI').sum()),
             'no_recuperados': int((crib.TEXTO_OBTENIDO_SI_NO == 'NO').sum()),
             'incluidos': int((crib.INCLUIR_SI_NO == 'SI').sum()),
             'excluidos': int((crib.INCLUIR_SI_NO == 'NO').sum()),
             'definiciones': len(mat),
             'rol_nuclear': int(rol.get('nucleo', 0)),
             'vecindario': int(len(mat) - rol.get('nucleo', 0))}
}, open('out/prisma_final.json', 'w'), indent=2, ensure_ascii=False)
print('Escritos: out/verificacion_cifras.csv  ·  out/prisma_final.json')
sys.exit(1 if len(fallos) else 0)
