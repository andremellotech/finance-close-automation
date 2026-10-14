# Configurar, conferir, executar e comparar

Este roteiro complementa o [guia de adaptação](adaptation-guide.md). Todos os comandos são executados localmente, no terminal aberto na raiz extraída do projeto. Instale primeiro as dependências conforme o guia. Com o ambiente virtual, use `.venv\Scripts\python.exe` no Windows no lugar de `python`.

## 1. Criar a configuração com perguntas

```bash
python -m finance_close setup --output local-config/meu-projeto
```

Pressione Enter para aceitar uma opção sugerida, ou informe sua escolha. O assistente pergunta nome do projeto, formato brasileiro ou ISO, separador CSV, aba Excel, nomes das seis colunas, centros, categorias, natureza, sinal e campos opcionais. Os códigos devem ser distintos dentro de cada cadastro. Para uma nova tentativa, use uma pasta de destino vazia.

São criados `perfil.json`, `catalogo.json`, `controle.csv` e `COMO-USAR.md`. **O controle tem apenas o cabeçalho.** Preencha uma linha por arquivo com quantidade e total esperados obtidos independentemente da origem. Não use a soma que deseja conferir como se fosse um controle independente. O controle usa `;` e ponto decimal, mesmo quando o perfil de entrada é brasileiro.

O assistente prepara as regras informadas; não infere o significado financeiro de contas nem converte seus arquivos. Leia o catálogo criado e confirme que ele representa seu caso. Os padrões REC/DESP do assistente não substituem automaticamente as categorias FAT/CUS do starter.

## 2. Conferir a preparação sem gerar planilhas

Para experimentar com o starter já preenchido:

```bash
python -m finance_close check --input starter/entrada --controls starter/controle.csv --catalog starter/catalogo.json --profile starter/perfil.json --period 2026-02
```

Para seu projeto, troque os quatro caminhos e a competência. `check` confere configuração, cabeçalhos, aba, formatos, campos, cadastros, duplicatas e controles. Erros de diferentes arquivos são mostrados na mesma chamada. Cada problema informa localização, motivo e ação sugerida quando possível. Um arquivo ilegível impede considerar a preparação pronta; contagens parciais não são apresentadas como um lote completo.

Acrescente `--json` para imprimir um diagnóstico estruturado, útil em outra automação. O comando não cria relatórios ou altera os arquivos de entrada. Um erro global de configuração pode impedir parte das verificações; corrija e repita. `run` sempre faz suas próprias validações, pois os arquivos podem mudar depois de `check`.

## 3. Processar e revisar as orientações

```bash
python -m finance_close run --input starter/entrada --controls starter/controle.csv --catalog starter/catalogo.json --profile starter/perfil.json --period 2026-02 --output local-output/revisao-01
```

Abra `local-output/revisao-01/relatorio.html`. Pendências e Rastreabilidade mostram o motivo e **Como revisar**, com arquivo, aba e linha. As ações também aparecem em `pendencias.csv` e na aba Pendencias do Excel, na coluna `acao_sugerida`.

Uma orientação pede conferência; não altera dados ou escolhe automaticamente uma versão conflitante. Corrija os arquivos de origem em sua cópia local, confira os controles com o responsável e execute outra vez, para `local-output/revisao-02`. Cada saída precisa estar vazia e fora da entrada.

## 4. Identificar a execução utilizada

O terminal informa o ID; o mesmo ID aparece em `resultado.json`, `execucao.json` e na seção expansível **Identificação da execução** do HTML. O registro inclui:

| Informação | Interpretação |
|---|---|
| ID | UUID da execução, mantido nos seus diferentes formatos |
| Gerado em UTC | Momento da identificação, com sufixo Z; não é horário local |
| Versão do programa/Python | Ambiente usado para gerar a saída |
| Catálogo/perfil/controle SHA-256 | Impressões das configurações efetivas, serializadas de forma estável; não são hashes dos arquivos JSON/CSV brutos |
| Fontes SHA-256 e bytes | Identificam os mesmos bytes que foram lidos e processados |

Espaços ou ordem das chaves de um JSON não alteram o hash da configuração efetiva. Valores do controle são considerados como quantidades e centavos normalizados. O perfil pode aparecer não informado em resultados produzidos diretamente pela API sem perfil. `run` sempre registra o perfil efetivo, incluindo o padrão.

Hashes ajudam a comparar conteúdo; não são assinatura, prova de autoria ou garantia de autenticidade. Resultados anteriores à identificação continuam utilizáveis na comparação, com aviso de ausência. Guarde a saída completa para reproduzir a conferência.

## 5. Comparar duas revisões

```bash
python -m finance_close compare --before local-output/revisao-01/resultado.json --after local-output/revisao-02/resultado.json --output local-output/comparacao-01-02
```

Abra `comparacao.html`. Há indicadores, tabela antes/depois, busca por ID/arquivo, filtro de classificação e links para CSV e JSON completos. O filtro inicial mostra somente alterações; escolha Todas para incluir os grupos sem mudança. Filtrar a tela não modifica os arquivos de comparação baixados.

| Classificação | Significado |
|---|---|
| Pendência resolvida | O mesmo grupo de ID tinha exclusões antes e suas linhas presentes depois estão aprovadas |
| Nova pendência | Um ID antes aprovado passa a ter exclusões |
| Adicionado / removido | Grupo presente em apenas um resultado; não se presume uma correspondência com outro ID |
| Alterado | Campos de um grupo aprovado mudaram |
| Alterado com pendência | Campos/classificações mudaram e o grupo ainda contém exclusões |
| Origem alterada | Mesmo conteúdo/classificação, com localização de origem diferente |
| Sem alteração | Campos normalizados, classificação e localização coincidem |

IDs repetidos são analisados como grupos, conservando todas as versões. A comparação usa multiconjuntos para não depender da ordem das linhas. Se a quantidade do grupo muda, `quantidade_linhas` fica explícita; campos com os mesmos valores distintos não são marcados como alterados apenas por remover uma repetição. Um ID ausente é identificado pelo arquivo, aba e linha; mudanças de posição podem produzir ocorrências adicionadas/removidas. Preencher ou renomear um ID não faz a ferramenta inferir que ele corrigiu outro registro.

Datas e valores são comparados na forma normalizada. Mudanças apenas de apresentação monetária, como 100.0 para 100.00, não são alteração financeira. Diferenças de período ou de catálogo/perfil geram avisos; um perfil não registrado em um dos resultados exige cautela. Os totais e contadores fornecidos são confrontados com as linhas antes da comparação. Isso não revalida toda a regra de negócio nem autentica os arquivos.

**Receita/gasto/resultado aprovados antes e depois podem representar populações diferentes.** A diferença não mede ganho financeiro nem comprova que todos os dados recebidos estão corretos. Confira controles, registros removidos e critérios da revisão. Uma pendência removida por exclusão pode deixar de aparecer, sem que tenha havido uma correção de negócio.

### Exemplo de revisão incluído

```bash
python -m finance_close compare --before examples/com-pendencias/resultado.json --after examples/validado/resultado.json --output local-output/comparacao-exemplo
```

Resultado esperado: **19 grupos**, 5 com pendência resolvida, 1 ocorrência sem ID removida e 13 sem alteração. As linhas aprovadas passam de 14 para 18 e o total aprovado parcial de 48.000,00 para 145.000,00 BRL. Consulte a [comparação pronta](../examples/comparacao/comparacao.html).

## 6. Interpretar os códigos de retorno

| Comando | 0 | 2 | 1 |
|---|---|---|---|
| setup | Configuração criada | — | Erro/interrupção; destino ocupado é preservado |
| check | Preparação pronta pelas regras | Pendências de dados/controle | Erro estrutural/configuração; leitura possivelmente parcial |
| run | Lote validado pelas regras | Relatórios gerados com pendências | Erro de leitura/configuração/exportação; saída parcial pode existir |
| compare | Arquivos de comparação gerados | — | Entrada inválida/inconsistente ou erro de exportação |

O retorno 0 de `compare` confirma a geração da comparação, não a aprovação do lote depois. Se um comando que escreve falhar, confira a mensagem e use uma nova pasta vazia antes de repetir. Erros de sintaxe/opções do terminal são reportados pelo argparse com retorno 2; isso difere do retorno 2 de uma execução válida de check/run com pendências.

## 7. Testar sua cópia

```bash
python -m unittest discover -s tests -v
```

O workflow `Validate automation` está configurado para **Windows e Ubuntu × Python 3.11, 3.12 e 3.13**, com UTF-8 explícito. São seis combinações independentes, usando a [matriz do GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations). Ele roda a suíte, gera os exemplos e verifica os comandos check/compare e a sintaxe JavaScript. Os resultados remotos só estarão disponíveis depois de enviar o projeto e executar o workflow.

Mantenha arquivos pessoais fora do pacote de publicação. Pastas `local-config`, `local-input` e `local-output` são ignoradas por Git; no upload manual pelo navegador, escolha somente os arquivos que deseja publicar.
