# Fundación Código Abierto

Hagamos del Caribe el nuevo epicentro tecnológico de Colombia. Este sistema reúne cómo se ve y cómo suena la Fundación Código Abierto (FCA) en la web, en los documentos y en los eventos, para que cualquier pieza nueva, la haga quien la haga, se reconozca como nuestra.

Se construyó a partir del membrete y las fichas de FCA (noviembre de 2026) y de la web codigoabierto.tech. Donde las dos fuentes difieren, manda el membrete en papel y la web en pantalla; las diferencias están anotadas abajo.

## Quiénes somos y cómo hablamos

FCA es una fundación sin ánimo de lucro de Barranquilla que lleva educación y acceso a la tecnología y a la inteligencia artificial a las comunidades del Atlántico y del Caribe colombiano, con prioridad para jóvenes y mujeres que nunca han tenido acceso. Su casa es la Casa Tech, en El Prado, donde funciona Costa Digital.

**La voz es cálida, directa y del Caribe.** Hablamos como la gente de la región: en primera persona del plural («formamos», «reunimos», «abrimos»), con frases cortas y verbos concretos.

| Hacemos | Evitamos |
| --- | --- |
| «Formamos talento, reunimos a la comunidad y abrimos oportunidades.» | «Somos un hub disruptivo de innovación que potencia sinergias.» |
| Cifras reales con su fuente: «4.816 participantes en 54 eventos». | Cifras redondeadas o sin fuente: «miles de personas impactadas». |
| Nombres propios y lugares: «la Casa Tech en El Prado». | Generalidades: «nuestras instalaciones». |
| Tú en la web y en redes; usted en cartas y documentos oficiales. | Mezclar tú y usted en la misma pieza. |
| Español de Colombia: punto de miles, coma decimal, fechas «13 de noviembre de 2026». | Anglicismos cuando hay palabra en español («evento», no «meetup», salvo en nombres propios). |

Los nombres propios se escriben siempre igual: **Fundación Código Abierto** (o **FCA** después de la primera mención), **Casa Tech**, **Costa Digital**, **TechCaribe Fest**, **Barranqui-IA**, **Tech Nights**.

## Fundamentos visuales

**Color.** La marca es azul sobre blanco y azul noche. `brand-blue` (#00A0F9) es el azul de las barras del logo y de la web: se usa en gráficos, barras y bloques grandes, pero no en texto pequeño, porque sobre blanco no alcanza el contraste. Para texto, enlaces, botones y foco se usa `brand-blue-strong` (#006BAD en claro, cian en oscuro). `surface-navy` (#050A30) es el azul noche de las tarjetas oscuras, la banda de contacto y las pastillas, con texto en `ink-inverse` y acentos en `cyan`. `teal` y `signal-green` son acentos pequeños: la regla de las citas y el punto de «en vivo».

**Tipografía.** Tres familias, cada una con un papel:
- **League Spartan** para titulares y cifras: pesada (700 a 800), compacta y con interlineado apretado.
- **Poppins** para todo el texto corrido, los botones y las etiquetas.
- **Space Mono** para el detalle técnico: kickers, pastillas, fechas y códigos. Es el guiño a «código».

**El motivo: las tres barras inclinadas.** Vienen del logo y son la firma de la marca. Aparecen a la izquierda de cada kicker, como franja en el pie de página y como patrón en portadas. Siempre en `brand-blue`, siempre inclinadas hacia la derecha y en grupos de tres (o cinco en franjas largas).

**La línea de circuito.** El encabezado del membrete lleva una línea fina en `brand-blue` que dobla en una esquina redondeada y termina en un punto, como una pista de circuito. Se usa una sola vez por pieza, en el encabezado o en la portada.

**Forma.** Los botones son píldoras (`radius-full`), las tarjetas tienen `radius-lg` y las fotos y secciones grandes `radius-xl`. Se prefiere un borde en `line` a una sombra; la única sombra es `shadow-card`.

**Espacio.** La unidad base es 8px (`space-2`). Las tarjetas llevan `space-6` de relleno y las secciones se separan con `space-16` en escritorio y `space-12` en móvil.

## Logo

Ver el grupo de recursos **Logos**. La versión principal lleva las tres barras en `brand-blue` y «FCA / Fundación Código Abierto» en negro; sobre azul noche se usa la versión con el nombre en blanco. Espacio libre alrededor: el alto de una barra. No se estira, no se rota y no se cambia el color de las barras.

## Iconografía

Íconos de línea en una cuadrícula de 24px, con trazo de 2px, puntas y uniones redondeadas y sin relleno, en `brand-blue-strong` (en `cyan` sobre `surface-navy`). Es el estilo que usan las fichas: personas, documento, calendario, ubicación, señal. Un ícono acompaña a un texto; nunca lo reemplaza.

## Fotografía

Fotos reales de la comunidad: auditorios llenos, equipos en la hackatón, la Casa Tech. Gente del Caribe haciendo cosas, no imágenes de banco ni ilustraciones genéricas de «tecnología». Con permiso de las personas que aparecen y con esquinas `radius-xl` en la web.

## Aplicaciones

- **Documentos y cartas:** membrete con el logo y la línea de circuito arriba, el pie con la franja de barras, el bloque «</> 0001 · Código Abierto · CA» y los datos de contacto. Kicker en Space Mono, titulares en League Spartan y texto en Poppins.
- **Fichas y presentaciones:** un kicker y un titular por página, tarjetas claras con una azul noche como máximo, cifras con `stat`.
- **Web:** fondo `surface-page`, botones píldora, secciones con un kicker («Calendario», «Comunidad», «Impacto») y su titular.

## Pendientes

- **Falta el logo en vector (SVG).** Los PNG de este sistema se recortaron del membrete; cuando exista el archivo vectorial, reemplázalos.
- **El teléfono no coincide:** la web publica el +57 300 552 3872 y el membrete y las fichas el 319 722 9143. Hay que definir uno.
- El azul `#0087D6` que usa el membrete para los kickers tiene 3,9:1 sobre blanco: sirve en papel y a tamaño grande, pero en pantalla los kickers van en `brand-blue-strong`.
