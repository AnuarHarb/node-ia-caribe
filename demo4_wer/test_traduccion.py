"""La métrica de traducción se puede comprobar a mano y lo publicable no lleva los poemas."""

from __future__ import annotations

import json
import unittest

from demo4_wer.traduccion import chrf, limpio, medir, palabras_acertadas, traducir

CORPUS = {
    "fuente": {"titulo": "Libro de prueba", "autores": ["Autora Uno"]},
    "ejemplo": {"id": "u1", "versos": 2},
    "unidades": [
        {
            "id": "u1",
            "paginas": "1-2",
            "poema_palenquero": "Uno",
            "poema_espanol": "One",
            "palenquero": ["verso alfa", "verso beta", "verso gama secreto", "verso delta secreto"],
            "espanol": ["línea alfa", "línea beta", "línea gama reservada", "línea delta reservada"],
        },
        {
            "id": "u2",
            "paginas": "3-4",
            "poema_palenquero": "Dos",
            "poema_espanol": "Two",
            "palenquero": ["otro verso oculto"],
            "espanol": ["otra línea oculta"],
        },
    ],
}


class Traduccion(unittest.TestCase):
    def test_limpia_como_el_wer_y_separa_por_puntuacion(self):
        self.assertEqual(limpio("Bantú.lingala, ¡Ubandu!"), "bantú lingala ubandu")

    def test_una_traduccion_identica_da_el_maximo_y_una_ajena_el_minimo(self):
        self.assertEqual(chrf(["suto senda"], ["Suto senda."]), 100.0)
        self.assertEqual(palabras_acertadas(["suto senda"], ["Suto senda."]), 100.0)
        self.assertEqual(chrf(["xyz"], ["suto senda"]), 0.0)
        self.assertEqual(palabras_acertadas(["xyz"], ["suto senda"]), 0.0)

    def test_palabras_acertadas_se_cuenta_a_mano(self):
        # De las 4 palabras humanas, el sistema escribió 1; las repetidas no cuentan dos veces.
        self.assertEqual(palabras_acertadas(["suto suto suto"], ["suto a sendaba kumo"]), 25.0)

    def test_sin_todas_las_salidas_no_hay_cifra_del_sistema(self):
        salidas = {"es-pal": {"u1": {"local": {"texto": "algo", "segundos": 1.0}}}}
        publico = medir(CORPUS, salidas)
        directa = publico["direcciones"][0]
        self.assertIsNone(directa["local"])
        self.assertIsNone(directa["referencia"])
        self.assertIn("chrf", directa["control"])

    def test_traduce_solo_lo_que_falta_y_mide(self):
        salidas: dict = {}
        self.assertEqual(traducir(CORPUS, salidas, "local", lambda pedido: "verso alfa\nverso beta"), 4)
        self.assertEqual(traducir(CORPUS, salidas, "local", lambda pedido: "no se llama"), 0)
        publico = medir(CORPUS, salidas)
        self.assertEqual(publico["estrofas"], 2)
        self.assertEqual(publico["poemas"], 2)
        self.assertIsNotNone(publico["direcciones"][0]["local"])

    def test_lo_publicable_solo_lleva_los_versos_del_ejemplo(self):
        salidas: dict = {}
        traducir(CORPUS, salidas, "local", lambda pedido: "salida uno\nsalida dos\nsalida tres reservada")
        texto = json.dumps(medir(CORPUS, salidas), ensure_ascii=False)
        for permitido in ("verso alfa", "verso beta", "línea alfa", "línea beta", "salida uno", "salida dos"):
            self.assertIn(permitido, texto)
        for privado in ("secreto", "reservada", "oculto", "oculta"):
            self.assertNotIn(privado, texto)


if __name__ == "__main__":
    unittest.main()
