"""Pruebas del método: kappa conocido, cegado reversible y forma de las 40 tareas."""

from __future__ import annotations

import unittest

from demo3_comparacion.metricas import calcular, cohen_kappa, kappa_cuadratico
from demo3_comparacion.paquete import construir_paquete
from demo3_comparacion.tareas import TAREAS


class Metodo(unittest.TestCase):
    def test_hay_40_tareas_balanceadas(self):
        self.assertEqual(len(TAREAS), 40)
        self.assertEqual(len({tarea["id"] for tarea in TAREAS}), 40)
        conteo: dict[str, int] = {}
        for tarea in TAREAS:
            self.assertTrue(tarea["entrada"].strip())
            self.assertTrue(tarea["instruccion"].strip())
            conteo[tarea["tipo"]] = conteo.get(tarea["tipo"], 0) + 1
        self.assertEqual(
            conteo,
            {
                "resumir_peticion": 8,
                "redactar_respuesta": 8,
                "clasificar_solicitud": 8,
                "extraer_datos": 8,
                "consulta_normativa": 8,
            },
        )

    def test_kappa_de_un_caso_calculado_a_mano(self):
        # Acuerdo observado 3/4. Azar = 0.5*0.25 + 0.5*0.75 = 0.5. Kappa = 0.5.
        self.assertAlmostEqual(cohen_kappa([1, 1, 2, 2], [1, 2, 2, 2]), 0.5)
        self.assertAlmostEqual(kappa_cuadratico([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]), 1.0)

    def test_el_paquete_ciego_no_revela_el_modelo(self):
        respuestas = {
            tarea["id"]: {"local": f"local-{tarea['id']}", "referencia": f"referencia-{tarea['id']}"}
            for tarea in TAREAS
        }
        ciego, clave = construir_paquete(respuestas, semilla=11, modelo_local="qwen2.5:3b", modelo_referencia="gpt-4o-mini")
        texto = str(ciego)
        self.assertNotIn("qwen", texto.lower())
        self.assertNotIn("gpt", texto.lower())
        self.assertNotIn("etiqueta_esperada", texto)
        letras_a = [clave["asignacion"][tarea["id"]]["A"] for tarea in TAREAS]
        self.assertIn("local", letras_a)
        self.assertIn("referencia", letras_a)
        primera = ciego["tareas"][0]
        mapa = clave["asignacion"][primera["id"]]
        self.assertEqual(primera["respuesta_a"], respuestas[primera["id"]][mapa["A"]])

    def test_calidad_comparable_y_kappa_con_dos_calificadores(self):
        respuestas = {
            tarea["id"]: {"local": "respuesta local", "referencia": "respuesta externa"}
            for tarea in TAREAS
        }
        _ciego, clave = construir_paquete(
            respuestas, semilla=3, modelo_local="modelo-local", modelo_referencia="modelo-externo"
        )
        puntajes_a = []
        puntajes_b = []
        for tarea_id, mapa in clave["asignacion"].items():
            for letra, camino in mapa.items():
                nota = 4 if camino == "local" else 5
                base = {
                    "id": tarea_id,
                    "respuesta": letra,
                    "exactitud": nota,
                    "completitud": nota,
                    "tono": nota,
                    "utilidad": nota,
                }
                puntajes_a.append(dict(base))
                puntajes_b.append(dict(base))
        resultado = calcular(
            clave,
            [
                {"calificador": "Uno", "paquete": clave["paquete"], "puntajes": puntajes_a},
                {"calificador": "Dos", "paquete": clave["paquete"], "puntajes": puntajes_b},
            ],
        )
        self.assertEqual(resultado["estado"], "calculado")
        self.assertEqual(resultado["tareas_calificadas"], 40)
        self.assertEqual(resultado["porcentaje_comparables"], 100.0)
        self.assertGreater(resultado["kappa"]["exactitud"]["cohen"], 0.99)


if __name__ == "__main__":
    unittest.main()
