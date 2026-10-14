# Comece por este exemplo

Dados inteiramente fictícios. Este exemplo troca nomes de colunas, formato de data, separadores numéricos e categorias, sem editar o motor Python.

Na raiz extraída do projeto, execute:

```bash
python -m finance_close run --input starter/entrada --controls starter/controle.csv --catalog starter/catalogo.json --profile starter/perfil.json --period 2026-02 --output local-output/primeira-adaptacao
```

Abra `local-output/primeira-adaptacao/relatorio.html` ou `fechamento.xlsx`. Resultado esperado: **2 recebidas, 2 aprovadas, receita 1.250,50 BRL, gastos 250,50 BRL e resultado 1.000,00 BRL**, com diferença de conciliação e ponte iguais a zero. O retorno esperado é 0. A descrição vazia é permitida por esse catálogo; sua coluna permanece presente.

O pacote inclui uma [execução pronta](../examples/adaptado/relatorio.html). Para adaptar a um novo caso, siga o [guia completo](../docs/adaptation-guide.md). Não coloque seus dados reais nesta pasta de exemplos públicos.
