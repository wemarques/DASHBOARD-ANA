# ✅ Solução Final: Adicionar Exceção no Windows Defender

Como não conseguimos desabilitar o Windows Defender (erro 0x800106ba), vamos adicionar uma **exceção permanente** para o arquivo hosts.

## 🎯 Método 1: Via Script PowerShell (Recomendado)

Execute como Administrador:

```powershell
cd C:\DASHBOARD-ANA\DASHBOARD-ANA
.\adicionar-excecao-defender.ps1
```

O script vai:
1. Adicionar exceção para o arquivo hosts
2. Abrir o Notepad automaticamente
3. Você edita e salva normalmente

## 🔧 Método 2: Manual (Se o script não funcionar)

### Passo 1: Adicionar Exceção

1. **Abra Configurações do Windows** (Windows + I)

2. **Vá em:**
   - **Privacidade e Segurança** → **Segurança do Windows**

3. **Clique em "Proteção contra vírus e ameaças"**

4. **Em "Configurações de proteção contra vírus e ameaças":**
   - Clique em **"Gerenciar configurações"**

5. **Role até "Exclusões":**
   - Clique em **"Adicionar ou remover exclusões"**

6. **Clique em "Adicionar uma exclusão"** → **"Arquivo"**

7. **Digite ou navegue até:**
   ```
   C:\Windows\System32\drivers\etc\hosts
   ```

8. **Clique em "Abrir"**

### Passo 2: Editar o Arquivo Hosts

Agora você pode editar normalmente:

```powershell
notepad C:\Windows\System32\drivers\etc\hosts
```

Ou via Explorador:
- Navegue até: `C:\Windows\System32\drivers\etc`
- Clique direito em `hosts` → Abrir com → Bloco de Notas

**Adicione no final do arquivo:**
```
127.0.0.1    dashboard-ana
```

**Salve (Ctrl+S)**

## ✅ Verificar

```powershell
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "dashboard-ana"
```

Se aparecer `127.0.0.1    dashboard-ana`, está correto!

## 🚀 Próximo Passo

Reinicie o Streamlit e acesse: `http://dashboard-ana:8501`

---

**Vantagem desta solução:** A exceção é permanente, então você poderá editar o arquivo hosts sempre que precisar sem problemas!

