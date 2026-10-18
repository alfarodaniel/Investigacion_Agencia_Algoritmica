"""Auditoria del lote 1 + plantilla v2 con atributos ampliados y rol del constructo."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import pandas as pd, numpy as np

m = pd.read_csv('data/N2_matriz_L1.csv', encoding='latin-1')

# --- varianza de cada atributo (lo que decide si sirve para el agrupamiento) --
print('== VARIANZA DE LOS ATRIBUTOS (lote 1, n=11) ==')
attrs = ['d1_locus_agencia', 'd2_requiere_conciencia', 'd3_gradual_binaria',
         'd4_momento_respecto_deliberacion', 'd5_medible', 'd5_tipo_indicador',
         'd7_umbrales_no_linealidad']
for a in attrs:
    vc = m[a].value_counts()
    # indice de diversidad de Simpson (1 - sum p^2); 0 = constante
    p = vc / vc.sum()
    simpson = 1 - (p ** 2).sum()
    marca = 'CONSTANTE - inutil para Jaccard' if len(vc) == 1 else (
            'casi constante' if simpson < 0.35 else 'discrimina')
    print(f'  {a:34s} k={len(vc)}  Simpson={simpson:.3f}  {marca}')

# --- rol del constructo: propuesta de reclasificacion ------------------------
# Derivada de los parafraseos del codificador, NO de los textos originales.
rol = {
 'N-001-D1': ('nucleo',    'autonomia del consumidor: el constructo mismo'),
 'N-006-D1': ('antecedente','AI-Augmented Memory: mecanismo del sistema que opera sobre la agencia'),
 'N-006-D2': ('nucleo',    'autonomy stance: tipologia de posturas de agencia'),
 'N-010-D1': ('marco_normativo','compromiso etico: principio de diseno que toma la autonomia como objeto a proteger'),
 'N-013-D1': ('antecedente','gobernanza algoritmica: mecanismo del sistema'),
 'N-013-D2': ('vecino',    'propiedad psicologica territorial: constructo contiguo, no de agencia'),
 'N-013-D3': ('consecuencia','intrusividad percibida: efecto de la intervencion algoritmica'),
 'N-014-D1': ('nucleo',    'autonomia en decisiones de gasto: el constructo mismo'),
 'N-016-D1': ('nucleo',    'autonomia del consumidor con rendicion de agencia: el constructo mismo'),
 'N-018-D1': ('antecedente','pluralidad de IA percibida: propiedad estructural de la arquitectura'),
 'N-018-D2': ('nucleo',    'autonomia del consumidor: el constructo mismo'),
}
m['rol_del_constructo_PROPUESTO'] = m['id_definicion'].map(lambda x: rol.get(x, ('', ''))[0])
m['rol_justificacion'] = m['id_definicion'].map(lambda x: rol.get(x, ('', ''))[1])
print('\n== ROL DEL CONSTRUCTO (propuesta a validar) ==')
print(m['rol_del_constructo_PROPUESTO'].value_counts().to_string())
for r in m.itertuples():
    print(f'  {r.id_definicion}  {r.rol_del_constructo_PROPUESTO:16s} {r.rol_justificacion}')

# --- teorias: recuento ------------------------------------------------------
print('\n== TEORIAS DECLARADAS: frecuencia de familias ==')
fam = {
 'Self-Determination Theory (SDT)': r'Self-Determination|SDT|Basic Psychological Need',
 'Stimulus-Organism-Response':      r'Stimulus-Organism|S-O-R|SOR',
 'EKB / proceso de decision':       r'EKB|Engel-Kollat',
 'Arquitectura de la decision / nudging': r'[Cc]hoice architecture|nudging',
 'Carga cognitiva':                 r'Cognitive Load',
 'Propiedad psicologica':           r'[Pp]sychological ownership|territorial',
 'Gobernanza algoritmica':          r'[Aa]lgorithmic governance',
 'Teoria del Comportamiento Planificado (TPB)': r'Planned Behavio|\bTPB\b|Ajzen',
 'TAM':                             r'\bTAM\b|Technology Acceptance',
}
t = m['T_teoria_declarada'].fillna('') + ' | ' + m['d6_modelo_consumidor_vinculado'].fillna('')
for k, pat in fam.items():
    print(f'  {k:46s} {int(t.str.contains(pat, regex=True).sum()):2d} / 11')

# --- cita literal: control de longitud --------------------------------------
print('\n== CONTROL DE CITA LITERAL (< 15 palabras) ==')
for r in m.itertuples():
    n = len(str(r.cita_literal_breve).split())
    if n >= 15:
        print(f'  EXCEDE  {r.id_definicion}  {n} palabras -> recortar')

m.to_csv('out/N2_matriz_L1_auditada.csv', index=False)
