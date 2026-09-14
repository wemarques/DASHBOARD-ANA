# 🔧 Troubleshooting - Problema com Senha

## ✅ Hash Verificado

O hash no arquivo está **CORRETO** para a senha `<sua senha>`:
- Hash no arquivo: `<hash configurado em Secrets: SENHA_HASH>`
- Senha correspondente: `<sua senha>`

## 🔍 Soluções Possíveis

### 1. Reiniciar o Streamlit

**Pare completamente o Streamlit:**
- No PowerShell, pressione `Ctrl + C` para parar
- Aguarde alguns segundos

**Inicie novamente:**
```powershell
cd C:\DASHBOARD-ANA\DASHBOARD-ANA
streamlit run app.py
```

### 2. Limpar Cache do Streamlit

O Streamlit pode estar usando cache antigo:

```powershell
# Pare o Streamlit primeiro (Ctrl + C)

# Limpar cache
streamlit cache clear

# Ou delete manualmente:
# Windows: C:\Users\<seu-usuario>\.streamlit\cache
```

### 3. Limpar Cache do Navegador

- Pressione `Ctrl + Shift + Delete`
- Ou use modo anônimo/privado do navegador
- Ou pressione `Ctrl + F5` para recarregar forçado

### 4. Verificar se Digitou Corretamente

Certifique-se de digitar exatamente: `<sua senha>`
- Sem espaços antes ou depois
- Tudo minúsculo
- Sem caracteres especiais ocultos

### 5. Usar o Modo Debug

Eu adicionei um modo debug temporário. Quando tentar entrar com senha errada:

1. Clique em "🔍 Debug (remover após testar)" que aparecerá
2. Veja os valores de hash sendo comparados
3. Isso ajuda a identificar o problema

### 6. Verificar se o Arquivo foi Salvo

Certifique-se de que:
- O arquivo `app.py` foi salvo (Ctrl+S)
- Você está editando o arquivo correto
- Não há múltiplas cópias do arquivo

### 7. Verificar Estado da Sessão

Se você já estava autenticado antes, pode haver um estado antigo:

1. Pare o Streamlit
2. Feche completamente o navegador
3. Inicie o Streamlit novamente
4. Tente entrar com a senha

## 🧪 Teste Rápido

Execute este comando para verificar o hash:

```powershell
python -c "import hashlib; print(hashlib.sha256('<sua senha>'.encode()).hexdigest())"
```

Deve retornar: `<hash configurado em Secrets: SENHA_HASH>`

## ✅ Se Nada Funcionar

1. Pare o Streamlit
2. Delete o cache: `streamlit cache clear`
3. Feche o navegador completamente
4. Reinicie o Streamlit
5. Abra uma nova janela anônima
6. Acesse `http://localhost:8501`
7. Digite: `<sua senha>`

---

**Nota:** O modo debug foi adicionado temporariamente. Após resolver o problema, você pode removê-lo do código se desejar.

