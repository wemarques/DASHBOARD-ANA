#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para verificar e gerar hash de senha"""

import hashlib

def hash_senha(senha):
    """Gera hash SHA256 da senha"""
    return hashlib.sha256(senha.encode()).hexdigest()

# Testar com a senha "ana2025"
senha_teste = "ana2025"
hash_atual_arquivo = "5fd698c40bb0cc98f7c00994b523dec70d4ddc3393e6d67de47a3c11be2d1984"

hash_calculado = hash_senha(senha_teste)

print("=" * 60)
print("VERIFICAÇÃO DE HASH DE SENHA")
print("=" * 60)
print(f"\nSenha testada: {senha_teste}")
print(f"\nHash calculado: {hash_calculado}")
print(f"Hash no arquivo: {hash_atual_arquivo}")
print(f"\nCorrespondencia: {hash_calculado == hash_atual_arquivo}")

if hash_calculado != hash_atual_arquivo:
    print("\nATENCAO: O hash nao corresponde!")
    print(f"   Use este hash no arquivo app.py:")
    print(f'   SENHA_HASH = "{hash_calculado}"')
else:
    print("\nHash esta correto! O problema pode ser:")
    print("   1. Streamlit não foi reiniciado após alteração")
    print("   2. Cache do navegador")
    print("   3. Erro ao digitar a senha")

print("\n" + "=" * 60)

