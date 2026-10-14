# Como usar

## 1. Conhecer a demonstração

Extraia o ZIP e abra `index.html`. A página funciona localmente, sem servidor ou biblioteca externa. No GitHub, HTML é exibido como código; para interação online, use o site publicado pelo Pages.

Alterne **Com pendências** e **Validado**. Visão geral resume o lote; Pendências mostra as linhas para revisão e **Como revisar**; Conciliação compara recebimento e controle; Rastreabilidade conserva todas as origens e os hashes. Pesquise ID, arquivo ou motivo e filtre classificação e centro de custo. **Exportar seleção CSV** respeita os filtros; os indicadores continuam mostrando o lote inteiro. **Baixar Excel** entrega a conferência completa do exemplo selecionado. Expanda **Identificação da execução** para consultar o ID e baixar o manifesto.

O [roteiro operacional completo](operations-guide.md) inclui assistente de configuração, pré-conferência sem exportação, orientações, identificação e comparação entre revisões. A [comparação de exemplo](../examples/comparacao/comparacao.html) já está pronta para explorar.

## 2. Executar a automação no computador

Com Python 3.11+ instalado, abra um terminal na pasta do projeto:

```bash
python -m pip install -r requirements.txt
python -m finance_close check --input sample-input/validado --controls config/controle.csv --period 2025-09
python -m finance_close run --input sample-input/validado --controls config/controle.csv --period 2025-09 --output local-output/validado-primeira-execucao
```

Use uma pasta de saída vazia. A rotina não substitui arquivos existentes por padrão e não permite saída dentro da entrada. Abra o Excel e os CSVs criados na pasta informada.

Cada execução também cria `relatorio.html`, com o período e os dados efetivamente processados. Abra-o no navegador; mantenha o Excel ao lado para seu botão de download. Não é necessário publicar o relatório para utilizá-lo.

Para o lote problemático:

```bash
python -m finance_close run --input sample-input/com-pendencias --controls config/controle.csv --period 2025-09 --output local-output/pendencias-primeira-execucao
```

O retorno 2 é esperado nesse exemplo e significa que os relatórios foram gerados com pendências. O retorno 0 indica lote validado; 1 significa erro de configuração/leitura e exige corrigir a mensagem antes de confiar na execução.

## 3. Revisar os problemas

| Problema demonstrado | Ação na origem |
|---|---|
| Centro XYZ | Conferir o cadastro correto do lançamento; no exemplo corrigido é ANA |
| ID ausente | Identificar o lançamento e preencher seu ID correto |
| Valor inválido | Consultar a fonte e preencher um valor numérico no contrato esperado |
| Competência diferente | Confirmar qual mês o lançamento pertence; não alterar o mês apenas para passar na regra |
| Repetição exata | Conferir se o envio foi duplicado e remover a repetição na origem |
| Mesmo ID com campos diferentes | Resolver o conflito na fonte antes de escolher uma versão |

Atualize o controle somente quando a origem correta tiver sido conferida. O objetivo não é fazer os números coincidirem artificialmente. Execute de novo para outra pasta de saída e use `compare` com os dois `resultado.json`, conforme o [guia operacional](operations-guide.md#5-comparar-duas-revisões). O exemplo **Validado** já contém o lote de referência sem os problemas inseridos.

## 4. Usar seus próprios arquivos

Comece com `python -m finance_close setup --output local-config/meu-projeto` para criar suas configurações por perguntas. Prepare CSV/XLSX numa pasta separada conforme o [dicionário](data-dictionary.md), confira seu catálogo e preencha o controle independente. Passe os caminhos em `--input`, `--controls`, `--catalog` e `--profile`, primeiro em `check` e depois em `run`. Mantenha IDs únicos no lote. A rotina aceita arquivos diretamente nessa pasta, sem busca recursiva em subpastas.

Para outros nomes de colunas, datas brasileiras, vírgula decimal e regras financeiras, use `--profile` e siga **[Crie seu próprio projeto](adaptation-guide.md)**. O [starter](../starter/LEIA-ME.md) fornece entrada, perfil, catálogo, controle e valores esperados. Sem perfil, o contrato original permanece disponível.

O controle esperado deve ser obtido independentemente da fonte responsável. Nos exemplos fictícios ele está previamente definido. Sem um controle independente, a rotina só teria um total calculado, não uma comparação com a origem.

O CSV aprovado pode ser importado no Power BI com separador `;`, codificação UTF-8 e interpretação do ponto decimal. Ele contém lançamentos detalhados com origem; não substitui automaticamente a base e as regras de outro relatório.

## 5. Recriar exemplos e testar

```bash
python -m finance_close demo
python -m unittest discover -s tests -v
```

`demo` restaura os exemplos fictícios e recria `examples/` e `index.html`. Ele não é o comando de processamento dos seus arquivos. O código da página está em `web/`; após uma alteração visual, rode `demo` para renovar o HTML autocontido.

O exemplo `examples/adaptado` foi executado pelo comando do starter. Para repeti-lo, use o comando da seção de adaptação com uma pasta de saída vazia. Alterações em `web/` também são usadas nos novos HTMLs gerados por `run`.

## 6. Publicar e apresentar

Siga o [guia para publicação pela web](publish-guide.md). Compartilhe a URL do Pages com quem quer explorar a demonstração. O repositório conserva o código, os exemplos e a documentação para quem quer reproduzir a rotina.
