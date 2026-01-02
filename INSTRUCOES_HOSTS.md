# 📝 Instruções para Configurar http://dashboard-ana

Para usar `http://dashboard-ana` ao invés de `http://localhost:8501`, você precisa editar o arquivo `hosts` do Windows.

## 🔧 Passos para Configuração

### 1. Abrir o arquivo hosts como Administrador

**Opção A - PowerShell (como Administrador):**
```powershell
notepad C:\Windows\System32\drivers\etc\hosts
```

**Opção B - Explorador de Arquivos:**
1. Abra o Explorador de Arquivos
2. Navegue até `C:\Windows\System32\drivers\etc\`
3. Clique com o botão direito em `hosts`
4. Selecione "Abrir com" → "Bloco de Notas"
5. Quando solicitado, escolha "Executar como administrador"

### 2. Adicionar a linha de mapeamento

Adicione esta linha no final do arquivo `hosts`:

```
127.0.0.1    dashboard-ana
```

O arquivo deve ficar assim:
```
# Copyright (c) 1993-2009 Microsoft Corp.
...
# localhost name resolution is handled within DNS itself.
127.0.0.1       localhost
::1             localhost
127.0.0.1       dashboard-ana    # <- Adicione esta linha
```

### 3. Salvar o arquivo

Salve o arquivo (Ctrl+S) e feche o editor.

### 4. Reiniciar o Streamlit

Pare o servidor Streamlit atual (Ctrl+C no terminal) e inicie novamente:

```bash
cd DASHBOARD-ANA
streamlit run app.py
```

### 5. Acessar o Dashboard

Agora você pode acessar usando:
- ✅ `http://dashboard-ana:8501`
- ✅ `http://127.0.0.1:8501` (continua funcionando)
- ✅ `http://localhost:8501` (continua funcionando)

## ⚠️ Observações Importantes

1. **Porta obrigatória**: Você ainda precisará incluir `:8501` na URL, pois o Streamlit roda nessa porta.
2. **Administrador necessário**: Editar o arquivo hosts requer privilégios de administrador.
3. **DNS local**: Esta configuração só funciona no seu computador local.
4. **Firewall**: Certifique-se de que a porta 8501 não está bloqueada pelo firewall.

## 🎯 Alternativa: Usar Porta 80 (Avançado)

Se quiser acessar apenas `http://dashboard-ana` (sem porta), seria necessário:
- Rodar o Streamlit na porta 80 (requer privilégios de administrador)
- OU configurar um proxy reverso (nginx, IIS, etc.)

Isso é mais complexo e geralmente não recomendado para desenvolvimento local.


