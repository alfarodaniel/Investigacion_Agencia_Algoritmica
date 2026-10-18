# Libro de códigos — Revisión sistemática "Agencia algorítmica"

Versión 1.0 · 2026-10-12 · Codificador: Daniel Alfaro Rojas
Unidad de análisis del Nivel 2: **la definición**, no el artículo. Un documento puede
aportar 0, 1 o varias definiciones codificables.

---

## 0. Diseño en dos niveles

| | Nivel 1 — Caracterización | Nivel 2 — Codificación definicional |
|---|---|---|
| Corpus | B1 completo (642) | B1 ∩ (B2 ∪ B3) = 76 |
| Objetivos | OE1 y OE3 | OE2 |
| Fuente del dato | Metadatos Scopus | Texto completo |
| Unidad | El documento | La definición |

El recorte del Nivel 2 es **pre-especificado**: el título del estudio delimita el
constructo *en la investigación de mercados*, y el núcleo lo operacionaliza como la
intersección entre el corpus del constructo y los corpus de vocabulario de
comportamiento del consumidor y de consumo sostenible.

---

## 1. Cribado a texto completo (archivo `N2_cribado_texto_completo_76.csv`)

### `TEXTO_OBTENIDO_SI_NO`
`SI` si se accedió al texto completo. `NO` si no fue recuperable; esos registros van al
PRISMA como "no recuperados" y se reportan.

### `INCLUIR_SI_NO`
Incluir solo si se cumplen **las dos** condiciones:
1. Aborda explícitamente la relación entre un sistema algorítmico y un proceso
   cognitivo o decisional de una persona en condición de consumidor o usuario.
2. Propone o discute al menos una definición, una dimensión o una medición del
   constructo o de un constructo equivalente.

> **Incluir**: un artículo que define la autonomía del consumidor frente a sistemas de
> recomendación y propone cómo medirla.
> **Excluir**: un artículo que usa un recomendador como herramienta de marketing verde
> sin problematizar la agencia (es instrumento, no objeto).
> **Excluir**: trabajo de *fairness* algorítmico puramente técnico sin sujeto decisor.
> **Excluir**: "manipulación algorítmica" en el sentido de manipulación de mercados
> financieros — homónimo, no el constructo. Registrar el motivo como `homonimo_financiero`.

### `MOTIVO_EXCLUSION`
Valores admitidos (cerrados, para el diagrama PRISMA):
`sin_definicion` · `sin_proceso_cognitivo` · `tecnico_puro` · `gobernanza_sin_agencia` ·
`homonimo_financiero` · `fuera_de_dominio` · `texto_no_recuperado` · `duplicado_tardio`

### `N_DEFINICIONES`
Número entero de definiciones codificables encontradas en el documento. Cuenta como
definición toda formulación que **atribuya un contenido al constructo**, no toda mención.
Una reformulación de la definición de otro autor sin añadido propio no cuenta; una
adopción explícita con matiz añadido, sí.

### `TIPO_ESTUDIO_empirico_teorico_mixto`
`empirico` (recoge o analiza datos primarios o secundarios) · `teorico` (conceptual,
filosófico, jurídico, ensayo) · `mixto` · `revision`.
**Determina la vía de evaluación de calidad.**

### `CALIDAD_MMAT_o_RUBRICA`
- Subconjunto `empirico` y `mixto` → **MMAT 2018**. Registrar como `MMAT:x/5`.
- Subconjunto `teorico` y `revision` → **rúbrica de rigor conceptual** (abajo).
  Registrar como `RC:x/8`.

#### Rúbrica de rigor conceptual (0–2 por criterio, máximo 8)
| Criterio | 0 | 1 | 2 |
|---|---|---|---|
| Claridad definicional | No define el término que usa | Define por ejemplos o sinónimos | Definición explícita y delimitada |
| Explicitación de supuestos | Supuestos ocultos | Algunos declarados | Supuestos ontológicos y normativos declarados |
| Trazabilidad argumental | Afirmaciones sin apoyo | Apoyo parcial | Cada afirmación sustantiva remite a evidencia o a premisa declarada |
| Delimitación de alcance | No declara límites | Límites genéricos | Declara contexto, población y condiciones de aplicación |

Aplicar MMAT a un ensayo filosófico-jurídico produce un puntaje sin sentido. La
bifurcación se declara en Metodología y es una decisión de diseño, no un atajo.

---

## 2. Matriz de definiciones (archivo `N2_matriz_definiciones_VACIA.csv`)

Una fila por definición. `id_definicion` = `<id_nucleo>-D1`, `-D2`, …

### Campos de procedencia
- `pagina_o_localizador` — obligatorio. Sin localizador la definición no es verificable.
- `cita_literal_breve` — **menos de 15 palabras**, entre comillas. Una sola por fuente en
  todo el artículo final. Si la formulación exacta no es el objeto de análisis, dejar vacío.
- `parafraseo_propio` — reformulación completa en palabras propias. Es el campo que se usa
  para codificar; la cita literal es solo respaldo.

### Campos TCCM
- `T_teoria_declarada` — teoría que el documento invoca explícitamente (TPB, SDT,
  racionalidad acotada, teoría crítica, etc.). `ninguna` si no declara.
- `C_contexto` — país o región, sector, plataforma, categoría de producto.
- `C_caracteristicas` — variables o constructos que el documento relaciona con el nuestro.
- `M_metodo` — diseño concreto (encuesta transversal, experimento, etnografía, análisis
  conceptual, auditoría algorítmica, revisión).

### Atributos definicionales — las siete variables del agrupamiento

| Código | Pregunta | Valores admitidos |
|---|---|---|
| `d1_locus_agencia` | ¿A qué se atribuye la agencia? | `sistema` · `usuario` · `relacion` · `distribuida` · `no_explicita` |
| `d2_requiere_conciencia` | ¿La definición presupone que el usuario es consciente de la mediación? | `si` · `no` · `indiferente` |
| `d3_gradual_binaria` | ¿El constructo admite grados? | `gradual` · `binaria` · `no_explicita` |
| `d4_momento_respecto_deliberacion` | ¿Dónde opera respecto del acto deliberativo? | `antes` · `durante` · `despues` · `transversal` · `no_explicita` |
| `d5_medible` | ¿Propone o admite medición? | `si_con_instrumento` · `si_sin_instrumento` · `no` |
| `d5_tipo_indicador` | Si es medible, ¿con qué? | `autoinforme` · `conductual` · `psicofisiologico` · `auditoria_algoritmica` · `documental` · `na` |
| `d6_modelo_consumidor_vinculado` | ¿Se ancla a un modelo de comportamiento del consumidor? | nombre del modelo o `ninguno` |
| `d7_umbrales_no_linealidad` | ¿Contempla saturación, reactancia o umbrales? | `si` · `no` |

**Regla de oro de la codificación:** se codifica lo que el texto *afirma*, no lo que el
texto *implica a juicio del codificador*. Ante duda entre un valor sustantivo y
`no_explicita`, se elige `no_explicita`. Un constructo emergente se caracteriza
precisamente por lo que todavía no dice, y rellenar esos huecos con interpretación propia
destruiría el hallazgo.

### Campos de control
- `codificador`, `fecha_codificacion`
- `ronda` — `1` para la codificación inicial; `2` para la recodificación diferida.

---

## 3. Fiabilidad

Doble codificación **diferida** de una submuestra aleatoria del 20 % del núcleo incluido,
con no menos de catorce días entre rondas y sin consultar la ronda 1. Se calcula kappa de
Cohen por cada atributo d1–d7 por separado, no un kappa global: un promedio escondería
que los atributos con más categorías (d1, d4) son los más difíciles de replicar.

Se declara como limitación que se trata de fiabilidad **intracodificador**, no
intercodificador, por ser un trabajo individual. El clasificador automático de triaje
ensayado sobre B1 y descartado (kappa de Cohen = 0,285 contra cribado manual ciego de 99
registros) se reporta en Limitaciones como procedimiento evaluado y rechazado, con su
métrica.

---

## 4. Análisis

Sobre la matriz definición × atributo, con las variables categóricas convertidas a
indicadores binarios: similitud de Jaccard, agrupamiento jerárquico de enlace promedio,
y comprobación de robustez con enlace de Ward y coeficiente cofenético. Semilla fija
`20261012`. El número de dimensiones se decide por el criterio declarado antes de mirar
el resultado: mayor salto en la distancia de fusión, verificado contra la silueta.

Las dimensiones emergen del procedimiento. Si el resultado contradice las tres
dimensiones propuestas en la Fase 2 (transparencia percibida, amplitud percibida del
conjunto de consideración, intensidad emocional percibida), **se reporta la contradicción**;
esa discrepancia sería, de hecho, un hallazgo más valioso que la confirmación.

---

# Adenda v2.0 — 2026-10-12, tras auditoría del lote 1 (11 definiciones, 7 documentos)

## A. Corpus factible y limitación de acceso

La recuperación de texto completo del lote 1 fue de 8 de 20, y está **enteramente
explicada por el estatus de acceso abierto**: 8 de 9 documentos en acceso abierto
recuperados, 0 de 11 en acceso restringido. El acceso institucional disponible (Elsevier
/ ScienceDirect) cubre solo 4 de los 76 documentos del núcleo, de los cuales 1 es de
acceso restringido.

**Corpus factible = 34 de 76 (44,7 %)**: 33 en acceso abierto más 1 de Elsevier.
Las editoriales no alcanzables son IGI Global (7 documentos), Springer (6), Emerald (6),
Taylor & Francis (3), IEEE (3), Sage (2) y Wiley (2).

Esta restricción se declara como limitación de acceso y se reporta además como
**hallazgo**: en un constructo emergente, menos de la mitad de la literatura indexada en
el campo es consultable sin suscripción institucional amplia, lo que condiciona
estructuralmente qué puede sintetizar un investigador individual.

## B. Rol del constructo — variable nueva, obligatoria

El lote 1 reveló que solo 5 de 11 definiciones definen la agencia o la autonomía del
consumidor; las 6 restantes definen constructos contiguos dentro del mismo modelo. Sin
distinguirlos, el agrupamiento jerárquico clasificaría por *tipo de constructo* en lugar
de por *concepción de la agencia*.

`rol_del_constructo` — valores admitidos:
- `nucleo` — define la agencia, la autonomía o la autoría cognitiva del consumidor.
- `antecedente` — define un mecanismo del sistema que opera sobre la agencia
  (gobernanza algorítmica, memoria aumentada, pluralidad de IA percibida).
- `consecuencia` — define un efecto de la intervención algorítmica (intrusividad
  percibida, reactancia).
- `marco_normativo` — define un principio de diseño o evaluación que toma la agencia
  como objeto a proteger.
- `vecino` — constructo contiguo que no pertenece a la cadena anterior.

**Regla de análisis:** el dendrograma se calcula sobre `nucleo`. Los otros cuatro roles se
reportan como el **vecindario semántico del constructo**, en una figura aparte, y son un
resultado por derecho propio: describen con qué se relaciona el constructo en los modelos
publicados.

## C. Atributos: dos retirados del agrupamiento, cuatro añadidos

Diversidad de Simpson sobre el lote 1 (0 = constante, no aporta a Jaccard):

| Atributo | k | Simpson | Destino |
|---|---:|---:|---|
| `d3_gradual_binaria` | 1 | 0,000 | **Fuera del agrupamiento.** Se reporta como consenso: 11/11 conciben el constructo como gradual. |
| `d5_medible` | 2 | 0,298 | **Fuera del agrupamiento.** Consenso: 0/11 lo declaran no medible. |
| `d1_locus_agencia` | 3 | 0,314 | Se conserva. Baja varianza pero sustantiva: 9/11 lo sitúan en la relación. |
| `d5_tipo_indicador` | 3 | 0,430 | Se conserva. |
| `d7_umbrales_no_linealidad` | 2 | 0,496 | Se conserva. |
| `d2_requiere_conciencia` | 3 | 0,645 | Se conserva. |
| `d4_momento_respecto_deliberacion` | 4 | 0,678 | Se conserva. |

Se siguen codificando d3 y d5_medible: su constancia es el hallazgo. Lo que se excluye es
su participación en el cálculo de similitud.

Cuatro atributos nuevos, derivados de las distinciones que el propio lote 1 hizo visibles:

| Código | Pregunta | Valores |
|---|---|---|
| `d8_naturaleza_del_constructo` | ¿Qué clase de entidad es? | `capacidad` · `condicion_relacional` · `propiedad_estructural` · `postura_o_disposicion` · `estado_psicologico` |
| `d9_via_de_perdida` | ¿Cómo se pierde o cede la agencia? | `delegacion_voluntaria` · `manipulacion_encubierta` · `filtrado_del_acceso` · `sobrecarga_cognitiva` · `no_aplica` · `no_explicita` |
| `d10_valencia_normativa` | ¿Cómo evalúa la mediación algorítmica? | `negativa` · `neutra` · `ambivalente` · `potencialmente_positiva` |
| `d11_nivel_de_analisis` | ¿En qué nivel se predica? | `individual` · `diadico_usuario_sistema` · `mercado_institucional` |

`d9` se añade porque el lote 1 contrapuso explícitamente la rendición voluntaria de
agencia (N-016, N-006-D2) a la manipulación encubierta y al filtrado del acceso; es la
distinción más prometedora del corpus y ningún atributo previo la capturaba.

## D. Correcciones al lote 1

1. `cita_literal_breve` excede el límite de 15 palabras en `N-006-D2` (15) y `N-013-D3`
   (17). Recortar.
2. `fecha_codificacion` quedó como número de serie de hoja de cálculo (46307). Formato
   ISO `2026-10-12`.
3. Codificar `rol_del_constructo` y `d8`–`d11` en las 11 filas existentes.

## E. Hallazgo teórico del lote 1

Entre las teorías declaradas en las 11 definiciones: Self-Determination Theory 5 veces,
Stimulus-Organism-Response 2, modelo EKB 2, arquitectura de la decisión y nudging 2,
carga cognitiva 1. **La Teoría del Comportamiento Planificado aparece 0 veces, y el
Modelo de Aceptación Tecnológica 0 veces.**

Esto obliga a reformular el marco de referencia del artículo. Las Fases 1 y 2
problematizaron el supuesto de agencia individual de la TPB; el corpus muestra que la
literatura del constructo no discute la TPB: se ancló en la teoría de la
autodeterminación. La TPB se conserva en el marco como el supuesto que la disciplina
receptora mantiene, no como el marco con el que la literatura del constructo dialoga, y
la divergencia se reporta en Discusión.
