import csv
import json
import subprocess
import sys
import tempfile
import unittest
import re
from copy import deepcopy
from pathlib import Path

from test_engine import row, control, CATALOG
from test_pipeline import write_csv

ROOT = Path(__file__).resolve().parents[1]


def cli(*args, stdin=None):
    return subprocess.run([sys.executable, '-m', 'finance_close', *map(str, args)], input=stdin, cwd=ROOT, capture_output=True, text=True)


def fixture(base, rows):
    directory = base / 'input'
    directory.mkdir()
    write_csv(directory / 'a.csv', rows)
    (base / 'catalogo.json').write_text(json.dumps(CATALOG), encoding='utf-8')
    (base / 'controle.csv').write_text('arquivo;linhas_esperadas;total_esperado_brl\na.csv;1;100.00\n', encoding='utf-8')
    return ['--input', directory, '--controls', base / 'controle.csv', '--catalog', base / 'catalogo.json', '--period', '2025-09']


class OperationsTests(unittest.TestCase):
    def test_execution_identity_is_unique_and_effective_config_hashes_are_stable(self):
        from finance_close.engine import process
        from finance_close.export import write_outputs
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = process([row()], control(), '2025-09', CATALOG)
            for index in (1, 2):
                write_outputs(result, base / str(index))
            first = json.loads((base / '1/resultado.json').read_text(encoding='utf-8'))
            second = json.loads((base / '2/resultado.json').read_text(encoding='utf-8'))
            self.assertNotEqual(first['execucao']['id'], second['execucao']['id'])
            self.assertRegex(first['execucao']['gerado_em_utc'], r'^\d{4}-\d{2}-\d{2}T.*Z$')
            self.assertEqual(first['execucao']['configuracoes'], second['execucao']['configuracoes'])
            changed = deepcopy(CATALOG)
            changed['centros']['ANA'] = 'Nome alterado'
            write_outputs(process([row()], control(), '2025-09', changed), base / '3')
            third = json.loads((base / '3/resultado.json').read_text(encoding='utf-8'))
            self.assertNotEqual(first['execucao']['configuracoes']['catalogo_sha256'], third['execucao']['configuracoes']['catalogo_sha256'])
            manifest = json.loads((base / '1/execucao.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['execucao'], first['execucao'])
            html = (base / '1/relatorio.html').read_text(encoding='utf-8')
            self.assertEqual(re.search(r'id="excel-download" href="([^"]+)"', html).group(1), 'fechamento.xlsx')
            payload = json.loads(re.search(r'id="demo-data">(.*?)</script>', html, re.S).group(1))
            self.assertEqual(payload['execucao']['execucao']['id'], first['execucao']['id'])
            self.assertIn('versao_aplicacao', first['execucao'])

    def test_pending_exports_include_action_and_keep_original_location(self):
        from finance_close.engine import process
        from finance_close.export import write_outputs
        import openpyxl
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'out'
            result = process([row(centro_custo='XX')], control(), '2025-09', CATALOG)
            write_outputs(result, target)
            data = json.loads((target / 'resultado.json').read_text(encoding='utf-8'))
            advice = data['linhas'][0]['orientacoes'][0]
            self.assertEqual(advice['codigo'], 'CENTRO_DESCONHECIDO')
            self.assertIn('cadastro', advice['acao'])
            self.assertEqual(data['linhas'][0]['linha'], 2)
            with (target / 'pendencias.csv').open(encoding='utf-8-sig', newline='') as stream:
                rows = list(csv.DictReader(stream, delimiter=';'))
            self.assertIn('cadastro', rows[0]['acao_sugerida'])
            book = openpyxl.load_workbook(target / 'fechamento.xlsx', data_only=False)
            self.assertEqual(book['Pendencias']['L6'].value, 'acao_sugerida')
            self.assertIn('cadastro', book['Pendencias']['L7'].value)
            book.close()

    def test_setup_creates_usable_configs_and_empty_independent_control(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'project'
            # Default choices: name, BR, separator, sheet, six column names,
            # one center, two categories, optional description and required center.
            answers = ['Meu projeto'] + [''] * 25
            run = cli('setup', '--output', target, stdin='\n'.join(answers) + '\n')
            self.assertEqual(run.returncode, 0, run.stderr)
            profile = json.loads((target / 'perfil.json').read_text(encoding='utf-8'))
            catalog = json.loads((target / 'catalogo.json').read_text(encoding='utf-8'))
            self.assertEqual(profile['nome'], 'Meu projeto')
            self.assertEqual(profile['entrada']['decimal'], ',')
            self.assertEqual(catalog['categorias']['REC']['natureza'], 'receita')
            self.assertEqual(catalog['categorias']['DESP']['natureza'], 'gasto')
            with (target / 'controle.csv').open(encoding='utf-8-sig') as stream:
                self.assertEqual(list(csv.DictReader(stream, delimiter=';')), [])
            original = (target / 'perfil.json').read_bytes()
            occupied = cli('setup', '--output', target, stdin='')
            self.assertEqual(occupied.returncode, 1)
            self.assertEqual((target / 'perfil.json').read_bytes(), original)

    def test_check_reports_every_bad_source_without_writing_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            args = fixture(base, [row(centro_custo='DESCONHECIDO')])
            (base / 'input/b.csv').write_text('cabecalho;errado\n1;2\n', encoding='utf-8')
            (base / 'input/c.xlsx').write_bytes(b'not a workbook')
            before = {p.relative_to(base): p.read_bytes() for p in base.rglob('*') if p.is_file()}
            run = cli('check', *args, '--json')
            self.assertEqual(run.returncode, 1, run.stderr)
            result = json.loads(run.stdout)
            self.assertFalse(result['pronto'])
            self.assertEqual({e['arquivo'] for e in result['erros_estrutura']}, {'b.csv', 'c.xlsx'})
            self.assertEqual(result['pendencias'][0]['arquivo'], 'a.csv')
            self.assertEqual(result['pendencias'][0]['linha'], 2)
            self.assertIn('cadastro', result['pendencias'][0]['acao'].lower())
            self.assertEqual(before, {p.relative_to(base): p.read_bytes() for p in base.rglob('*') if p.is_file()})

    def test_check_distinguishes_ready_and_business_pending(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            args = fixture(base, [row()])
            ready = cli('check', *args, '--json')
            self.assertEqual(ready.returncode, 0, ready.stderr)
            self.assertTrue(json.loads(ready.stdout)['pronto'])
            write_csv(base / 'input/a.csv', [row(amount='ruim')])
            pending = cli('check', *args, '--json')
            self.assertEqual(pending.returncode, 2, pending.stderr)
            self.assertFalse(json.loads(pending.stdout)['pronto'])
            self.assertTrue(any(p['codigo'] == 'VALOR_INVALIDO' for p in json.loads(pending.stdout)['pendencias']))


if __name__ == '__main__':
    unittest.main()
