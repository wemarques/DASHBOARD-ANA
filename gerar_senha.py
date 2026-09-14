#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Hash de Senha para Dashboard Ana
Este script gera o hash SHA256 de uma senha para uso no sistema de autenticação.
"""

import hashlib
import getpass

def gerar_hash_senha():
    print("=" * 50)
    print("🔐 GERADOR DE HASH DE SENHA - Dashboard Ana")
    print("=" * 50)
    print()
    
    # Solicitar senha (oculta durante digitação)
    senha = getpass.getpass("Digite a nova senha: ")
    
    if not senha:
        print("\n❌ Erro: A senha não pode estar vazia!")
        return
    
    if len(senha) < 6:
        print("\n⚠️  Aviso: Senha muito curta! Recomendamos no mínimo 8 caracteres.")
        continuar = input("Deseja continuar mesmo assim? (s/n): ")
        if continuar.lower() != 's':
            print("Operação cancelada.")
            return
    
    # Gerar hash SHA256
    hash_senha = hashlib.sha256(senha.encode()).hexdigest()
    
    print("\n" + "=" * 50)
    print("✅ Hash gerado com sucesso!")
    print("=" * 50)
    print()
    print("📋 Copie o hash abaixo:")
    print()
    print(f'    SENHA_HASH = "{hash_senha}"')
    print()
    print("=" * 50)
    print()
    print("💡 Instruções (o hash NÃO vai mais no código):")
    print("   Streamlit Cloud: app -> (...) -> Settings -> Secrets e cole a linha acima")
    print("   Local: crie .streamlit/secrets.toml com a linha acima")
    print("          (ou exporte DASHBOARD_ANA_SENHA_HASH)")
    print("   Depois reinicie o app.")
    print()
    print("⚠️  Nunca commite o hash: o repositório é público.")
    print()
    print("🔒 Sua nova senha estará ativa após reiniciar o app!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        gerar_hash_senha()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
