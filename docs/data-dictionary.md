# Contrato dos dados

## Lançamentos

CSV: UTF-8 (BOM opcional), separador `;`, cabeçalho na primeira linha. Excel: arquivo `.xlsx`, aba `Lancamentos`, cabeçalho na primeira linha. As seis colunas precisam estar presentes, sem nomes repetidos ou colunas extras.

Este é o contrato **padrão**, mantido quando `--profile` não é informado. Um perfil pode mapear os nomes, escolher outra aba, data `br` ou `iso`, decimal e milhar e permitir colunas extras explícitas. Consulte o [guia de adaptação](adaptation-guide.md). As seis colunas mapeadas continuam necessárias.

| Campo | Regra |
|---|---|
| registro_id | Texto obrigatório e único no lote; espaços nas extremidades são removidos |
| data_competencia | Data AAAA-MM-DD no CSV; data tipada também aceita no Excel; deve pertencer a `--period` |
| centro_custo | Chave do catálogo; os exemplos usam ANA, ENG e OPS |
| categoria | REV, DIR, PES, TEC, COM ou ADM no catálogo dos exemplos |
| descricao | Texto obrigatório |
| valor_brl | Número com ponto decimal e até duas casas; finito; receita ≥ 0 e gasto ≤ 0 |

Valores como `1.250,50`, `R$ 10`, notação científica ou mais de duas casas decimais não são normalizados silenciosamente. Prepare-os no contrato esperado. As somas internas são inteiras em centavos. Zeros são valores válidos.

As convenções de sinal são próprias desta demonstração. O projeto não infere se uma linha é um estorno ou um lançamento fiscal.

O catálogo 1.1 associa cada categoria a `nome`, `natureza` (`receita`/`gasto`) e `sinal` (`nao_negativo`/`nao_positivo`/`livre`). A lista `obrigatorios` pode permitir centro/descrição vazios; ID, data, categoria e valor continuam estruturais. Um centro preenchido deve ser cadastrado. Catálogos antigos de texto continuam aceitos com a convenção legada: REV é receita não negativa e as demais categorias são gastos não positivos. Para novos casos, declare as regras explicitamente.

Na Base aprovada do Excel, a coluna `natureza` registra a classificação resolvida pelo catálogo. As fórmulas do resumo somam essa coluna canônica, evitando confundir códigos como FAT/fat ou 01/1 no recálculo. As saídas são registros da execução; após mudar catálogo ou dados, execute novamente para outra pasta.

## Controles

`config/controle.csv` tem `arquivo`, `linhas_esperadas` e `total_esperado_brl`. O nome é o arquivo da entrada, com extensão. A quantidade é inteira não negativa e o total usa o mesmo formato monetário. Cada arquivo tem exatamente um controle. Controles repetidos ou inválidos são erro de configuração.

O controle considera todas as linhas recebidas, inclusive as que depois são excluídas. Um arquivo pode conciliar e ainda conter linhas inválidas. Um controle de arquivo ausente ou um arquivo sem controle impede liberação.

## Classificações únicas

- **APROVADO:** campos, período, cadastro, sinal e ID atendem às regras.
- **PENDENTE:** uma ou mais validações falharam.
- **DUPLICADO:** repetição exata, excluída após a primeira ocorrência. A ordem é nome do arquivo e linha.
- **CONFLITO:** mesmo ID com campos diferentes. Todas as versões são excluídas.

Conflito tem precedência sobre pendência; uma repetição exata de uma linha já inválida permanece pendente e recebe também o motivo de duplicidade. Cada linha aparece uma vez na rastreabilidade, com todos os motivos aplicáveis.

## Valores e rastreabilidade nas saídas

`resultado.json` usa valores monetários com sufixo `_centavos`. Os CSVs e o Excel exibem BRL. `arquivo`, `aba` e `linha` indicam a origem. Em CSV, linha é a linha física inicial do registro, inclusive com texto entre aspas ocupando várias linhas. O SHA-256 identifica os bytes do arquivo de entrada. Fórmulas Excel e células com erro são preservadas para classificação e não podem aprovar um registro.

O JSON de `run` inclui `perfil_entrada`, o catálogo normalizado e `campos_origem` de cada linha, além dos campos canônicos normalizados. `relatorio.html` incorpora esse mesmo resultado, sem buscar dados em serviços externos. CSVs exportados usam campos normalizados; consulte os campos de origem e o arquivo preservado quando precisar confrontar o formato recebido.

Texto que possa ser interpretado como fórmula é escapado com apóstrofo nos CSVs de saída. No XLSX é escrito como texto. O conteúdo normalizado original continua disponível no JSON; fontes não são modificadas.

Quando um valor não pode ser somado, ele não é tratado como zero válido. O total quantificável e o contador de valores não quantificáveis são apresentados separadamente, e a conciliação fica incompleta.

## Orientações, identificação e comparação (1.2)

Cada linha inclui `orientacoes`: uma lista de objetos `codigo`, `problema` e `acao`, correspondente aos motivos da classificação. A orientação também aparece como `acao_sugerida` no CSV e na aba Pendencias do Excel. Ela não altera nem aprova o lançamento.

`schema_versao: 1` identifica o contrato do resultado. `execucao` contém `id`, `gerado_em_utc`, `versao_aplicacao`, `versao_python` e `configuracoes` com `catalogo_sha256`, `perfil_sha256` e `controle_sha256`. `execucao.json` conserva esses campos, a competência e as fontes. As impressões das configurações representam os valores efetivos normalizados; o SHA das fontes representa os bytes lidos. Não são assinaturas de autenticidade.

`comparacao.json` tem `tipo_documento: comparacao`, competências/identificações antes e depois, avisos, fontes alteradas, métricas e grupos. Cada grupo conserva todas as linhas de `antes`/`depois`, campos alterados, tipo e total aprovado em centavos. IDs preenchidos são chaves exatas; sem ID, a chave é arquivo/aba/linha. A comparação valida consistência entre linhas e resumo, mas não substitui toda a validação de negócio de `run`. Consulte as [classificações e limites](operations-guide.md#5-comparar-duas-revisões).
