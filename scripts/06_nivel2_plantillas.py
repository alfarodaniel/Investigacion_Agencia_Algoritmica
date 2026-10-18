"""NIVEL 2: plantillas de cribado a texto completo y de extraccion definicional."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, re

OUT = 'out'
B = {k: pd.read_csv(f'data/{k}_scopus_20261012.csv') for k in ['B1', 'B2', 'B3']}
s = {k: set(d['EID']) for k, d in B.items()}
nuc = s['B1'] & (s['B2'] | s['B3'])
d = B['B1']
sub = d[d['EID'].isin(nuc)].copy()
sub['en_B2'] = sub['EID'].isin(s['B2'])
sub['en_B3'] = sub['EID'].isin(s['B3'])
sub = sub.sort_values(['Year', 'Cited by'], ascending=[False, False]).reset_index(drop=True)
sub.insert(0, 'id_nucleo', ['N-%03d' % i for i in range(1, len(sub) + 1)])

# --- campo disciplinar refinado (INFERIDO del titulo de la fuente) ----------
DISC = [
 ('Marketing y consumo',        r'market|consum|retail|advertis|brand|commerce|promotion|macromarket'),
 ('Gestion y organizaciones',   r'business|manage|managerial|human resource|employee|organi[sz]ation|knowledge management|decision'),
 ('Comunicacion y medios',      r'communicat|media|journalis|press|broadcast|convergence|first monday|semiotic'),
 ('Computacion, IS y HCI',      r'comput|informat|human-?comput|hci|\bchi\b|intellig|data|system|software|ceur|acm|ieee|lecture notes|machine learning|cryptograph|blockchain|network|mipro|ict'),
 ('Etica, derecho y politica',  r'ethic|law|legal|polic|right|justice|regulat|govern|philos|topoi|dharma|direito|filosofi|dia-noesis'),
 ('Psicologia y conducta',      r'psycholog|behavio|cognit|mind|personality'),
 ('Sociologia y humanidades',   r'sociol|societ|cultur|humanit|religio|anthropol|social science|leisure|heritage|gender|porn studies'),
 ('Artes y creacion',           r'\bart|aesthet|performing|music|design|technoetic|visual'),
 ('Sostenibilidad y ambiente',  r'sustainab|environment|clean|energ|climate|green'),
 ('Educacion y bibliotecas',    r'educat|learning|teach|pedago|curricul|literacy|librar|student|scholarship'),
 ('Salud',                      r'health|medic|nurs|clinic|psychiatr|jmir'),
 ('Multidisciplinar',           r'^nature$|scientific reports|plos one|science advances|encyclopedia|heliyon'),
]
def disc(x):
    t = str(x).lower()
    for n, p in DISC:
        if re.search(p, t):
            return n
    return 'Otros / no clasificado'

b1 = B['B1'].copy()
b1['campo_inferido'] = b1['Source title'].apply(disc)
t1e = b1['campo_inferido'].value_counts().rename('n').to_frame()
t1e['%'] = (t1e['n'] / len(b1) * 100).round(1)
print('== T1e CAMPO DISCIPLINAR (INFERIDO del titulo de la fuente) ==')
print(t1e.to_string())
t1e.to_csv(f'{OUT}/T1e_campo_INFERIDO.csv')

sub['campo_inferido'] = sub['Source title'].apply(disc)
print('\n== Campo dentro del nucleo (76) ==')
print(sub['campo_inferido'].value_counts().to_string())

# --- plantilla de cribado a texto completo ---------------------------------
cols = ['id_nucleo', 'Authors', 'Title', 'Year', 'Source title', 'Document Type',
        'Publication Stage', 'Cited by', 'DOI', 'Open Access', 'en_B2', 'en_B3',
        'campo_inferido', 'Author Keywords', 'Abstract']
crib = sub[cols].copy()
for c in ['TEXTO_OBTENIDO_SI_NO', 'INCLUIR_SI_NO', 'MOTIVO_EXCLUSION',
          'N_DEFINICIONES', 'TIPO_ESTUDIO_empirico_teorico_mixto',
          'CALIDAD_MMAT_o_RUBRICA', 'NOTAS']:
    crib[c] = ''
crib.to_csv(f'{OUT}/N2_cribado_texto_completo_76.csv', index=False)

# --- plantilla de extraccion: una fila por DEFINICION ----------------------
esquema = ['id_definicion', 'id_nucleo', 'doi_fuente', 'autores_anio', 'pagina_o_localizador',
           'cita_literal_breve', 'parafraseo_propio',
           'T_teoria_declarada', 'C_contexto', 'C_caracteristicas', 'M_metodo',
           'd1_locus_agencia', 'd2_requiere_conciencia', 'd3_gradual_binaria',
           'd4_momento_respecto_deliberacion', 'd5_medible', 'd5_tipo_indicador',
           'd6_modelo_consumidor_vinculado', 'd7_umbrales_no_linealidad',
           'codificador', 'fecha_codificacion', 'ronda']
pd.DataFrame(columns=esquema).to_csv(f'{OUT}/N2_matriz_definiciones_VACIA.csv', index=False)
print('\nPlantillas escritas.')
print('Nucleo por anio:'); print(sub['Year'].value_counts().sort_index().to_string())
