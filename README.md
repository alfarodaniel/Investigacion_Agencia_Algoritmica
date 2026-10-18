# Agencia algorítmica como constructo emergente en la investigación de mercados

**Revisión sistemática de definiciones, dimensiones y operacionalizaciones (2021–2026)**

Datos y código para reproducibilidad del artículo. Las **112 cifras publicadas se recalculan desde los datos crudos con una sola orden** y el repositorio incluye el informe de verificación.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Licencia código](https://img.shields.io/badge/c%C3%B3digo-MIT-green)
![Licencia texto](https://img.shields.io/badge/texto%20y%20datos-CC--BY--4.0-lightgrey)

---

## El problema que aborda el estudio

Los sistemas de recomendación hiper-personalizados han dejado de operar como canal para constituirse en arquitectos del conjunto de consideración del consumidor. Varias teorias nombran ya ese desplazamiento —*algorithmic agency*, *consumer autonomy*, *illusion of autonomy*, *algorithmic bounded rationality*—, pero con lenguajes distintos, lo que dificulta su medición integrada.

La revisión toma **la definición, y no el artículo, como unidad de análisis**: de 18 documentos se extrajeron 40 definiciones (2,22 por documento), lo que hace visible un acuerdo que una revisión convencional habría pasado por alto.

### Tres resultados

| Hallazgo | Cifra |
|---|---|
| El nombre propio del constructo es minoritario en su propia literatura | *algorithmic agency* aparece en el **7,8 %** de los 642 documentos; *algorithmic curation* en el 36,4 % |
| El campo está disperso de forma medible | 642 documentos en **496 fuentes**; 63,4 % del corpus en revistas con un solo documento; Herfindahl 0,0029; **1,87 áreas temáticas por documento** |
| Las literaturas no dialogan | Solo el **11,5 %** del corpus del constructo toca el vocabulario de comportamiento del consumidor, y el **1,2 %** el de consumo sostenible |

Y dos consensos en las 40 definiciones: el constructo es **gradual** (40/40) y **relacional** (26/40, frente a 9 que lo sitúan en el sistema y 5 en el usuario).

---

## Inicio rápido

```bash
git clone https://github.com/<usuario>/<repositorio>.git
cd <repositorio>

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

bash run_all.sh                      # ~2 minutos
cat out/verificacion_cifras.csv      # las 112 cifras y su recálculo
```

No hay rutas que editar: los guiones resuelven la raíz del repositorio desde su propia ubicación.

---

## Verificación automática

El guion `scripts/15_verificacion_cifras.py` recalcula desde los datos de entrada **cada cifra publicada en el artículo** y la compara con el valor impreso. Devuelve código de salida `0` si todas coinciden y `1` si alguna discrepa, de modo que puede integrarse en una comprobación continua.

```bash
python3 scripts/15_verificacion_cifras.py
# Cifras verificadas: 112  ·  coinciden: 112  ·  discrepan: 0
```

Durante el desarrollo, este guion detectó dos inconsistencias reales en el manuscrito —una mediana de kappa calculada sobre un valor marcado como no interpretable, y un índice de Rand ajustado cruzado entre dos particiones—. Ambas se corrigieron antes de la publicación. Esa es la función del guion.

---

## Estructura

```
.
├── Articulo_Alfaro_Agencia_Algoritmica.pdf
├── run_all.sh               Ejecuta la cadena completa
├── requirements.txt         Dependencias con versiones exactas
├── MANIFEST.csv             SHA-256 de cada archivo
├── data/                    ENTRADAS · solo lectura
├── docs/                    Libro de códigos
├── scripts/                 15 guiones de Python + 1 de Node.js
├── out/                     Tablas, figuras y artículo maquetado · regenerable
└── logs/                    Registro por paso · regenerable
```

`rm -rf out logs && bash run_all.sh` reconstruye todo sin pérdida.

---

## Cadena de análisis

| Guion | Qué hace | Produce |
|---|---|---|
| `00_caracterizacion.py` | Integridad y descriptivos de B1 | Distribución anual, acceso abierto, citas |
| `01_triaje.py` | Clasificador por reglas + muestra ciega | 99 registros para cribado humano |
| `02_validacion_umbral.py` | Valida el clasificador | **κ = 0,285 → se descarta** |
| `03_solapamiento.py` | Intersecciones entre cadenas | Núcleo de 76 documentos |
| `04_prevalencia_y_supervisado.py` | Prevalencia estratificada + control supervisado | 181 incluidos estimados; AUC 0,884 |
| `05_nivel1_caracterizacion.py` | Tablas del Nivel 1 | Tabla 1, Tabla 2, Herfindahl |
| `06_nivel2_plantillas.py` | Plantillas de codificación | Formularios de cribado y extracción |
| `07_auditoria_lote1.py` | Auditoría del primer lote | Diversidad de Simpson por atributo |
| `08_prisma_y_acceso.py` | Acceso por editorial | 42 de 76 inaccesibles |
| `09_cluster.py` · `10_final.py` | Jaccard + enlace promedio | **4 dimensiones**, silueta 0,247 |
| `14_kappa_y_sensibilidad.py` | Fiabilidad y sensibilidad | Tabla 3; ARI 0,537 |
| `15_verificacion_cifras.py` | **Verificación integral** | `verificacion_cifras.csv` |
| `11`, `13`, `14_*.py` | Figuras | PRISMA, dendrograma, intersección |

---

## Honestidad metodológica

El repositorio conserva deliberadamente lo que no funcionó, porque forma parte del registro:

- **El clasificador de triaje se descarta.** Alcanzó κ = 0,285 contra cribado humano ciego. Se conserva su código y su validación. Ajustar el umbral hasta obtener un número presentable habría sido sobreajuste sobre la misma muestra de validación.
- **La fiabilidad es desigual.** Cuatro de los once atributos quedaron por debajo de κ = 0,35. Uno de ellos, la exigencia de conciencia (κ = 0,143), es justamente el que separa dos de las cuatro dimensiones. El artículo lo reporta y jerarquiza los hallazgos en consecuencia.
- **La estructura es moderada.** Silueta 0,247. El análisis de sensibilidad sobre atributos fiables devuelve tres dimensiones en lugar de cuatro (ARI 0,537). Las dimensiones son agrupamientos interpretables, no particiones nítidas.
- **La fiabilidad es intracodificador, no intercodificador.** Trabajo individual, con un intervalo de cuatro días entre rondas, inferior al recomendado.

---

## Qué no es reproducible, y por qué

**Los textos completos.** Los 45 documentos leídos están sujetos a derechos de autor y no se redistribuyen. Sus DOI están en `data/N2_cribado_FINAL.csv`; 33 de los 76 del núcleo están en acceso abierto.

**El juicio del codificador.** Los seis archivos de codificación manual son producto de la lectura humana, no de un cálculo. Un replicador producirá archivos similares pero no idénticos, y la Tabla 3 cuantifica la magnitud esperable de esa diferencia.

**El corpus en el tiempo.** Scopus indexa de forma continua: reejecutar las cadenas devolverá más registros. Para reproducir exactamente el estudio deben usarse los exportes congelados al 12 de octubre de 2026.

---

## Datos y licencias

Este repositorio combina materiales con tres regímenes distintos:

| Material | Licencia |
|---|---|
| Código (`scripts/`, `run_all.sh`) | MIT |
| Libro de códigos (`docs/`) | CC BY 4.0 |
| Archivos de codificación manual (`data/N2_*`, `data/RONDA2.csv`, `data/B1_muestra_*`) | CC BY 4.0 |
| Exportes de Scopus (`data/B*_scopus_*.csv`) | Datos de Elsevier · véase la nota siguiente |


---

## Cómo citar

**El artículo**

> Alfaro Rojas, D. (2026). La agencia algorítmica como constructo emergente en la investigación de mercados: revisión sistemática de definiciones, dimensiones y operacionalizaciones (2021–2026). Instituto Europeo de Posgrado.

**El repositorio**

> Alfaro Rojas, D. (2026). *Paquete de reproducibilidad: agencia algorítmica en la investigación de mercados* [Datos y código]. GitHub. https://github.com/alfarodaniel/Investigacion_Agencia_Algoritmica

El archivo `CITATION.cff` permite a GitHub generar la cita automáticamente.

---

## Autor

**Daniel Alfaro Rojas** — Doctorado en Ciencias Administrativas, Instituto Europeo de Posgrado · Bogotá, Colombia

Ingeniero de sistemas con maestría en inteligencia analítica de datos.

---

## Agradecimiento metodológico

El procesamiento de datos bibliográficos, la ejecución de los guiones de análisis, la generación de figuras y el apoyo a la redacción se realizaron con asistencia de inteligencia artificial. Las decisiones metodológicas, los criterios de elegibilidad, la codificación de la totalidad de las definiciones y la interpretación de los resultados son del autor, único responsable del contenido. La declaración completa está en la sección 7 del artículo.
