# 🔐 Como Executar Script como Administrador

## Método 1: PowerShell - Clique com Botão Direito (Mais Fácil)

1. **Navegue até a pasta** `DASHBOARD-ANA` no Explorador de Arquivos
2. **Clique com o botão direito** no arquivo `configurar-hosts.ps1`
3. Selecione **"Executar com PowerShell"** ou **"Executar como administrador"**
4. Se aparecer um aviso, clique em **"Sim"** para permitir

## Método 2: PowerShell Aberto como Administrador

1. **Abra o Menu Iniciar** (Windows)
2. Digite **"PowerShell"**
3. **Clique com o botão direito** em "Windows PowerShell" ou "PowerShell"
4. Selecione **"Executar como administrador"**
5. Clique em **"Sim"** quando solicitado
6. No PowerShell aberto, execute:
   ```powershell
   cd C:\DASHBOARD-ANA\DASHBOARD-ANA
   .\configurar-hosts.ps1
   ```

## Método 3: Terminal do Windows (Windows Terminal)

1. **Abra o Menu Iniciar** e digite **"Terminal"** ou **"Windows Terminal"**
2. Clique com botão direito → **"Executar como administrador"**
3. No terminal, execute:
   ```powershell
   cd C:\DASHBOARD-ANA\DASHBOARD-ANA
   .\configurar-hosts.ps1
   ```

## Método 4: Prompt de Comando (CMD) como Administrador

1. **Abra o Menu Iniciar** e digite **"cmd"**
2. **Clique com o botão direito** em "Prompt de Comando"
3. Selecione **"Executar como administrador"**
4. Execute:
   ```cmd
   cd C:\DASHBOARD-ANA\DASHBOARD-ANA
   powershell -ExecutionPolicy Bypass -File .\configurar-hosts.ps1
   ```

## ⚠️ Se Der Erro de Política de Execução

Se aparecer um erro sobre política de execução, execute este comando primeiro:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois execute o script novamente.

## ✅ Verificação

Após executar, o script mostrará uma mensagem de sucesso. Você pode verificar se funcionou abrindo o arquivo hosts:

```powershell
notepad C:\Windows\System32\drivers\etc\hosts
```

Procure pela linha: `127.0.0.1    dashboard-ana`


