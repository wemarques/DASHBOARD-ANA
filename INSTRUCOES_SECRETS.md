# 🔐 Configurando Persistência de Dados (Secrets)

Para que o Dashboard Ana salve automaticamente suas alterações (quitações, antecipações) no GitHub e evite perda de dados, você precisa configurar o **Token de Acesso** no Streamlit Cloud.

## 1. Criar um Token no GitHub

1. Acesse [GitHub Developer Settings](https://github.com/settings/tokens).
2. Clique em **Generate new token** -> **Generate new token (classic)**.
3. Dê um nome (ex: `Streamlit Dashboard`).
4. Em **Select scopes**, marque a caixa:
   - [x] `repo` (Full control of private repositories)
5. Clique em **Generate token** no final da página.
6. **COPIE O TOKEN** (ele começa com `ghp_...`). Você não poderá vê-lo novamente.

## 2. Configurar no Streamlit Cloud

1. Acesse seu painel em [share.streamlit.io](https://share.streamlit.io/).
2. Localize o app `dashboard-ana`.
3. Clique nos três pontos (`⋮`) ao lado do app e selecione **Settings**.
4. Vá para a aba **Secrets**.
5. Na caixa de texto, cole o seguinte conteúdo (substituindo pelo seu token):

```toml
GITHUB_TOKEN = "cole_seu_token_aqui_ghp_xxxxxxxxxxxx"
```

6. Clique em **Save**.

## ✅ Pronto!

Agora o aplicativo terá permissão para salvar o arquivo `dados_dashboard_ana.json` diretamente no seu repositório GitHub toda vez que você fizer uma alteração.

### Como verificar se funcionou?
Faça uma alteração no app (ex: quite um mês ou adicione um item). Se não aparecer erro no canto superior direito e os dados persistirem após reiniciar a página, a configuração foi um sucesso.
