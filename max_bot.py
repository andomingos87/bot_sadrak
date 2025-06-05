from playwright.sync_api import sync_playwright
import time
import os
from telebot import types

# Fluxo principal iniciado após a escolha do app Max
def iniciar_fluxo_max(bot, message, usuarios_em_autenticacao):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Voltar", callback_data="voltar"))
    bot.send_message(chat_id, "Você escolheu o app *Max*.\nAgora digite o *nome de usuário* que deseja criar no painel:", parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: receber_novo_username(bot, msg, usuarios_em_autenticacao))

def receber_novo_username(bot, message, usuarios_em_autenticacao):
    chat_id = message.chat.id
    novo_user = message.text.strip()
    usuarios_em_autenticacao[str(chat_id) + "_novo_user"] = novo_user

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Voltar", callback_data="voltar"))
    bot.send_message(chat_id, "Agora digite a *senha* para esse novo usuário:", parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: receber_nova_senha(bot, msg, usuarios_em_autenticacao))

def receber_nova_senha(bot, message, usuarios_em_autenticacao):
    chat_id = message.chat.id
    nova_senha = message.text.strip()
    novo_user = usuarios_em_autenticacao.get(str(chat_id) + "_novo_user")

    bot.send_message(chat_id, "🔄 Acessando o painel e cadastrando o novo usuário... Aguarde.")

    try:
        resposta = executar_login(novo_user, nova_senha)
        bot.send_message(chat_id, resposta)
        if resposta.startswith("✅ Usuário"):
            markup = types.InlineKeyboardMarkup()
            btn_max = types.InlineKeyboardButton("MaxPlayer", callback_data="app_escolhido:MaxPlayer")
            btn_quick = types.InlineKeyboardButton("QuickPlayer", callback_data="app_escolhido:QuickPlayer")
            markup.add(btn_max, btn_quick)
            bot.send_message(
                chat_id,
                """Escolha o aplicativo que deseja acessar\n Se você está tendo problemas, mande /sair e faça /entrar novamente!\nNão envie mensagens com o menu aberto.\n\nMENU ATUALIZADO em 04/06/2025 20:59""",
                reply_markup=markup
            )
    except Exception as e:
        bot.send_message(chat_id, f"❌ Erro ao cadastrar o usuário:\n`{str(e)}`", parse_mode="Markdown")

    usuarios_em_autenticacao.pop(chat_id, None)
    usuarios_em_autenticacao.pop(str(chat_id) + "_novo_user", None)

def executar_login(novo_username, nova_senha):
    painel_email = os.getenv("PAINEL_MAX_EMAIL")
    painel_senha = os.getenv("PAINEL_MAX_SENHA")

    try:
        print("[INFO] Iniciando automação com Playwright...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print("[INFO] Acessando página de login...")
            page.goto("https://my-beta.maxplayer.tv/auth/login", timeout=60000)

            page.fill('#exampleEmail', painel_email)
            page.fill('#examplePassword', painel_senha)
            page.click('button.btn-primary')

            print("[INFO] Aguardando redirecionamento...")
            page.wait_for_url("**/dashboard", timeout=15000)

            print("[INFO] Acessando aba 'Customers'...")
            page.click("a[href='/customers']")
            page.wait_for_load_state('networkidle')

            print("[INFO] Clicando em 'Add New User'...")
            page.click("button.btn-green")
            page.wait_for_selector("#iptv_user", timeout=10000)

            print("[INFO] Selecionando domínio cr61.net...")
            page.select_option("select#name", value="1739318193890969526")

            print(f"[INFO] Preenchendo usuário: {novo_username}")
            page.fill("#iptv_user", novo_username)

            print("[INFO] Preenchendo senha do novo usuário...")
            page.fill("#iptv_pass", nova_senha)

            print("[INFO] Clicando em 'Create'...")
            page.locator("button.btn-primary", has_text="Create").click()

            print("[INFO] Aguardando finalização...")
            time.sleep(5)

            print("[INFO] Encerrando navegador...")
            browser.close()

            # Mensagem de sucesso
            bot_message = f"✅ Usuário '{novo_username}' criado com sucesso no painel."
            return bot_message

    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return "❌ Erro durante o processo. Por favor, digite /iniciar e tente novamente."