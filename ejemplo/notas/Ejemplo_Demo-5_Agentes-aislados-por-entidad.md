# Demo 5. Agentes aislados por entidad

Nodo IA Caribe · Convocatoria 54

**Criterio cumplido.** El intento de lectura cruzada quedó bloqueado, pasaron 11 de 11 pruebas y el registro de auditoría conserva su cadena íntegra.

| Campo | Contenido |
| --- | --- |
| Pregunta que responde | **¿Cada entidad puede tener un agente que no vea los datos de las otras?** |
| Respuesta medida | Sí: pasaron 11 de 11 pruebas; acceso cruzado bloqueado: sí; auditoría íntegra: sí. |
| Qué sostiene en el proyecto | El arnés y los agentes. |
| Fecha de la prueba | 9 de noviembre de 2026, 23:33 |
| Responsable | Anuar Harb |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Video | <https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing> |
| Código y datos | <https://github.com/AnuarHarb/node-ia-caribe> |

## 1. Objetivo

Mostrar que la arquitectura de agentes aislados por entidad ya existe y está probada: dos agentes de dos entidades trabajan en el mismo nodo y ninguno puede leer ni escribir los archivos del otro.

**Criterio de éxito:**acceso cruzado bloqueado y las 11 pruebas pasando.

## 2. Montaje

| Componente | Detalle |
| --- | --- |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Prototipo | Un nodo que entrega a cada entidad un agente con su propia caja de archivos. Toda lectura, escritura y listado pasa por el agente; si la ruta sale de la caja, la operación se niega y se anota. |
| Entidades | Dos, ficticias: alcaldia-santa-marta y gobernacion-atlantico. |
| Datos | Ficticios: un trámite inventado y una lista inventada de cupos escolares. |
| Registro de auditoría | Cada operación queda en una línea con su resultado y un hash que encadena la línea anterior; si alguien cambia o borra una línea, la cadena deja de cuadrar. |
| Software | Python 3.12.2, pruebas con unittest de la biblioteca estándar. No usa modelo de lenguaje. |
| Internet | No usa red: el prototipo solo lee y escribe archivos en el equipo. |

## 3. Procedimiento

1. Se crea un entorno nuevo con las dos cajas y sus archivos ficticios.
2. Cada agente escribe una nota de trabajo en su propia caja.
3. El agente de la alcaldía intenta leer un archivo de la gobernación usando una ruta que sale de su caja.
4. Se muestra el registro de auditoría y se verifica su cadena de hashes.
5. Se corren las 11 pruebas automatizadas, cada una en un directorio temporal propio: lectura y escritura propias, trabajo simultáneo, lectura, escritura y listado cruzados, rutas con «..», enlaces simbólicos y auditoría.

## 4. Resultados

**Acceso cruzado:**el agente de la alcaldía pidió el archivo ../gobernacion-atlantico/educacion/cupos-mahates.txt de la otra entidad. El nodo lo negó (motivo: fuera_del_aislamiento) y dejó el intento en el registro.

**Tabla 1. Registro de auditoría de la corrida, en orden**

| # | Entidad | Acción | Ruta pedida | Resultado | Motivo |
| --- | --- | --- | --- | --- | --- |
| 1 | alcaldia-santa-marta | escribir | pqrs/turno-1042.txt | permitido | dentro_de_la_entidad |
| 2 | gobernacion-atlantico | escribir | educacion/cupos-mahates.txt | permitido | dentro_de_la_entidad |
| 3 | alcaldia-santa-marta | escribir | pqrs/nota-de-trabajo.txt | permitido | dentro_de_la_entidad |
| 4 | gobernacion-atlantico | escribir | educacion/nota-de-trabajo.txt | permitido | dentro_de_la_entidad |
| 5 | alcaldia-santa-marta | leer | ../gobernacion-atlantico/educacion/cupos-mahates.txt | denegado | fuera_del_aislamiento |

Cadena de hashes del registro: **íntegra.** Se verifica recalculando el hash de cada línea a partir de la anterior.

**Tabla 2. Las 11 pruebas automatizadas: 11 de 11 pasaron**

| Prueba | Esperado | Obtenido |
| --- | --- | --- |
| test_01_lectura_propia_entidad_a | El agente de la alcaldía lee un archivo de su propia caja. | pasó |
| test_02_lectura_propia_entidad_b | El agente de la gobernación lee un archivo de su propia caja. | pasó |
| test_03_trabajo_simultaneo | Dos agentes de dos entidades escriben y leen a la vez, cada uno en su caja. | pasó |
| test_04_lectura_cruzada_bloqueada | Un agente no obtiene el archivo de la otra entidad. | pasó |
| test_05_escritura_cruzada_bloqueada | Un agente no escribe en la caja de la otra entidad. | pasó |
| test_06_listado_cruzado_bloqueado | El listado de una entidad no muestra los archivos de la otra, ni a través de un enlace. | pasó |
| test_07_traversal_de_ruta_bloqueado | Una ruta absoluta y una ruta con .. no salen de la caja. | pasó |
| test_08_escape_por_symlink_bloqueado | Un enlace simbólico hacia el archivo de otra entidad no se puede leer. | pasó |
| test_09_auditoria_registra_bloqueo | El intento bloqueado queda en el registro, sin el contenido del archivo ajeno. | pasó |
| test_10_auditoria_registra_acceso_permitido | Una lectura dentro de la propia caja queda registrada como permitida. | pasó |
| test_11_cadena_de_auditoria_integra | El registro íntegro verifica, y una alteración se detecta. | pasó |

## 5. Limitaciones

- **Entorno simulado.**Un solo computador, datos ficticios y entidades inventadas. No hay red ni entidades reales.
- **El aislamiento está en las herramientas del agente.**Quien ya controla el proceso de Python puede saltárselo. No se usan usuarios distintos del sistema operativo ni contenedores.
- **El registro es un archivo en el mismo equipo.**La cadena de hashes detecta si alguien cambia o quita una línea, pero no impide que quien tenga acceso al disco borre el archivo o lo reescriba entero.
- **No es el nodo del proyecto.**Es la prueba de concepto de la arquitectura (TRL 3). En las fases siguientes el mismo aislamiento se debe sostener con entidades reales y con un registro que no dependa de un solo proceso.

## 6. Enlaces

- **Video:**<https://drive.google.com/drive/folders/1JtBeA1K9i7CE9_z_gD65JP6rT34B4t58?usp=sharing>
- **Repositorio:**<https://github.com/AnuarHarb/node-ia-caribe>
- **Código:**`demo5_agentes/nodo.py`, `demo5_agentes/test_aislamiento.py`, `demo5_agentes/en_vivo.py`.
- **Datos medidos:**`resultados/demo5/informe.json`, `resultados/demo5/pruebas.csv`.
- **Para repetirla:**`python -m demo5_agentes.en_vivo`.
