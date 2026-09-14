"""Testes do modelo de itens (puro: sem Streamlit, sem arquivo, sem GitHub)."""

import unittest

import itens_modelo as m

NOMES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
MESES = [f"{n}/{str(a)[2:]}" for a in range(2025, 2029) for n in NOMES]
QUITADOS = MESES[:MESES.index("ago/26") + 1]


def plano_legado():
    """Como o Plano de Saúde está hoje no JSON: sem 'continuo', total_parcelas 0."""
    return {
        "id": "planoSaude", "nome": "Plano de Saúde", "valor": 1518.93, "tipo": "credito",
        "inicio": "jan/25", "fim": "dez/28", "antecipacoes": [],
        "contrato": {"inicio_original": "jan/25", "fim_original": "dez/28",
                     "total_parcelas": 0, "valor_parcela": 1518.93},
    }


def bancorbras():
    ants = []
    for origem, destino in [("fev/26", "nov/25"), ("mar/26", "nov/25"), ("abr/26", "nov/25"),
                            ("mai/26", "dez/25"), ("jun/26", "dez/25"), ("jul/26", "dez/25")]:
        ants.append({"origem": origem, "destino": destino, "valor_antecipado": 398.57,
                     "status": "confirmada", "mes_original_parcela": origem})
    return {
        "id": "custom_2", "nome": "Bancorbras Vila Galé", "valor": 398.57, "tipo": "debito",
        "inicio": "jan/26", "fim": "dez/26", "antecipacoes": ants,
        "contrato": {"inicio_original": "jan/26", "fim_original": "dez/26",
                     "total_parcelas": 12, "valor_parcela": 398.57},
    }


def geladeira():
    return {"id": "geladeira", "nome": "Geladeira", "valor": 152.48, "tipo": "debito",
            "inicio": "jul/25", "fim": "jun/27", "antecipacoes": []}


class TestContinuo(unittest.TestCase):
    def test_legado_com_total_parcelas_zero_e_continuo(self):
        self.assertTrue(m.eh_continuo(plano_legado()))
        self.assertFalse(m.eh_continuo(bancorbras()))
        self.assertFalse(m.eh_continuo(geladeira()))  # sem contrato: parcelado

    def test_marca_explicita_vence(self):
        item = plano_legado()
        item["continuo"] = False
        self.assertFalse(m.eh_continuo(item))

    def test_continuo_ignora_fim_gravado(self):
        item = plano_legado()
        item["fim"] = "jun/26"
        s = m.serie(item, MESES)
        self.assertEqual(s[MESES.index("dez/28")], 1518.93)

    def test_reajuste_vale_a_partir_do_mes_e_nao_muda_o_passado(self):
        item = m.registrar_reajuste(plano_legado(), "out/26", 1702.40, MESES)
        s = m.serie(item, MESES)
        self.assertEqual(s[MESES.index("jan/25")], 1518.93)
        self.assertEqual(s[MESES.index("set/26")], 1518.93)
        self.assertEqual(s[MESES.index("out/26")], 1702.40)
        self.assertEqual(s[MESES.index("dez/28")], 1702.40)
        self.assertEqual(m.valor_vigente(item, "nov/26", MESES), 1702.40)

    def test_reajuste_no_mesmo_mes_substitui(self):
        item = m.registrar_reajuste(plano_legado(), "out/26", 1702.40, MESES)
        item = m.registrar_reajuste(item, "out/26", 1650.00, MESES)
        self.assertEqual(item["reajustes"], [{"a_partir_de": "out/26", "valor": 1650.0}])

    def test_reajustes_ficam_em_ordem_e_podem_ser_removidos(self):
        item = m.registrar_reajuste(plano_legado(), "jan/28", 1900.0, MESES)
        item = m.registrar_reajuste(item, "jan/27", 1700.0, MESES)
        self.assertEqual([r["a_partir_de"] for r in item["reajustes"]], ["jan/27", "jan/28"])
        item = m.remover_reajuste(item, "jan/27", MESES)
        self.assertEqual(m.valor_vigente(item, "jun/27", MESES), 1518.93)
        self.assertEqual(m.valor_vigente(item, "jun/28", MESES), 1900.0)

    def test_validar_reajuste(self):
        item = plano_legado()
        self.assertTrue(m.validar_reajuste(item, "jan/25", 1700.0, MESES))  # no início
        self.assertTrue(m.validar_reajuste(item, "out/26", 1518.93, MESES))  # mesmo valor
        self.assertTrue(m.validar_reajuste(item, "out/26", 0, MESES))
        self.assertEqual(m.validar_reajuste(item, "out/26", 1702.40, MESES), [])

    def test_reajuste_futuro_nao_afeta_meses_quitados(self):
        antes = plano_legado()
        depois = m.registrar_reajuste(antes, "out/26", 1702.40, MESES)
        self.assertEqual(m.meses_quitados_afetados(antes, depois, MESES, QUITADOS), [])

    def test_reajuste_retroativo_lista_meses_quitados(self):
        antes = plano_legado()
        depois = m.registrar_reajuste(antes, "jul/26", 1702.40, MESES)
        self.assertEqual(m.meses_quitados_afetados(antes, depois, MESES, QUITADOS), ["jul/26", "ago/26"])


class TestEdicao(unittest.TestCase):
    def test_editar_preserva_antecipacoes_e_contrato(self):
        item = bancorbras()
        novo = m.editar_item(item, MESES, nome="Bancorbras", tipo="debito")
        self.assertEqual(novo["nome"], "Bancorbras")
        self.assertEqual(novo["antecipacoes"], item["antecipacoes"])
        self.assertEqual(novo["contrato"], item["contrato"])
        self.assertEqual((novo["valor"], novo["inicio"], novo["fim"]), (398.57, "jan/26", "dez/26"))

    def test_editar_nao_altera_o_original(self):
        item = plano_legado()
        m.registrar_reajuste(item, "out/26", 1702.40, MESES)
        m.editar_item(item, MESES, nome="Outro", tipo="debito")
        self.assertEqual(item, plano_legado())

    def test_editar_parcelas_recalcula_fim_e_contrato(self):
        novo = m.editar_item(geladeira(), MESES, nome="Geladeira", tipo="debito",
                             valor=150.0, inicio="jul/25", parcelas=12)
        self.assertEqual(novo["fim"], "jun/26")
        self.assertEqual(novo["contrato"]["total_parcelas"], 12)
        self.assertEqual(novo["contrato"]["valor_parcela"], 150.0)

    def test_editar_continuo_mantem_reajustes_e_marca_explicita(self):
        item = m.registrar_reajuste(plano_legado(), "jan/27", 1700.0, MESES)
        novo = m.editar_item(item, MESES, nome="Plano de Saúde", tipo="credito", valor=1500.0, inicio="jan/25")
        self.assertTrue(novo["continuo"])
        self.assertEqual(novo["reajustes"], [{"a_partir_de": "jan/27", "valor": 1700.0}])
        self.assertEqual(novo["contrato"]["total_parcelas"], 0)

    def test_troca_de_tipo_afeta_todos_os_meses_quitados_com_valor(self):
        antes = geladeira()
        depois = m.editar_item(antes, MESES, nome="Geladeira", tipo="credito")
        afetados = m.meses_quitados_afetados(antes, depois, MESES, QUITADOS)
        self.assertEqual(afetados, MESES[MESES.index("jul/25"):MESES.index("ago/26") + 1])

    def test_exclusao_conta_meses_de_destino_das_antecipacoes(self):
        afetados = m.meses_quitados_afetados(bancorbras(), None, MESES, QUITADOS)
        self.assertEqual(afetados, ["nov/25", "dez/25", "jan/26", "ago/26"])

    def test_resumo_ignora_mudanca_so_de_marcacao(self):
        item = plano_legado()
        novo = m.editar_item(item, MESES, nome="Plano de Saúde", tipo="credito")
        self.assertEqual(m.resumo(novo, MESES), m.resumo(item, MESES))


class TestNovoItem(unittest.TestCase):
    def test_id_unico_mesmo_depois_de_exclusao(self):
        itens = [{"id": "custom_0"}, {"id": "custom_2"}, {"id": "custom_3"}]
        self.assertNotIn(m.novo_id(itens), {"custom_0", "custom_2", "custom_3"})

    def test_criar_parcelado_calcula_fim(self):
        item = m.criar_item([], nome=" Conserto ", tipo="debito", valor=250, inicio="out/26",
                            meses=MESES, continuo=False, parcelas=3)
        self.assertEqual((item["nome"], item["fim"]), ("Conserto", "dez/26"))
        self.assertEqual(item["contrato"]["total_parcelas"], 3)
        self.assertFalse(m.eh_continuo(item))

    def test_criar_continuo_vai_ate_o_fim_do_horizonte(self):
        item = m.criar_item([], nome="Academia", tipo="debito", valor=99.9, inicio="out/26",
                            meses=MESES, continuo=True)
        self.assertEqual(item["fim"], "dez/28")
        self.assertTrue(m.eh_continuo(item))
        self.assertEqual(item["reajustes"], [])

    def test_validar_item(self):
        itens = [geladeira()]
        base = dict(tipo="debito", valor=100.0, inicio="out/26", meses=MESES, continuo=False, parcelas=2)
        self.assertEqual(m.validar_item(itens, nome="Novo", **base), [])
        self.assertTrue(m.validar_item(itens, nome="  geladeira ", **base))  # duplicado
        self.assertEqual(m.validar_item(itens, nome="Geladeira", id_atual="geladeira", **base), [])
        self.assertTrue(m.validar_item(itens, nome="", **base))
        self.assertTrue(m.validar_item(itens, nome="Novo", **{**base, "valor": 0}))
        self.assertTrue(m.validar_item(itens, nome="Novo", **{**base, "inicio": "dez/28"}))  # passa do horizonte

    def test_validar_inicio_depois_de_reajuste(self):
        erros = m.validar_item([], nome="Plano", tipo="credito", valor=1500.0, inicio="mar/27",
                               meses=MESES, continuo=True, reajustes=["jan/27"])
        self.assertTrue(erros)

    def test_novo_item_no_passado_afeta_meses_quitados(self):
        item = m.criar_item([], nome="X", tipo="debito", valor=10, inicio="jul/26",
                            meses=MESES, continuo=False, parcelas=3)
        self.assertEqual(m.meses_quitados_afetados(None, item, MESES, QUITADOS), ["jul/26", "ago/26"])


class TestSerieNoAcerto(unittest.TestCase):
    def test_bancorbras_como_no_app(self):
        s = m.serie_no_acerto(bancorbras(), MESES)
        self.assertAlmostEqual(s[MESES.index("nov/25")], 398.57 * 3)
        self.assertAlmostEqual(s[MESES.index("dez/25")], 398.57 * 3)
        self.assertAlmostEqual(s[MESES.index("jan/26")], 398.57)
        self.assertAlmostEqual(s[MESES.index("mar/26")], 0.0)
        self.assertAlmostEqual(s[MESES.index("set/26")], 398.57)


if __name__ == "__main__":
    unittest.main()
