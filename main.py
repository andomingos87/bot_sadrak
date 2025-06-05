import telebot
from telebot import types
from dotenv import load_dotenv
import os
from sheets_utils import usuario_existe, obter_senha

load_dotenv()
apikey = os.getenv("BOT_TELEGRAM_API")
bot = telebot.TeleBot(apikey)

usuarios_em_autenticacao = {}  # Armazena estado temporário por chat_id

# ──────────────────────────────
# Comando /entrar
# ──────────────────────────────
@bot.message_handler(commands=['entrar'])
def iniciar(message):
    bot.send_message(message.chat.id, "Digite o seu nome de usuário:")
    bot.register_next_step_handler(message, receber_username)

# ──────────────────────────────
# Comando /sair
# ──────────────────────────────
@bot.message_handler(commands=['sair'])
def sair(message):
    usuarios_em_autenticacao.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "Você saiu. \nPara entrar novamente envie /entrar")

# ──────────────────────────────
# Etapa: receber o nome de usuário
# ──────────────────────────────
def receber_username(message):
    username = message.text.strip()

    markup = types.InlineKeyboardMarkup()
    botao_sim = types.InlineKeyboardButton("Sim", callback_data=f"confirmar:{username}")
    botao_nao = types.InlineKeyboardButton("Não", callback_data="negar")
    markup.add(botao_sim, botao_nao)

    bot.send_message(
        message.chat.id,
        f"Você digitou *{username}*, está correto?",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# ──────────────────────────────
# Resposta aos botões (callback)
# ──────────────────────────────
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        chat_id = call.message.chat.id

        if call.data.startswith("confirmar:"):
            username = call.data.split(":")[1]

            if usuario_existe(username):
                usuarios_em_autenticacao[chat_id] = username
                bot.send_message(chat_id, "Usuário encontrado ✅\nAgora digite sua senha:")
                bot.register_next_step_handler(call.message, verificar_senha)
            else:
                bot.send_message(chat_id, f"O usuário *{username}* **não foi encontrado** na base ❌", parse_mode='Markdown')

        elif call.data == "negar":
            bot.send_message(chat_id, "Ok. Digite novamente seu nome de usuário:")
            bot.register_next_step_handler(call.message, receber_username)

        elif call.data.startswith("app_escolhido:"):
            app_escolhido = call.data.split(":")[1]

            if app_escolhido == "MaxPlayer":
                from max_bot import iniciar_fluxo_max
                iniciar_fluxo_max(bot, call.message, usuarios_em_autenticacao)

            elif app_escolhido == "QuickPlayer":
                from quick_bot import iniciar_fluxo_quick
                iniciar_fluxo_quick(bot, call.message)

    except Exception as e:
        bot.send_message(call.message.chat.id, "❌ Ocorreu um erro interno. Por favor, tente novamente ou contate o suporte.")
        print(f"[ERRO callback_query] {str(e)}")

# ──────────────────────────────
# Verificar senha do usuário autenticador
# ──────────────────────────────
def verificar_senha(message):
    chat_id = message.chat.id
    senha_digitada = message.text.strip()

    if chat_id not in usuarios_em_autenticacao:
        bot.send_message(chat_id, "Sessão expirada. Digite /iniciar para começar novamente.")
        return

    username = usuarios_em_autenticacao[chat_id]
    senha_correta = obter_senha(username)

    if senha_digitada == senha_correta:
        from datetime import datetime
        datahora_menu = datetime.now().strftime("%d/%m/%Y %H:%M")
        markup = types.InlineKeyboardMarkup()
        btn_max = types.InlineKeyboardButton("MaxPlayer", callback_data="app_escolhido:MaxPlayer")
        btn_quick = types.InlineKeyboardButton("QuickPlayer", callback_data="app_escolhido:QuickPlayer")
        markup.add(btn_max, btn_quick)
        bot.send_message(
            chat_id,
            f"""✅ Autenticação bem-sucedida.\n\n
Revenda: {username}!
                         
Escolha o aplicativo que deseja acessar\nSe você está tendo problemas, mande /sair e faça /entrar novamente!\nNão envie mensagens com o menu aberto.\n\nMENU ATUALIZADO em {datahora_menu}""",
            reply_markup=markup
        )
    else:
        bot.send_message(chat_id, "❌ Senha incorreta. Tente novamente:")
        bot.register_next_step_handler(message, verificar_senha)

# ──────────────────────────────
# Handler genérico
# ──────────────────────────────
def verificar(mensagem):
    return mensagem.text not in ["/iniciar", "/sair"]

@bot.message_handler(func=verificar)
def responder(message):
    bot.send_message(
        message.chat.id,
        """👋 Olá! Seja bem-vindo(a) ao app.plugtv.
Aqui você acessa tudo de forma simples e rápida!

Use os comandos abaixo para começar:
📲 /entrar – Para começar a usar o bot
🚪 /sair – Para encerrar a sessão"""
    )

if __name__ == "__main__":
    bot.polling()

