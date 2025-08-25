# FenixBot - Deploy GitHub

## Como hospedar gratuitamente:

### 1. No Railway (GRÁTIS):
1. Crie conta no [Railway](https://railway.app)
2. Conecte seu GitHub
3. Importe este repositório
4. Adicione variável `DISCORD_TOKEN` nas settings
5. Deploy automático!

### 2. No Heroku:
1. Crie conta no [Heroku](https://heroku.com)
2. Instale Heroku CLI
3. Clone o repositório
4. Configure o token:
   ```bash
   heroku config:set DISCORD_TOKEN=seu_token_aqui
   ```
5. Deploy: `git push heroku main`

### 3. No Render (GRÁTIS):
1. Conecte GitHub no [Render](https://render.com)
2. Crie Web Service
3. Configure variável DISCORD_TOKEN
4. Deploy!

## Arquivos incluídos:
- `Procfile` - Para Heroku
- `requirements_github.txt` - Dependências
- `runtime.txt` - Versão Python
- `.env.example` - Exemplo de variáveis

## Comandos do bot:
- `/setup` - Configurar categorias
- `/painel` - Criar painel de tickets

Bot roda 24/7 automaticamente após deploy!