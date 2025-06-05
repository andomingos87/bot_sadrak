import gspread

# Abre a planilha e retorna o conteúdo da coluna com nomes de usuário
def carregar_usuarios(nome_planilha, nome_aba, coluna_nome):
    gc = gspread.service_account(filename='service_account.json')
    planilha = gc.open(nome_planilha)
    aba = planilha.worksheet(nome_aba)
    nomes = aba.col_values(coluna_nome)
    return [nome.strip().lower() for nome in nomes if nome.strip()]

# Verifica se o usuário existe
def usuario_existe(username, nome_planilha="app.plugtv_bot", nome_aba="usuarios", coluna_nome=1):
    nomes = carregar_usuarios(nome_planilha, nome_aba, coluna_nome)
    return username.strip().lower() in nomes

# Retorna a senha associada a um nome de usuário

def get_dns_url_from_sheet(nome_planilha="app.plugtv_bot", nome_aba="DNS", linha=2, coluna=1):
    """
    Retorna o valor da célula A2 da aba DNS da planilha padrão.
    """
    gc = gspread.service_account(filename='service_account.json')
    planilha = gc.open(nome_planilha)
    aba = planilha.worksheet(nome_aba)
    valor = aba.cell(linha, coluna).value
    return valor.strip() if valor else None

def obter_senha(username, nome_planilha="app.plugtv_bot", nome_aba="usuarios", col_usuario=1, col_senha=2):
    gc = gspread.service_account(filename='service_account.json')
    planilha = gc.open(nome_planilha)
    aba = planilha.worksheet(nome_aba)

    usuarios = aba.col_values(col_usuario)
    senhas = aba.col_values(col_senha)

    for i, nome in enumerate(usuarios):
        if nome.strip().lower() == username.strip().lower():
            if i < len(senhas):
                return senhas[i].strip()
    return None
