"""Exportadores do produto: CSV, JSON e relatório Excel reproduzível."""
import csv
import json
from pathlib import Path

import xlsxwriter
from .engine import FIELDS, money
from .audit import ensure_execution

DETAIL_HEADERS = ["arquivo", "aba", "linha", *FIELDS, "status", "motivos"]


def _detail(entry):
    return [entry["arquivo"], entry["aba"], entry["linha"], *[money(entry["valor_centavos"]) if field == "valor_brl" and entry["valor_centavos"] is not None else entry[field] for field in FIELDS], entry["status"], " | ".join(entry["erros"])]


def _csv(path, headers, values):
    def safe(value):
        if isinstance(value, str) and value.lstrip().startswith(("=", "+", "@", "-")):
            # Money has a strict numeric grammar; other formula-like text is escaped.
            try:
                from .engine import parse_cents
                parse_cents(value)
            except ValueError:
                return "'" + value
        return value
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(headers)
        writer.writerows([[safe(v) for v in row] for row in values])


def write_outputs(result, output_dir, overwrite=False):
    result = ensure_execution(result)
    target = Path(output_dir)
    if target.exists() and any(target.iterdir()) and not overwrite:
        raise ValueError("Escolha uma pasta de saída vazia; arquivos existentes foram preservados")
    target.mkdir(parents=True, exist_ok=True)
    approved = [entry for entry in result["linhas"] if entry["status"] == "APROVADO"]
    excluded = [entry for entry in result["linhas"] if entry["status"] != "APROVADO"]
    _csv(target / "base_aprovada.csv", DETAIL_HEADERS, [_detail(e) for e in approved])
    _csv(target / "pendencias.csv", DETAIL_HEADERS + ['acao_sugerida'], [_detail(e) + [' | '.join(a['acao'] for a in e.get('orientacoes', []))] for e in excluded])
    _csv(target / "rastreabilidade.csv", DETAIL_HEADERS + ["sha256_arquivo"], [_detail(e) + [result["fontes"].get(e["arquivo"], {}).get("sha256", "")] for e in result["linhas"]])
    controls_headers = ["arquivo", "linhas_recebidas", "linhas_esperadas", "total_recebido_brl", "total_esperado_brl", "diferenca_brl", "valores_nao_quantificaveis", "status"]
    controls_values = [[c["arquivo"], c["linhas_recebidas"], c["linhas_esperadas"], money(c["total_recebido_centavos"]), money(c["total_esperado_centavos"]) if c["total_esperado_centavos"] is not None else "", money(c["diferenca_centavos"]) if c["diferenca_centavos"] is not None else "", c["valores_nao_quantificaveis"], c["status"]] for c in result["conciliacao"]]
    _csv(target / "conciliacao.csv", controls_headers, controls_values)
    (target / "resultado.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    manifest = {key: result[key] for key in ('schema_versao', 'execucao', 'competencia', 'fontes')}
    (target / 'execucao.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    _workbook(target / "fechamento.xlsx", result, approved, excluded, controls_headers, controls_values)
    from .report import render_run_report
    render_run_report(result, target / 'relatorio.html', result.get('perfil_entrada', {}).get('nome', 'Fechamento mensal'))
    return target


def _workbook(path, result, approved, excluded, controls_headers, controls_values):
    book = xlsxwriter.Workbook(path, {"strings_to_formulas": False, "strings_to_urls": False})
    data_note = 'Dados fictícios' if result.get('demonstrativo') else 'Dados da execução'
    book.set_properties({"title": "Finance Close Automation", "author": "André Mello", "comments": data_note + '. Relatório exportado pelo produto Python.'})
    formats = {
        "title": book.add_format({"font_name": "Arial", "font_size": 20, "bold": True, "font_color": "#FFFFFF", "bg_color": "#142C38", "valign": "vcenter"}),
        "sub": book.add_format({"font_name": "Arial", "font_size": 10, "font_color": "#52707B", "text_wrap": True, "valign": "vcenter"}),
        "head": book.add_format({"font_name": "Arial", "font_size": 10, "bold": True, "font_color": "#FFFFFF", "bg_color": "#254553", "text_wrap": True, "valign": "vcenter"}),
        "text": book.add_format({"font_name": "Arial", "font_size": 10, "valign": "vcenter", "text_wrap": True, "bottom": 1, "bottom_color": "#E2E9EC"}),
        "num": book.add_format({"font_name": "Arial", "font_size": 10, "num_format": '#,##0.00;[Red](#,##0.00);0.00', "valign": "vcenter", "bottom": 1, "bottom_color": "#E2E9EC"}),
        "integer": book.add_format({"font_name": "Arial", "font_size": 11, "num_format": "0", "valign": "vcenter"}),
        "ready": book.add_format({"font_name": "Arial", "font_size": 11, "bold": True, "font_color": "#0C6B4C", "bg_color": "#E1F4EC", "valign": "vcenter"}),
        "pending": book.add_format({"font_name": "Arial", "font_size": 11, "bold": True, "font_color": "#965A0B", "bg_color": "#FFF0D8", "valign": "vcenter"}),
    }
    summary = book.add_worksheet("Resumo")

    def header(sheet, title, columns, subtitle):
        sheet.hide_gridlines(2)
        sheet.set_default_row(25)
        sheet.merge_range(0, 0, 1, max(columns - 1, 3), title, formats["title"])
        sheet.merge_range(2, 0, 3, max(columns - 1, 3), subtitle, formats["sub"])
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.fit_to_pages(1, 0)
        sheet.set_margins(0.3, 0.3, 0.4, 0.4)
        sheet.set_footer('&LFinance Close Automation — ' + data_note + '&R&P / &N')

    header(summary, "Fechamento mensal", 4, f"Competência {result['competencia']} · Valores em BRL · {data_note}. Com pendências, a base é parcial.")
    summary.set_column("A:A", 37)
    summary.set_column("B:B", 25)
    summary.set_column("C:D", 13)
    summary.write_row(5, 0, ["Indicador", "Resultado"], formats["head"])
    s = result["resumo"]
    metrics = [("Status", "VALIDADO" if result["liberado"] else "COM PENDÊNCIAS"), ("Competência", result["competencia"]), ("Arquivos recebidos", s["arquivos"]), ("Linhas recebidas", s["recebidas"]), ("Linhas aprovadas", s["aprovadas"]), ("Pendências de validação", s["pendentes"]), ("Duplicatas excluídas", s["duplicadas"]), ("Linhas em conflito de ID", s["conflitos"]), ("Valores não quantificáveis", s["valores_nao_quantificaveis"])]
    for index, (label, value) in enumerate(metrics, 6):
        summary.write(index, 0, label, formats["text"])
        summary.write(index, 1, value, formats["integer"] if isinstance(value, int) else formats["text"])
    summary.write("B7", metrics[0][1], formats["ready"] if result["liberado"] else formats["pending"])
    last = max(7, 6 + len(approved))
    def nature_formula(nature):
        return '=' + ('-' if nature == 'gasto' else '') + f'SUMIF(\'Base aprovada\'!L7:L{last},"{nature}",\'Base aprovada\'!I7:I{last})'
    formula_values = [("A17", "Receitas da base aprovada", "B17", nature_formula('receita'), s["receitas_centavos"]), ("A18", "Gastos líquidos da base aprovada", "B18", nature_formula('gasto'), s["gastos_centavos"]), ("A19", "Resultado da base aprovada", "B19", "=B17-B18", s["total_aprovado_centavos"]), ("A22", "Parcela aprovada", "B22", f"=SUM('Base aprovada'!I7:I{last})", s["total_aprovado_centavos"])]
    for label_cell, label, cell, formula, cached in formula_values:
        summary.write(label_cell, label, formats["text"])
        summary.write_formula(cell, formula, formats["num"], cached / 100)
    for label_cell, label, cell, cents in [("A21", "Recebido quantificável", "B21", s["total_recebido_centavos"]), ("A23", "Parcela excluída quantificável", "B23", s["total_excluido_centavos"])]:
        summary.write(label_cell, label, formats["text"])
        summary.write_number(cell, cents / 100, formats["num"])
    summary.write("A24", "Diferença da ponte", formats["text"])
    summary.write_formula("B24", "=B21-B22-B23", formats["num"], 0)
    summary.merge_range("A27:D29", "Conciliação compara as linhas recebidas aos controles de origem. Qualidade define quais linhas entram na base aprovada. Com valor inválido, a soma recebida é apenas a parcela quantificável.", formats["sub"])
    summary.freeze_panes(6, 0)
    summary.print_area("A1:D29")

    def detail_sheet(name, entries, trace=False):
        sheet = book.add_worksheet(name)
        resolved_nature = name == 'Base aprovada'
        with_action = name == 'Pendencias'
        headers = DETAIL_HEADERS + (["sha256_arquivo"] if trace else []) + (['natureza'] if resolved_nature else []) + (['acao_sugerida'] if with_action else [])
        header(sheet, name, len(headers), 'Origem preservada por arquivo, aba e linha · Valores em BRL · ' + data_note)
        sheet.write_row(5, 0, headers, formats["head"])
        sheet.set_row(5, 32)
        for col in range(len(headers)):
            sheet.set_column(col, col, 19)
        sheet.set_column("C:C", 9)
        sheet.set_column("H:H", 34)
        sheet.set_column("K:K", 42)
        if trace:
            sheet.set_column("L:L", 25)
        if with_action:
            sheet.set_column('L:L', 64)
        for index, entry in enumerate(entries, 6):
            values = _detail(entry) + ([result["fontes"].get(entry["arquivo"], {}).get("sha256", "")] if trace else [])
            if resolved_nature:
                values.append(result['catalogo']['categorias'][entry['categoria']]['natureza'])
            if with_action:
                values.append(' | '.join(a['acao'] for a in entry.get('orientacoes', [])))
            for col, value in enumerate(values):
                if col == 8 and entry["valor_centavos"] is not None:
                    sheet.write_number(index, col, entry["valor_centavos"] / 100, formats["num"])
                elif col == 2:
                    sheet.write_number(index, col, int(value), formats["integer"])
                elif value == "":
                    sheet.write_blank(index, col, None, formats["text"])
                else:
                    sheet.write_string(index, col, str(value), formats["text"])
            sheet.set_row(index, 90 if with_action else 46 if trace else 36)
        if not entries:
            sheet.write("A7", "Sem linhas nesta seleção", formats["sub"])
        sheet.freeze_panes(6, 3)
        sheet.autofilter(5, 0, max(6, 5 + len(entries)), len(headers) - 1)
        sheet.repeat_rows(0, 5)
        sheet.print_area(0, 0, max(6, 5 + len(entries)), len(headers) - 1)

    detail_sheet("Base aprovada", approved)
    detail_sheet("Pendencias", excluded)
    sheet = book.add_worksheet("Conciliacao")
    header(sheet, "Conciliação por arquivo", len(controls_headers), "Quantidade e total recebidos comparados ao controle · INCOMPLETO indica valores que não puderam ser somados")
    sheet.set_column("A:A", 24)
    sheet.set_column("B:G", 21)
    sheet.set_column("H:H", 23)
    sheet.write_row(5, 0, ["Arquivo", "Linhas recebidas", "Linhas esperadas", "Recebido quantificável (BRL)", "Controle (BRL)", "Diferença (BRL)", "Valores não quantificáveis", "Status"], formats["head"])
    sheet.set_row(5, 36)
    for index, values in enumerate(controls_values, 6):
        for col, value in enumerate(values):
            if col in (3, 4, 5) and value != "":
                sheet.write_number(index, col, float(value), formats["num"])
            else:
                sheet.write(index, col, value if value is not None else "—", formats["text"])
        sheet.set_row(index, 36)
    sheet.freeze_panes(6, 1)
    sheet.autofilter(5, 0, max(6, 5 + len(controls_values)), 7)
    detail_sheet("Rastreabilidade", result["linhas"], True)
    book.close()
