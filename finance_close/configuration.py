"""Contratos explícitos de catálogo e formato de entrada, sem inferência."""
from copy import deepcopy
from datetime import date, datetime
import json
from pathlib import Path
import re

FIELDS = ('registro_id', 'data_competencia', 'centro_custo', 'categoria', 'descricao', 'valor_brl')
CORE = {'registro_id', 'data_competencia', 'categoria', 'valor_brl'}
DEFAULT_PROFILE = {'nome': 'Fechamento mensal', 'entrada': {
    'separador': ';', 'aba': 'Lancamentos', 'colunas': {field: field for field in FIELDS},
    'formato_data': 'iso', 'decimal': '.', 'milhar': '', 'permitir_colunas_extras': False}}


def normalize_catalog(catalog):
    if not isinstance(catalog, dict) or set(catalog) - {'centros', 'categorias', 'obrigatorios'}:
        raise ValueError('Catálogo inválido ou com opções desconhecidas')
    centers, categories = catalog.get('centros'), catalog.get('categorias')
    if not isinstance(centers, dict) or not isinstance(categories, dict) or not categories:
        raise ValueError('Catálogo precisa de centros e categorias; informe ao menos uma categoria')
    if any(not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip() for k, v in centers.items()):
        raise ValueError('Centros devem associar códigos a nomes não vazios')
    normalized = {}
    for code, rule in categories.items():
        if not isinstance(code, str) or not re.fullmatch(r'[\w-]{1,40}', code):
            raise ValueError('Código de categoria deve ter letras, números, hífen ou sublinhado')
        if isinstance(rule, str):
            # Compatibility with v1.0 catalogs only; new catalogs declare the nature.
            rule = {'nome': rule, 'natureza': 'receita' if code == 'REV' else 'gasto', 'sinal': 'nao_negativo' if code == 'REV' else 'nao_positivo'}
        if not isinstance(rule, dict) or set(rule) != {'nome', 'natureza', 'sinal'} or not isinstance(rule.get('nome'), str) or not rule['nome'].strip():
            raise ValueError('Cada categoria precisa de nome, natureza e sinal')
        if rule['natureza'] not in ('receita', 'gasto') or rule['sinal'] not in ('nao_negativo', 'nao_positivo', 'livre'):
            raise ValueError('Natureza ou sinal de categoria inválido')
        normalized[code] = dict(rule)
    required = catalog.get('obrigatorios', list(FIELDS))
    if not isinstance(required, list) or any(not isinstance(f, str) for f in required) or len(set(required)) != len(required) or not CORE <= set(required) or not set(required) <= set(FIELDS):
        raise ValueError('Campos obrigatórios inválidos: ID, data, categoria e valor são estruturais')
    return {'centros': dict(centers), 'categorias': normalized, 'obrigatorios': list(required)}


def normalize_profile(profile=None):
    if profile is None:
        return deepcopy(DEFAULT_PROFILE)
    if not isinstance(profile, dict) or set(profile) - {'nome', 'entrada'}:
        raise ValueError('Perfil inválido ou com opções desconhecidas')
    result = deepcopy(DEFAULT_PROFILE)
    result['nome'] = profile.get('nome', result['nome'])
    if not isinstance(result['nome'], str) or not result['nome'].strip():
        raise ValueError('Nome do projeto precisa ser um texto não vazio')
    options = profile.get('entrada', {})
    if not isinstance(options, dict) or set(options) - set(result['entrada']):
        raise ValueError('Opções de entrada desconhecidas no perfil')
    result['entrada'].update(options)
    opt = result['entrada']
    columns = opt['colunas']
    if not isinstance(columns, dict) or set(columns) != set(FIELDS) or any(not isinstance(v, str) or not v.strip() for v in columns.values()) or len(set(columns.values())) != len(FIELDS):
        raise ValueError('Mapeamento de colunas inválido: seis campos com nomes de origem distintos')
    if opt['separador'] not in (';', ',', '\t') or opt['decimal'] not in ('.', ',') or opt['milhar'] not in ('', '.', ',') or opt['decimal'] == opt['milhar']:
        raise ValueError('Separador ou formato numérico inválido no perfil')
    if opt['formato_data'] not in ('iso', 'br') or type(opt['permitir_colunas_extras']) is not bool or not isinstance(opt['aba'], str) or not opt['aba'].strip():
        raise ValueError('Formato de data, aba ou opção de colunas extras inválida')
    return result


def load_profile(path=None):
    return normalize_profile(json.loads(Path(path).read_text(encoding='utf-8')) if path else None)


def normalize_record(record, options):
    values = {field: record[column] for field, column in options['colunas'].items()}
    origin = {field: value.isoformat() if isinstance(value, (date, datetime)) else str(value) if value is not None else '' for field, value in values.items()}
    errors = []
    raw_date = values['data_competencia']
    if isinstance(raw_date, str) and raw_date.strip():
        raw_date = raw_date.strip()
        pattern, date_format = (r'\d{4}-\d{2}-\d{2}', '%Y-%m-%d') if options['formato_data'] == 'iso' else (r'\d{2}/\d{2}/\d{4}', '%d/%m/%Y')
        try:
            if not re.fullmatch(pattern, raw_date):
                raise ValueError()
            values['data_competencia'] = datetime.strptime(raw_date, date_format).date().isoformat()
        except ValueError:
            errors.append('DATA_FORMATO_INVALIDO')
    raw_amount = values['valor_brl']
    invalid_amount = False
    if isinstance(raw_amount, str) and raw_amount.strip():
        raw_amount = raw_amount.strip()
        group = re.escape(options['milhar'])
        integer = rf'(?:[0-9]+|[0-9]{{1,3}}(?:{group}[0-9]{{3}})+)' if group else r'[0-9]+'
        pattern = rf'-?{integer}(?:{re.escape(options["decimal"])}[0-9]{{1,2}})?'
        if re.fullmatch(pattern, raw_amount):
            values['valor_brl'] = raw_amount.replace(options['milhar'], '') if group else raw_amount
            values['valor_brl'] = values['valor_brl'].replace(options['decimal'], '.')
        else:
            invalid_amount = True
    elif isinstance(raw_amount, (int, float)) and not isinstance(raw_amount, bool):
        values['valor_brl'] = str(raw_amount)
    return {**values, 'campos_origem': origin, '_input_errors': errors, '_valor_formato_invalido': invalid_amount}
