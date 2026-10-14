# Verificação da versão 1.2.0

Conferência executada em 14/10/2026, com Python 3.12 e Node.js do ambiente local.

## Automação

- `python -m unittest discover -s tests`: 47 testes aprovados na rodada final local, em Windows com Python 3.12.14.
- `python -m finance_close demo`: os dois exemplos e o HTML foram gerados com sucesso.
- `node --check web/app.js` e `node --check web/comparison.js`: sintaxe JavaScript aprovada.
- Casos cobertos: dinheiro e sinais, campos/cadastros/competência, duplicatas, conflitos entre arquivos, controles ausentes, lote vazio, fórmulas/erros Excel, CSV com múltiplas linhas e caracteres inválidos, segurança dos caminhos de saída e consistência das exportações.
- Uma revisão independente encontrou quatro problemas de leitura/rastreabilidade. Foram corrigidos com testes de regressão: erros de célula Excel, fórmulas sem cache no fim da aba, linha física inicial de CSV e truncamento de valores contendo NUL.
- Na revisão independente da extensão 1.1, um achado sobre critérios SUMIF foi corrigido: a Base aprovada agora inclui natureza canônica (`receita`/`gasto`), usada nas fórmulas, em vez de agrupar por códigos que o Excel possa tratar como equivalentes. Regressões com FAT/fat e 01/1 verificam classificação, fórmulas e valores 100/30/70.
- Os novos testes também cobrem catálogo renomeado, obrigatórios opcionais/estruturais, sinal livre explícito, mapeamento de CSV/XLSX, formatos brasileiros, rejeição de formatos mistos, colunas extras, título escapado, tokens de template nos dados e HTML da execução.
- A extensão 1.2 cobre assistente com controle vazio e preservação de destino ocupado; diagnóstico agregado sem exportar/aprovar leitura parcial; orientações nas saídas; IDs únicos e hashes estáveis; comparação por grupos, IDs trocados/ausentes, mudanças de origem, avisos e rejeição de resumo/liberação inconsistente.
- Durante a conferência visual da comparação foi reproduzido e corrigido, com teste antes/depois, um falso destaque de campos idênticos quando uma duplicata era removida. A mudança de quantidade agora é explícita, separada dos valores que realmente diferem.
- A conferência dos links do pacote identificou um endereço inicial incorreto para o Excel no HTML de execução; o JavaScript já o corrigia na tela, mas o HTML agora é gravado com o caminho certo desde a geração. Um teste de regressão confere o endereço estático.
- A revisão independente da extensão 1.2 foi solicitada, mas não executada por limite de uso da conta. A revisão local de código, os testes automatizados e a conferência visual descritos aqui foram concluídos; não se declara aprovação independente para esta extensão.

## Resultados conferidos

| Indicador | Com pendências | Validado |
|---|---:|---:|
| Recebidas | 21 | 18 |
| Aprovadas | 14 | 18 |
| Excluídas | 7 | 0 |
| Valores não quantificáveis | 1 | 0 |
| Resultado aprovado (BRL) | 48.000,00, parcial | 145.000,00 |
| Diferença recebido quantificável − aprovado − excluído quantificável (BRL) | 0,00 | 0,00 |

Os valores em centavos do JSON foram confrontados com CSV, células numéricas e caches das fórmulas Excel. Os registros de origem e hashes dos arquivos também são preservados.

O starter adaptado de fevereiro de 2026 possui 1 CSV, 2 linhas aprovadas, receita 1.250,50 BRL, gastos 250,50 BRL e resultado 1.000,00 BRL. As diferenças da conciliação e da ponte são zero. Seu relatório é gerado por `run --profile`, usando nomes e formatos de entrada diferentes dos exemplos originais.

A comparação com pendências → validado contém 19 grupos: 5 resolvidos, 1 ocorrência sem ID removida e 13 sem alteração. As 14/18 aprovadas e os 48.000,00/145.000,00 BRL foram confrontados com os resultados de origem. Essa diferença reflete populações aprovadas distintas, não um ganho financeiro.

## Página e Excel

A página foi aberta por HTTP local no navegador integrado. Foram conferidas as quatro perspectivas, alternância dos exemplos, busca, filtros de classificação e centro, estado sem pendências, instruções expansíveis e endereço do Excel de cada exemplo. Um CSV filtrado foi baixado e lido: continha somente ENG-004, correspondente à busca por valor inválido.

O layout foi inspecionado em desktop e nas larguras de 390 e 320 pixels. As tabelas extensas mantêm rolagem própria e a página não transbordou horizontalmente nesses tamanhos. Não foram registrados avisos ou erros de console nessa navegação.

Na versão 1.1, o relatório do starter foi conferido com fevereiro de 2026, 1 arquivo, 2 aprovadas, busca por ID `0001`, rastreabilidade, conciliação sem diferença e estado sem pendências. O link de Excel aponta ao arquivo da mesma pasta. Desktop e larguras 390/320 px foram conferidos; a demonstração original também conservou a alternância dos lotes e os resultados 48.000,00/145.000,00 BRL. Capturas reais estão em `docs/images/`.

Na 1.2, a busca por ENG-004 mostrou a orientação correspondente; alternar para Validado mostrou zero pendências e atualizou o link de manifesto para a execução correta. Foram conferidos ID/versão no acordeão e no JSON. Na comparação, os filtros mostraram 5 resolvidos, a busca isolou ENG-004, uma busca inexistente produziu estado vazio e Todas exibiu 19 grupos. As identificações antes/depois foram exibidas. A comparação e a página principal, inclusive identificação expandida, foram conferidas em 390/320 px, sem transbordamento horizontal da página. As tabelas mantêm rolagem própria. Não houve avisos/erros de console nessa navegação. A captura `preview-comparacao.jpg` mostra o resultado real no navegador.

As cinco abas do relatório foram renderizadas para inspeção de títulos, colunas, números e conteúdo. Abertura e recálculo no aplicativo Microsoft Excel não foram executados. As fórmulas do resumo possuem valores calculados em cache, testados contra o motor Python.

O resumo e a Base aprovada do exemplo adaptado também foram renderizados e inspecionados, incluindo a coluna de natureza. A leitura independente confirmou os valores 1.250,50/250,50/1.000,00 e diferença de ponte zero. O importador visual pode normalizar a exibição de IDs numéricos com zeros iniciais; as células XLSX são gravadas como texto, e a preservação dos IDs é verificada na leitura dos arquivos e no HTML.

A coluna `acao_sugerida` da aba Pendencias foi renderizada e inspecionada com as sete exclusões. As oito imagens dos resumos e detalhes foram produzidas e inspecionadas; o processo do renderizador terminou com código 1 após salvar as imagens, sem diagnóstico adicional. A renderização é evidência visual, não recálculo no aplicativo Microsoft Excel; valores, fórmulas e orientações dos arquivos salvos foram conferidos por leitura independente.

## Alcance

O ZIP preserva as pastas, exclui caches Python e permanece abaixo de 100 arquivos. A conferência do pacote verifica integridade, links locais Markdown/HTML, formatos XLSX/JPEG, identificações, hashes das fontes e valores das planilhas. Uma cópia extraída é usada para executar `run` e `check` nos três exemplos e `compare` nos dois lotes originais, confrontando retornos 0/2 e os resultados de negócio com os incluídos no pacote.

O workflow está configurado para seis combinações Windows/Ubuntu × Python 3.11/3.12/3.13, com UTF-8 explícito. Os seis jobs remotos ainda não foram executados nesta entrega; somente o ambiente Windows/Python 3.12 local foi testado. O YAML foi conferido por leitura, sem alegação de lint por parser dedicado.

Os testes e exemplos demonstram as regras documentadas desta versão; não representam homologação de um processo contábil real. A publicação remota e a execução do workflow no GitHub dependem de enviar o pacote ao repositório. A demonstração no navegador contém resultados previamente processados; a automação roda localmente em Python.
