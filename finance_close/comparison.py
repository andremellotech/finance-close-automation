"""Comparação de resultados por grupos de ID, com conferência dos totais."""
from collections import Counter, defaultdict
from datetime import date
import json
from pathlib import Path
import re
from .audit import fingerprint
from .configuration import FIELDS, normalize_catalog
from .engine import money

TYPES = {'PENDENCIA_RESOLVIDA': 'resolvidos', 'NOVA_PENDENCIA': 'novas_pendencias', 'ADICIONADO': 'adicionados', 'REMOVIDO': 'removidos', 'ALTERADO': 'alterados', 'ALTERADO_COM_PENDENCIA': 'alterados_com_pendencia', 'ORIGEM_ALTERADA': 'origem_alterada', 'SEM_ALTERACAO': 'sem_alteracao'}
METRICS = ('recebidas', 'aprovadas', 'excluidas', 'valores_nao_quantificaveis', 'receitas_centavos', 'gastos_centavos', 'total_recebido_centavos', 'total_aprovado_centavos', 'total_excluido_centavos')


def validate_result(result):
    if not isinstance(result, dict) or not isinstance(result.get('linhas'), list) or not isinstance(result.get('resumo'), dict) or not isinstance(result.get('fontes'), dict):
        raise ValueError('Resultado inválido: informe resultado.json de uma execução, não um manifesto ou uma comparação')
    if 'schema_versao' in result and (type(result['schema_versao']) is not int or result['schema_versao'] != 1):
        raise ValueError('Versão de schema de resultado não suportada')
    period = result.get('competencia', '')
    if not isinstance(period, str) or not re.fullmatch(r'\d{4}-\d{2}', period):
        raise ValueError('Competência inválida no resultado')
    date.fromisoformat(period + '-01')
    catalog = normalize_catalog(result.get('catalogo'))
    rows = result['linhas']
    for row in rows:
        if not isinstance(row, dict) or any(not isinstance(row.get(f), str) for f in (*FIELDS, 'arquivo', 'aba')) or type(row.get('linha')) is not int or row['linha'] < 1:
            raise ValueError('Linha ou localização inválida no resultado')
        if row.get('status') not in ('APROVADO', 'PENDENTE', 'DUPLICADO', 'CONFLITO') or not isinstance(row.get('erros'), list) or any(not isinstance(e, str) for e in row['erros']):
            raise ValueError('Classificação inválida no resultado')
        value = row.get('valor_centavos')
        if value is not None and type(value) is not int:
            raise ValueError('Valores do resultado precisam estar em centavos inteiros ou nulos')
        if row['status'] == 'APROVADO' and (value is None or row['erros'] or row['categoria'] not in catalog['categorias']):
            raise ValueError('Linha aprovada inconsistente no resultado')
    approved = [r for r in rows if r['status'] == 'APROVADO']
    count = Counter(r['status'] for r in rows)
    expected = {
        'arquivos': len(set(result['fontes']) | {r['arquivo'] for r in rows}),
        'recebidas': len(rows), 'aprovadas': len(approved), 'excluidas': len(rows)-len(approved),
        'pendentes': count['PENDENTE'], 'duplicadas': count['DUPLICADO'], 'conflitos': count['CONFLITO'],
        'valores_nao_quantificaveis': sum(r['valor_centavos'] is None for r in rows),
        'total_recebido_centavos': sum(r['valor_centavos'] or 0 for r in rows),
        'total_aprovado_centavos': sum(r['valor_centavos'] for r in approved),
        'total_excluido_centavos': sum(r['valor_centavos'] or 0 for r in rows if r['status'] != 'APROVADO'),
        'receitas_centavos': sum(r['valor_centavos'] for r in approved if catalog['categorias'][r['categoria']]['natureza'] == 'receita'),
        'gastos_centavos': -sum(r['valor_centavos'] for r in approved if catalog['categorias'][r['categoria']]['natureza'] == 'gasto'),
    }
    if any(type(result['resumo'].get(k)) is not int or result['resumo'][k] != v for k, v in expected.items()):
        raise ValueError('Resumo inconsistente com as linhas do resultado; use o arquivo original da execução')
    if type(result.get('liberado')) is not bool:
        raise ValueError('Status de liberação ausente ou inválido')
    if result['liberado'] and (not rows or len(approved) != len(rows) or not isinstance(result.get('conciliacao'), list) or not result['conciliacao'] or any(c.get('status') != 'CONCILIADO' for c in result['conciliacao'])):
        raise ValueError('Liberação inconsistente com as linhas ou os controles')
    return {**result, 'catalogo': catalog}


def _groups(rows):
    groups = defaultdict(list)
    for row in rows:
        key = ('id', row['registro_id']) if row['registro_id'] else ('sem_id', row['arquivo'], row['aba'], row['linha'])
        groups[key].append(row)
    return groups


def _business(row):
    fields = tuple(row[f] if f != 'valor_brl' else row['valor_centavos'] if row['valor_centavos'] is not None else row['valor_brl'] for f in FIELDS)
    return (*fields, row['status'], tuple(sorted(set(row['erros']))))


def _locations(rows):
    return Counter((_business(r), r['arquivo'], r['aba'], r['linha']) for r in rows)


def _approved_total(rows):
    return sum(r['valor_centavos'] for r in rows if r['status'] == 'APROVADO')


def compare_results(before, after):
    before, after = validate_result(before), validate_result(after)
    old, new = _groups(before['linhas']), _groups(after['linhas'])
    groups = []
    for key in sorted(set(old) | set(new), key=repr):
        left, right = old.get(key, []), new.get(key, [])
        if not left:
            kind = 'ADICIONADO'
        elif not right:
            kind = 'REMOVIDO'
        elif Counter(_business(r) for r in left) == Counter(_business(r) for r in right):
            kind = 'SEM_ALTERACAO' if _locations(left) == _locations(right) else 'ORIGEM_ALTERADA'
        elif any(r['status'] != 'APROVADO' for r in left) and all(r['status'] == 'APROVADO' for r in right):
            kind = 'PENDENCIA_RESOLVIDA'
        elif all(r['status'] == 'APROVADO' for r in left) and any(r['status'] != 'APROVADO' for r in right):
            kind = 'NOVA_PENDENCIA'
        else:
            kind = 'ALTERADO_COM_PENDENCIA' if any(r['status'] != 'APROVADO' for r in right) else 'ALTERADO'
        def value(row, field):
            return row['valor_centavos'] if field == 'valor_brl' and row['valor_centavos'] is not None else row[field]
        # A removed duplicate changes row count, not every repeated field value.
        # Equal-sized groups retain multiplicity checks; different-sized groups
        # compare distinct values and expose the count change separately.
        collect = Counter if len(left) == len(right) else set
        changed = [field for field in (*FIELDS, 'status') if collect(value(r, field) for r in left) != collect(value(r, field) for r in right)] if left and right else []
        if left and right and len(left) != len(right):
            changed.append('quantidade_linhas')
        groups.append({'registro_id': key[1] if key[0] == 'id' else '', 'referencia_sem_id': ' · '.join(map(str, key[1:])) if key[0] == 'sem_id' else '', 'tipo': kind, 'campos_alterados': changed, 'antes': left, 'depois': right, 'aprovado_antes_centavos': _approved_total(left), 'aprovado_depois_centavos': _approved_total(right)})
    counts = Counter(g['tipo'] for g in groups)
    warnings = []
    if before['competencia'] != after['competencia']:
        warnings.append({'codigo': 'COMPETENCIAS_DIFERENTES', 'mensagem': 'Os períodos são diferentes; mudanças não devem ser interpretadas automaticamente como correções.'})
    def rules(result):
        return {'catalogo': result['catalogo'], 'perfil': result.get('perfil_entrada')}
    if fingerprint(rules(before)) != fingerprint(rules(after)):
        warnings.append({'codigo': 'CONFIGURACOES_DIFERENTES', 'mensagem': 'Catálogo ou perfil diferem, ou não foram registrados em um dos arquivos. Avalie o efeito das regras antes de interpretar as diferenças.'})
    if not before.get('execucao') or not after.get('execucao'):
        warnings.append({'codigo': 'IDENTIFICACAO_AUSENTE', 'mensagem': 'Um resultado não tem identificação de execução. A comparação usa o conteúdo fornecido e não comprova sua autenticidade.'})
    changed_sources = [name for name in sorted(set(before['fontes']) | set(after['fontes'])) if before['fontes'].get(name) != after['fontes'].get(name)]
    return {'schema_versao': 1, 'tipo_documento': 'comparacao', 'competencia_antes': before['competencia'], 'competencia_depois': after['competencia'], 'execucao_antes': before.get('execucao'), 'execucao_depois': after.get('execucao'), 'liberado_antes': before['liberado'], 'liberado_depois': after['liberado'], 'avisos': warnings, 'fontes_alteradas': changed_sources,
            'resumo': {'grupos': len(groups), **{label: counts[kind] for kind, label in TYPES.items()}},
            'metricas': {key: {'antes': before['resumo'][key], 'depois': after['resumo'][key], 'diferenca': after['resumo'][key]-before['resumo'][key]} for key in METRICS}, 'grupos': groups}


def write_comparison(comparison, output):
    from .export import _csv
    from .comparison_report import render_comparison
    target = Path(output)
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ValueError('Escolha uma pasta de comparação vazia; arquivos existentes foram preservados')
    target.mkdir(parents=True, exist_ok=True)
    (target / 'comparacao.json').write_text(json.dumps(comparison, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    def origin(rows):
        return ' | '.join(f"{r['arquivo']} / {r['aba']} / linha {r['linha']}" for r in rows)
    headers = ['registro_id', 'referencia_sem_id', 'tipo', 'linhas_antes', 'linhas_depois', 'aprovado_antes_brl', 'aprovado_depois_brl', 'origens_antes', 'origens_depois', 'campos_alterados']
    values = [[g['registro_id'], g['referencia_sem_id'], g['tipo'], len(g['antes']), len(g['depois']), money(g['aprovado_antes_centavos']), money(g['aprovado_depois_centavos']), origin(g['antes']), origin(g['depois']), ', '.join(g['campos_alterados'])] for g in comparison['grupos']]
    _csv(target / 'comparacao.csv', headers, values)
    render_comparison(comparison, target / 'comparacao.html')
    return target
