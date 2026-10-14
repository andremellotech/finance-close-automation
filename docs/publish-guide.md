# Publicar pelo site do GitHub

Este projeto não exige GitHub Desktop. O pacote foi organizado para caber no limite de 100 arquivos por upload do navegador.

Use **finance-close-automation-github-v1.2.0.zip**, preparado para envio ao repositório. Ele contém código, configurações fictícias, testes, guias e exemplos completos, com as pastas preservadas. Planos internos de desenvolvimento e caches não fazem parte deste pacote. Não envie o próprio ZIP na aba Code: extraia antes.

Se o repositório já existir, use **Add file → Upload files** nele; não é necessário apagar ou recriar. Atualize os arquivos nos mesmos caminhos. O upload não remove arquivos antigos que tenham ficado soltos na raiz: confira antes de excluir qualquer item. Não foi verificado o estado remoto do seu repositório nesta preparação.

1. Crie um repositório público chamado **finance-close-automation** na conta **andremellotech**. Deixe README desligado, sem licença e sem .gitignore: o pacote já contém esses arquivos.
2. Baixe o ZIP como **um único arquivo** e use **Extrair tudo** no Windows. Abra a pasta interna `finance-close-automation` e confira as subpastas. Não baixe os arquivos da lista do ZIP um por um.
3. No repositório vazio, clique em **uploading an existing file**. Arraste o **conteúdo da pasta interna** para a área de upload, com as pastas inteiras.
4. Antes do commit, confira os caminhos: `sample-input/validado/engenharia.xlsx`, `examples/validado/fechamento.xlsx` e `finance_close/engine.py`. Se aparecer apenas `engine.py`, sem a pasta, cancele aquele envio e arraste a pasta inteira do Explorador. Não envie a pasta externa envolvendo tudo.
5. Confirme **Commit changes** na branch **main**. A raiz deve mostrar principalmente pastas e os poucos arquivos de apresentação/configuração.

Mensagem sugerida para o primeiro envio: `Publicar Finance Close Automation v1.2.0`. Para atualizar uma cópia existente: `Atualizar documentação e pacote de publicação v1.2.0`. Se a branch exigir revisão, envie para uma nova branch e abra a pull request pelo próprio site.

Depois do envio, confira esta estrutura:

```text
.github/workflows/validate.yml
config/
docs/
examples/
finance_close/
sample-input/
starter/
tests/
web/
.gitignore
.nojekyll
CHANGELOG.md
CONTRIBUTING.md
LICENSE
README.md
VERSION
index.html
requirements.txt
```

Não deve existir uma segunda pasta `finance-close-automation` envolvendo esses itens dentro do repositório. Arquivos como `engine.py` e `fechamento.xlsx` devem estar nas suas pastas, sem cópias renomeadas com `(1)` ou `(2)` na raiz.

## Colocar a demonstração no ar

Como a página já foi gerada e está no pacote, o modo mais simples é:

1. Abra **Settings → Pages**.
2. Em **Source**, selecione **Deploy from a branch**.
3. Selecione **main** e a pasta **/(root)**. Clique em **Save**.
4. Aguarde o deployment e abra **Visit site**. O endereço esperado é `https://andremellotech.github.io/finance-close-automation/`; use a URL confirmada pelo GitHub.
5. Na engrenagem de **About**, preencha **Website** com o endereço do site.

O README já aponta para o Pages da conta **andremellotech** e deste repositório. Se mudar conta ou nome, atualize esses links e os de `web/template.html`, depois gere a página novamente. O endereço só deve ser anunciado como disponível depois que **Visit site** abrir a demonstração.

O workflow `Validate automation` é separado da publicação. Está configurado para seis combinações: Windows/Ubuntu × Python 3.11/3.12/3.13. Quando `.github/workflows/validate.yml` estiver presente, ele instala as dependências, testa, recria os exemplos, confere `check`/`compare` e a sintaxe dos dois scripts JavaScript. Verifique o resultado de cada combinação na aba Actions após publicar; configuração local não comprova que os jobs remotos passaram. O site publica o HTML e os exemplos que foram enviados à branch. Depois de modificar os dados ou o código, gere e envie os resultados atualizados.

Confira também `examples/comparacao/comparacao.html` e `docs/operations-guide.md`. Não envie suas pastas locais de configuração, entrada ou saída. `.gitignore` não filtra arquivos escolhidos manualmente para upload pelo navegador.

Se a pasta `.github` não aparecer no envio, ainda é possível publicar a demonstração por branch. Para adicionar a validação, crie pelo editor web o arquivo `.github/workflows/validate.yml` e copie o conteúdo correspondente do pacote. Não é preciso configurar permissões amplas de escrita para os testes.

Descrição sugerida (copie sem acrescentar `>`):

```text
Automação do fechamento mensal com Python e Excel: consolidação CSV/XLSX, qualidade de dados, conciliação e rastreabilidade, com exemplos fictícios.
```

Tópicos: python, pandas, excel, data-quality, financial-analysis, automation, portfolio.

## Conferência após publicar

1. **Code:** README com imagem e links; estrutura com pastas, sem arquivos achatados.
2. **Pages:** demonstração abre, alterna os lotes e oferece a comparação; os links do README usam o site para interação.
3. **Downloads da demonstração:** o Excel corresponde ao lote selecionado; CSV/JSON da comparação ficam na mesma pasta do seu HTML.
4. **Actions:** veja os seis resultados de `Validate automation`. Em caso de falha, abra o job e leia a primeira etapa com erro. O workflow não publica o site nem modifica os arquivos da branch.

O repositório público permite consultar e baixar o código. A lista de arquivos faz parte da aba Code do GitHub; a apresentação visual fica no README e no Pages. Para compartilhar o portfólio, use o endereço do Pages.

Referências: [Upload de arquivos e pastas](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository) e [publicação do Pages por branch](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
