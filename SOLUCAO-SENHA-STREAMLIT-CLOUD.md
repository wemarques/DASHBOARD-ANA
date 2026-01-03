# 🔧 Solução: Senha não Funciona no Streamlit Cloud

## ✅ Verificação

O hash está **correto** no código:
- Hash no arquivo: `5fd698c40bb0cc98f7c00994b523dec70d4ddc3393e6d67de47a3c11be2d1984`
- Senha correspondente: `ana2025`

## 🔍 Possíveis Causas

### 1. Cache do Navegador

**Solução:**
- Limpe o cache do navegador (`Ctrl + Shift + Delete`)
- OU use uma janela anônima/privada
- OU pressione `Ctrl + F5` para recarregar forçado

### 2. Estado de Sessão Antigo

**Solução:**
1. Feche completamente o navegador
2. Abra uma nova janela anônima
3. Acesse o link do Streamlit Cloud novamente
4. Tente fazer login

### 3. Código no GitHub Diferente

**Verifique:**
1. Acesse: https://github.com/wemarques/DASHBOARD-ANA/blob/master/app.py
2. Procure pela linha com `SENHA_HASH`
3. Deve ser: `SENHA_HASH = "5fd698c40bb0cc98f7c00994b523dec70d4ddc3393e6d67de47a3c11be2d1984"`

**Se estiver diferente:**
1. Faça commit novamente:
```bash
git add app.py
git commit -m "Corrigir hash da senha"
git push origin master
```
2. Aguarde o redeploy automático no Streamlit Cloud (1-2 minutos)

### 4. Erro ao Digitar

**Certifique-se de:**
- Digitar exatamente: `ana2025`
- Tudo minúsculo
- Sem espaços antes ou depois
- Sem caracteres especiais ocultos

## 🚀 Solução Rápida

1. **Faça commit novamente** (para garantir que o código está atualizado):
   ```bash
   git add app.py
   git commit -m "Garantir hash correto"
   git push origin master
   ```

2. **No Streamlit Cloud:**
   - Vá em "Settings" → "Reboot app" (se disponível)
   - Ou aguarde 1-2 minutos para redeploy automático

3. **Teste novamente:**
   - Abra uma janela anônima
   - Acesse o link do Streamlit Cloud
   - Digite: `ana2025`

## 🧪 Teste Local Primeiro

Antes de testar no Streamlit Cloud, teste localmente:

```bash
streamlit run app.py
```

Se funcionar localmente mas não funcionar no Cloud, é problema de cache ou estado de sessão.

## ✅ Se Ainda Não Funcionar

Crie um novo hash para uma senha diferente:

```python
import hashlib
nova_senha = "MINHA_NOVA_SENHA"
print(hashlib.sha256(nova_senha.encode()).hexdigest())
```

Depois atualize no `app.py` e faça commit novamente.

