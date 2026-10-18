"""PRISMA en formato vertical estrecho, para ancho de columna."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = 'out'
TINTA, SUAVE, BORDE = '#1a1a1a', '#6b6b6b', '#b9bfc7'
AZUL, AZUL_C, GRIS_C = '#2d5f8a', '#cfe0ee', '#f0f1f3'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': TINTA})

fig, ax = plt.subplots(figsize=(3.05, 5.6), dpi=400)
ax.set_xlim(0, 100); ax.set_ylim(0, 200); ax.axis('off')

def caja(x, y, w, h, txt, fc=GRIS_C, ec=BORDE, fs=4.6, bold=False, lw=.7):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.8,rounding_size=1.6',
                                fc=fc, ec=ec, lw=lw))
    ax.text(x + w/2, y + h/2, txt, ha='center', va='center', fontsize=fs,
            linespacing=1.55, fontweight='bold' if bold else 'normal')

def fl(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=5,
                                 lw=.7, color=SUAVE, shrinkA=0, shrinkB=0))

def etapa(y, t, fs=4.8):
    ax.text(1.5, y, t, ha='left', va='center', fontsize=fs, color=AZUL,
            fontweight='bold', rotation=90)

MX, MW, CX = 12, 86, 55

etapa(177, 'IDENTIFICACIÓN', 4.4)
caja(MX, 166, MW, 22, 'Registros identificados en Scopus\n(ejecución 12-10-2026)\n'
     'B1 constructo = 642\nB2 constructo × consumidor = 525\nB3 constructo × sostenible = 59\n'
     'Total bruto = 1 226', AZUL_C, AZUL)
fl(CX, 166, CX, 162)
caja(MX, 151, MW, 11, 'Duplicados entre búsquedas = 106\n→ Registros únicos = 1 120')
fl(CX, 151, CX, 143)

etapa(131, 'NIVEL 1', 4.4)
caja(MX, 123, MW, 20, 'CARACTERIZACIÓN BIBLIOMÉTRICA\nCorpus B1 completo (n = 642)\n'
     'Solo metadatos; sin lectura de\ntexto completo\n→ Objetivos específicos 1 y 3',
     AZUL_C, AZUL, 4.6, True, 1.2)
fl(CX, 123, CX, 115)

etapa(70, 'NIVEL 2', 4.4)
caja(MX, 104, MW, 11, 'Núcleo pre-especificado\nB1 ∩ (B2 ∪ B3)   ·   n = 76')
fl(CX, 104, CX, 96)
caja(MX, 83, MW, 13, 'Texto completo evaluado · n = 45\n'
     '31 no recuperados por restricción\nde acceso a la fuente')
fl(CX, 83, CX, 75)
caja(MX, 62, MW, 13, 'Documentos incluidos · n = 18\n'
     '27 excluidos tras lectura por\nausencia de definición codificable')
fl(CX, 62, CX, 54)
caja(MX, 42, MW, 12, 'Definiciones extraídas · n = 40\n(2,22 por documento incluido)', AZUL_C, AZUL)
fl(42, 42, 30, 34); fl(68, 42, 80, 34)
caja(1, 16, 52, 18, 'Rol nuclear\nn = 19 (18 + 1 atípica)\nAgrupamiento jerárquico\n'
     'sobre atributos definicionales\n→ Objetivo específico 2', AZUL_C, AZUL, 4.5, True, 1.2)
caja(56, 16, 43, 18, 'Vecindario semántico\nn = 21\n11 antecedentes\n4 consecuencias\n'
     '3 marcos normativos\n3 vecinos', GRIS_C, BORDE, 4.3)

caja(MX, 1, MW, 10, 'Sensibilidad (no incorporada): B1b = 785,\n'
     '+143 sobre B1 (+22,3 %); añade "consumer\nagency" y "algorithmic nudg*"',
     '#fbfbfb', BORDE, 4.1)

plt.tight_layout(pad=.2)
plt.savefig(f'{OUT}/F1_prisma_col.png', bbox_inches='tight', facecolor='white')
print('F1_prisma_col.png')
