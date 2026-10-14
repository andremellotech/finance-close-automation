"""Pré-conferência agregada: não exporta nem aprova uma leitura parcial."""
from datetime import date
from pathlib import Path
import re
from .configuration import load_profile
from .engine import process
from .guidance import explain
from .io import load_catalog, load_controls, scan_rows


def diagnose(input_dir, controls_path, period, catalog_path, profile_path=None):
    errors, pending, loaded = [], [], {}
    for key, path, loader in [('perfil', profile_path, load_profile), ('catalogo', catalog_path, load_catalog), ('controle', controls_path, load_controls)]:
        try:
            loaded[key] = loader(path)
        except Exception as exc:
            errors.append({'codigo': 'CONFIGURACAO_INVALIDA', 'arquivo': Path(path).name if path else key, 'problema': str(exc), 'acao': f'Confira o arquivo de {key} e seu formato conforme o guia.'})
    try:
        if not re.fullmatch(r'\d{4}-\d{2}', period):
            raise ValueError()
        date.fromisoformat(period + '-01')
    except (ValueError, TypeError):
        errors.append({'codigo': 'COMPETENCIA_INVALIDA', 'arquivo': '', 'problema': 'Competência inválida', 'acao': 'Informe --period como AAAA-MM, com ano e mês válidos.'})
    rows, sources = [], {}
    if 'perfil' in loaded:
        try:
            rows, sources, read_errors = scan_rows(input_dir, loaded['perfil'])
            errors.extend(read_errors)
        except Exception as exc:
            errors.append({'codigo': 'ENTRADA_INVALIDA', 'arquivo': '', 'problema': str(exc), 'acao': 'Confira a pasta --input e a presença de arquivos CSV/XLSX diretamente nela.'})
    result = None
    if len(loaded) == 3 and not any(e['codigo'] == 'COMPETENCIA_INVALIDA' for e in errors):
        try:
            result = process(rows, loaded['controle'], period, loaded['catalogo'], sources)
            for row in result['linhas']:
                for advice in row['orientacoes']:
                    pending.append({**advice, 'arquivo': row['arquivo'], 'aba': row['aba'], 'linha': row['linha'], 'registro_id': row['registro_id']})
            failed = {e['arquivo'] for e in errors}
            for item in result['conciliacao']:
                if item['status'] != 'CONCILIADO' and item['arquivo'] not in failed:
                    pending.append({**explain([item['status']])[0], 'arquivo': item['arquivo'], 'aba': '', 'linha': None, 'registro_id': ''})
        except Exception as exc:
            errors.append({'codigo': 'CONTROLE_INVALIDO', 'arquivo': Path(controls_path).name, 'problema': str(exc), 'acao': 'Confira quantidades inteiras e totais com ponto decimal no controle independente.'})
    status = 1 if errors else 2 if pending or not result or not result['liberado'] else 0
    return {'status': status, 'pronto': status == 0, 'leitura_parcial': bool(errors), 'erros_estrutura': errors, 'pendencias': pending, 'resumo': result['resumo'] if result and not errors else None, 'linhas_lidas': len(rows)}


def describe_diagnosis(report):
    lines = ['VERIFICAÇÃO: ' + {0: 'PRONTO PELAS REGRAS', 1: 'ERRO DE PREPARAÇÃO/LEITURA', 2: 'COM PENDÊNCIAS'}[report['status']]]
    if report['leitura_parcial']:
        lines.append('A leitura pode estar incompleta; nenhum lote foi aprovado e nenhuma saída foi criada.')
    for issue in [*report['erros_estrutura'], *report['pendencias']]:
        location = issue.get('arquivo') or 'configuração'
        if issue.get('linha'):
            location += f" · {issue.get('aba', '')} · linha {issue['linha']}"
        lines.append(f"[{issue['codigo']}] {location}: {issue['problema']}\n  Ação: {issue['acao']}")
    if report['pronto']:
        lines.append('Preparação conferida. run repetirá as validações; confira também os controles de negócio.')
    return '\n'.join(lines)
