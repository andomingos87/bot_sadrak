# Bot Telegram Sadrak

Bot de automação para gestão de playlists IPTV, integração com Google Sheets e automação de fluxos para QuickPlayer e MaxPlayer.

## Funcionalidades
- Autenticação de usuários via Telegram
- Integração dinâmica com Google Sheets para URLs e dados
- Fluxos automatizados para QuickPlayer e MaxPlayer
- Gerenciamento de usuários e senhas
- Interface interativa por botões inline

## Pré-requisitos
- Python 3.8+
- Conta no Google Cloud com planilha e service account configurada
- Playwright instalado para automação de navegador
- Variáveis de ambiente configuradas (ver `.env`)

## Instalação
1. Clone o repositório:
   ```bash
   git clone git@github.com:andomingos87/bot_sadrak.git
   cd bot_sadrak
   ```
2. Crie um ambiente virtual e ative:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Instale o Playwright e os browsers:
   ```bash
   playwright install
   ```

## Configuração
1. Crie um arquivo `.env` com as variáveis:
   ```env
   BOT_TELEGRAM_API=seu_token_telegram
   API_SADRAK=seu_token_api
   LINK_SHEETS=url_da_sua_planilha_google
   PAINEL_MAX_EMAIL=seu_email
   PAINEL_MAX_SENHA=sua_senha
   ```
2. Coloque o arquivo `service_account.json` (Google Cloud) na raiz do projeto.

## Como rodar
```bash
python main.py
```
O bot ficará disponível no Telegram para interação.

## Observações
- A URL base do QuickPlayer é lida dinamicamente da aba `DNS` da sua planilha Google Sheets, célula `A2`.
- Não compartilhe seu `.env` nem `service_account.json`.
- O diretório `videos_quick/` e arquivos sensíveis estão no `.gitignore`.

## Dicas de uso
- Use `/entrar` para iniciar o fluxo de autenticação.
- Siga as instruções do bot para cada etapa.
- Se tiver problemas, envie `/sair` e recomece.

---

Desenvolvido por Anderson Domingos

