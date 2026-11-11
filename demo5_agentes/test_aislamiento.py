"""Once pruebas del aislamiento entre entidades. Datos ficticios."""

from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path

from demo5_agentes.entidades import ALCALDIA, GOBERNACION, RUTA_SECRETO_GOBERNACION
from demo5_agentes.nodo import AccesoDenegado, Nodo

SECRETO = "SECRETO-BOLIVAR-8841"


def escenario():
    temporal = tempfile.TemporaryDirectory(prefix="nodo-")
    nodo = Nodo(temporal.name)
    alcaldia = nodo.abrir(ALCALDIA)
    gobernacion = nodo.abrir(GOBERNACION)
    alcaldia.escribir("pqrs/turno-1042.txt", "Radicado ficticio 1042. Certificado de residencia.")
    gobernacion.escribir("educacion/cupos-mahates.txt", SECRETO)
    return temporal, nodo, alcaldia, gobernacion


class Aislamiento(unittest.TestCase):
    def test_01_lectura_propia_entidad_a(self):
        """El agente de la alcaldía lee un archivo de su propia caja."""
        temporal, _nodo, alcaldia, _gobernacion = escenario()
        with temporal:
            texto = alcaldia.leer("pqrs/turno-1042.txt")
            self.assertIn("1042", texto)

    def test_02_lectura_propia_entidad_b(self):
        """El agente de la gobernación lee un archivo de su propia caja."""
        temporal, _nodo, _alcaldia, gobernacion = escenario()
        with temporal:
            texto = gobernacion.leer("educacion/cupos-mahates.txt")
            self.assertEqual(texto, SECRETO)

    def test_03_trabajo_simultaneo(self):
        """Dos agentes de dos entidades escriben y leen a la vez, cada uno en su caja."""
        temporal, nodo, alcaldia, gobernacion = escenario()
        with temporal:
            barrera = threading.Barrier(2)
            errores: list[BaseException] = []

            def trabajar(agente, nombre: str) -> None:
                try:
                    barrera.wait(timeout=5)
                    agente.escribir(nombre, f"trabajo de {agente.entidad}")
                    leido = agente.leer(nombre)
                    if leido != f"trabajo de {agente.entidad}":
                        raise AssertionError("leyó un contenido que no era el suyo")
                except BaseException as exc:  # noqa: BLE001 - se reporta al hilo principal
                    errores.append(exc)

            hilos = [
                threading.Thread(target=trabajar, args=(alcaldia, "en-curso.txt")),
                threading.Thread(target=trabajar, args=(gobernacion, "en-curso.txt")),
            ]
            for hilo in hilos:
                hilo.start()
            for hilo in hilos:
                hilo.join(timeout=5)
            self.assertFalse(any(hilo.is_alive() for hilo in hilos))
            self.assertEqual(errores, [])
            self.assertTrue(nodo.auditoria.integra())

    def test_04_lectura_cruzada_bloqueada(self):
        """Un agente no obtiene el archivo de la otra entidad."""
        temporal, _nodo, alcaldia, gobernacion = escenario()
        with temporal:
            with self.assertRaises(AccesoDenegado) as ctx:
                alcaldia.leer(RUTA_SECRETO_GOBERNACION)
            self.assertNotIn(SECRETO, str(ctx.exception))
            self.assertEqual(gobernacion.leer("educacion/cupos-mahates.txt"), SECRETO)

    def test_05_escritura_cruzada_bloqueada(self):
        """Un agente no escribe en la caja de la otra entidad."""
        temporal, _nodo, alcaldia, gobernacion = escenario()
        with temporal:
            with self.assertRaises(AccesoDenegado):
                alcaldia.escribir(f"../{GOBERNACION}/educacion/robado.txt", "intruso")
            self.assertNotIn("robado.txt", gobernacion.listar())
            self.assertEqual(gobernacion.leer("educacion/cupos-mahates.txt"), SECRETO)

    def test_06_listado_cruzado_bloqueado(self):
        """El listado de una entidad no muestra los archivos de la otra, ni a través de un enlace."""
        temporal, _nodo, alcaldia, gobernacion = escenario()
        with temporal:
            puerta = Path(alcaldia.caja) / "puerta"
            puerta.symlink_to(gobernacion.caja)
            nombres = alcaldia.listar()
            self.assertIn("pqrs/turno-1042.txt", nombres)
            self.assertFalse(any("cupos" in nombre or "puerta" in nombre for nombre in nombres))
            self.assertNotIn(SECRETO, "\n".join(nombres))

    def test_07_traversal_de_ruta_bloqueado(self):
        """Una ruta absoluta y una ruta con .. no salen de la caja."""
        temporal, _nodo, alcaldia, _gobernacion = escenario()
        with temporal:
            with self.assertRaises(AccesoDenegado):
                alcaldia.leer("/etc/passwd")
            with self.assertRaises(AccesoDenegado):
                alcaldia.leer("../../../../../../etc/passwd")

    def test_08_escape_por_symlink_bloqueado(self):
        """Un enlace simbólico hacia el archivo de otra entidad no se puede leer."""
        temporal, _nodo, alcaldia, gobernacion = escenario()
        with temporal:
            destino = Path(gobernacion.caja) / "educacion" / "cupos-mahates.txt"
            enlace = Path(alcaldia.caja) / "atajo.txt"
            enlace.symlink_to(destino)
            with self.assertRaises(AccesoDenegado) as ctx:
                alcaldia.leer("atajo.txt")
            self.assertNotIn(SECRETO, str(ctx.exception))

    def test_09_auditoria_registra_bloqueo(self):
        """El intento bloqueado queda en el registro, sin el contenido del archivo ajeno."""
        temporal, nodo, alcaldia, _gobernacion = escenario()
        with temporal:
            with self.assertRaises(AccesoDenegado):
                alcaldia.leer(RUTA_SECRETO_GOBERNACION)
            bloqueos = [
                evento
                for evento in nodo.auditoria.eventos()
                if evento["resultado"] == "denegado" and evento["accion"] == "leer"
            ]
            self.assertGreaterEqual(len(bloqueos), 1)
            self.assertEqual(bloqueos[-1]["motivo"], "fuera_del_aislamiento")
            self.assertNotIn(SECRETO, nodo.auditoria.path.read_text(encoding="utf-8"))

    def test_10_auditoria_registra_acceso_permitido(self):
        """Una lectura dentro de la propia caja queda registrada como permitida."""
        temporal, nodo, alcaldia, _gobernacion = escenario()
        with temporal:
            alcaldia.leer("pqrs/turno-1042.txt")
            permitidos = [
                evento
                for evento in nodo.auditoria.eventos()
                if evento["entidad"] == ALCALDIA
                and evento["accion"] == "leer"
                and evento["resultado"] == "permitido"
            ]
            self.assertEqual(len(permitidos), 1)
            self.assertEqual(permitidos[0]["ruta"], "pqrs/turno-1042.txt")

    def test_11_cadena_de_auditoria_integra(self):
        """El registro íntegro verifica, y una alteración se detecta."""
        with tempfile.TemporaryDirectory(prefix="nodo-") as carpeta:
            nodo = Nodo(carpeta)
            self.assertTrue(nodo.auditoria.integra())
            nodo.abrir(ALCALDIA).escribir("nota.txt", "dato ficticio")
            self.assertTrue(nodo.auditoria.integra())
            original = nodo.auditoria.path.read_text(encoding="utf-8")
            alterado = original.replace("permitido", "denegado", 1)
            self.assertNotEqual(original, alterado)
            nodo.auditoria.path.write_text(alterado, encoding="utf-8")
            self.assertFalse(nodo.auditoria.integra())


if __name__ == "__main__":
    unittest.main()
