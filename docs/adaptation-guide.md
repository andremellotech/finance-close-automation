# Crie seu próprio projeto

O objetivo deste roteiro é adaptar a rotina e conseguir explicar o resultado. Primeiro reproduza um exemplo conhecido; depois use uma cópia local com seus próprios arquivos.

## 1. Prepare uma cópia e o ambiente

Extraia o ZIP inteiro, preservando as pastas. Abra um terminal na pasta que contém `README.md` e `finance_close/`. No Windows:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nos comandos abaixo, substitua `python` por `.venv\Scripts\python.exe` para usar esse ambiente. Não é necessário ativar scripts no PowerShell. Python 3.11 ou posterior deve estar instalado.

Mantenha entradas e resultados de uso próprio em uma pasta local separada do repositório público. Os arquivos deste pacote são fictícios; isso não se aplica automaticamente aos arquivos que você acrescentar.

## 2. Reproduza a primeira adaptação

```bash
python -m finance_close run --input starter/entrada --controls starter/controle.csv --catalog starter/catalogo.json --profile starter/perfil.json --period 2026-02 --output local-output/primeira-adaptacao
```

Abra `relatorio.html` dentro da pasta de saída. A execução deve retornar **0**, com 2 aprovadas, nenhuma excluída, receitas de **1.250,50**, gastos de **250,50** e resultado de **1.000,00 BRL**. O arquivo deve conciliar e a diferença da ponte deve ser zero. Compare com o [exemplo já executado](../examples/adaptado/relatorio.html).

## 3. Escolha as regras do seu caso

Se preferir começar com perguntas, execute `python -m finance_close setup --output local-config/meu-projeto`. O assistente cria perfil, catálogo e um controle sem valores, além de instruções. As seções seguintes explicam as mesmas configurações para conferência ou edição manual. Veja o [roteiro operacional](operations-guide.md).

Copie `starter/catalogo.json` para sua pasta local e edite centros e categorias. Cada categoria possui:

| Opção | Valores | Efeito |
|---|---|---|
| `nome` | Texto | Descreve a categoria |
| `natureza` | `receita` ou `gasto` | Define onde ela entra no resumo financeiro e nas fórmulas Excel |
| `sinal` | `nao_negativo`, `nao_positivo` ou `livre` | Aceita respectivamente ≥ 0, ≤ 0 ou ambos os sinais |

Exemplo: `FAT` pode ser receita e `CUS` pode ser gasto; os códigos não precisam ser `REV` e `DIR`. Use letras, números, hífen ou sublinhado nos códigos. Para um estorno, só use `livre` quando isso representar a convenção definida para aquela categoria.

`obrigatorios` contém os campos cujo conteúdo não pode ficar vazio. ID, data, categoria e valor são estruturais e não podem ser desabilitados. Centro e descrição podem ser opcionais; um centro preenchido ainda precisa existir no cadastro. As seis colunas continuam necessárias. Nomes/valores desconhecidos na configuração são rejeitados.

O resultado é soma de receitas menos gastos líquidos; os gastos são exibidos com o sinal da origem invertido. Um estorno pode reduzir os gastos, inclusive tornar seu total negativo. A regra não determina automaticamente se um lançamento contábil é correto.

## 4. Mapeie os nomes e formatos de entrada

Copie `starter/perfil.json`. Em `nome`, coloque o nome usado no título do relatório. Em `entrada.colunas`, a chave é fixa e o valor é o cabeçalho do seu arquivo:

| Campo interno | Exemplo de cabeçalho |
|---|---|
| `registro_id` | `ID` |
| `data_competencia` | `Data` |
| `centro_custo` | `Centro` |
| `categoria` | `Conta` |
| `descricao` | `Descrição` |
| `valor_brl` | `Valor` |

Cada nome de origem deve ser distinto, respeitando espaços, maiúsculas e acentos. Os arquivos de um lote usam o mesmo perfil. Se suas áreas usam formatos diferentes, padronize-os antes de reunir o lote.

| Opção de entrada | Como escolher |
|---|---|
| `separador` | `;`, `,` ou `\t` para CSV UTF-8 |
| `aba` | Nome exato da aba XLSX, com cabeçalho na primeira linha |
| `formato_data` | `br` para DD/MM/AAAA ou `iso` para AAAA-MM-DD |
| `decimal` | `,` ou `.` |
| `milhar` | `.`, `,` ou texto vazio; deve ser diferente do decimal |
| `permitir_colunas_extras` | `false` rejeita colunas extras; `true` ignora as extras, preservando a exigência das seis mapeadas |

O perfil brasileiro aceita `1.250,50` e `1250,50`. Separadores de milhar precisam formar grupos de três dígitos. Não há adivinhação de formato. Uma data ou um número com formato incompatível vira pendência; um valor não quantificável deixa a conciliação incompleta. Datas e números tipados no Excel são aceitos sem reinterpretar a formatação visual da célula. Fórmulas e erros de célula continuam impedindo aprovação.

Sem `--profile`, permanece o contrato original: cabeçalhos internos, aba `Lancamentos`, CSV `;`, data ISO e ponto decimal. Não edite os arquivos Python para trocar as regras descritas neste guia.

## 5. Prepare um controle independente

O CSV de controle mantém o formato técnico `arquivo;linhas_esperadas;total_esperado_brl`, com ponto decimal. O perfil de entrada não altera o controle. Cada arquivo deve ter uma linha de controle com o nome e a extensão exatos.

Obtenha quantidade e total de uma conferência independente da fonte responsável. O controle é do **recebido antes das exclusões**. Não ajuste o controle apenas para coincidir com o total calculado pelo programa.

## 6. Execute e confira

Faça primeiro a pré-conferência, usando os caminhos do seu projeto:

```bash
python -m finance_close check --input starter/entrada --controls starter/controle.csv --catalog starter/catalogo.json --profile starter/perfil.json --period 2026-02
```

`check` não exporta arquivos. Ele reúne problemas de leitura e dados com orientações; erro de leitura impede considerar a preparação pronta. `run` repete as validações ao processar os arquivos.

Passe os caminhos locais de sua entrada, controle, catálogo e perfil ao comando `run`; informe `--period AAAA-MM`. Escolha uma pasta de saída vazia, fora da entrada. Para repetir, use uma nova pasta, por exemplo `local-output/revisao-02`.

| Conferência | O que precisa ser explicado |
|---|---|
| Quantidades | Recebidas = aprovadas + excluídas; nenhuma linha deve desaparecer |
| Pendências | Motivo, arquivo, aba e linha de cada exclusão |
| Duplicatas/conflitos | Confirmar na origem qual envio ou registro está correto |
| Conciliação | Quantidades e valores recebidos comparados com controles independentes |
| Valores desconhecidos | Contador separado; o total quantificável não representa o total completo |
| Ponte | Recebido quantificável = aprovado + excluído quantificável |
| Resumo financeiro | Receitas e gastos das linhas aprovadas conforme o catálogo |

**Retornos:** 0 = validado pelas regras; 2 = relatórios gerados com pendências; 1 = erro de leitura/configuração/exportação. Com retorno 1, uma pasta parcial pode existir; corrija a causa e use outra saída vazia. Nunca considere apenas a existência de um arquivo como sucesso.

O HTML, o Excel, os CSVs e o JSON representam a mesma execução. O HTML funciona offline com CSS, JavaScript e dados internos; mantenha o Excel ao lado para o botão de download funcionar. O JSON conserva o perfil utilizado, o catálogo efetivo, os valores normalizados, os campos de origem e hashes dos arquivos. Não há envio de dados a um serviço remoto pelo processamento.

Na versão 1.2, `execucao.json` registra a identificação e as configurações efetivas; o HTML mostra esse mesmo ID. A coluna `acao_sugerida` orienta a revisão das pendências. Depois de corrigir a origem e executar em nova pasta, compare os dois resultados com `compare`; consulte o [guia operacional](operations-guide.md#5-comparar-duas-revisões) para não confundir remoção, troca de ID e correção.

**Validado pelas regras não equivale a fechamento de negócio aprovado.** O responsável ainda deve conferir a origem, os controles e se as convenções representam o caso. Uma ponte que fecha, sozinha, não prova que os dados recebidos estão corretos.

## 7. Mantenha e personalize a cópia

Execute `python -m unittest discover -s tests -v` depois de alterar código. Acrescente um teste com valores conhecidos do seu novo caso: por exemplo, receita 100 e custo −30 precisam resultar em 70. Confira o relatório com uma soma independente. Os testes existentes não homologam automaticamente novas regras de negócio.

Para personalizar a apresentação, edite títulos e links em `web/template.html`, estilos em `web/style.css` e componentes em `web/app.js`. Uma nova execução já usa esses arquivos. `python -m finance_close demo` restaura os dois exemplos fictícios originais e a página pública; não cria a página a partir dos seus próprios dados. Para isso, abra o `relatorio.html` da sua execução.

Para publicar, use o [guia web](publish-guide.md). Revise os arquivos escolhidos para publicação: HTML e Excel contêm os dados processados. Conserve apenas exemplos autorizados e fictícios no portfólio público.
