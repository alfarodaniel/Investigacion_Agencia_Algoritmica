#!/usr/bin/env bash
# Ejecuta la cadena completa de análisis del artículo sobre agencia algorítmica.
# Uso:  bash run_all.sh            (desde cualquier directorio)
#
# Los pasos marcados [MANUAL] en el HANDBOOK no se ejecutan aquí: sus resultados
# ya están en data/ como archivos de entrada. Este guion reproduce únicamente los
# pasos computacionales.

set -euo pipefail
export SRL_RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SRL_RAIZ"
mkdir -p out logs

PY="python3 -I"
ts() { date '+%H:%M:%S'; }
paso() {
  local n="$1"; shift
  echo ""
  echo "──────────────────────────────────────────────────────────────"
  echo "[$(ts)]  PASO $n  ·  $*"
  echo "──────────────────────────────────────────────────────────────"
}

paso C1 "Integridad y caracterización base de B1"
$PY scripts/00_caracterizacion.py          | tee logs/C1_caracterizacion.log

paso C2 "Clasificador de triaje por reglas y muestra de validación"
$PY scripts/01_triaje.py                   | tee logs/C2_triaje.log

paso C3 "Validación del clasificador contra cribado ciego  (RESULTADO: se descarta)"
$PY scripts/02_validacion_umbral.py        | tee logs/C3_validacion.log

paso C4 "Solapamiento entre B1, B1b, B2 y B3"
$PY scripts/03_solapamiento.py             | tee logs/C4_solapamiento.log

paso C5 "Prevalencia ponderada y clasificador supervisado (control)"
$PY scripts/04_prevalencia_y_supervisado.py| tee logs/C5_prevalencia.log

paso C6 "NIVEL 1 · tablas de caracterización e intersecciones"
$PY scripts/05_nivel1_caracterizacion.py   | tee logs/C6_nivel1.log

paso C7 "NIVEL 2 · plantillas de cribado y de extracción"
$PY scripts/06_nivel2_plantillas.py        | tee logs/C7_plantillas.log

paso C8 "Auditoría del lote 1 de codificación"
$PY scripts/07_auditoria_lote1.py          | tee logs/C8_auditoria.log

paso C9 "PRISMA y análisis de acceso por editorial"
$PY scripts/08_prisma_y_acceso.py          | tee logs/C9_prisma.log

paso C10 "Agrupamiento exploratorio (selección de k)"
$PY scripts/09_cluster.py                  | tee logs/C10_cluster_expl.log

paso C11 "Agrupamiento definitivo · 4 dimensiones + atípico · TCCM"
$PY scripts/10_final.py                    | tee logs/C11_cluster_final.log

paso C12 "Fiabilidad intracodificador (kappa) y análisis de sensibilidad"
$PY scripts/14_kappa_y_sensibilidad.py     | tee logs/C12_kappa.log

paso C13 "VERIFICACIÓN INTEGRAL de las 112 cifras publicadas"
$PY scripts/15_verificacion_cifras.py      | tee logs/C13_verificacion.log

paso C14 "Figuras a ancho de página (no usadas en la versión final)"
$PY scripts/11_figuras.py                  | tee logs/C14_figuras_ancho.log

paso C15 "Figuras 2 y 3 a ancho de columna (versión publicada)"
$PY scripts/12_figuras_columna.py          | tee logs/C15_figuras_col.log

paso C16 "Figura 1 PRISMA a ancho de columna (versión publicada)"
$PY scripts/13_prisma_columna.py           | tee logs/C16_prisma_col.log

echo ""
echo "=============================================================="
echo "  Cadena completa. Salidas en out/ ; registros en logs/"
echo "=============================================================="
