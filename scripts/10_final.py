"""Analisis definitivo: 4 dimensiones + atipico, vecindario semantico, TCCM."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram, cophenet
from sklearn.metrics import silhouette_score
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

SEED = 20261012; np.random.seed(SEED)
OUT = 'out'
m = pd.read_csv('data/N2_matriz_FINAL.csv', encoding='latin-1')
A = ['d1_locus_agencia','d2_requiere_conciencia','d4_momento_respecto_deliberacion','d5_medible',
     'd5_tipo_indicador','d7_umbrales_no_linealidad','d8_naturaleza_del_constructo',
     'd9_via_de_perdida','d10_valencia_normativa','d11_nivel_de_analisis']

nuc = m[m.rol_del_constructo == 'nucleo'].reset_index(drop=True)
ATIP = 'N-044-D1'
sub = nuc[nuc.id_definicion != ATIP].reset_index(drop=True)

X = pd.get_dummies(sub[A].astype(str)).astype(int)
X = X.drop(columns=X.columns[X.nunique() == 1])
D = pdist(X.values, metric='jaccard'); Z = linkage(D, 'average')
K = 4
sub['dimension'] = fcluster(Z, K, 'maxclust')
sil = silhouette_score(squareform(D), sub['dimension'], metric='precomputed')
print(f'SOLUCION: n={len(sub)} (+1 atipico), k={K}, silueta={sil:.3f}, cofenetica={cophenet(Z,D)[0]:.3f}')

NOMBRE = {}
print('\n== PERFIL DE CADA DIMENSION ==')
for d, g in sub.groupby('dimension'):
    print(f'\n--- D{d} (n={len(g)}) ---')
    perfil = {}
    for a in A:
        vc = g[a].value_counts(); dom = vc.index[0]; pr = vc.iloc[0]/len(g)
        base = nuc[a].value_counts(normalize=True).get(dom, 0)
        if pr >= 0.75:
            marca = ' <<' if pr - base > .35 else ''
            print(f'   {a:34s} {dom:26s} {vc.iloc[0]}/{len(g)}{marca}')
            perfil[a] = dom
    NOMBRE[d] = perfil
    print('   ', '; '.join(sorted(set(str(x) for x in g.autores_anio))))

sub.to_csv(f'{OUT}/N2_dimensiones_final.csv', index=False)

# --- figura dendrograma final ---------------------------------------------
plt.rcParams.update({'font.size': 8, 'font.family': 'DejaVu Sans'})
fig, ax = plt.subplots(figsize=(7.4, 5.2), dpi=200)
etq = [f"{r.id_definicion}  {str(r.autores_anio)[:30]}" for r in sub.itertuples()]
dendrogram(Z, labels=etq, orientation='right', ax=ax,
           color_threshold=Z[-(K-1), 2], above_threshold_color='#9aa0a6')
ax.set_xlabel('Distancia de Jaccard (enlace promedio)')
ax.set_title('Figura 2. Agrupamiento jerarquico de atributos definicionales\n'
             f'n = {len(sub)} definiciones nucleares; k = {K}; silueta = {sil:.3f}\n'
             f'({ATIP}, Heo 2025, excluida por atipica y reportada aparte)', loc='left', fontsize=8.5)
ax.spines[['top','right']].set_visible(False); ax.grid(axis='x', alpha=.25, lw=.5)
plt.tight_layout(); plt.savefig(f'{OUT}/F2_dendrograma.png', bbox_inches='tight')

# --- vecindario semantico --------------------------------------------------
vec = m[m.rol_del_constructo != 'nucleo']
print(f'\n== VECINDARIO SEMANTICO (n={len(vec)}) ==')
print(vec['rol_del_constructo'].value_counts().to_string())
for rol, g in vec.groupby('rol_del_constructo'):
    print(f'\n  {rol} (n={len(g)}): locus={g.d1_locus_agencia.value_counts().to_dict()}')
    print(f'     nivel={g.d11_nivel_de_analisis.value_counts().to_dict()}')

# --- TCCM ------------------------------------------------------------------
def fam(serie, patrones):
    out = {}
    for k, p in patrones.items():
        out[k] = int(serie.fillna('').str.contains(p, regex=True, case=False).sum())
    return out
T = fam(m['T_teoria_declarada'], {
  'Autodeterminacion (SDT)': r'self-?determination|\bSDT\b|basic psychological need',
  'Estimulo-Organismo-Respuesta': r'stimulus-?organism|S-?O-?R|\bSOR\b',
  'Arquitectura de decision / nudging': r'choice architecture|nudg',
  'Carga cognitiva': r'cognitive load',
  'Procesamiento de informacion / EKB': r'\bEKB\b|engel-?kollat|information processing',
  'Teoria critica / autonomia normativa': r'critical|normative autonomy|manipulat',
  'Confianza / aceptacion tecnologica': r'\bTAM\b|technology acceptance|trust',
  'Comportamiento planificado (TPB)': r'planned behavio|\bTPB\b|ajzen',
})
print('\n== T — TEORIAS DECLARADAS (n=40 definiciones) ==')
for k, v in sorted(T.items(), key=lambda x: -x[1]): print(f'  {k:40s} {v:3d}')

M = fam(m['M_metodo'], {
  'Encuesta + SEM/PLS': r'SEM|PLS|ecuaciones estructurales|structural',
  'Experimento': r'experiment|aleatoriz|randomi|between-?subjects|escenario',
  'Cualitativo (entrevistas, tematico)': r'entrevist|interview|tematic|thematic|etnograf|focus',
  'Mixto': r'mixto|mixed',
  'Conceptual / teorico': r'conceptual|teoric|analisis conceptual|ensayo|filosof',
  'Revision': r'revision|review|bibliometr',
  'Mineria de texto / datos': r'mineria|text mining|minado|computational',
})
print('\n== M — METODOS (n=40 definiciones) ==')
for k, v in sorted(M.items(), key=lambda x: -x[1]): print(f'  {k:40s} {v:3d}')

pd.DataFrame({'Teoria': list(T), 'n': list(T.values())}).to_csv(f'{OUT}/T4_TCCM_teorias.csv', index=False)
pd.DataFrame({'Metodo': list(M), 'n': list(M.values())}).to_csv(f'{OUT}/T4_TCCM_metodos.csv', index=False)
print('\nArchivos finales escritos.')
