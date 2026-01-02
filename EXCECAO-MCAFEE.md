# 🛡️ Adicionar Exceção no McAfee para Arquivo Hosts

Como você usa McAfee, precisa adicionar uma exceção no McAfee para poder editar o arquivo hosts.

## 🔧 Método: Adicionar Exceção no McAfee

### Passo 1: Abrir o McAfee

1. **Localize o ícone do McAfee** na bandeja do sistema (canto inferior direito)
   - OU procure "McAfee" no Menu Iniciar

2. **Clique com botão direito no ícone** → **"Abrir McAfee Security"**
   - OU clique duas vezes no ícone

### Passo 2: Adicionar Exceção de Arquivo

**Opção A - Interface Nova do McAfee:**

1. Na tela principal, procure por **"Proteção Real-Time"** ou **"Real-Time Scanning"**
2. Clique em **"Configurações"** ou **"Settings"**
3. Procure por **"Exclusões"**, **"Exclusions"** ou **"Exceções"**
4. Clique em **"Adicionar"** ou **"Add"**
5. Selecione **"Arquivo"** ou **"File"**
6. Digite ou navegue até:
   ```
   C:\Windows\System32\drivers\etc\hosts
   ```
7. Clique em **"OK"** ou **"Adicionar"**
8. Confirme as alterações

**Opção B - Menu Proteção:**

1. No McAfee, vá em **"Proteção"** ou **"Protection"**
2. Clique em **"Vírus e Spyware"** ou **"Virus and Spyware Protection"**
3. Clique em **"Configurações"** ou **"Settings"**
4. Procure por **"Exclusões"** ou **"Exclusions"**
5. Clique em **"Adicionar arquivo"** ou **"Add File"**
6. Digite: `C:\Windows\System32\drivers\etc\hosts`
7. Salve as alterações

**Opção C - Se Não Encontrar:**

1. No McAfee, procure por **"Configurações Avançadas"** ou **"Advanced Settings"**
2. Vá em **"Exclusões"** ou **"Exclusions"**
3. Adicione o arquivo: `C:\Windows\System32\drivers\etc\hosts`

### Passo 3: Desabilitar Temporariamente (Alternativa)

Se não conseguir adicionar exceção, pode desabilitar temporariamente:

1. No McAfee, vá em **"Configurações"**
2. **"Proteção Real-Time"** ou **"Real-Time Scanning"**
3. **Desative temporariamente**
4. Edite o arquivo hosts
5. **Reative imediatamente**

## 📝 Editar o Arquivo Hosts

Depois de adicionar a exceção (ou desabilitar temporariamente):

1. **Abra PowerShell como Administrador** (Windows + X → PowerShell Admin)

2. **Execute:**
   ```powershell
   notepad C:\Windows\System32\drivers\etc\hosts
   ```

3. **No Notepad:**
   - Vá até o final do arquivo
   - Adicione esta linha (em uma nova linha):
     ```
     127.0.0.1    dashboard-ana
     ```
   - Salve (Ctrl+S)
   - Feche o Notepad

4. **Se você desativou temporariamente, REATIVE o McAfee agora!**

## ✅ Verificar

```powershell
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "dashboard-ana"
```

Se aparecer `127.0.0.1    dashboard-ana`, está correto!

## 🚀 Próximo Passo

Reinicie o Streamlit e acesse: `http://dashboard-ana:8501`

---

**Nota:** A versão do McAfee pode variar, então os menus podem ter nomes ligeiramente diferentes. Procure por palavras-chave como: "Exclusões", "Exclusions", "Exceções", "Settings", "Configurações".

