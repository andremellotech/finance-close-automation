import unittest
from finance_close.engine import process, parse_cents

CATALOG = {"centros": {"ANA": "Analytics", "ENG": "Engenharia", "OPS": "Operações"}, "categorias": {"REV": "Receita", "DIR": "Custos", "PES": "Pessoal", "TEC": "Tecnologia", "COM": "Comercial", "ADM": "Administrativo"}}


def row(id="A1", amount="100.00", **changes):
    item = dict(registro_id=id, data_competencia="2025-09-01", centro_custo="ANA", categoria="REV", descricao="Receita fictícia", valor_brl=amount, arquivo="a.csv", aba="CSV", linha=2)
    item.update(changes)
    return item


def control(lines=1, total="100.00", file="a.csv"):
    return {file: {"linhas_esperadas": lines, "total_esperado_brl": total}}


class EngineTests(unittest.TestCase):
    def test_money_is_exact_and_rejects_ambiguous_or_nonfinite(self):
        self.assertEqual(parse_cents("123456.78"), 12345678)
        self.assertEqual(parse_cents("-0.01"), -1)
        for invalid in ("NaN", "Infinity", "1.234", "1,23", "R$ 1.00", "", True, None):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                parse_cents(invalid)

    def test_valid_receipt_and_expense_are_reconciled(self):
        result = process([row(), row("A2", "-35.25", categoria="DIR", linha=3)], control(2, "64.75"), "2025-09", CATALOG)
        self.assertTrue(result["liberado"])
        self.assertEqual(result["resumo"]["aprovadas"], 2)
        self.assertEqual(result["resumo"]["total_aprovado_centavos"], 6475)
        self.assertEqual(result["conciliacao"][0]["status"], "CONCILIADO")

    def test_exact_duplicate_keeps_only_first(self):
        result = process([row(), row(linha=3)], control(2, "200.00"), "2025-09", CATALOG)
        self.assertEqual([r["status"] for r in result["linhas"]], ["APROVADO", "DUPLICADO"])
        self.assertFalse(result["liberado"])
        self.assertEqual(result["resumo"]["total_excluido_centavos"], 10000)

    def test_conflicting_id_excludes_both_files(self):
        controls = {**control(), **control(1, "101.00", "b.csv")}
        result = process([row(), row(amount="101.00", arquivo="b.csv")], controls, "2025-09", CATALOG)
        self.assertEqual([r["status"] for r in result["linhas"]], ["CONFLITO", "CONFLITO"])
        self.assertEqual(result["resumo"]["aprovadas"], 0)

    def test_missing_fields_catalog_period_and_sign_are_rejected(self):
        cases = [{"registro_id": ""}, {"centro_custo": "XX"}, {"categoria": "X"}, {"data_competencia": "2025-09-31"}, {"data_competencia": "2025-08-01"}, {"descricao": ""}, {"valor_brl": "-1.00"}]
        for change in cases:
            with self.subTest(change=change):
                result = process([row(**change)], control(), "2025-09", CATALOG)
                self.assertEqual(result["linhas"][0]["status"], "PENDENTE")
                self.assertFalse(result["liberado"])

    def test_non_numeric_amount_makes_control_incomplete(self):
        result = process([row(amount="inválido")], control(), "2025-09", CATALOG)
        self.assertEqual(result["conciliacao"][0]["status"], "INCOMPLETO")
        self.assertEqual(result["resumo"]["valores_nao_quantificaveis"], 1)

    def test_missing_and_orphan_controls_block_release(self):
        for controls in ({}, {**control(), **control(1, "5", "ausente.csv")}):
            with self.subTest(controls=controls):
                result = process([row()], controls, "2025-09", CATALOG)
                self.assertFalse(result["liberado"])

    def test_empty_batch_never_releases(self):
        result = process([], {}, "2025-09", CATALOG)
        self.assertFalse(result["liberado"])

    def test_numeric_bridge_includes_excluded_rows(self):
        result = process([row(), row("B", "30.00", centro_custo="XX"), row("C", "bad")], control(3, "130.00"), "2025-09", CATALOG)
        self.assertEqual(result["resumo"]["total_recebido_centavos"], 13000)
        self.assertEqual(result["resumo"]["total_aprovado_centavos"], 10000)
        self.assertEqual(result["resumo"]["total_excluido_centavos"], 3000)

    def test_invalid_period_is_rejected(self):
        for period in ("2025-13", "2025-1", "", "x"):
            with self.subTest(period=period), self.assertRaises(ValueError):
                process([row()], control(), period, CATALOG)


if __name__ == "__main__":
    unittest.main()
