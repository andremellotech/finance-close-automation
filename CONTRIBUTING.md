# Usar como base e contribuir

## Criar seu próprio caso

1. Faça um fork ou baixe o projeto completo e extraia mantendo as pastas.
2. Instale as dependências de `requirements.txt` em Python 3.11 ou posterior.
3. Siga o [guia operacional](docs/operations-guide.md): `setup` prepara as configurações; preencha o controle independente; use `check` antes de `run`.
4. Confira o resultado contra um caso conhecido e depois compare duas revisões com `compare`.
5. Se publicar sua cópia, atualize os links da conta/repositório no README e em `web/template.html`. Gere novamente o HTML e os exemplos que deseja publicar. O [guia de publicação](docs/publish-guide.md) explica o upload pelo navegador.

Não altere `sample-input` para trabalhar com arquivos particulares. Use `local-input`, `local-config` e `local-output`, que ficam fora do pacote público. No upload manual, `.gitignore` não remove os arquivos que você selecionar.

## Alterar o código

Crie uma branch no seu fork e mantenha cada alteração focada em um problema. Para correções, inclua um teste que reproduza o comportamento. Use dados fictícios com resultado esperado conhecido; preserve ID, origem, centavos e controles independentes.

Na raiz do projeto:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests
node --check web/app.js
node --check web/comparison.js
```

Node.js é usado na conferência da sintaxe da interface; a execução da automação requer Python. Se mudar os arquivos de `web`, gere novamente a demonstração com `python -m finance_close demo`. Para renovar a comparação de exemplo, use `compare` com os dois resultados recém-gerados em uma saída vazia.

`demo` recria os dois lotes originais e a página principal. O starter adaptado e a comparação são exemplos gerados separadamente; veja os comandos e valores esperados no [guia operacional](docs/operations-guide.md).

Antes de propor uma mudança, descreva o problema, o comportamento resultante e as verificações executadas. Confira também telas pequenas se alterar o layout. A matriz do GitHub Actions precisa passar na sua cópia; testes locais não comprovam execução remota.

## Relatar um problema

Informe versão do projeto, sistema, versão do Python, comando executado, retorno e mensagem recebida. Se possível, envie um exemplo mínimo fictício e o resultado esperado. Remova caminhos pessoais e conteúdo confidencial antes de publicar a descrição.

O código e os exemplos fictícios são distribuídos sob a [licença MIT](LICENSE). Regras de um novo processo financeiro precisam ser conferidas pelo responsável pelo caso.
