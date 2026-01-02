# 🚀 Guia Rápido de Atualização e Acesso

## 📥 Como Atualizar o Dashboard no Seu Computador

Se você já tem o projeto clonado e quer obter as novas funcionalidades:

### Passo 1: Abra o terminal na pasta do projeto

```bash
cd DASHBOARD-ANA
```

### Passo 2: Baixe as atualizações do GitHub

```bash
git pull origin master
```

### Passo 3: Atualize as dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Execute o dashboard

```bash
streamlit run app.py
```

---

## 📱 Como Acessar pelo Celular

### Requisitos
- Celular e computador devem estar **na mesma rede Wi-Fi**
- O dashboard deve estar rodando no computador

### Passo a Passo

#### 1️⃣ Descubra o IP do seu computador

**No Windows (PowerShell ou CMD):**
```bash
ipconfig
```
Procure por **"Endereço IPv4"** (exemplo: `192.168.1.100`)

**No macOS (Terminal):**
```bash
ifconfig | grep "inet "
```

**No Linux (Terminal):**
```bash
hostname -I
```

#### 2️⃣ Execute o Streamlit com acesso externo

No terminal, na pasta do projeto:

```bash
streamlit run app.py --server.address 0.0.0.0
```

#### 3️⃣ Acesse pelo celular

Abra o navegador do celular e digite:

```
http://SEU_IP:8501
```

**Exemplo real:**
Se o IP do seu computador for `192.168.1.100`, acesse:
```
http://192.168.1.100:8501
```

---

## ✨ Novas Funcionalidades (Janeiro 2026)

### 1. Editar e Excluir TODOS os Itens
- Agora você pode editar e excluir **qualquer item**, incluindo os itens padrão (Plano de Saúde, Geladeira, etc.)
- Cada item tem botões de **✏️ Editar** e **🗑️ Excluir**

### 2. Quadro Resumo Gerencial
- **Métricas visuais**: Total de débitos, créditos, saldo e percentual de meses quitados
- **Gráfico de Evolução Mensal**: Barras coloridas mostrando saldo positivo (verde) e negativo (vermelho)
- **Gráfico de Pizza**: Visualize a proporção de cada despesa no total
- **Tabela Resumo**: Lista completa de itens com totais acumulados

### 3. Interface Melhorada
- Design mais profissional e organizado
- Ícones visuais para facilitar navegação
- Cores e formatação aprimoradas

---

## 🔧 Solução de Problemas

### Não consigo acessar pelo celular

**Verifique:**
1. ✅ Celular e computador estão na **mesma rede Wi-Fi**?
2. ✅ Você executou com `--server.address 0.0.0.0`?
3. ✅ O IP está correto?
4. ✅ O firewall do computador não está bloqueando a porta 8501?

**Desabilitar firewall temporariamente (Windows):**
- Painel de Controle → Sistema e Segurança → Firewall do Windows → Desativar firewall

### Erro ao instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Porta 8501 já está em uso

O Streamlit automaticamente usará a próxima porta disponível (8502, 8503, etc.). Verifique a mensagem no terminal.

---

## 📞 Precisa de Ajuda?

Abra uma issue no GitHub: https://github.com/wemarques/DASHBOARD-ANA/issues

---

**Desenvolvido com ❤️ para gestão financeira pessoal**
