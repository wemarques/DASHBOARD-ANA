# 🔒 Resolvendo Bloqueio do Arquivo Hosts - Guia Definitivo

O arquivo hosts está completamente bloqueado (nem consegue ler). Isso indica bloqueio agressivo do antivírus/Windows Defender.

## ✅ SOLUÇÃO DEFINITIVA (Recomendada)

### Desabilitar Windows Defender Temporariamente

**IMPORTANTE:** Faça isso apenas enquanto edita, depois REATIVE imediatamente!

1. **Abra Configurações do Windows:**
   - Pressione `Windows + I`
   - OU clique no Menu Iniciar → Configurações

2. **Navegue até Segurança:**
   - **Privacidade e Segurança** → **Segurança do Windows**
   - OU digite "Segurança do Windows" no menu Iniciar

3. **Abra Proteção contra vírus e ameaças**

4. **Em "Configurações de proteção contra vírus e ameaças":**
   - Clique em **"Gerenciar configurações"**

5. **Desative temporariamente:**
   - **"Proteção em tempo real"** → Desligar
   - Se perguntar, confirme

6. **AGORA edite o arquivo hosts:**
   ```powershell
   notepad C:\Windows\System32\drivers\etc\hosts
   ```
   
   Adicione no final:
   ```
   127.0.0.1    dashboard-ana
   ```
   
   Salve (Ctrl+S) e feche

7. **REATIVE IMEDIATAMENTE a Proteção em tempo real!**

## 🔧 Alternativa: Adicionar Exceção Permanente

Se você vai editar hosts com frequência, adicione uma exceção permanente:

1. **Segurança do Windows** → **Proteção contra vírus e ameaças**

2. **Configurações** → **Gerenciar configurações**

3. Role até **"Exclusões"** → **"Adicionar ou remover exclusões"**

4. **"Adicionar uma exclusão"** → **"Arquivo"**

5. Digite ou navegue até:
   ```
   C:\Windows\System32\drivers\etc\hosts
   ```

6. Clique em **"Abrir"**

Agora você poderá editar o arquivo hosts normalmente sem desabilitar a proteção!

## 🆘 Se Você Tem Antivírus de Terceiros

Se você usa Avast, Kaspersky, Norton, McAfee, Bitdefender, etc.:

1. Abra o programa do antivírus
2. Procure por:
   - "Proteção de arquivos do sistema"
   - "Proteção de hosts"
   - "Exclusões" ou "Exceções"
3. Adicione uma exceção para: `C:\Windows\System32\drivers\etc\hosts`
4. Ou desative temporariamente a proteção

## ⚡ Método Rápido via PowerShell (Desabilitar/Reativar)

Se você quiser fazer tudo pelo PowerShell (requer Admin):

### Desabilitar:
```powershell
Set-MpPreference -DisableRealtimeMonitoring $true
```

### Editar hosts:
```powershell
notepad C:\Windows\System32\drivers\etc\hosts
```

### Reativar:
```powershell
Set-MpPreference -DisableRealtimeMonitoring $false
```

⚠️ **ATENÇÃO:** Use este método apenas se souber o que está fazendo. Reative SEMPRE após editar!

## ✅ Verificar se Funcionou

Depois de editar, verifique:

```powershell
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "dashboard-ana"
```

Se aparecer `127.0.0.1    dashboard-ana`, está correto!

## 🚀 Próximo Passo

Reinicie o Streamlit e acesse: `http://dashboard-ana:8501`

