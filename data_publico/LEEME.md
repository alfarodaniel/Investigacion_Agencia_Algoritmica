# Versión redistribuible de los exportes de Scopus

Estos archivos contienen **únicamente identificadores y metadatos factuales**:
EID, DOI, año, tipo de documento, etapa de publicación y estatus de acceso
abierto. No incluyen título, resumen, palabras clave, autores ni referencias,
que son material licenciado por Elsevier y por los editores originales.

| Cadena | Registros | Con DOI | Acceso abierto |
|---|---:|---:|---:|
| B1 | 642 | 603 | 323 |
| B1b | 785 | 743 | 401 |
| B2 | 525 | 497 | 197 |
| B3 | 59 | 57 | 28 |

## Cómo reconstruir el corpus completo

1. Ejecutar en Scopus las cuatro cadenas documentadas en `HANDBOOK.md`,
   sección 4.1, con ventana `PUBYEAR > 2020 AND PUBYEAR < 2027` e idiomas
   inglés y español.
2. Exportar en CSV con los campos *Citation information*, *Bibliographical
   information* y *Abstract & keywords* (y *References* en B1 y B1b).
3. Filtrar el resultado por los EID listados en estos archivos, para obtener
   exactamente el corpus congelado al 12 de octubre de 2026 y descartar lo
   indexado con posterioridad.
4. Guardar los archivos resultantes en `data/` con los nombres
   `B1_scopus_20261012.csv`, `B1b_scopus_20261012.csv`,
   `B2_scopus_20261012.csv` y `B3_scopus_20261012.csv`.
5. Ejecutar `bash run_all.sh`.

La verificación de `scripts/16_verificacion_cifras.py` debe arrojar las 112
cifras coincidentes.
