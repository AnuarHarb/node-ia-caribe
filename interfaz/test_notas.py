"""Las cinco notas técnicas se pueden generar y cumplen la plantilla de la especificación.

Uso:  python -m unittest interfaz.test_notas
"""

from __future__ import annotations

import unittest

from interfaz.catalogo import DEMOS
from interfaz.documento import a_html, a_markdown, a_pdf, caracteres_sin_glifo
from interfaz.informe_export import PAGINAS_MAXIMAS, PAGINAS_MINIMAS
from interfaz.informes import cargar
from interfaz.notas import documento

SECCIONES = ["1. Objetivo", "2. Montaje", "3. Procedimiento", "4. Resultados", "5. Limitaciones", "6. Enlaces"]


class NotasTecnicas(unittest.TestCase):
    def test_cada_nota_trae_las_seis_secciones_de_la_plantilla(self):
        for demo_id in DEMOS:
            with self.subTest(demo=demo_id):
                informe = cargar(demo_id)
                if informe is None and demo_id != 2:
                    self.skipTest(f"el demo {demo_id} no se ha corrido en este equipo")
                doc = documento(demo_id, informe)
                self.assertEqual([seccion["titulo"] for seccion in doc["secciones"]], SECCIONES)
                campos = [campo for campo, _ in doc["ficha"]]
                for esperado in ("Responsable", "Equipo", "Video", "Código y datos"):
                    self.assertIn(esperado, campos)

    def test_cada_nota_cabe_en_dos_o_tres_paginas(self):
        for demo_id in DEMOS:
            with self.subTest(demo=demo_id):
                informe = cargar(demo_id)
                if informe is None and demo_id != 2:
                    self.skipTest(f"el demo {demo_id} no se ha corrido en este equipo")
                _, paginas = a_pdf(documento(demo_id, informe))
                self.assertGreaterEqual(paginas, PAGINAS_MINIMAS)
                self.assertLessEqual(paginas, PAGINAS_MAXIMAS)

    def test_el_pdf_puede_dibujar_todo_el_texto(self):
        for demo_id in DEMOS:
            with self.subTest(demo=demo_id):
                self.assertEqual(caracteres_sin_glifo(documento(demo_id, cargar(demo_id))), [])

    def test_las_tres_salidas_dicen_lo_mismo(self):
        for demo_id in DEMOS:
            with self.subTest(demo=demo_id):
                doc = documento(demo_id, cargar(demo_id))
                html = a_html(doc)
                markdown = a_markdown(doc)
                self.assertIn('<article class="nota"', html)
                for seccion in doc["secciones"]:
                    self.assertIn(seccion["titulo"], html)
                    self.assertIn(seccion["titulo"], markdown)

    def test_sin_informe_la_nota_queda_pendiente_y_no_inventa_resultados(self):
        for demo_id in DEMOS:
            with self.subTest(demo=demo_id):
                doc = documento(demo_id, None)
                self.assertEqual(doc["estado"]["clase"], "pendiente")
                datos, paginas = a_pdf(doc)
                self.assertTrue(datos.startswith(b"%PDF"))
                self.assertGreaterEqual(paginas, 1)

    def test_un_informe_viejo_o_incompleto_no_rompe_la_nota(self):
        for demo_id in DEMOS:
            with self.subTest(demo=demo_id):
                doc = documento(demo_id, {"demo": demo_id, "fecha": "2026-11-09T23:33:00-05:00"})
                self.assertTrue(a_pdf(doc)[0].startswith(b"%PDF"))
                self.assertNotEqual(doc["estado"]["clase"], "ok")


if __name__ == "__main__":
    unittest.main()
