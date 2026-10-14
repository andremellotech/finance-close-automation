"""Orientações de revisão: explicam problemas sem alterar dados ou controles."""
MESSAGES = {
    'CENTRO_DESCONHECIDO': ('Centro de custo não cadastrado', 'Confira o cadastro e o centro informado na origem; corrija o lançamento ou inclua um centro válido no catálogo.'),
    'CATEGORIA_DESCONHECIDA': ('Categoria não cadastrada', 'Confira a conta de origem e sua categoria no catálogo, incluindo natureza e sinal permitido.'),
    'DATA_INVALIDA': ('Data inválida', 'Consulte a fonte e preencha uma data de calendário válida no formato definido no perfil.'),
    'DATA_FORMATO_INVALIDO': ('Data diferente do formato configurado', 'Confira formato_data no perfil: br exige DD/MM/AAAA e iso exige AAAA-MM-DD; ajuste o perfil ou a origem após conferir o formato correto.'),
    'FORA_COMPETENCIA': ('Lançamento fora da competência', 'Confirme a qual mês o lançamento pertence. Não altere a data apenas para passar na regra; separe o lote correto ou informe a competência adequada.'),
    'VALOR_INVALIDO': ('Valor não quantificável', 'Confira o valor na fonte e os separadores decimal/milhar do perfil. Use número com até duas casas; não substitua um valor desconhecido por zero.'),
    'SINAL_INCOMPATIVEL': ('Sinal incompatível com a categoria', 'Confira natureza e convenção de sinal no catálogo. Investigue eventuais estornos antes de corrigir o valor ou a regra.'),
    'DUPLICATA_EXATA': ('Repetição exata do lançamento', 'Confirme se houve reenvio duplicado e elimine a repetição na origem somente após a conferência.'),
    'CONFLITO_ID': ('Mesmo ID com campos diferentes', 'Confira todas as versões desse ID na origem e resolva o conflito. Nenhuma versão é escolhida automaticamente.'),
    'FORMULA_NAO_ACEITA': ('Fórmula na entrada Excel', 'Confira o cálculo na origem e forneça valores conferidos em uma cópia de entrada; não confie em cache de fórmula não recalculada.'),
    'DIVERGENTE': ('Arquivo diverge do controle', 'Confronte quantidade e total com o controle independente e investigue a origem. Não ajuste o controle apenas para coincidir com o total calculado.'),
    'INCOMPLETO': ('Total recebido incompleto', 'Resolva os valores não quantificáveis antes de conciliar o arquivo; o total mostrado inclui somente a parcela que pôde ser somada.'),
    'SEM_CONTROLE': ('Arquivo sem controle independente', 'Obtenha quantidade e total esperados com o responsável pela origem e preencha uma linha de controle para esse arquivo.'),
    'ARQUIVO_AUSENTE': ('Arquivo esperado não recebido', 'Confira o nome no controle e peça o arquivo correspondente à origem; não considere uma ausência como saldo zero.'),
    'VAZIO': ('Arquivo sem lançamentos', 'Confirme se a origem enviou o arquivo correto e se o período deveria conter lançamentos.'),
}


def explain(codes):
    result = []
    for code in dict.fromkeys(codes):
        if code.startswith('CAMPO_VAZIO:'):
            field = code.split(':', 1)[1]
            problem, action = f'Campo obrigatório vazio: {field}', f'Preencha {field} com a informação conferida na origem. Consulte o mapeamento do perfil para localizar sua coluna.'
        elif code.startswith('ERRO_CELULA_EXCEL:'):
            field = code.split(':', 1)[1]
            problem, action = f'Erro de célula Excel: {field}', f'Resolva o erro na célula de origem de {field} e forneça um valor conferido.'
        else:
            problem, action = MESSAGES.get(code, (code, 'Confira o registro na origem e as regras documentadas antes de executar novamente.'))
        result.append({'codigo': code, 'problema': problem, 'acao': action})
    return result
