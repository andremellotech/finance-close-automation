import json
import tempfile
import unittest
from pathlib import Path
from finance_close.demo import generate_demo
from finance_close.io import load_rows


class DemoTests(unittest.TestCase):
    def test_two_examples_have_hand_checked_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generate_demo(root)
            good = json.loads((root / "examples/validado/resultado.json").read_text(encoding="utf-8"))
            bad = json.loads((root / "examples/com-pendencias/resultado.json").read_text(encoding="utf-8"))
            self.assertTrue(good["liberado"])
            self.assertEqual(good["resumo"]["recebidas"], 18)
            self.assertEqual(good["resumo"]["total_aprovado_centavos"], 14500000)
            self.assertFalse(bad["liberado"])
            self.assertEqual(bad["resumo"]["recebidas"], 21)
            self.assertEqual(bad["resumo"]["aprovadas"], 14)
            self.assertEqual(bad["resumo"]["pendentes"], 4)
            self.assertEqual(bad["resumo"]["duplicadas"], 1)
            self.assertEqual(bad["resumo"]["conflitos"], 2)
            self.assertEqual(bad["resumo"]["total_recebido_centavos"], 53722550)
            self.assertEqual(bad["resumo"]["total_aprovado_centavos"], 4800000)
            self.assertEqual(bad["resumo"]["total_excluido_centavos"], 48922550)
            self.assertEqual(bad["resumo"]["valores_nao_quantificaveis"], 1)
            # The source contains a real typed Excel date and is read end to end.
            rows, _ = load_rows(root / "sample-input/validado")
            self.assertEqual(len(rows), 18)
            self.assertEqual(str(rows[6]["data_competencia"])[:10], "2025-09-15")

    def test_report_embeds_the_results_without_external_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generate_demo(root)
            from html.parser import HTMLParser
            class Page(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.external, self.scripts, self.collect = [], [], False
                def handle_starttag(self, tag, attrs):
                    attrs = dict(attrs)
                    if tag in ("script", "link", "img") and any(str(attrs.get(k, "")).startswith("http") for k in ("src", "href")):
                        self.external.append(attrs)
                    self.collect = tag == "script" and attrs.get("id") == "demo-data"
                def handle_endtag(self, tag):
                    if tag == "script":
                        self.collect = False
                def handle_data(self, value):
                    if self.collect:
                        self.scripts.append(value)
            page = Page()
            page.feed((root / "index.html").read_text(encoding="utf-8"))
            self.assertFalse(page.external)
            embedded = json.loads("".join(page.scripts))
            self.assertEqual(embedded["validado"]["resumo"]["aprovadas"], 18)
            self.assertEqual(embedded["com-pendencias"]["resumo"]["aprovadas"], 14)


if __name__ == "__main__":
    unittest.main()
