"""F2 y F3 redimensionadas a ancho de columna (3,0 pulgadas)."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from sklearn.metrics import silhouette_score
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = 'out'
TINTA, SUAVE, BORDE = '#1a1a1a', '#6b6b6b', '#b9bfc7'
AZUL, GRIS_C = '#2d5f8a', '#eceef1'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': TINTA})

# ---------------- F2: dendrograma a ancho de columna ------------------------
m = pd.read_csv('data/N2_matriz_FINAL.csv', encoding='latin-1')
A = ['d1_locus_agencia','d2_requiere_conciencia','d4_momento_respecto_deliberacion','d5_medible',
     'd5_tipo_indicador','d7_umbrales_no_linealidad','d8_naturaleza_del_constructo',
     'd9_via_de_perdida','d10_valencia_normativa','d11_nivel_de_analisis']
nuc = m[m.rol_del_constructo == 'nucleo'].reset_index(drop=True)
sub = nuc[nuc.id_definicion != 'N-044-D1'].reset_index(drop=True)
X = pd.get_dummies(sub[A].astype(str)).astype(int)
X = X.drop(columns=X.columns[X.nunique() == 1])
D = pdist(X.values, metric='jaccard'); Z = linkage(D, 'average'); K = 4
lab = fcluster(Z, K, 'maxclust')
sil = silhouette_score(squareform(D), lab, metric='precomputed')

NOM = {1: 'D4 Condición diádica', 2: 'D3 Estado psicológico', 3: 'D2 Erosión no consciente', 4: 'D1 Facultad individual'}
fig, ax = plt.subplots(figsize=(3.05, 3.9), dpi=400)
etq = [f"{r.autores_anio}" for r in sub.itertuples()]
dendrogram(Z, labels=etq, orientation='right', ax=ax,
           color_threshold=Z[-(K-1), 2], above_threshold_color='#9aa0a6')
ax.set_xlabel('Distancia de Jaccard', fontsize=6)
ax.tick_params(axis='y', labelsize=5.2, length=0)
ax.tick_params(axis='x', labelsize=5.2, colors=SUAVE, length=0)
ax.spines[['top','right','left']].set_visible(False)
ax.spines['bottom'].set_color(BORDE)
ax.grid(axis='x', alpha=.25, lw=.4)
plt.tight_layout(pad=.3)
plt.savefig(f'{OUT}/F2_dendrograma_col.png', bbox_inches='tight', facecolor='white')
print('F2_dendrograma_col.png  silueta=%.3f' % sil)

# ---------------- F3: interseccion a ancho de columna -----------------------
fig, (a1, a2) = plt.subplots(2, 1, figsize=(3.05, 3.5), dpi=400,
                             gridspec_kw={'height_ratios': [1, .85]})
nom = ['B1\nconstructo', 'B2\n× consumidor', 'B3\n× sostenible']
val = [642, 525, 59]
b = a1.bar(nom, val, color=[AZUL, '#5b8bb0', '#9dbdd4'], width=.6,
           edgecolor='white', linewidth=1.2)
for r, v in zip(b, val):
    a1.text(r.get_x()+r.get_width()/2, v+16, f'{v}', ha='center', fontsize=6.4, fontweight='bold')
a1.set_ylabel('Documentos', fontsize=6); a1.set_ylim(0, 760)
a1.set_title('a) Tamaño de cada corpus', loc='left', fontsize=6.6, fontweight='bold')
a1.spines[['top','right']].set_visible(False); a1.spines[['left','bottom']].set_color(BORDE)
a1.grid(axis='y', alpha=.3, lw=.4); a1.set_axisbelow(True)
a1.tick_params(labelsize=5.6, colors=SUAVE, length=0)

et = ['B1 ∩ B2\nconstructo y\nconsumidor', 'B1 ∩ B3\nconstructo y\nsostenible']
pr = [74/642*100, 8/642*100]; nn = [74, 8]
y = np.arange(2)
a2.barh(y, [100, 100], color=GRIS_C, height=.46, edgecolor='white', linewidth=1.2)
a2.barh(y, pr, color=[AZUL, '#9dbdd4'], height=.46, edgecolor='white', linewidth=1.2)
for i, (pp, n) in enumerate(zip(pr, nn)):
    a2.text(pp+3, i, f'{pp:.1f} %  (n = {n})'.replace('.', ','), va='center',
            fontsize=6.2, fontweight='bold')
a2.set_yticks(y); a2.set_yticklabels(et, fontsize=5.4)
a2.set_xlim(0, 100); a2.set_xlabel('% del corpus del constructo (B1 = 642)', fontsize=6)
a2.set_title('b) Intersección entre literaturas', loc='left', fontsize=6.6, fontweight='bold')
a2.spines[['top','right','left']].set_visible(False); a2.spines['bottom'].set_color(BORDE)
a2.grid(axis='x', alpha=.3, lw=.4); a2.set_axisbelow(True)
a2.tick_params(labelsize=5.6, colors=SUAVE, length=0); a2.invert_yaxis()
plt.tight_layout(pad=.4)
plt.savefig(f'{OUT}/F3_interseccion_col.png', bbox_inches='tight', facecolor='white')
print('F3_interseccion_col.png')
