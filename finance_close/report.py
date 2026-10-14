"""Páginas autocontidas dos exemplos ou de uma execução local."""
import json
from html import escape
from pathlib import Path


def render_report(results, output, title='Finance Close Automation', mode='demo'):
    source = Path(__file__).resolve().parents[1] / "web"
    html = (source / "template.html").read_text(encoding="utf-8")
    def encoded(value):
        return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    first = next(iter(results.values()))
    year, month = first['competencia'].split('-')
    months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    demo = mode == 'demo'
    paths = {key: f'examples/{key}/fechamento.xlsx' if demo else 'fechamento.xlsx' for key in results}
    context = {'mode': mode, 'title': title, 'excelPaths': paths, 'manifestPaths': {key: f'examples/{key}/execucao.json' if demo else 'execucao.json' for key in results}}
    switch = '<button type="button" data-case="com-pendencias" aria-pressed="true">Com pendências <span>01</span></button><button type="button" data-case="validado" aria-pressed="false">Validado <span>02</span></button>' if demo else '<span class="mini-label">PROCESSAMENTO LOCAL</span>'
    center_count, file_count = len(first['catalogo']['centros']), first['resumo']['arquivos']
    input_note = f"{center_count} {'centro cadastrado' if center_count == 1 else 'centros cadastrados'} · {file_count} {'arquivo' if file_count == 1 else 'arquivos'}<br>"
    replacements = {
        '__PAGE_TITLE__': escape(title),
        '__HERO__': 'O fechamento começa<br>com <em>dados conferidos.</em>' if demo else 'Conferência<br>do <em>fechamento.</em>',
        '__LEAD__': 'Da consolidação dos arquivos à base aprovada.<br>Explore as pendências, os controles e a origem de cada lançamento.' if demo else f'Resultados de <strong>{escape(title)}</strong>.<br>Confira o lote processado, as pendências e a origem de cada lançamento.',
        '__CASE_CAPTION__': 'CASO DEMONSTRATIVO' if demo else 'COMPETÊNCIA PROCESSADA',
        '__PERIOD__': f'{months[int(month)-1]} <span>{year}</span>',
        '__INPUT_NOTE__': input_note + ('Dados inteiramente fictícios' if demo else 'Dados fornecidos nesta execução'),
        '__CASE_HEADING__': 'EXPLORE O PROCESSO' if demo else 'RELATÓRIO DA EXECUÇÃO',
        '__CASE_NOTE__': 'Compare o lote recebido com o exemplo validado.' if demo else 'Indicadores e tabelas calculados a partir dos arquivos processados.',
        '__CASE_SWITCH__': switch,
        '__EXCEL_PATH__': escape(next(iter(paths.values())), quote=True),
        '__COMPARISON_LINK__': '<p class="under-note"><a href="examples/comparacao/comparacao.html">Explorar a comparação entre os dois lotes →</a> · <a href="docs/operations-guide.md">Guia de configuração e operação</a></p>' if demo else '',
        '__GUIDE_NOTE__': 'Esta página apresenta exemplos processados. A automação de arquivos Excel/CSV é executada pelo Python, fora do navegador.' if demo else 'Este HTML contém os dados desta execução. Para conferir outro lote, execute a rotina novamente. Compartilhe o relatório somente com quem pode acessar esses dados.',
        '__FOOTNOTE__': 'Dados fictícios · Sem integração corporativa' if demo else 'Relatório local · Confira os controles de origem',
        '__DATA__': encoded(results), '__CONTEXT__': encoded(context),
        '__CSS__': (source / 'style.css').read_text(encoding='utf-8'),
        '__JS__': (source / 'app.js').read_text(encoding='utf-8'),
    }
    # Replace template tokens before inserting assets or user-controlled text.
    import re
    html = re.sub(r'__[A-Z_]+__', lambda match: replacements.get(match[0], match[0]), html)
    Path(output).write_text(html, encoding="utf-8")


def render_run_report(result, output, title='Fechamento mensal'):
    render_report({'execucao': result}, output, title=title, mode='run')
