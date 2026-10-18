"""(a) Prevalencia ponderada de inclusion en B1. (b) Clasificador supervisado validado."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score

SEED = 20261012
m = pd.read_csv('out/validacion_merge.csv')
tri = pd.read_csv('out/B1_triaje.csv')

# ---------- (a) prevalencia ponderada por banda ----------
tam = tri['banda'].value_counts()
res = []
for b, g in m.groupby('banda'):
    N, n = tam[b], len(g)
    res.append({'banda': b, 'N_banda': N, 'n_muestra': n,
                'p_incluir': g['incluir'].mean(), 'p_definicion': g['definicion'].mean(),
                'est_incluir': N * g['incluir'].mean(), 'est_definicion': N * g['definicion'].mean()})
R = pd.DataFrame(res).sort_values('banda')
print('== PREVALENCIA PONDERADA (estimador estratificado) ==')
print(R.to_string(index=False, float_format=lambda x: f'{x:.3f}'))
EI, ED, N = R['est_incluir'].sum(), R['est_definicion'].sum(), tam.sum()
# error estandar (muestreo estratificado sin reposicion)
var = sum((row.N_banda**2) * (1 - row.n_muestra/row.N_banda) *
          (row.p_incluir*(1-row.p_incluir))/max(row.n_muestra-1, 1) for row in R.itertuples())
print(f'\nIncluidos estimados en B1: {EI:.0f} de {N}  ({EI/N:.1%})  IC95% aprox +/- {1.96*np.sqrt(var):.0f}')
print(f'Con definicion codificable:  {ED:.0f} de {N}  ({ED/N:.1%})')

# ---------- (b) clasificador supervisado ----------
txt_cols = ['Title', 'Abstract', 'Author Keywords', 'Index Keywords']
tri['texto'] = tri[txt_cols].fillna('').agg(' '.join, axis=1)
lab = m[['id_registro', 'incluir']].merge(tri[['id_registro', 'texto']], on='id_registro')
X, y = lab['texto'].values, lab['incluir'].values.astype(int)
print(f'\n== SUPERVISADO: {len(y)} etiquetas, {y.sum()} positivas ==')

pipe = make_pipeline(
    TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), min_df=2, max_df=0.9, stop_words='english'),
    LogisticRegression(C=1.0, class_weight='balanced', max_iter=2000, random_state=SEED))
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
p = cross_val_predict(pipe, X, y, cv=cv, method='predict_proba')[:, 1]
print(f'AUC validado (5-fold): {roc_auc_score(y, p):.3f}')
print(f"{'umbral':>7} {'sens':>7} {'espec':>7} {'%retenido':>10}")
for q in np.arange(0.05, 0.95, 0.05):
    pred = p >= q
    sens = (pred & (y == 1)).sum() / max((y == 1).sum(), 1)
    espec = (~pred & (y == 0)).sum() / max((y == 0).sum(), 1)
    print(f'{q:>7.2f} {sens:>7.3f} {espec:>7.3f} {pred.mean():>9.1%}')
cand = [q for q in np.arange(0.05, 0.95, 0.01)
        if (p >= q)[y == 1].mean() >= 0.95]
if cand:
    q = max(cand)
    print(f'\nMayor umbral con sensibilidad >= 0.95: {q:.2f} -> retiene {(p>=q).mean():.1%}')
else:
    print('\nNingun umbral alcanza sensibilidad >= 0.95')
