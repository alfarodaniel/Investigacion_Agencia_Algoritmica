"""Fiabilidad intracodificador (kappa de Cohen por atributo) y analisis de sensibilidad.

Entradas : data/N2_matriz_FINAL.csv   (ronda 1, codificacion inicial)
           data/RONDA2.csv            (ronda 2, recodificacion ciega diferida)
Salidas  : out/T5_kappa.csv
           out/sensibilidad_agrupamiento.csv
Reproduce: Tabla 3 del articulo y el parrafo de analisis de sensibilidad (seccion 4.7).
"""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, numpy as np
from sklearn.metrics import cohen_kappa_score, adjusted_rand_score, silhouette_score
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster, cophenet

SEMILLA = 20261012
np.random.seed(SEMILLA)

ATRIBUTOS = ['d1_locus_agencia', 'd2_requiere_conciencia', 'd3_gradual_binaria',
             'd4_momento_respecto_deliberacion', 'd5_medible', 'd5_tipo_indicador',
             'd7_umbrales_no_linealidad', 'd8_naturaleza_del_constructo',
             'd9_via_de_perdida', 'd10_valencia_normativa', 'd11_nivel_de_analisis']
# d3 y d6 quedan fuera del agrupamiento: d3 es constante; d6 es texto libre
AGRUPA = [a for a in ATRIBUTOS if a != 'd3_gradual_binaria']
ATIPICA = 'N-044-D1'

r1 = pd.read_csv('data/N2_matriz_FINAL.csv', encoding='latin-1')
r2 = pd.read_csv('data/RONDA2.csv', encoding='latin-1')
nuc = r1[r1.rol_del_constructo == 'nucleo'].reset_index(drop=True)
print(f'Definiciones nucleares en ronda 1: {len(nuc)}')
print(f'Definiciones recodificadas en ronda 2: {len(r2)}')

# ============ 1) KAPPA POR ATRIBUTO ==========================================
m = nuc[['id_definicion'] + ATRIBUTOS].merge(
    r2[['id_definicion'] + ATRIBUTOS], on='id_definicion', suffixes=('_1', '_2'))
print(f'Definiciones emparejadas entre rondas: {len(m)}\n')

filas = []
print(f'{"atributo":36s} {"acuerdo":>8} {"kappa":>8} {"categorias":>11}')
for a in ATRIBUTOS:
    x = m[a + '_1'].astype(str).str.strip()
    y = m[a + '_2'].astype(str).str.strip()
    acuerdo = (x == y).mean()
    cats = sorted(set(x) | set(y))
    kappa = cohen_kappa_score(x, y, labels=cats) if len(cats) > 1 else np.nan
    filas.append({'atributo': a, 'acuerdo': round(acuerdo, 3),
                  'kappa': round(kappa, 3) if not np.isnan(kappa) else None,
                  'n_categorias': len(cats)})
    k = f'{kappa:8.3f}' if not np.isnan(kappa) else f'{"n/a":>8}'
    print(f'{a:36s} {acuerdo:8.3f} {k} {len(cats):11d}')

T5 = pd.DataFrame(filas).sort_values('kappa', ascending=False, na_position='last')
T5.to_csv('out/T5_kappa.csv', index=False)
# d3 es practicamente constante (18/19 de acuerdo, una sola categoria sustantiva):
# su kappa no es interpretable y se excluye de los estadisticos de resumen.
NO_INTERPRETABLE = {'d3_gradual_binaria'}
ks = [f['kappa'] for f in filas
      if f['kappa'] is not None and f['atributo'] not in NO_INTERPRETABLE]
print(f'\nAcuerdo medio (11 atributos)        = {np.mean([f["acuerdo"] for f in filas]):.3f}')
print(f'Kappa mediano ({len(ks)} interpretables) = {np.median(ks):.3f}'
      f'   (rango {min(ks):.3f} a {max(ks):.3f})')
print('d3_gradual_binaria se excluye: kappa no interpretable por ausencia de varianza.')

FIABLES = [f['atributo'] for f in filas
           if f['kappa'] is not None and f['kappa'] >= 0.40 and f['atributo'] in AGRUPA]
print(f'\nAtributos con kappa >= 0,40 usados en la sensibilidad ({len(FIABLES)}):')
for a in FIABLES: print('   -', a)

# ============ 2) ANALISIS DE SENSIBILIDAD ====================================
sub = nuc[nuc.id_definicion != ATIPICA].reset_index(drop=True)

def agrupa(df, atributos, etiqueta):
    X = pd.get_dummies(df[atributos].astype(str)).astype(int)
    X = X.drop(columns=X.columns[X.nunique() == 1])
    D = pdist(X.values, metric='jaccard')
    Z = linkage(D, method='average')
    coph = cophenet(Z, D)[0]
    print(f'\n--- {etiqueta}: n={len(df)}, {X.shape[1]} indicadores, cofenetica={coph:.3f}')
    res = []
    for k in range(2, 7):
        lab = fcluster(Z, k, 'maxclust')
        tam = [int(v) for v in np.bincount(lab)[1:]]
        sil = silhouette_score(squareform(D), lab, metric='precomputed')
        degenerada = min(tam) == 1
        res.append({'esquema': etiqueta, 'k': k, 'silueta': round(sil, 3),
                    'tamanos': str(tam), 'degenerada': degenerada,
                    'cofenetica': round(coph, 3)})
        print(f'   k={k}  silueta={sil:.3f}  tamanos={tam}'
              f'{"  [DEGENERADA: conglomerado unitario]" if degenerada else ""}')
    return Z, D, pd.DataFrame(res)

Z_full, D_full, r_full = agrupa(sub, AGRUPA, 'COMPLETO (10 atributos, pre-especificado)')
Z_fia,  D_fia,  r_fia  = agrupa(sub, FIABLES, f'FIABLES ({len(FIABLES)} atributos, kappa>=0,40)')

lab_full = fcluster(Z_full, 4, 'maxclust')
lab_fia3 = fcluster(Z_fia, 3, 'maxclust')
lab_fia4 = fcluster(Z_fia, 4, 'maxclust')
ari3 = adjusted_rand_score(lab_full, lab_fia3)
ari4 = adjusted_rand_score(lab_full, lab_fia4)
print(f'\nIndice de Rand ajustado  completo(k=4) vs fiables(k=4) = {ari4:.3f}')
print(f'Indice de Rand ajustado  completo(k=4) vs fiables(k=3) = {ari3:.3f}')

sens = pd.concat([r_full, r_fia], ignore_index=True)
sens.loc[len(sens)] = {'esquema': 'ARI completo(k=4) vs fiables(k=4)', 'k': None,
                       'silueta': round(ari4, 3), 'tamanos': '', 'degenerada': None,
                       'cofenetica': None}
sens.loc[len(sens)] = {'esquema': 'ARI completo(k=4) vs fiables(k=3)', 'k': None,
                       'silueta': round(ari3, 3), 'tamanos': '', 'degenerada': None,
                       'cofenetica': None}
sens.to_csv('out/sensibilidad_agrupamiento.csv', index=False)
print('\nEscritos: out/T5_kappa.csv  ·  out/sensibilidad_agrupamiento.csv')
