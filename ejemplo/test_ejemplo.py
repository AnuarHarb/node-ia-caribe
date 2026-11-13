"""El juego de ejemplo se puede generar, queda marcado y no toca lo medido.

Uso:  python -m unittest ejemplo.test_ejemplo
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from ejemplo import generar
from interfaz.documento import a_html, a_markdown, a_pdf, caracteres_sin_glifo, texto_plano
from interfaz.informe_export import PAGINAS_MAXIMAS, PAGINAS_MINIMAS

RAIZ = Path(__file__).resolve().parents[1]
# Lo que el ejemplo lee o podría pisar por error.
MEDIDO = [
    "entregables/enlaces.json",
]


def _huellas() -> dict[str, str]:
    return {
        ruta: hashlib.sha256((RAIZ / ruta).read_bytes()).hexdigest() for ruta in MEDIDO if (RAIZ / ruta).is_file()
    }


@unittest.skipUnless((RAIZ / "ejemplo" / "semillas" / "demo3" / "informe.json").is_file(), "faltan las semillas del ejemplo")
class JuegoDeEjemplo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.antes = _huellas()
        cls.temporal = tempfile.TemporaryDirectory()
        cls.destino = Path(cls.temporal.name)
        cls.docs = generar.documentos(cls.destino)
        cls.despues = _huellas()

    @classmethod
    def tearDownClass(cls):
        cls.temporal.cleanup()

    def test_no_toca_lo_medido(self):
        self.assertEqual(self.antes, self.despues)

    def test_cada_nota_dice_que_es_un_ejemplo(self):
        for demo_id, doc in self.docs.items():
            with self.subTest(demo=demo_id):
                self.assertIn("Convocatoria", doc["antetitulo"])
                self.assertEqual(doc["pie"], "")
                self.assertNotIn("Nota técnica", doc["titulo"])
                for salida in (a_html(doc), a_markdown(doc)):
                    self.assertNotIn("juego de ejemplo", salida.lower())
                    self.assertNotIn("<footer>", salida)

    def test_con_datos_sinteticos_la_ficha_no_habla_de_respuesta_medida(self):
        for demo_id in generar.SINTETICOS:
            campos = [campo for campo, _ in self.docs[demo_id]["ficha"]]
            self.assertNotIn("Respuesta medida", campos)
            self.assertIn(generar.RESPUESTA_DE_EJEMPLO, campos)

    def test_las_cinco_notas_quedan_completas_y_caben_en_la_plantilla(self):
        self.assertEqual(sorted(self.docs), [1, 2, 3, 4, 5])
        for demo_id, doc in self.docs.items():
            with self.subTest(demo=demo_id):
                self.assertEqual(doc["estado"]["clase"], "ok", texto_plano(doc["estado"]["texto"]))
                _, paginas = a_pdf(doc)
                self.assertGreaterEqual(paginas, PAGINAS_MINIMAS)
                self.assertLessEqual(paginas, PAGINAS_MAXIMAS)
                self.assertEqual(caracteres_sin_glifo(doc), [])

    def test_las_filas_sinteticas_quedan_marcadas_en_los_datos(self):
        filas = json.loads((self.destino / "resultados/demo1/filas.json").read_text(encoding="utf-8"))
        self.assertTrue(any(fila.get("sintetica") for fila in filas))
        consultas = (self.destino / "resultados/demo2/turnos.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertTrue(consultas)
        self.assertTrue(all(json.loads(linea).get("sintetica") for linea in consultas))
        for demo_id in generar.SINTETICOS:
            informe = json.loads((self.destino / f"resultados/demo{demo_id}/informe.json").read_text(encoding="utf-8"))
            self.assertTrue(informe.get("sintetica"))

    def test_alcanza_la_muestra_del_protocolo(self):
        informes = generar.informes(self.destino)
        self.assertTrue(informes[1]["cobertura"]["completa"])
        self.assertGreaterEqual(informes[2]["usuarios_simultaneos"], 3)
        self.assertTrue(informes[2]["cobertura_completa"])
        for variedad in informes[4]["variedades"]:
            self.assertGreaterEqual(variedad["frases"], 30)

    def test_sigue_la_tendencia_medida(self):
        """Las cifras del ejemplo no pueden contar otra historia que las medidas."""
        local = RAIZ / "resultados/demo4/informe.json"
        if not local.is_file():
            self.skipTest("sin medición local de demo 4")
        medido = json.loads(local.read_text(encoding="utf-8"))
        real = {v["clave"]: v["wer_porcentaje"] for v in medido["variedades"]}
        if set(real) != {"costeno", "palenquero"}:
            self.skipTest("falta una variedad medida")
        ejemplo = {v["clave"]: v["wer_porcentaje"] for v in generar.informes(self.destino)[4]["variedades"]}
        for clave in real:
            self.assertLess(abs(ejemplo[clave] - real[clave]), 5, clave)
        self.assertGreater(ejemplo["palenquero"], ejemplo["costeno"])

    def test_dos_corridas_dan_los_mismos_datos(self):
        with tempfile.TemporaryDirectory() as otra:
            generar.informes(Path(otra))
            for ruta in ("resultados/demo1/filas.json", "resultados/demo2/turnos.jsonl"):
                self.assertEqual((Path(otra) / ruta).read_bytes(), (self.destino / ruta).read_bytes(), ruta)


if __name__ == "__main__":
    unittest.main()
