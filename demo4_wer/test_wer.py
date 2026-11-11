"""Comprueba la normalización y un WER calculable a mano."""

from __future__ import annotations

import unittest

from demo4_wer.wer import wer_corpus
from medicion import coincide, normalizar


class ErrorDeReconocimiento(unittest.TestCase):
    def test_normaliza_como_pide_la_especificacion(self):
        self.assertEqual(normalizar("¿A qué horas, atienden?"), "a qué horas atienden")
        self.assertTrue(coincide("El certificado.", "el certificado"))
        self.assertFalse(coincide("certificado", "residencia"))

    def test_wer_de_una_sustitucion(self):
        # 1 sustitución en 4 palabras.
        resultado = wer_corpus(
            ["el certificado de residencia"],
            ["el certificado de recidencia"],
        )
        self.assertEqual(resultado["frases"], 1)
        self.assertAlmostEqual(resultado["wer"], 0.25)
        self.assertEqual(resultado["wer_porcentaje"], 25.0)
        self.assertEqual(resultado["sustituciones"], 1)


if __name__ == "__main__":
    unittest.main()
