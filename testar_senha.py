#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para testar a função de hash de senha"""

import hashlib

def hash_senha(senha):
    """Gera hash SHA256 da senha"""
    return hashlib.sha256(senha.encode()).hexdigest()

# Testar
SENHA_HASH = "5fd698c40bb0cc98f7c00994b523dec70d4ddc3393e6d67de47a3c11be2d1984"
senha_teste = "ana2025"

hash_calculado = hash_senha(senha_teste)

print("=" * 60)
print("TESTE DE AUTENTICACAO")
print("=" * 60)
print(f"\nSenha testada: {senha_teste}")
print(f"\nHash calculado: {hash_calculado}")
print(f"Hash esperado:  {SENHA_HASH}")
print(f"\nResultado: {'OK - SENHA CORRETA!' if hash_calculado == SENHA_HASH else 'ERRO - HASH NAO CONFERE!'}")
print("=" * 60)

# Testar outras senhas (devem falhar)
senhas_erradas = ["Ana2025", "ana 2025", "ANA2025", "ana2026", ""]
print("\nTestando senhas incorretas:")
for senha in senhas_erradas:
    hash_test = hash_senha(senha)
    resultado = "OK" if hash_test == SENHA_HASH else "FALHOU (correto)"
    print(f"  '{senha}': {resultado}")

