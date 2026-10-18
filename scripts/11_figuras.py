"""Figuras 1 y 3 para el manuscrito. Estilo de revista: sobrio, seguro en escala de grises."""
# --- portabilidad: resuelve la raiz del paquete y trabaja con rutas relativas ---
import os as _os
_RAIZ = _os.environ.get('SRL_RAIZ') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(_RAIZ)
# -----------------------------------------------------------------------------
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np, json

OUT = 'out'
TINTA  = '#1a1a1a'; SUAVE = '#6b6b6b'; BORDE = '#b9bfc7'
AZUL   = '#2d5f8a'; AZUL_C = '#c9dcea'; GRIS_C = '#eceef1'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'text.color': TINTA, 'axes.labelcolor': TINTA})

# ===================== FIGURA 1 — PRISMA ====================================
fig, ax = plt.subplots(figsize=(7.0, 8.4), dpi=220)
ax.set_xlim(0, 100); ax.set_ylim(0, 118); ax.axis('off')

def caja(x, y, w, h, texto, relleno=GRIS_C, borde=BORDE, negrita=None, fs=7.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.6,rounding_size=1.2',
                                fc=relleno, ec=borde, lw=.9))
    ax.text(x + w/2, y + h/2, texto, ha='center', va='center', fontsize=fs,
            color=TINTA, linespacing=1.45, fontweight=negrita or 'normal')

def flecha(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=9,
                                 lw=.9, color=SUAVE, shrinkA=0, shrinkB=0))

def etapa(y, txt):
    ax.text(1.5, y, txt, ha='left', va='center', fontsize=7.6, color=AZUL,
            fontweight='bold', rotation=90)

# --- identificacion
etapa(104, 'IDENTIFICACIÓN')
caja(10, 99, 56, 11,
     'Registros identificados en Scopus (12-10-2026)\n'
     'B1 constructo = 642 · B2 constructo × consumidor = 525\n'
     'B3 constructo × consumo sostenible = 59\nTotal = 1 226', AZUL_C)
caja(70, 99, 28, 11, 'Búsqueda de sensibilidad\nB1b = 785\n(+143 sobre B1)', '#f7f8f9')
flecha(38, 99, 38, 94.5)
caja(10, 86.5, 56, 8, 'Duplicados entre búsquedas eliminados = 106\n→ Registros únicos = 1 120')
flecha(38, 86.5, 38, 82)

# --- nivel 1
etapa(74, 'NIVEL 1')
caja(10, 71, 56, 11,
     'CORPUS DE CARACTERIZACIÓN BIBLIOMÉTRICA\n'
     'B1 completo (n = 642)\nAnálisis de metadatos; sin lectura de texto completo\n'
     '→ Objetivos específicos 1 y 3', AZUL_C, AZUL, 'bold')
flecha(38, 71, 38, 66.5)

# --- nivel 2
etapa(44, 'NIVEL 2')
caja(10, 59, 56, 7.5, 'Núcleo pre-especificado  B1 ∩ (B2 ∪ B3)\nn = 76 documentos')
flecha(38, 59, 38, 54)
caja(10, 46.5, 56, 7.5, 'Texto completo evaluado\nn = 45')
caja(70, 46.5, 28, 7.5, 'No recuperados por\nrestricción de acceso\nn = 31', '#f7f8f9')
flecha(66, 50.2, 70, 50.2)
flecha(38, 46.5, 38, 41.5)
caja(10, 34, 56, 7.5, 'Documentos incluidos\nn = 18')
caja(70, 34, 28, 7.5, 'Excluidos tras lectura\nn = 27\n(sin definición codificable)', '#f7f8f9')
flecha(66, 37.7, 70, 37.7)
flecha(38, 34, 38, 29)

caja(10, 21.5, 56, 7.5, 'Definiciones extraídas\nn = 40  (2,22 por documento)', AZUL_C)

caja(4, 9, 42, 7.5, 'Rol nuclear → agrupamiento jerárquico\nn = 19  (18 + 1 atípica)\n→ Objetivo específico 2', AZUL_C, AZUL, 'bold')
caja(50, 9, 46, 7.5, 'Vecindario semántico\nn = 21  (11 antecedentes, 4 consecuencias,\n3 marcos normativos, 3 vecinos)')
flecha(30, 21.5, 25, 16.5); flecha(46, 21.5, 60, 16.5)

ax.text(50, 3.5, 'Figura 1. Diagrama de flujo PRISMA 2020 adaptado al diseño en dos niveles.',
        ha='center', fontsize=7.6, color=SUAVE, style='italic')
plt.tight_layout(); plt.savefig(f'{OUT}/F1_prisma.png', bbox_inches='tight', facecolor='white')
print('F1_prisma.png')

# ===================== FIGURA 3 — INTERSECCION ==============================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.3), dpi=220,
                               gridspec_kw={'width_ratios': [1.15, 1]})

# panel A: tamano de cada corpus
nom = ['B1\nconstructo', 'B2\n× consumidor', 'B3\n× sostenible']
val = [642, 525, 59]
b = ax1.bar(nom, val, color=[AZUL, '#5b8bb0', '#9dbdd4'], width=.62,
            edgecolor='white', linewidth=1.6)
for r, v in zip(b, val):
    ax1.text(r.get_x() + r.get_width()/2, v + 14, f'{v}', ha='center',
             fontsize=8.2, fontweight='bold', color=TINTA)
ax1.set_ylabel('Documentos indexados')
ax1.set_ylim(0, 720)
ax1.set_title('a) Tamaño de cada corpus', loc='left', fontsize=8.4, fontweight='bold')
ax1.spines[['top','right']].set_visible(False)
ax1.spines[['left','bottom']].set_color(BORDE)
ax1.grid(axis='y', alpha=.3, lw=.5, color=BORDE); ax1.set_axisbelow(True)
ax1.tick_params(colors=SUAVE, length=0)

# panel B: interseccion como proporcion del corpus del constructo
et = ['B1 ∩ B2\nconstructo y\ncomportamiento\ndel consumidor',
      'B1 ∩ B3\nconstructo y\nconsumo\nsostenible']
pr = [74/642*100, 8/642*100]; nn = [74, 8]
y = np.arange(len(et))
ax2.barh(y, [100, 100], color=GRIS_C, height=.5, edgecolor='white', linewidth=1.6)
bb = ax2.barh(y, pr, color=[AZUL, '#9dbdd4'], height=.5, edgecolor='white', linewidth=1.6)
for i, (p, n) in enumerate(zip(pr, nn)):
    ax2.text(p + 2.5, i, f'{p:.1f} %   (n = {n})'.replace('.',','), va='center', fontsize=8.2,
             fontweight='bold', color=TINTA)
ax2.set_yticks(y); ax2.set_yticklabels(et, fontsize=7.2)
ax2.set_xlim(0, 100); ax2.set_xlabel('% del corpus del constructo (B1 = 642)')
ax2.set_title('b) Intersección entre literaturas', loc='left', fontsize=8.4, fontweight='bold')
ax2.spines[['top','right','left']].set_visible(False)
ax2.spines['bottom'].set_color(BORDE)
ax2.grid(axis='x', alpha=.3, lw=.5, color=BORDE); ax2.set_axisbelow(True)
ax2.tick_params(colors=SUAVE, length=0)
ax2.invert_yaxis()

fig.suptitle('Figura 3. Desconexión entre la literatura del constructo y las literaturas de consumo',
             x=.01, ha='left', fontsize=8.6, fontweight='bold', y=1.03)
plt.tight_layout(); plt.savefig(f'{OUT}/F3_interseccion.png', bbox_inches='tight', facecolor='white')
print('F3_interseccion.png')
