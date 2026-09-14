"""Testes do modelo de antecipação (puro: sem Streamlit, sem arquivo, sem GitHub)."""

import unittest

import antecipacao_modelo as ant
import itens_modelo as modelo
from test_itens_modelo import MESES, QUITADOS, bancorbras, plano_legado


def geladeira():
    return {
        "id": "geladeira", "nome": "Geladeira", "valor": 152.48, "tipo": "debito",
        "inicio": "jul/25", "fim": "jun/27", "antecipacoes": [],
        "contrato": {"inicio_original": "jul/25", "fim_original": "jun/27",
                     "total_parcelas": 24, "valor_parcela": 152.48},
    }


def lava_roupas():
    return {"id": "custom_3", "nome": "Lava roupas mãe", "valor": 100.0, "tipo": "credito",
            "inicio": "jul/26", "fim": "abr/27"}


def todos():
    return [plano_legado(), geladeira(), bancorbras(), lava_roupas()]


class TestDisponiveis(unittest.TestCase):
    def test_so_parcelas_de_itens_que_abatem(self):
        self.assertTrue(ant.pode_antecipar(geladeira()))
        self.assertFalse(ant.pode_antecipar(plano_legado()))  # contínuo e crédito
        self.assertFalse(ant.pode_antecipar(lava_roupas()))   # crédito

    def test_geladeira_tem_as_parcelas_nao_quitadas(self):
        disp = ant.parcelas_disponiveis(geladeira(), MESES, QUITADOS)
        self.assertEqual(disp[0], "set/26")
        self.assertEqual(disp[-1], "jun/27")
        self.assertEqual(len(disp), 10)

    def test_bancorbras_exclui_quitadas_e_ja_antecipadas(self):
        self.assertEqual(ant.parcelas_disponiveis(bancorbras(), MESES, QUITADOS),
                         ["set/26", "out/26", "nov/26", "dez/26"])

    def test_numero_da_parcela(self):
        self.assertEqual(ant.numero_parcela(geladeira(), "set/26", MESES), (15, 24))
        self.assertEqual(ant.numero_parcela(geladeira(), "jan/25", MESES), (None, 24))


class TestValidacao(unittest.TestCase):
    def test_destino_nao_pode_ser_uma_das_parcelas(self):
        self.assertTrue(ant.validar(geladeira(), ["set/26", "out/26"], "out/26", MESES, QUITADOS))

    def test_parcela_quitada_nao_pode_ser_antecipada(self):
        self.assertTrue(ant.validar(geladeira(), ["ago/26"], "set/26", MESES, QUITADOS))

    def test_sem_parcelas(self):
        self.assertTrue(ant.validar(geladeira(), [], "set/26", MESES, QUITADOS))

    def test_valido(self):
        self.assertEqual(ant.validar(geladeira(), ["out/26", "nov/26"], "set/26", MESES, QUITADOS), [])

    def test_adiamento_e_identificado(self):
        self.assertEqual(ant.adiadas(["set/26", "jan/27"], "dez/26", MESES), ["set/26"])
        self.assertEqual(ant.adiadas(["out/26"], "set/26", MESES), [])


class TestAntecipar(unittest.TestCase):
    def test_cria_um_registro_por_parcela_no_formato_do_backend(self):
        novo = ant.antecipar(geladeira(), ["nov/26", "out/26"], "set/26", MESES, motivo="  13º  ")
        regs = novo["antecipacoes"]
        self.assertEqual([r["origem"] for r in regs], ["out/26", "nov/26"])
        for r in regs:
            self.assertEqual(r["destino"], "set/26")
            self.assertEqual(r["status"], "confirmada")
            self.assertEqual(r["valor_antecipado"], 152.48)
            self.assertEqual(r["mes_original_parcela"], r["origem"])
            self.assertEqual(r["motivo"], "13º")
            self.assertEqual(r["id_parcela"], f"geladeira_{r['origem']}")
        self.assertEqual(len({r["id_antecipacao"] for r in regs}), 2)

    def test_valor_sai_da_origem_e_entra_no_destino(self):
        novo = ant.antecipar(geladeira(), ["out/26", "nov/26"], "set/26", MESES)
        s = modelo.serie_no_acerto(novo, MESES)
        self.assertAlmostEqual(s[MESES.index("set/26")], 152.48 * 3)
        self.assertAlmostEqual(s[MESES.index("out/26")], 0.0)
        self.assertAlmostEqual(s[MESES.index("nov/26")], 0.0)
        self.assertAlmostEqual(s[MESES.index("dez/26")], 152.48)

    def test_nao_altera_o_original_e_tira_das_disponiveis(self):
        item = geladeira()
        novo = ant.antecipar(item, ["out/26"], "set/26", MESES)
        self.assertEqual(item, geladeira())
        self.assertNotIn("out/26", ant.parcelas_disponiveis(novo, MESES, QUITADOS))

    def test_efeito_no_acerto(self):
        itens = todos()
        antes = itens[1]
        depois = ant.antecipar(antes, ["out/26", "nov/26"], "set/26", MESES)
        linhas = {m: (a, d) for m, a, d in ant.efeito(itens, antes, depois, MESES)}
        self.assertEqual(set(linhas), {"set/26", "out/26", "nov/26"})
        self.assertAlmostEqual(linhas["set/26"][0], 1067.88)
        self.assertAlmostEqual(linhas["set/26"][1], 1067.88 - 304.96)
        self.assertAlmostEqual(linhas["out/26"][1], 1067.88 + 152.48)

    def test_destino_quitado_afeta_mes_quitado(self):
        antes = geladeira()
        depois = ant.antecipar(antes, ["out/26"], "ago/26", MESES)
        self.assertEqual(modelo.meses_quitados_afetados(antes, depois, MESES, QUITADOS), ["ago/26"])

    def test_restaura_fim_do_contrato(self):
        item = geladeira()
        item["fim"] = "dez/26"
        self.assertEqual(ant.antecipar(item, ["out/26"], "set/26", MESES)["fim"], "jun/27")


class TestCancelar(unittest.TestCase):
    def test_cancelar_devolve_o_valor_a_origem(self):
        antecipado = ant.antecipar(geladeira(), ["out/26"], "set/26", MESES)
        ident = antecipado["antecipacoes"][0]["id_antecipacao"]
        cancelado = ant.cancelar(antecipado, ident)
        reg = cancelado["antecipacoes"][0]
        self.assertEqual(reg["status"], "cancelada")
        self.assertIn("cancelado_em", reg)
        self.assertEqual(modelo.serie_no_acerto(cancelado, MESES), modelo.serie_no_acerto(geladeira(), MESES))
        self.assertIn("out/26", ant.parcelas_disponiveis(cancelado, MESES, QUITADOS))

    def test_cancelar_duas_vezes_ou_id_desconhecido_falha(self):
        antecipado = ant.antecipar(geladeira(), ["out/26"], "set/26", MESES)
        ident = antecipado["antecipacoes"][0]["id_antecipacao"]
        cancelado = ant.cancelar(antecipado, ident)
        with self.assertRaises(ValueError):
            ant.cancelar(cancelado, ident)
        with self.assertRaises(ValueError):
            ant.cancelar(antecipado, "nao-existe")

    def test_cancelar_antecipacao_real_do_bancorbras_afeta_meses_quitados(self):
        item = bancorbras()
        item["antecipacoes"][0]["id_antecipacao"] = "a1"  # fev/26 -> nov/25
        cancelado = ant.cancelar(item, "a1")
        self.assertEqual(modelo.meses_quitados_afetados(item, cancelado, MESES, QUITADOS), ["nov/25", "fev/26"])


if __name__ == "__main__":
    unittest.main()
