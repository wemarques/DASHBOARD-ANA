# 🔒 Solução para Arquivo Hosts Bloqueado

O arquivo hosts está sendo bloqueado por um processo de segurança (antivírus/Windows Defender).

## 🎯 Solução Rápida (Recomendada)

### Opção 1: Desabilitar Temporariamente o Windows Defender

1. **Abra as Configurações do Windows** (Windows + I)

2. **Vá em:**
   - **Privacidade e Segurança** → **Segurança do Windows**
   - Ou digite "Windows Security" no menu Iniciar

3. **Clique em "Proteção contra vírus e ameaças"**

4. **Em "Configurações de proteção contra vírus e ameaças"**, clique em **"Gerenciar configurações"**

5. **Desabilite temporariamente "Proteção em tempo real"**

6. **Agora tente editar o arquivo hosts novamente:**
   ```powershell
   notepad C:\Windows\System32\drivers\etc\hosts
   ```

7. **Depois de editar, REATIVE a proteção em tempo real!**

### Opção 2: Adicionar Exceção no Windows Defender

1. **Abra Segurança do Windows** (Windows + I → Privacidade e Segurança → Segurança do Windows)

2. **Vá em "Proteção contra vírus e ameaças"**

3. **Em "Configurações de proteção contra vírus e ameaças"**, clique em **"Gerenciar configurações"**

4. **Role até "Exclusões"** e clique em **"Adicionar ou remover exclusões"**

5. **Clique em "Adicionar uma exclusão"** → **"Arquivo"**

6. **Adicione:**
   ```
   C:\Windows\System32\drivers\etc\hosts
   ```

7. **Agora tente editar o arquivo hosts novamente**

## 🔧 Método Alternativo: Copiar e Colar

Se ainda não funcionar, tente este método:

1. **Copie o arquivo hosts para outro local:**
   ```powershell
   Copy-Item C:\Windows\System32\drivers\etc\hosts C:\temp\hosts -Force
   ```

2. **Edite a cópia:**
   ```powershell
   notepad C:\temp\hosts
   ```
   - Adicione a linha: `127.0.0.1    dashboard-ana`
   - Salve

3. **Copie de volta (como Administrador):**
   ```powershell
   Copy-Item C:\temp\hosts C:\Windows\System32\drivers\etc\hosts -Force
   ```

## ⚠️ Se Você Tem Antivírus de Terceiros

Se você usa Avast, Kaspersky, Norton, McAfee, etc.:

1. Abra o programa do antivírus
2. Procure por "Exclusões" ou "Exceções"
3. Adicione o arquivo `C:\Windows\System32\drivers\etc\hosts` às exceções
4. Tente editar novamente

## ✅ Após Editar

Depois de adicionar a linha `127.0.0.1    dashboard-ana` ao arquivo hosts:

1. **Verifique se funcionou:**
   ```powershell
   Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "dashboard-ana"
   ```

2. **Reinicie o Streamlit**

3. **Acesse:** `http://dashboard-ana:8501`

