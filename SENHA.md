# 🔐 Configuração de Senha do Dashboard Ana

## 🔑 Senha Padrão

**Senha atual:** `ana2025`

---

## 🔄 Como Alterar a Senha

### Opção 1: Gerar Nova Senha (Recomendado)

1. **Abra o terminal/PowerShell**

2. **Execute o Python para gerar o hash da sua nova senha:**

```python
import hashlib

# Substitua "MINHA_NOVA_SENHA" pela senha que você quer usar
nova_senha = "MINHA_NOVA_SENHA"
hash_senha = hashlib.sha256(nova_senha.encode()).hexdigest()
print(f"Hash da senha: {hash_senha}")
```

3. **Copie o hash gerado**

4. **Abra o arquivo `app.py`**

5. **Procure pela linha** (por volta da linha 27):

```python
SENHA_HASH = "8b5e7c8c8f3c3e4a9d2f1b6a7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d"
```

6. **Substitua o hash** pelo hash que você gerou:

```python
SENHA_HASH = "SEU_NOVO_HASH_AQUI"
```

7. **Salve o arquivo**

---

### Opção 2: Usar o Script Gerador de Senha

1. **Crie um arquivo chamado `gerar_senha.py`** na pasta do projeto:

```python
import hashlib

print("=== Gerador de Hash de Senha ===\n")
senha = input("Digite a nova senha: ")
hash_senha = hashlib.sha256(senha.encode()).hexdigest()

print(f"\n✅ Hash gerado com sucesso!")
print(f"📋 Copie o hash abaixo:\n")
print(hash_senha)
print(f"\n💡 Cole este hash no arquivo app.py na linha SENHA_HASH")
```

2. **Execute:**

```bash
python gerar_senha.py
```

3. **Siga as instruções na tela**

---

## 🔒 Segurança

- A senha é armazenada como **hash SHA256** (não é possível reverter para a senha original)
- Nunca compartilhe o arquivo `app.py` com o hash da senha
- Use senhas fortes (mínimo 8 caracteres, letras, números e símbolos)

---

## 🚪 Como Fazer Logout

Após fazer login, você verá um botão **"🚪 Sair"** na barra lateral esquerda. Clique nele para fazer logout.

---

## 💡 Dicas

- **Senha esquecida?** Você precisará editar o `app.py` e gerar um novo hash
- **Múltiplos usuários?** Atualmente o sistema suporta apenas uma senha. Para múltiplos usuários, considere usar Streamlit Cloud com autenticação OAuth
- **Senha muito simples?** Use um gerenciador de senhas para criar senhas fortes

---

## 📝 Exemplos de Senhas Fortes

❌ **Fracas:** `123456`, `senha`, `ana`  
✅ **Fortes:** `Ana@2025!Financ`, `D@sh#Ana$2025`, `F1n@nc3!Ana25`

---

**Desenvolvido com 🔒 segurança em mente**
