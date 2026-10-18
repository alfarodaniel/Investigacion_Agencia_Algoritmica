"""PRISMA 2020 con la restriccion de acceso + tabla de acceso reportable."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, json, re

c = pd.read_csv('data/N2_cribado_L1.csv', encoding='latin-1')
c['oa'] = c['Open Access'].notna()
c['elsevier'] = c['DOI'].astype(str).str.startswith('10.1016')
c['alcanzable'] = c['oa'] | c['elsevier']

B = {k: pd.read_csv(f'data/{k}_scopus_20261012.csv') for k in ['B1','B1b','B2','B3']}
s = {k: set(d['EID']) for k, d in B.items()}

# ---------- tabla de acceso por editorial ----------------------------------
EDIT = {'10.1016':'Elsevier','10.1177':'Sage','10.1002':'Wiley','10.1007':'Springer',
        '10.1080':'Taylor & Francis','10.1108':'Emerald','10.3390':'MDPI','10.4018':'IGI Global',
        '10.1109':'IEEE','10.1111':'Wiley','10.1063':'AIP','10.54648':'Kluwer/Wolters',
        '10.3389':'Frontiers','10.1145':'ACM'}
def ed(doi):
    p = re.match(r'^(10\.\d+)', str(doi))
    return EDIT.get(p.group(1), 'Otras') if p else 'Sin DOI'
c['editorial'] = c['DOI'].apply(ed)
t = pd.crosstab(c['editorial'], c['alcanzable'], margins=True, margins_name='Total')
t.columns = ['No alcanzable', 'Alcanzable', 'Total'] if len(t.columns) == 3 else t.columns
t = t.sort_values('Total', ascending=False)
print('== ACCESO AL TEXTO COMPLETO POR EDITORIAL (nucleo, n=76) ==')
print(t.to_string())
t.to_csv('out/T3_acceso_por_editorial.csv')

print('\n== RESUMEN DE ACCESO ==')
res = pd.DataFrame({
  'Categoria': ['Acceso abierto (cualquier via)', 'Restringido pero Elsevier/ScienceDirect',
                'Restringido sin acceso institucional', 'TOTAL nucleo'],
  'n': [int(c['oa'].sum()), int((~c['oa'] & c['elsevier']).sum()),
        int((~c['alcanzable']).sum()), len(c)]})
res['%'] = (res['n'] / len(c) * 100).round(1)
print(res.to_string(index=False))
res.to_csv('out/T3b_resumen_acceso.csv', index=False)

# ---------- PRISMA ----------------------------------------------------------
alc = int(c['alcanzable'].sum())
leidos = int((c['TEXTO_OBTENIDO_SI_NO'] == 'SI').sum())
incl = int((c['INCLUIR_SI_NO'] == 'SI').sum())
excl = int((c['INCLUIR_SI_NO'] == 'NO').sum())
defs = 11

prisma = {
 'IDENTIFICACION': {
   'B1 constructo (bloque A), Scopus 2026-10-12': len(s['B1']),
   'B1b sensibilidad (A + consumer agency, algorithmic nudg*)': len(s['B1b']),
   'B2 arquitectura x consumidor': len(s['B2']),
   'B3 arquitectura x sostenible': len(s['B3']),
   'Registros brutos sumados': sum(len(v) for v in s.values()),
   'Duplicados entre busquedas': sum(len(v) for v in s.values()) - len(set().union(*s.values())),
   'Registros unicos': len(set().union(*s.values())),
 },
 'NIVEL_1_caracterizacion': {
   'Corpus de caracterizacion bibliometrica (B1)': len(s['B1']),
   'Analizado con metadatos, sin lectura de texto completo': len(s['B1']),
 },
 'NIVEL_2_codificacion': {
   'Nucleo pre-especificado B1 ∩ (B2 ∪ B3)': len(s['B1'] & (s['B2'] | s['B3'])),
   'Texto completo alcanzable': alc,
   'No alcanzable por restriccion de acceso': len(c) - alc,
   'Texto completo evaluado (lote 1)': leidos,
   'Incluidos (lote 1)': incl,
   'Excluidos (lote 1)': excl,
   'Motivos de exclusion (lote 1)': c.loc[c['INCLUIR_SI_NO']=='NO','MOTIVO_EXCLUSION'].value_counts().to_dict(),
   'Definiciones extraidas (lote 1)': defs,
   'Pendientes de lectura': alc - leidos,
 },
 'PROYECCION_al_cierre': {
   'Incluidos esperados': round(alc * incl / leidos),
   'Definiciones esperadas': round(alc * defs / leidos),
   'De ellas, rol nucleo (5/11 observado)': round(alc * defs / leidos * 5/11),
 },
}
print('\n== PRISMA ==')
print(json.dumps(prisma, indent=2, ensure_ascii=False))
json.dump(prisma, open('out/prisma_counts.json','w'), indent=2, ensure_ascii=False)

# ---------- candidatos a solicitud al autor --------------------------------
cand = c[~c['alcanzable']].sort_values('Cited by', ascending=False).head(6)
cols = ['id_nucleo','Authors2','Title','Year','Source title','Cited by','DOI','editorial']
cand[cols].to_csv('out/solicitud_a_autores.csv', index=False)
print('\n== CANDIDATOS A SOLICITUD DIRECTA AL AUTOR ==')
for r in cand.itertuples():
    print(f'  [{r._8:>3}] {str(r.Title)[:68]}')
    print(f'        {str(r._5)[:48]} | {r.editorial} | {r.DOI}')
