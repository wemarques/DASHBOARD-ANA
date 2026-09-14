# 🚀 Guia de Deploy Público - Dashboard Ana

Agora que o Dashboard Ana está protegido por senha, você pode publicá-lo de forma segura!

---

## 🔐 Sistema de Autenticação

✅ **Tela de login implementada**  
✅ **Senha padrão:** `<sua senha>`  
✅ **Hash SHA256** (seguro)  
✅ **Botão de logout** na sidebar  

---

## 🌐 Opções de Deploy Público

### 1️⃣ Streamlit Community Cloud (RECOMENDADO)

**Vantagens:**
- ✅ Gratuito para apps públicos
- ✅ Deploy automático do GitHub
- ✅ HTTPS incluído
- ✅ Fácil de usar

**Como fazer:**

1. **Acesse:** https://share.streamlit.io/

2. **Faça login** com sua conta GitHub

3. **Clique em "New app"**

4. **Preencha:**
   - Repository: `wemarques/DASHBOARD-ANA`
   - Branch: `master`
   - Main file path: `app.py`

5. **Clique em "Deploy"**

6. **Aguarde** alguns minutos

7. **Pronto!** Seu app estará disponível em:
   ```
   https://seu-usuario-dashboard-ana.streamlit.app
   ```

8. **Compartilhe o link** com quem você quiser. Só quem tiver a senha consegue acessar!

---

### 2️⃣ Render (Alternativa Gratuita)

**Vantagens:**
- ✅ Gratuito (750h/mês)
- ✅ Deploy automático
- ✅ HTTPS incluído

**Como fazer:**

1. **Acesse:** https://render.com/

2. **Crie uma conta gratuita**

3. **Clique em "New +" → "Web Service"**

4. **Conecte seu GitHub** e selecione `DASHBOARD-ANA`

5. **Configure:**
   - Name: `dashboard-ana`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

6. **Clique em "Create Web Service"**

7. **Aguarde o deploy** (5-10 minutos)

8. **Acesse:** `https://dashboard-ana.onrender.com`

---

### 3️⃣ Railway (Alternativa com Créditos)

**Vantagens:**
- ✅ $5 de crédito grátis/mês
- ✅ Deploy rápido
- ✅ Interface moderna

**Como fazer:**

1. **Acesse:** https://railway.app/

2. **Login com GitHub**

3. **New Project → Deploy from GitHub repo**

4. **Selecione** `DASHBOARD-ANA`

5. **Adicione variável de ambiente:**
   - `PORT`: `8501`

6. **Deploy automático!**

---

## 🔑 Gerenciamento de Senha

### Como Alterar a Senha

**Opção 1: Usar o script gerador**

```bash
python gerar_senha.py
```

Siga as instruções na tela e copie o hash gerado.

**Opção 2: Manualmente**

1. Abra o Python:
   ```python
   import hashlib
   nova_senha = "MINHA_NOVA_SENHA"
   print(hashlib.sha256(nova_senha.encode()).hexdigest())
   ```

2. Copie o hash

3. Edite `app.py` na linha ~27:
   ```python
   SENHA_HASH = "SEU_NOVO_HASH_AQUI"
   ```

4. Faça commit e push:
   ```bash
   git add app.py
   git commit -m "chore: Atualizar senha"
   git push origin master
   ```

5. O deploy será atualizado automaticamente!

---

## 📱 Compartilhamento

### Como Compartilhar com Outras Pessoas

1. **Obtenha o link** do seu app publicado (ex: `https://dashboard-ana.streamlit.app`)

2. **Compartilhe o link** + **senha** com quem você quiser:
   ```
   🔗 Link: https://dashboard-ana.streamlit.app
   🔑 Senha: <sua senha>
   ```

3. **Só quem tiver a senha** consegue acessar os dados!

---

## 🔒 Segurança

### ✅ O que está protegido:
- Acesso ao dashboard (requer senha)
- Dados financeiros (só visíveis após login)
- Edição de itens (só após autenticação)

### ⚠️ Importante:
- **Não compartilhe a senha publicamente**
- **Troque a senha padrão** (`<sua senha>`) por uma senha forte
- **Use senhas diferentes** para cada pessoa (se necessário, crie múltiplas versões)

### 💡 Dicas de Senha Forte:
- Mínimo 8 caracteres
- Letras maiúsculas e minúsculas
- Números e símbolos
- Exemplo: `Ana@Fin2025!`

---

## 🆘 Problemas Comuns

### App não carrega após deploy
- Verifique se `requirements.txt` está atualizado
- Veja os logs no painel da plataforma
- Certifique-se que `plotly` está no requirements

### Senha não funciona
- Verifique se o hash está correto no `app.py`
- Certifique-se de fazer commit e push após alterar
- Aguarde o redeploy automático (1-2 minutos)

### Dados não persistem
- Dados são salvos em `dados_dashboard_ana.json`
- Em deploys gratuitos, dados podem ser perdidos após reinicialização
- Para persistência permanente, considere usar banco de dados (PostgreSQL, MongoDB)

---

## 📊 Próximos Passos

Após o deploy, você pode:

1. ✅ **Testar o acesso** pelo link público
2. ✅ **Alterar a senha** para uma senha forte
3. ✅ **Compartilhar com outras pessoas**
4. ✅ **Acessar de qualquer lugar** (computador, celular, tablet)
5. ✅ **Fazer logout** quando terminar de usar

---

## 🎉 Pronto!

Seu Dashboard Ana agora está:
- 🌐 **Público** (acessível pela internet)
- 🔒 **Protegido** (requer senha)
- 📱 **Responsivo** (funciona em celular)
- 🚀 **Compartilhável** (envie o link para quem quiser)

---

**Desenvolvido com 🔐 segurança e ❤️ praticidade**
