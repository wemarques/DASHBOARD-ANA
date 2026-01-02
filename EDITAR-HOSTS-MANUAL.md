# 📝 Editar Arquivo Hosts Manualmente

Como o script automático está tendo problemas (arquivo bloqueado), siga estas instruções para editar manualmente:

## 🔧 Método 1: Via PowerShell (Recomendado)

1. **Abra o PowerShell como Administrador** (Windows + X → PowerShell Admin)

2. **Execute este comando:**
   ```powershell
   cd C:\DASHBOARD-ANA\DASHBOARD-ANA
   .\abrir-hosts-admin.ps1
   ```

   Ou execute diretamente:
   ```powershell
   notepad C:\Windows\System32\drivers\etc\hosts
   ```

3. **No Notepad que abrir:**
   - Vá até o final do arquivo
   - Adicione esta linha:
     ```
     127.0.0.1    dashboard-ana
     ```
   - Salve o arquivo (Ctrl+S)
   - Feche o Notepad

## 🔧 Método 2: Via Explorador de Arquivos

1. **Abra o Explorador de Arquivos** (Windows + E)

2. **Navegue até:**
   ```
   C:\Windows\System32\drivers\etc
   ```

3. **Clique com botão direito** no arquivo `hosts`

4. Selecione **"Abrir com"** → **"Bloco de Notas"**

5. **Se pedir permissão de administrador**, clique em **"Continuar"** ou **"Sim"**

6. **No Notepad:**
   - Vá até o final do arquivo
   - Adicione esta linha:
     ```
     127.0.0.1    dashboard-ana
     ```
   - Salve (Ctrl+S)
   - Feche

## ✅ Verificar se Funcionou

Após editar, teste no PowerShell:

```powershell
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "dashboard-ana"
```

Se aparecer a linha `127.0.0.1    dashboard-ana`, está correto!

## 🚀 Próximo Passo

Depois de configurar, reinicie o Streamlit e acesse:
- `http://dashboard-ana:8501`

