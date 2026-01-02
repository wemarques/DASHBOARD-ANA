# 📊 Dashboard Ana

Um **sistema financeiro pessoal** desenvolvido com Streamlit para gerenciar despesas, receitas e prazos de forma intuitiva e visual.

## 🎯 Funcionalidades

- **Gerenciamento de Despesas e Receitas**: Adicione, edite e remova itens de despesa ou receita com valores mensais.
- **Prazos Flexíveis**: Defina períodos de início e fim para cada item (ex: parcelamentos, assinaturas).
- **Controle de Quitação**: Marque meses como "quitados" para acompanhar o progresso.
- **Resumo Financeiro**: Visualize totais de débitos, créditos e saldo em tempo real.
- **Filtro por Ano**: Navegue facilmente entre os anos (2025 a 2028).
- **Persistência de Dados**: Todos os dados são salvos localmente em JSON.

## 🚀 Como Instalar

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

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

Execute a aplicação com o comando:

```bash
streamlit run app.py
```

A aplicação será aberta no seu navegador padrão em `http://localhost:8501`.

### Interface Principal

- **Quadro Resumo**: Exibe totais de débitos, créditos, saldo e meses quitados.
- **Adicionar Novo Item**: Expanda a seção para criar uma nova despesa ou receita.
- **Filtro por Ano**: Selecione um ano específico para visualizar apenas aquele período.
- **Cards de Mês**: Cada mês é exibido em um card expansível com detalhes dos itens e saldo.
- **Itens Personalizados**: Gerencie os itens que você criou (editar/remover).

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

- Itens personalizados (nome, valor, tipo, período)
- Meses marcados como quitados

**Nota**: Este arquivo contém informações financeiras pessoais. Não o compartilhe publicamente.

## 🛠️ Desenvolvimento

### Estrutura de Código

- **Geração de Meses**: Função que cria lista de meses de jan/25 a dez/28.
- **Itens Padrão**: Despesas pré-configuradas (Plano de Saúde, Viagem, etc.).
- **Cálculo de DataFrame**: Monta tabela com todos os itens e calcula saldos.
- **Interface Streamlit**: Componentes visuais e interatividade.

### Extensões Futuras

- Gráficos de tendências financeiras
- Exportação de relatórios em PDF
- Categorização de despesas
- Integração com APIs de bancos

## 📄 Licença

Este projeto é de uso pessoal. Sinta-se livre para modificar e adaptar conforme necessário.

## 👤 Autor

Desenvolvido para gerenciar finanças pessoais de forma prática e visual.

---

**Dúvidas ou sugestões?** Sinta-se à vontade para abrir uma issue ou entrar em contato.
