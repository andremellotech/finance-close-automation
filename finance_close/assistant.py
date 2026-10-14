"""Assistente local para preparar configuração sem inferir controles esperados."""
import csv
import json
from pathlib import Path
import re
from .configuration import FIELDS, normalize_catalog, normalize_profile


def setup_project(output, ask=input):
    target = Path(output)
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ValueError('Escolha uma pasta de configuração vazia; arquivos existentes foram preservados')

    def question(label, default, valid=lambda value: bool(value)):
        while True:
            try:
                value = ask(f'{label} [{default}]: ').strip() or str(default)
            except EOFError as exc:
                raise ValueError('Assistente interrompido: faltaram respostas; nenhuma configuração foi gravada') from exc
            if valid(value):
                return value
            print('Resposta inválida. Confira as opções e tente novamente.')

    def count(label, default):
        return int(question(label, default, lambda v: v.isdecimal() and 1 <= int(v) <= 100))

    def code(label, default, existing):
        return question(label, default, lambda v: re.fullmatch(r'[\w-]{1,40}', v) is not None and v not in existing)

    name = question('Nome do projeto', 'Meu fechamento')
    brazilian = question('Formato: 1=ISO/ponto decimal; 2=brasileiro', '2', lambda v: v in ('1', '2')) == '2'
    delimiter = question('Separador CSV: 1=ponto e vírgula; 2=vírgula; 3=tabulação', '1', lambda v: v in ('1', '2', '3'))
    sheet = question('Nome da aba Excel', 'Dados' if brazilian else 'Lancamentos')
    defaults = ['ID', 'Data', 'Centro', 'Conta', 'Descrição', 'Valor'] if brazilian else list(FIELDS)
    columns = {field: question('Cabeçalho de ' + field, default) for field, default in zip(FIELDS, defaults)}
    centers = {}
    for index in range(count('Quantidade de centros de custo', '1')):
        key = code('Código do centro', 'GERAL' if index == 0 else f'CC{index+1:02}', centers)
        centers[key] = question('Nome do centro', 'Área geral' if index == 0 else key)
    categories = {}
    for index in range(count('Quantidade de categorias', '2')):
        key = code('Código da categoria', 'REC' if index == 0 else 'DESP' if index == 1 else f'CAT{index+1:02}', categories)
        label = question('Nome da categoria', 'Receitas' if index == 0 else 'Gastos')
        nature = question('Natureza: 1=receita; 2=gasto', '1' if index == 0 else '2', lambda v: v in ('1', '2'))
        sign = question('Sinal: 1=não negativo; 2=não positivo; 3=livre', nature, lambda v: v in ('1', '2', '3'))
        categories[key] = {'nome': label, 'natureza': {'1': 'receita', '2': 'gasto'}[nature], 'sinal': {'1': 'nao_negativo', '2': 'nao_positivo', '3': 'livre'}[sign]}
    required = ['registro_id', 'data_competencia', 'categoria', 'valor_brl']
    for field, default in [('descricao', 'n'), ('centro_custo', 's')]:
        if question(field + ' obrigatório? s/n', default, lambda v: v in ('s', 'n')) == 's':
            required.append(field)
    profile = normalize_profile({'nome': name, 'entrada': {'separador': {'1': ';', '2': ',', '3': '\t'}[delimiter], 'aba': sheet, 'colunas': columns, 'formato_data': 'br' if brazilian else 'iso', 'decimal': ',' if brazilian else '.', 'milhar': '.' if brazilian else '', 'permitir_colunas_extras': False}})
    catalog = normalize_catalog({'centros': centers, 'categorias': categories, 'obrigatorios': required})
    target.mkdir(parents=True, exist_ok=True)
    if any(target.iterdir()):
        raise ValueError('A pasta deixou de estar vazia; nenhuma configuração será substituída')
    for filename, content in [('perfil.json', profile), ('catalogo.json', catalog)]:
        (target / filename).write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding='utf-8')
    with (target / 'controle.csv').open('w', encoding='utf-8', newline='') as stream:
        csv.writer(stream, delimiter=';').writerow(['arquivo', 'linhas_esperadas', 'total_esperado_brl'])
    (target / 'COMO-USAR.md').write_text('''# Sua configuração

Preencha controle.csv com quantidade e total obtidos de uma conferência independente, um arquivo por linha. Use ponto decimal. O assistente não calcula o controle a partir da entrada.

Na raiz do projeto, substitua SUA_PASTA, SUA_CONFIG e AAAA-MM nos comandos:

```bash
python -m finance_close check --input SUA_PASTA --controls SUA_CONFIG/controle.csv --catalog SUA_CONFIG/catalogo.json --profile SUA_CONFIG/perfil.json --period AAAA-MM
python -m finance_close run --input SUA_PASTA --controls SUA_CONFIG/controle.csv --catalog SUA_CONFIG/catalogo.json --profile SUA_CONFIG/perfil.json --period AAAA-MM --output local-output/nova-execucao
```

Escolha uma saída vazia, fora da entrada. Abra relatorio.html na saída e confira pendências e controles. Para detalhes, veja docs/operations-guide.md e docs/adaptation-guide.md no projeto. Mantenha seus dados reais fora do repositório público.
''', encoding='utf-8')
    return target
