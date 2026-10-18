# Finance Close Automation

**Do arquivo recebido à base aprovada: uma rotina de fechamento mensal com qualidade, conciliação e rastreabilidade.**

![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB)
![pandas](https://img.shields.io/badge/pandas-150458)
![Dados fictícios](https://img.shields.io/badge/dados-fict%C3%ADcios-lightgrey)

Projeto de portfólio de [André Mello](https://github.com/andremellotech), com Python, pandas e Excel. Todos os dados são fictícios.

[**Abrir demonstração**](https://andremellotech.github.io/finance-close-automation/) · [**Comparar os lotes**](https://andremellotech.github.io/finance-close-automation/examples/comparacao/comparacao.html) · [Como usar](docs/user-guide.md) · [Configurar e adaptar](docs/operations-guide.md)

![Demonstração do fechamento mensal](docs/images/preview-desktop.jpg)

> **Dica:** na aba *Code* do GitHub, arquivos HTML aparecem como código. Use **Abrir demonstração** para interagir (disponível após ativar o GitHub Pages) ou baixe o projeto, extraia e abra `index.html` offline.

## Sumário

- [O problema](#o-problema)
- [Início rápido](#início-rápido)
- [Dois exemplos executados pela mesma rotina](#dois-exemplos-executados-pela-mesma-rotina)
- [O que sai da execução](#o-que-sai-da-execução)
- [Comandos e códigos de saída](#comandos-e-códigos-de-saída)
- [Use como base para outro projeto](#use-como-base-para-outro-projeto)
- [Compare duas revisões](#compare-duas-revisões)
- [Regras que tornam o resultado conferível](#regras-que-tornam-o-resultado-conferível)
- [Estrutura](#estrutura)
- [Limites desta versão](#limites-desta-versão)
- [Novidades da versão 1.2](#novidades-da-versão-12)
- [Contribuir, autor e licença](#contribuir-autor-e-licença)

## O problema

Uma pasta com planilhas e CSVs pode reunir períodos diferentes, registros repetidos e cadastros inconsistentes. Somar tudo sem conferir essas condições produz uma consolidação difícil de explicar.

Este projeto importa os lançamentos de três áreas fictícias, classifica cada linha, compara os arquivos com controles de origem e exporta uma base aprovada. A lista de pendências conserva o motivo e a linha que precisa de revisão.

**Fluxo:** configurar → conferir a preparação → processar e conciliar → revisar orientações → comparar revisões.

## Início rápido

Requer Python 3.11 ou posterior. Abra o terminal na pasta extraída do projeto:

```bash
# 1. Instalar dependências
python -m pip install -r requirements.txt

# 2. Conferir a preparação (não exporta relatórios)
python -m finance_close check --input sample-input/validado --controls config/controle.csv --period 2025-09

# 3. Processar, conciliar e exportar
python -m finance_close run --input sample-input/validado --controls config/controle.csv --period 2025-09 --output local-output/meu-fechamento
```

Abra `local-output/meu-fechamento/relatorio.html` para ver o resultado.

- Use uma pasta de saída **vazia e fora da entrada**. As fontes são preservadas.
- Para experimentar o lote com problemas, troque `sample-input/validado` por `sample-input/com-pendencias` e use outra pasta de saída.
- Para recriar os exemplos originais e a página, e rodar os testes:

```bash
python -m finance_close demo
python -m unittest discover -s tests -v
```

`demo` restaura os dados fictícios e os relatórios demonstrativos. Para seus próprios arquivos, use `run` com uma pasta separada e seu próprio controle.

## Dois exemplos executados pela mesma rotina

| Resultado | Com pendências | Validado |
|---|---:|---:|
| Arquivos | 3 | 3 |
| Linhas recebidas | 21 | 18 |
| Aprovadas | 14 | 18 |
| Pendências de validação | 4 | 0 |
| Duplicatas excluídas | 1 | 0 |
| Linhas em conflito de ID | 2 | 0 |
| Resultado da base aprovada | R$ 48.000,00, parcial | R$ 145.000,00 |
| Liberação pelas regras demonstrativas | Pendente | Validado |

No primeiro lote há centro de custo desconhecido, campo obrigatório vazio, valor inválido, competência diferente, repetição exata e ID conflitante. Os totais foram calculados a partir dos arquivos de exemplo.

> O valor parcial não representa um resultado financeiro fechado, nem uma comparação de performance com o lote validado.

## O que sai da execução

| Arquivo | Uso |
|---|---|
| `base_aprovada.csv` | Linhas aceitas, com origem, prontas para importação em ferramenta de análise |
| `pendencias.csv` | Linhas excluídas, classificação, motivos e ação sugerida |
| `conciliacao.csv` | Quantidades e totais recebidos versus controles |
| `rastreabilidade.csv` | Todas as linhas, com arquivo, aba, linha e SHA-256 da fonte |
| `resultado.json` | Mesmo resultado estruturado, com valores em centavos inteiros |
| `execucao.json` | Manifesto com ID, momento UTC, versões, hashes das regras e fontes |
| `fechamento.xlsx` | Resumo, Base aprovada, Pendencias, Conciliacao e Rastreabilidade |
| `relatorio.html` | Relatório interativo autocontido, com busca, filtros e link para o Excel |

As abas Excel preservam as linhas de detalhe e têm filtros, cabeçalhos congelados e formatos numéricos. O resumo contém fórmulas ligadas à base aprovada e uma ponte de valores recebidos/aprovados/excluídos. Os valores armazenados e os caches das fórmulas são verificados automaticamente; a abertura visual no Microsoft Excel não foi executada nesta entrega.

## Comandos e códigos de saída

| Comando | O que faz |
|---|---|
| `setup` | Assistente por perguntas: cria perfil, catálogo e controle vazio |
| `check` | Diagnóstico de preparação e dados, sem exportar relatórios |
| `run` | Processa, concilia e exporta todos os relatórios |
| `compare` | Mostra o que mudou entre dois resultados |
| `demo` | Restaura os exemplos fictícios e os relatórios demonstrativos |

| Código | Significado |
|---:|---|
| `0` | Validado |
| `2` | Pendências (os relatórios são gerados para revisão) |
| `1` | Erro de leitura ou configuração |

## Use como base para outro projeto

Categorias, natureza financeira, sinais e campos obrigatórios podem ser configurados sem editar o motor. O perfil de entrada mapeia os nomes das seis colunas e define aba, data e separadores numéricos. Para começar com perguntas:

```bash
python -m finance_close setup --output local-config/meu-projeto
```

O assistente gera perfil, catálogo, controle apenas com cabeçalho e um roteiro local. Prepare seus arquivos e preencha o controle independente antes de usar `check` e `run`. O [guia operacional](docs/operations-guide.md) acompanha cada etapa.

Para experimentar a adaptação com cabeçalhos em português e valores brasileiros:

```bash
python -m finance_close run --input starter/entrada --controls starter/controle.csv --catalog starter/catalogo.json --profile starter/perfil.json --period 2026-02 --output local-output/primeira-adaptacao
```

Abra `local-output/primeira-adaptacao/relatorio.html`. O exemplo deve retornar `0`: duas linhas aprovadas, receita de 1.250,50 BRL, gastos de 250,50 BRL e resultado de 1.000,00 BRL. Siga o [guia de adaptação](docs/adaptation-guide.md) para montar seu catálogo, mapear entradas, obter controles independentes e conferir os resultados.

> Os dados usados em sua cópia não devem ser publicados automaticamente.

## Compare duas revisões

```bash
python -m finance_close compare --before examples/com-pendencias/resultado.json --after examples/validado/resultado.json --output local-output/comparacao-exemplo
```

Abra `comparacao.html` na nova pasta. O exemplo contém 19 grupos: 5 com pendência resolvida, 1 ocorrência sem ID removida e 13 sem alteração.

- IDs renomeados não são associados automaticamente; grupos adicionados e removidos ficam explícitos.
- A diferença entre totais aprovados pode refletir populações diferentes e não mede ganho financeiro.

Veja a [comparação online](https://andremellotech.github.io/finance-close-automation/examples/comparacao/comparacao.html) após publicar, ou abra `examples/comparacao/comparacao.html` na cópia extraída. Consulte as [regras de interpretação](docs/operations-guide.md#5-comparar-duas-revisões).

## Regras que tornam o resultado conferível

- **Dinheiro em centavos inteiros.** Validado e somado em centavos. O perfil define os formatos de entrada; CSVs de saída e controle usam ponto decimal e ponto e vírgula.
- **Catálogo.** Define natureza financeira e sinal permitido. Os exemplos originais usam receita não negativa e gastos não positivos.
- **IDs repetidos.** Com os mesmos campos, conservam a primeira ocorrência. Se algum campo difere, todas as versões do ID são excluídas como conflito.
- **Controle.** Refere-se ao arquivo recebido antes das exclusões. A base aprovada é uma população diferente e não precisa repetir o total recebido.
- **Valores não numéricos.** Tornam a conciliação incompleta; a parcela quantificável e a quantidade de valores desconhecidos ficam expostas.
- **Liberação.** O lote só é validado sem exclusões e com todos os controles conciliados. Fontes vazias ou controles ausentes impedem a liberação.

Consulte o [dicionário](docs/data-dictionary.md) e o [guia de uso](docs/user-guide.md) para o contrato completo. Os resultados e os limites da conferência estão no [registro de verificação](docs/verification.md): testes de regras, adaptação, integração e conferência das exportações.

## Estrutura

```text
config/           Catálogo e controles fictícios
starter/          Exemplo inicial de adaptação, perfil e controle
sample-input/     Entradas CSV e Excel dos dois exemplos
finance_close/    Leitura, motor, exportação, CLI e geradores
examples/         Saídas reais dos exemplos
web/              Código da demonstração
docs/             Guias e captura de tela
tests/            Testes de regras e integração
.github/          Validação automática em Windows e Ubuntu
index.html        Demonstração autocontida para abrir ou publicar
```

O repositório mantém os arquivos necessários para reprodução; a demonstração publicada é a entrada para quem deseja apenas explorar o resultado.

## Limites desta versão

- A página pública apresenta exemplos já processados: não executa Python nem recebe arquivos do visitante.
- A rotina local aceita `.csv` e `.xlsx` com seis campos internos; o perfil permite mapear cabeçalhos, aba e formatos.
- Fórmulas na entrada são sinalizadas como pendência.
- Não há conexão com SAP, ERP, banco de dados, fechamento fiscal ou livro contábil.
- As convenções de cada caso precisam ser conferidas pelo responsável; passar nas validações configuradas não significa aprovação do fechamento de negócio.

Não são atribuídas economias de tempo ou ganhos financeiros a uma empresa real. O foco é demonstrar uma rotina testável e explicar o destino de cada registro.

## Novidades da versão 1.2

- **Assistente `setup`:** cria perfil e catálogo por perguntas, com controle vazio para preenchimento independente.
- **Diagnóstico `check`:** reúne problemas de preparação e dados sem exportar relatórios.
- **Como revisar:** cada pendência traz uma ação sugerida no HTML, CSV e Excel.
- **Comparação `compare`:** mostra o que mudou entre dois resultados, com busca e filtros por ID.
- **Identificação:** ID, horário UTC, versões e hashes das configurações e fontes processadas.
- **Validação contínua:** matriz configurada para Windows/Ubuntu e Python 3.11/3.12/3.13; a execução remota depende da publicação.

## Contribuir, autor e licença

**Publicando sua cópia?** Siga o [passo a passo para o GitHub web](docs/publish-guide.md). Para reutilizar ou contribuir, consulte [CONTRIBUTING](CONTRIBUTING.md).

[André Mello no LinkedIn](https://www.linkedin.com/in/aamello/) · [Financial Performance Analytics](https://github.com/andremellotech/financial-performance-analytics)

Código e exemplos fictícios sob [licença MIT](LICENSE).
