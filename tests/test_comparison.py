import csv
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from finance_close.engine import process
from finance_close.demo import generate_demo
from test_engine import row, control, CATALOG

ROOT = Path(__file__).resolve().parents[1]


class ComparisonTests(unittest.TestCase):
    def test_removing_duplicate_does_not_claim_identical_values_changed(self):
        from finance_close.comparison import compare_results
        before = process([row(amount='100', linha=2), row(amount='100', linha=3)], control(2, '200'), '2025-09', CATALOG)
        after = process([row(amount='100', linha=2)], control(), '2025-09', CATALOG)
        group = compare_results(before, after)['grupos'][0]
        self.assertEqual(group['tipo'], 'PENDENCIA_RESOLVIDA')
        self.assertEqual(group['campos_alterados'], ['status', 'quantidade_linhas'])
        conflict = process([row(amount='100', linha=2), row(amount='101', linha=3)], control(2, '201'), '2025-09', CATALOG)
        changed = compare_results(conflict, after)['grupos'][0]['campos_alterados']
        self.assertEqual(changed, ['valor_brl', 'status', 'quantidade_linhas'])

    def test_money_format_only_does_not_claim_a_field_change(self):
        from finance_close.comparison import compare_results
        before = process([row(amount='100.0')], control(), '2025-09', CATALOG)
        after = process([row(amount='100.00')], control(), '2025-09', CATALOG)
        group = compare_results(before, after)['grupos'][0]
        self.assertEqual(group['tipo'], 'SEM_ALTERACAO')
        self.assertEqual(group['campos_alterados'], [])

    def test_false_release_claim_is_rejected(self):
        from finance_close.comparison import compare_results
        before = process([row(centro_custo='XX')], control(), '2025-09', CATALOG)
        inconsistent = deepcopy(before)
        inconsistent['liberado'] = True
        with self.assertRaisesRegex(ValueError, 'libera|Liber'):
            compare_results(before, inconsistent)

    def test_demo_review_has_five_resolved_groups_and_one_missing_id_removed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            generate_demo(root)
            target = root / 'comparison'
            run = subprocess.run([sys.executable, '-m', 'finance_close', 'compare', '--before', str(root / 'examples/com-pendencias/resultado.json'), '--after', str(root / 'examples/validado/resultado.json'), '--output', str(target)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads((target / 'comparacao.json').read_text(encoding='utf-8'))
            self.assertEqual(data['resumo']['grupos'], 19)
            self.assertEqual(data['resumo']['resolvidos'], 5)
            self.assertEqual(data['resumo']['removidos'], 1)
            self.assertEqual(data['resumo']['sem_alteracao'], 13)
            self.assertEqual(data['metricas']['total_aprovado_centavos'], {'antes': 4800000, 'depois': 14500000, 'diferenca': 9700000})
            self.assertTrue((target / 'comparacao.html').exists())
            with (target / 'comparacao.csv').open(encoding='utf-8-sig', newline='') as stream:
                self.assertEqual(len(list(csv.DictReader(stream, delimiter=';'))), 19)
            occupied = subprocess.run(run.args, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(occupied.returncode, 1)

    def test_renamed_or_filled_id_is_not_inferred_as_resolved(self):
        from finance_close.comparison import compare_results
        for old_id in ('ANTIGO', ''):
            with self.subTest(old_id=old_id):
                before = process([row(id=old_id)], control(), '2025-09', CATALOG)
                after = process([row(id='NOVO')], control(), '2025-09', CATALOG)
                data = compare_results(before, after)
                self.assertEqual(data['resumo']['resolvidos'], 0)
                self.assertEqual(data['resumo']['adicionados'], 1)
                self.assertEqual(data['resumo']['removidos'], 1)

    def test_reordered_conflicting_versions_are_origin_change_not_financial_change(self):
        from finance_close.comparison import compare_results
        before = process([row(amount='100', linha=2), row(amount='101', linha=3)], control(2, '201'), '2025-09', CATALOG)
        after = process([row(amount='101', linha=2), row(amount='100', linha=3)], control(2, '201'), '2025-09', CATALOG)
        data = compare_results(before, after)
        self.assertEqual(data['resumo']['grupos'], 1)
        self.assertEqual(data['grupos'][0]['tipo'], 'ORIGEM_ALTERADA')
        self.assertEqual(data['resumo']['resolvidos'], 0)
        self.assertEqual(len(data['grupos'][0]['antes']), 2)
        self.assertEqual(data['metricas']['total_aprovado_centavos']['diferenca'], 0)

    def test_inconsistent_summary_is_rejected_and_different_period_rules_warn(self):
        from finance_close.comparison import compare_results
        before = process([row()], control(), '2025-09', CATALOG)
        invalid = deepcopy(before)
        invalid['resumo']['recebidas'] = 999
        with self.assertRaisesRegex(ValueError, 'resumo|Resumo'):
            compare_results(before, invalid)
        catalog = deepcopy(CATALOG)
        catalog['centros']['ANA'] = 'Outro nome'
        after = process([row(data_competencia='2025-10-01')], control(), '2025-10', catalog)
        data = compare_results(before, after)
        self.assertIn('COMPETENCIAS_DIFERENTES', [a['codigo'] for a in data['avisos']])
        self.assertIn('CONFIGURACOES_DIFERENTES', [a['codigo'] for a in data['avisos']])

    def test_unsafe_ids_stay_text_in_csv_and_html(self):
        from finance_close.comparison import compare_results, write_comparison
        with tempfile.TemporaryDirectory() as temp:
            before = process([row(id='=1+1')], control(), '2025-09', CATALOG)
            after = process([row(id='<img src=x onerror=alert(1)>')], control(), '2025-09', CATALOG)
            target = Path(temp) / 'out'
            write_comparison(compare_results(before, after), target)
            html = (target / 'comparacao.html').read_text(encoding='utf-8')
            self.assertNotIn('<img src=x', html)
            with (target / 'comparacao.csv').open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.DictReader(stream, delimiter=';'))
            self.assertIn("'=1+1", [r['registro_id'] for r in rows])


if __name__ == '__main__':
    unittest.main()
