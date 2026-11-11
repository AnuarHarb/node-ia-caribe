# Nota técnica · Agentes aislados por entidad

Evidencia del punto de partida (TRL 3). Proyecto Nodo IA Caribe.

| Campo | Contenido |
| --- | --- |
| Fecha de la prueba | 2026-11-09T23:33:27-05:00 |
| Responsable | Anuar Harb |
| Enlace al video | `entregables/VIDEO-LABORATORIO.md` y capturas `.webm` en `resultados/demo5/historial/` |
| Enlace al repositorio o a los datos | Repositorio local · carpetas `demo5_agentes` y `resultados/demo5` |

## 1. Objetivo

Que la arquitectura de agentes aislados por entidad ya existe y está probada, en entorno simulado y con datos ficticios.

## 2. Montaje

| Componente | Detalle |
| --- | --- |
| Equipo | Apple M2 Pro, 16 GB, macOS-14.6.1-arm64-arm-64bit, Python 3.12.2 |
| Modelos y versiones | No usa modelo de lenguaje. El prototipo es la mediación de archivos y el registro de auditoría en `demo5_agentes/nodo.py`. |
| Software | Python 3.12.2, pruebas `unittest` de la biblioteca estándar. |
| Conexión a internet durante la prueba | No. |

Dos entidades ficticias: `alcaldia-santa-marta` y `gobernacion-atlantico`. Cada una tiene una caja de archivos. Toda lectura, escritura y listado pasa por el agente. Si la ruta resuelta sale de la caja, la operación se niega y se anota.

## 3. Procedimiento

1. Se crea un entorno nuevo con las dos cajas y archivos ficticios de un trámite y de unos cupos escolares.
2. Los dos agentes escriben, cada uno en su caja, una nota de trabajo.
3. El agente de la alcaldía intenta leer `../gobernacion-atlantico/educacion/cupos-mahates.txt`.
4. Se muestra el registro de auditoría y se verifica la cadena de hashes.
5. Se corren las 11 pruebas automatizadas, cada una en un directorio temporal propio.
6. Se guardan `resultados/demo5/pruebas.csv`, `informe.json` e `informe.html`.

## 4. Resultados

Criterio cumplido: Sí. Acceso cruzado bloqueado: True (fuera_del_aislamiento). Auditoría íntegra: True. Pruebas: 11 de 11.

| Prueba | Resultado esperado | Resultado obtenido |
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

La prueba demuestra el mecanismo en un solo computador y con datos ficticios. La mediación está en las herramientas del agente: quien ya controla el proceso de Python puede saltársela. No usa usuarios distintos del sistema operativo, ni red, ni entidades reales. No es el nodo del borde ni el enrutador soberano. Sirve como prueba de concepto de la arquitectura (TRL 3). El proyecto, en las fases siguientes, tiene que sostener el mismo aislamiento con entidades reales y con un registro que no dependa de un solo proceso.

## Guion del video

Se ven las dos cajas, el intento de lectura cruzada bloqueado, la tabla de auditoría y las 11 pruebas en pasado. Comando: `python -m demo5_agentes.en_vivo`.
