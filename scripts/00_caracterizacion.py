"""Caracterizacion e integridad del corpus B1 (Scopus, ejecucion 2026-10-12)."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, re, json

df = pd.read_csv('data/B1_scopus_20261012.csv')
print('Registros:', len(df))

# --- integridad -------------------------------------------------------------
print('\n== INTEGRIDAD ==')
print('DOI ausente:', df['DOI'].isna().sum())
print('Resumen ausente:', df['Abstract'].isna().sum())
print('Resumen "[No abstract available]":',
      df['Abstract'].astype(str).str.contains(r'\[No abstract available\]', case=False, na=False).sum())
print('Author Keywords ausentes:', df['Author Keywords'].isna().sum())
print('References ausentes:', df['References'].isna().sum())
print('EID duplicado:', df['EID'].duplicated().sum())

def norm_doi(x):
    if pd.isna(x): return None
    return re.sub(r'^https?://(dx\.)?doi\.org/', '', str(x).strip().lower())
df['doi_norm'] = df['DOI'].apply(norm_doi)
print('DOI duplicado (entre los que tienen DOI):',
      df.loc[df['doi_norm'].notna(), 'doi_norm'].duplicated().sum())

def norm_title(x):
    return re.sub(r'[^a-z0-9]', '', str(x).lower())
df['title_norm'] = df['Title'].apply(norm_title)
print('Titulo normalizado duplicado:', df['title_norm'].duplicated().sum())

# --- caracterizacion --------------------------------------------------------
print('\n== ANO ==');            print(df['Year'].value_counts().sort_index().to_string())
print('\n== TIPO DOCUMENTAL =='); print(df['Document Type'].value_counts(dropna=False).to_string())
print('\n== ESTADO DE PUBLICACION =='); print(df['Publication Stage'].value_counts(dropna=False).to_string())
print('\n== IDIOMA ==');         print(df['Language of Original Document'].value_counts(dropna=False).head(10).to_string())
print('\n== ACCESO ABIERTO ==')
oa = df['Open Access'].fillna('(sin etiqueta OA)')
print('Con alguna etiqueta OA:', (df['Open Access'].notna()).sum(), f'({(df["Open Access"].notna()).mean():.1%})')
print(oa.value_counts().head(8).to_string())
print('\n== CITAS ==')
print(df['Cited by'].describe().to_string())
print('Con 0 citas:', (df['Cited by'].fillna(0) == 0).sum())
print('\n== FUENTES MAS FRECUENTES ==')
print(df['Source title'].value_counts().head(20).to_string())

df.to_csv('out/B1_normalizado.csv', index=False)
