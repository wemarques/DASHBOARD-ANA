# 📊 Dashboard Ana

Um **sistema de gestão financeira pessoal** desenvolvido com Streamlit para gerenciar despesas, receitas e prazos de forma intuitiva e visual, com gráficos interativos e análises gerenciais.

## 🎯 Funcionalidades

### 💼 Gestão Financeira
- **Adicionar, Editar e Excluir Itens**: Gerencie todos os itens de despesa ou receita (incluindo itens padrão).
- **Prazos Flexíveis**: Defina períodos de início e fim para cada item (ex: parcelamentos, assinaturas).
- **Controle de Quitação**: Marque meses como "quitados" para acompanhar o progresso.

### 📊 Visualizações Gerenciais
- **Métricas em Tempo Real**: Total de débitos, créditos, saldo e percentual de meses quitados.
- **Gráfico de Evolução Mensal**: Visualize o saldo mês a mês com barras coloridas (positivo/negativo).
- **Gráfico de Pizza**: Veja a distribuição proporcional de suas despesas.
- **Tabela Resumo**: Lista completa de itens com totais acumulados.

### 📅 Detalhamento
- **Filtro por Ano**: Navegue facilmente entre os anos (2025 a 2028).
- **Detalhamento Mensal**: Expanda cada mês para ver itens, prazos e saldos específicos.
- **Persistência de Dados**: Todos os dados são salvos localmente em JSON.

## 🚀 Como Instalar

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Passos de Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/wemarques/DASHBOARD-ANA.git
   cd DASHBOARD-ANA
   ```

2. **Crie um ambiente virtual** (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Como Usar

### 💻 Acesso Local (Computador)

Execute a aplicação com o comando:

```bash
streamlit run app.py
```

A aplicação será aberta no seu navegador padrão em `http://localhost:8501`.

### 📱 Acesso via Celular (Mesma Rede Wi-Fi)

Para acessar o dashboard pelo celular, você precisa estar **na mesma rede Wi-Fi** que o computador onde o Streamlit está rodando.

#### Passo 1: Descobrir o IP do Computador

**No Windows:**
```bash
ipconfig
```
Procure por "Endereço IPv4" (exemplo: `192.168.1.100`)

**No macOS/Linux:**
```bash
ifconfig
# ou
ip addr show
```
Procure pelo endereço IP da interface de rede ativa (exemplo: `192.168.1.100`)

#### Passo 2: Executar o Streamlit com Acesso Externo

```bash
streamlit run app.py --server.address 0.0.0.0
```

#### Passo 3: Acessar pelo Celular

No navegador do celular, digite:

```
http://SEU_IP:8501
```

**Exemplo:** Se o IP do seu computador for `192.168.1.100`, acesse:
```
http://192.168.1.100:8501
```

### 🔒 Nota de Segurança

- O acesso via celular só funciona na **mesma rede Wi-Fi**.
- Para acesso público pela internet, considere usar serviços como **Streamlit Cloud**, **Heroku** ou **AWS**.

## 📝 Estrutura do Projeto

```
DASHBOARD-ANA/
├── app.py                    # Aplicação principal Streamlit
├── requirements.txt          # Dependências do projeto
├── .gitignore               # Arquivos ignorados pelo Git
├── README.md                # Este arquivo
└── dados_dashboard_ana.json # Dados salvos (gerado automaticamente)
```

## 💾 Dados

Os dados são salvos automaticamente em `dados_dashboard_ana.json` e incluem:

- Todos os itens (despesas e receitas) com seus detalhes
- Meses marcados como quitados

**Nota**: Este arquivo contém informações financeiras pessoais. Não o compartilhe publicamente.

## 🛠️ Desenvolvimento

### Estrutura de Código

- **Geração de Meses**: Função que cria lista de meses de jan/25 a dez/28.
- **Sistema de Itens Unificado**: Todos os itens (padrão e personalizados) são gerenciados da mesma forma.
- **Cálculo de DataFrame**: Monta tabela com todos os itens e calcula saldos.
- **Visualizações com Plotly**: Gráficos interativos de evolução e distribuição.
- **Interface Streamlit**: Componentes visuais e interatividade.

### Tecnologias Utilizadas

- **Streamlit**: Framework web para aplicações de dados
- **Pandas**: Manipulação e análise de dados
- **Plotly**: Gráficos interativos e visualizações

### Extensões Futuras

- Upload de PDFs de faturas e contracheques
- Categorização automática de despesas
- Exportação de relatórios em PDF/Excel
- Integração com APIs de bancos
- Previsões e análises preditivas
- Deploy em nuvem para acesso remoto

## 🎨 Interface

### Resumo Gerencial
- Métricas principais com destaque visual
- Gráfico de barras de evolução mensal do saldo
- Gráfico de pizza com distribuição de despesas
- Tabela resumo de todos os itens cadastrados

### Gerenciar Itens
- Adicionar novos itens de despesa ou receita
- Editar qualquer item existente (nome, valor, tipo, período)
- Excluir itens que não são mais necessários

### Detalhamento Mensal
- Filtro por ano para facilitar navegação
- Cards expansíveis para cada mês
- Visualização de itens ativos no mês
- Indicador de prazos (prestações)
- Botão para marcar/desmarcar mês como quitado

## 📄 Licença

Este projeto é de uso pessoal. Sinta-se livre para modificar e adaptar conforme necessário.

## 👤 Autor

Desenvolvido para gerenciar finanças pessoais de forma prática, visual e profissional.

---

## 🆘 Suporte

**Problemas comuns:**

1. **Erro ao instalar dependências**: Certifique-se de ter Python 3.8+ instalado.
2. **Porta 8501 ocupada**: O Streamlit usará automaticamente a próxima porta disponível.
3. **Não consigo acessar pelo celular**: Verifique se está na mesma rede Wi-Fi e se o firewall não está bloqueando a porta 8501.

**Dúvidas ou sugestões?** Abra uma issue no GitHub ou entre em contato.

---

**Última atualização:** Janeiro 2026
