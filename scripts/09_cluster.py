"""Jaccard + agrupamiento jerarquico sobre la matriz definicion x atributo. Semilla fija."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram, cophenet
from sklearn.metrics import silhouette_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SEED = 20261012
np.random.seed(SEED)
OUT = 'out'
m = pd.read_csv('data/N2_matriz_FINAL.csv', encoding='latin-1')

# d3 es constante en n=40 -> consenso, fuera del calculo de similitud
ATTRS = ['d1_locus_agencia', 'd2_requiere_conciencia', 'd4_momento_respecto_deliberacion',
         'd5_medible', 'd5_tipo_indicador', 'd7_umbrales_no_linealidad',
         'd8_naturaleza_del_constructo', 'd9_via_de_perdida',
         'd10_valencia_normativa', 'd11_nivel_de_analisis']

print('== CONSENSO (atributos sin varianza, n=40) ==')
print('  d3_gradual_binaria: 40/40 "gradual" -> consenso pleno, excluido del agrupamiento')

def binariza(df):
    X = pd.get_dummies(df[ATTRS].astype(str), prefix=ATTRS, prefix_sep='=')
    return X.astype(int)

def analiza(df, etiqueta):
    X = binariza(df)
    # columnas constantes no aportan a Jaccard
    const = X.columns[X.nunique() == 1].tolist()
    X = X.drop(columns=const)
    print(f'\n{"="*68}\n{etiqueta}: n={len(df)} definiciones, {X.shape[1]} indicadores binarios')
    if const: print(f'  indicadores constantes retirados: {len(const)}')
    D = pdist(X.values, metric='jaccard')
    print(f'  Jaccard: media={D.mean():.3f}  min={D.min():.3f}  max={D.max():.3f}')

    res = {}
    for met in ['average', 'ward', 'complete']:
        Z = linkage(D if met != 'ward' else X.values, method=met,
                    metric='euclidean' if met == 'ward' else None) if met == 'ward' else linkage(D, method=met)
        coph = cophenet(Z, D)[0]
        res[met] = (Z, coph)
        print(f'  enlace {met:9s} correlacion cofenetica = {coph:.3f}')

    Z = res['average'][0]
    print(f'\n  Seleccion del numero de dimensiones (enlace promedio):')
    print(f'  {"k":>3} {"silueta":>9} {"salto_fusion":>13} {"tamanos"}')
    alturas = Z[:, 2]
    mejor = None
    for k in range(2, min(9, len(df))):
        lab = fcluster(Z, k, criterion='maxclust')
        if len(set(lab)) < 2: continue
        sil = silhouette_score(squareform(D), lab, metric='precomputed')
        salto = alturas[-(k-1)] - alturas[-k] if k < len(alturas) else np.nan
        tam = np.bincount(lab)[1:]
        print(f'  {k:>3} {sil:>9.3f} {salto:>13.3f}  {list(tam)}')
        if mejor is None or sil > mejor[1]: mejor = (k, sil)
    print(f'  -> mayor silueta en k={mejor[0]} (silueta={mejor[1]:.3f})')
    return X, D, res, mejor

# ---------- A: solo rol nucleo (analisis principal) ------------------------
nuc = m[m['rol_del_constructo'] == 'nucleo'].reset_index(drop=True)
Xn, Dn, resn, mejorn = analiza(nuc, 'A. CORPUS NUCLEAR (rol = nucleo)')

# ---------- B: las 40 definiciones (robustez) -----------------------------
Xa, Da, resa, mejora = analiza(m, 'B. TODAS LAS DEFINICIONES (robustez)')

# ---------- dimensiones resultantes del analisis principal ----------------
k = mejorn[0]
Zn = resn['average'][0]
nuc['dimension'] = fcluster(Zn, k, criterion='maxclust')
print(f'\n{"="*68}\n== DIMENSIONES EMERGENTES (k={k}) ==')
for d, g in nuc.groupby('dimension'):
    print(f'\n--- Dimension {d}  (n={len(g)}) ---')
    for a in ATTRS:
        vc = g[a].value_counts()
        dom = vc.index[0]; prop = vc.iloc[0] / len(g)
        if prop >= 0.6:
            print(f'    {a:34s} {dom}  ({vc.iloc[0]}/{len(g)})')
    print('    definiciones:', ', '.join(g['id_definicion'].tolist()))
    print('    autores:', '; '.join(sorted(set(str(x) for x in g['autores_anio']))))

nuc.to_csv(f'{OUT}/N2_nucleo_con_dimension.csv', index=False)

# ---------- figura: dendrograma -------------------------------------------
plt.rcParams.update({'font.size': 8, 'font.family': 'DejaVu Sans'})
fig, ax = plt.subplots(figsize=(7.2, 5.6), dpi=200)
etq = [f"{r.id_definicion}  {str(r.autores_anio)[:26]}" for r in nuc.itertuples()]
dendrogram(Zn, labels=etq, orientation='right', ax=ax,
           color_threshold=Zn[-(k-1), 2], above_threshold_color='#9aa0a6')
ax.set_xlabel('Distancia de Jaccard (enlace promedio)')
ax.set_title(f'Agrupamiento de atributos definicionales del constructo\n'
             f'n = {len(nuc)} definiciones nucleares · k = {k} dimensiones', loc='left')
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='x', alpha=.25, lw=.5)
plt.tight_layout()
plt.savefig(f'{OUT}/F2_dendrograma.png', bbox_inches='tight')
print(f'\nF2_dendrograma.png escrito')

# ---------- matriz de similitud -------------------------------------------
orden = dendrogram(Zn, no_plot=True)['leaves']
S = 1 - squareform(Dn)
np.fill_diagonal(S, 1)
fig, ax = plt.subplots(figsize=(6.4, 5.6), dpi=200)
im = ax.imshow(S[np.ix_(orden, orden)], cmap='YlGnBu', vmin=0, vmax=1)
ax.set_xticks(range(len(orden))); ax.set_yticks(range(len(orden)))
ax.set_xticklabels([nuc['id_definicion'][i] for i in orden], rotation=90, fontsize=6)
ax.set_yticklabels([nuc['id_definicion'][i] for i in orden], fontsize=6)
plt.colorbar(im, label='Similitud de Jaccard', shrink=.8)
ax.set_title('Similitud entre definiciones nucleares', loc='left')
plt.tight_layout(); plt.savefig(f'{OUT}/F2b_matriz_similitud.png', bbox_inches='tight')
print('F2b_matriz_similitud.png escrito')
