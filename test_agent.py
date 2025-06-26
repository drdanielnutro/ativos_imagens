#!/usr/bin/env python3
"""
Script de teste para o agente de geração de ativos
"""

# Importar o agente
from ativos_imagens.agent import root_agent, check_asset_inventory, create_asset

print("=== TESTE DO AGENTE DE GERAÇÃO DE ATIVOS ===\n")

# Teste 1: Verificar inventário
print("1. Verificando inventário de ativos...")
print("-" * 50)
result = check_asset_inventory()
print(result)
print("\n")

# Teste 2: Criar uma animação Lottie
print("2. Criando animação LOAD-02 (loading_bounce)...")
print("-" * 50)
result = create_asset("LOAD-02")
print(result)
print("\n")

# Teste 3: Criar um SVG
print("3. Criando padrão SVG UI-01 (pattern_dots)...")
print("-" * 50)
result = create_asset("UI-01")
print(result)
print("\n")

# Teste 4: Tentar criar um ativo que não podemos
print("4. Tentando criar SFX-01 (áudio)...")
print("-" * 50)
result = create_asset("SFX-01")
print(result)
print("\n")

# Teste 5: Criar um ícone SVG
print("5. Criando ícone ICO-01 (camera_fun)...")
print("-" * 50)
result = create_asset("ICO-01")
print(result)
print("\n")

print("=== TESTES CONCLUÍDOS ===")
print("\nPara interagir com o agente via ADK:")
print("1. No diretório raiz do projeto, execute: adk web")
print("2. Abra http://127.0.0.1:8000 no navegador")
print("3. Selecione 'ativos_imagens' no menu")
print("4. Experimente comandos como:")
print("   - 'Verifique o inventário'")
print("   - 'Crie o ativo LOAD-03'")
print("   - 'Crie todos os ícones SVG'")