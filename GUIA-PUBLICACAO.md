# 🌐 Guia Completo de Publicação - Dashboard Ana

Este guia mostra como publicar seu Dashboard Ana na internet para acesso público ou privado.

## 📋 Opções de Publicação

1. **[Streamlit Cloud](#streamlit-cloud-recomendado)** ⭐ (Mais fácil e gratuito)
2. [Render](#render-gratuito)
3. [Heroku](#heroku)
4. [AWS/Azure/GCP](#aws-azure-gcp-avancado)
5. [VPS Próprio](#vps-proprio)

---

## 🚀 Streamlit Cloud (Recomendado)

**Vantagens:**
- ✅ Totalmente gratuito
- ✅ Deploy automático via GitHub
- ✅ Atualização automática a cada push
- ✅ HTTPS incluído
- ✅ Muito fácil de configurar

### Passo 1: Preparar o Repositório

Certifique-se de que seu código está no GitHub:

```bash
# Se ainda não fez commit:
git add .
git commit -m "Preparar para deploy"
git push origin master
```

### Passo 2: Criar Arquivo de Configuração (Opcional)

Crie um arquivo `.streamlit/config.toml` na raiz do projeto:

```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

### Passo 3: Publicar no Streamlit Cloud

1. **Acesse:** https://streamlit.io/cloud
2. **Faça login** com sua conta GitHub
3. **Clique em "New app"**
4. **Configure:**
   - **Repository:** Seu repositório GitHub
   - **Branch:** `master` (ou a branch principal)
   - **Main file:** `app.py`
   - **App URL:** Escolha um nome único (ex: `dashboard-ana`)
5. **Clique em "Deploy"**

Aplicação estará disponível em: `https://dashboard-ana.streamlit.app`

### ⚠️ Importante: Segurança

Como sua aplicação tem senha, você pode:

1. **Manter a senha** (público com proteção por senha)
2. **Remover a senha** (totalmente público)
3. **Adicionar autenticação extra** via Streamlit Secrets

**Para adicionar senha via Secrets:**

1. No Streamlit Cloud, vá em **"Settings"** → **"Secrets"**
2. Adicione:
```toml
[senha]
HASH = "<hash configurado em Secrets: SENHA_HASH>"
```

---

## 🔵 Render (Gratuito)

Render oferece hospedagem gratuita com algumas limitações.

### Passo 1: Criar arquivos de configuração

**Crie `render.yaml` na raiz:**
```yaml
services:
  - type: web
    name: dashboard-ana
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: PORT
        value: 8501
```

### Passo 2: Publicar no Render

1. **Acesse:** https://render.com
2. **Crie uma conta** (pode usar GitHub)
3. **Clique em "New +"** → **"Web Service"**
4. **Conecte seu repositório GitHub**
5. **Configure:**
   - **Name:** dashboard-ana
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
6. **Clique em "Create Web Service"**

---

## 🟣 Heroku

Heroku oferece plano gratuito limitado.

### Passo 1: Instalar Heroku CLI

Baixe em: https://devcenter.heroku.com/articles/heroku-cli

### Passo 2: Criar arquivos necessários

**Crie `Procfile` na raiz:**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Crie `setup.sh`:**
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = \$PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

**Atualize `requirements.txt`** (certifique-se de incluir todas as dependências):
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.0.0
```

### Passo 3: Publicar

```bash
# Login no Heroku
heroku login

# Criar app
heroku create dashboard-ana

# Publicar
git push heroku master

# Abrir
heroku open
```

---

## ☁️ AWS / Azure / GCP (Avançado)

Para ambientes de produção mais robustos.

### AWS (EC2 ou Elastic Beanstalk)

1. **Criar instância EC2**
2. **Instalar Python e dependências**
3. **Configurar Nginx como proxy reverso**
4. **Usar PM2 ou systemd para manter rodando**

### Azure (App Service)

1. **Criar App Service**
2. **Configurar deployment via GitHub**
3. **Ajustar configurações de Python**

### Google Cloud Platform (Cloud Run)

1. **Criar Dockerfile**
2. **Publicar container no Cloud Run**
3. **Configurar HTTPS**

---

## 🖥️ VPS Próprio

Se você tem um servidor próprio (DigitalOcean, Linode, etc.)

### Passo 1: Conectar ao servidor

```bash
ssh usuario@seu-servidor.com
```

### Passo 2: Instalar dependências

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python
sudo apt install python3 python3-pip -y

# Instalar Nginx
sudo apt install nginx -y
```

### Passo 3: Clonar repositório

```bash
cd /var/www
git clone https://github.com/seu-usuario/DASHBOARD-ANA.git
cd DASHBOARD-ANA
pip3 install -r requirements.txt
```

### Passo 4: Configurar Nginx

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Passo 5: Usar PM2 para manter rodando

```bash
# Instalar PM2
npm install -g pm2

# Iniciar aplicação
cd /var/www/DASHBOARD-ANA
pm2 start "streamlit run app.py --server.port 8501" --name dashboard-ana

# Salvar configuração
pm2 save
pm2 startup
```

---

## 🔒 Considerações de Segurança

### 1. Senha de Acesso

- ✅ Mantenha a senha forte
- ✅ Considere usar variáveis de ambiente para o hash
- ✅ Não commite o hash no código (use secrets)

### 2. HTTPS

- ✅ Streamlit Cloud inclui HTTPS automaticamente
- ✅ Para outros serviços, configure SSL/TLS (Let's Encrypt é gratuito)

### 3. Dados Sensíveis

- ✅ Não commite `dados_dashboard_ana.json`
- ✅ Use banco de dados ou storage seguro em produção
- ✅ Considere criptografar dados sensíveis

### 4. Rate Limiting

- ✅ Configure limites de requisições
- ✅ Use autenticação adicional se necessário

---

## 📝 Checklist Antes de Publicar

- [ ] Código está no GitHub
- [ ] `requirements.txt` está atualizado
- [ ] `.gitignore` exclui arquivos sensíveis
- [ ] Senha está configurada corretamente
- [ ] Testado localmente
- [ ] README está atualizado

---

## 🆘 Problemas Comuns

### Erro ao fazer deploy

- Verifique se todas as dependências estão em `requirements.txt`
- Confirme que o arquivo principal é `app.py`
- Veja os logs de erro no painel do serviço

### Aplicação não inicia

- Verifique os logs de erro
- Confirme que a porta está configurada corretamente
- Teste localmente primeiro

### Dados não persistem

- Em serviços cloud, os dados podem ser temporários
- Considere usar banco de dados ou storage permanente

---

## 🎯 Recomendação Final

Para começar rapidamente, use **Streamlit Cloud**:
- ✅ Mais fácil
- ✅ Gratuito
- ✅ Sem configuração complexa
- ✅ Atualização automática

Acesse: https://streamlit.io/cloud

---

**Dúvidas?** Consulte a documentação do serviço escolhido ou abra uma issue no GitHub.

