"""Validacion del clasificador contra cribado manual ciego. Estima el umbral."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, numpy as np

crib = pd.read_csv('data/B1_muestra_validacion_99_CRIBADA.csv', encoding='latin-1')
clave = pd.read_csv('out/muestra_validacion_CLAVE.csv')
tri = pd.read_csv('out/B1_triaje.csv', usecols=['id_registro', 'score', 'banda', 's1_def', 's2_ctx', 's3_exc'])

m = crib[['id_registro', 'INCLUIR_SI_NO', 'APORTA_DEFINICION_SI_NO', 'MOTIVO_EXCLUSION']].merge(tri, on='id_registro', how='left')
m['incluir'] = m['INCLUIR_SI_NO'].str.strip().str.upper().eq('SI')
m['definicion'] = m['APORTA_DEFINICION_SI_NO'].str.strip().str.upper().eq('SI')
print('n =', len(m), '| incluidos:', m['incluir'].sum(), '| con definicion:', m['definicion'].sum())
print('\nIncluidos por banda:')
print(m.groupby('banda', observed=True)[['incluir', 'definicion']].agg(['sum', 'count']).to_string())

# los sin resumen (score NaN) van siempre a revision manual: fuera de la curva
cur = m[m['score'].notna()].copy()
print('\nRegistros en la curva (con resumen):', len(cur))

print('\n== SENSIBILIDAD / ESPECIFICIDAD POR UMBRAL (criterio: INCLUIR) ==')
print(f"{'corte':>6} {'TP':>4} {'FN':>4} {'FP':>4} {'TN':>4} {'sens':>7} {'espec':>7} {'VPP':>7} {'%retenido':>10}")
filas = []
for c in range(int(cur['score'].min()), int(cur['score'].max()) + 1):
    pred = cur['score'] >= c
    tp = int((pred & cur['incluir']).sum());  fn = int((~pred & cur['incluir']).sum())
    fp = int((pred & ~cur['incluir']).sum()); tn = int((~pred & ~cur['incluir']).sum())
    sens = tp / (tp + fn) if tp + fn else np.nan
    espec = tn / (tn + fp) if tn + fp else np.nan
    vpp = tp / (tp + fp) if tp + fp else np.nan
    filas.append((c, sens, espec, vpp))
    print(f'{c:>6} {tp:>4} {fn:>4} {fp:>4} {tn:>4} {sens:>7.3f} {espec:>7.3f} {vpp:>7.3f} {pred.mean():>9.1%}')

# kappa de Cohen en el mejor corte con sens>=0.95
ok = [f for f in filas if f[1] >= 0.95]
corte = max(ok, key=lambda f: f[0])[0] if ok else int(cur['score'].min())
pred = cur['score'] >= corte
po = (pred == cur['incluir']).mean()
pe = pred.mean() * cur['incluir'].mean() + (1 - pred.mean()) * (1 - cur['incluir'].mean())
kappa = (po - pe) / (1 - pe)
print(f'\nUmbral elegido (mayor corte con sensibilidad >= 0.95): score >= {corte}')
print(f'Acuerdo observado = {po:.3f} | kappa de Cohen = {kappa:.3f}')

# --- aplicacion a los 642 ---------------------------------------------------
full = pd.read_csv('out/B1_triaje.csv',
                   usecols=['id_registro', 'Title', 'Year', 'Source title', 'Document Type',
                            'Publication Stage', 'DOI', 'Cited by', 'Open Access', 'score',
                            'banda', 's1_def', 's2_ctx', 's3_exc', 'sin_resumen'])
full['pasa_triaje'] = (full['score'] >= corte) | full['sin_resumen']
n_pasa = int(full['pasa_triaje'].sum())
print(f'\n== APLICACION A B1 (n=642) ==')
print(f'Pasan a lectura manual de resumen: {n_pasa} ({n_pasa/len(full):.1%})')
print(f'Excluidos por regla: {len(full)-n_pasa}')
print('\nPasan, por ano:'); print(full[full.pasa_triaje]['Year'].value_counts().sort_index().to_string())

# proyeccion de definiciones codificables
tasa_def = cur.loc[cur['score'] >= corte, 'definicion'].mean()
print(f'\nTasa de "aporta definicion" entre los que pasan el corte (en muestra): {tasa_def:.3f}')
print(f'Proyeccion de articulos con definicion en B1: {tasa_def*n_pasa:.0f}')

full.to_csv('out/B1_triaje_aplicado.csv', index=False)
m.to_csv('out/validacion_merge.csv', index=False)
