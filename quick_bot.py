from playwright.sync_api import sync_playwright
import time
import re
from telebot import types
from sheets_utils import get_dns_url_from_sheet, get_epg_url_from_sheet

# Dicionário temporário para armazenar dados por chat
dados_quick = {}

def iniciar_fluxo_quick(bot, message):
    chat_id = message.chat.id
    print(f"[QuickBot] Iniciando fluxo para chat_id={chat_id}")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Voltar", callback_data="voltar"))
    bot.send_message(chat_id, "🚀 Você escolheu o app *Quick*.\n\nPor favor, envie o número do *MAC address*.\nExemplo: `XX:XX:XX:XX:XX:XX`", parse_mode='Markdown', reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: receber_mac(bot, msg, chat_id))

def receber_mac(bot, message, chat_id):
    mac = message.text.strip()
    dados_quick[chat_id] = {"mac": mac}
    print(f"[QuickBot] MAC recebido: {mac}")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Voltar", callback_data="voltar"))
    bot.send_message(chat_id, "Agora envie o link M3U:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: receber_url_m3u(bot, msg, chat_id))

def receber_url_m3u(bot, message, chat_id):
    url_original = message.text.strip()
    # Busca dinâmica da URL base na planilha
    url_base = get_dns_url_from_sheet()
    if not url_base:
        bot.send_message(chat_id, "❌ Erro ao obter a URL base do sistema Quick. Contate o suporte.")
        return
    url_alterada = re.sub(r"^https?://[^/]+", url_base, url_original)
    dados_quick[chat_id]["url"] = url_alterada
    print(f"[QuickBot] URL original recebida: {url_original}")
    print(f"[QuickBot] URL alterada para: {url_alterada}")

    bot.send_message(chat_id, "✅ Dados recebidos!\nAguarde enquanto fazemos o envio para o sistema Quick.")
    
    sucesso = automatizar_quick(dados_quick[chat_id]["mac"], url_alterada)

    if sucesso:
        print("[QuickBot] Envio concluído com sucesso.")
        bot.send_message(chat_id, "✅ *Concluído!* A playlist foi enviada com sucesso para o Quick.", parse_mode='Markdown')
        # Envia menu de escolha de app
        from telebot import types
        markup = types.InlineKeyboardMarkup()
        btn_max = types.InlineKeyboardButton("MaxPlayer", callback_data="app_escolhido:MaxPlayer")
        btn_quick = types.InlineKeyboardButton("QuickPlayer", callback_data="app_escolhido:QuickPlayer")
        markup.add(btn_max, btn_quick)
        bot.send_message(
            chat_id,
            """Escolha o aplicativo que deseja acessar\n Se você está tendo problemas, mande /sair e faça /entrar novamente!\nNão envie mensagens com o menu aberto.\n\nMENU ATUALIZADO em 04/06/2025 20:59""",
            reply_markup=markup
        )
    else:
        print("[QuickBot] Falha no envio da playlist.")
        bot.send_message(chat_id, "❌ Ocorreu um erro ao enviar a playlist. Tente novamente mais tarde.")

def automatizar_quick(mac, url):
    print("[QuickBot] Iniciando automação com Playwright...")
    print(f"[QuickBot] MAC: {mac}")
    print(f"[QuickBot] URL: {url}")
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            pagina = navegador.new_page()
            print("[QuickBot] Acessando página do QuickPlayer...")
            pagina.goto("https://quickplayer.app/#/upload-playlist")

            print("[QuickBot] Preenchendo MAC...")
            pagina.fill('input#mac', mac)

            print("[QuickBot] Aguardando validação do MAC...")
            pagina.wait_for_selector("span.message_success-text__NtfBt", timeout=5000)

            print("[QuickBot] Preenchendo URL da playlist...")
            pagina.fill('input#upload-playlist-by-url_url', url)

            # Preencher o campo EPG com a URL correta
            epg_url = get_epg_url_from_sheet()
            if epg_url:
                print(f"[QuickBot] Preenchendo EPG: {epg_url}")
                pagina.fill('input#upload-playlist-by-url_epg_url', epg_url)
            else:
                print("[QuickBot] Não foi possível obter a URL do EPG.")

            print("[QuickBot] Preenchendo nome da lista: PLUGTV")
            pagina.wait_for_selector('#upload-playlist-by-url_name', timeout=10000)
            pagina.fill('#upload-playlist-by-url_name', "PLUGTV")

            print("[QuickBot] Clicando no botão Upload...")
            pagina.click("button:has-text('Upload')")

            time.sleep(3)
            navegador.close()
            print("[QuickBot] Automação finalizada com sucesso.")
        return True
    except Exception as e:
        print("[ERRO QUICK]", e)
        return False
