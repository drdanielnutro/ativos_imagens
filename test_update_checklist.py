#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do update_checklist_status
"""
import sys
from pathlib import Path
import json

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ativos_imagens.tools.asset_manager import AssetManager

def test_update_checklist():
    """Testa atualização do checklist JSON"""
    print("🧪 Testando atualização do checklist JSON...\n")
    
    # Inicializar AssetManager
    asset_manager = AssetManager(project_root=str(project_root))
    
    # Carregar especificações e status
    asset_manager.load_specifications()
    asset_manager.load_checklist_status()
    
    # Testar com um ativo pendente
    test_asset = "SFX-03"  # Este está pendente conforme visto no teste anterior
    
    print(f"📝 Testando atualização do ativo {test_asset}...")
    
    # Verificar status atual
    json_path = project_root / "docs" / "definicoes" / "checklist_ativos_criados.json"
    
    print(f"\n1️⃣ Status ANTES da atualização:")
    with open(json_path, 'r', encoding='utf-8') as f:
        data_before = json.load(f)
    
    asset_before = data_before["assets"][test_asset]
    print(f"   Status: {asset_before['status']}")
    print(f"   Completed date: {asset_before['completed_date']}")
    print(f"   Total completed: {data_before['completed']}")
    
    # Executar atualização
    print(f"\n2️⃣ Executando update_checklist_status('{test_asset}', 'completed')...")
    result = asset_manager.update_checklist_status(test_asset, 'completed')
    print(f"   Resultado: {'✅ Sucesso' if result else '❌ Falhou'}")
    
    # Verificar status após
    print(f"\n3️⃣ Status DEPOIS da atualização:")
    with open(json_path, 'r', encoding='utf-8') as f:
        data_after = json.load(f)
    
    asset_after = data_after["assets"][test_asset]
    print(f"   Status: {asset_after['status']}")
    print(f"   Completed date: {asset_after['completed_date']}")
    print(f"   Total completed: {data_after['completed']}")
    
    # Verificar se mudou
    if asset_before['status'] != asset_after['status']:
        print(f"\n✅ Status mudou de '{asset_before['status']}' para '{asset_after['status']}'")
    else:
        print(f"\n❌ Status NÃO mudou! Continua '{asset_after['status']}'")
    
    if data_before['completed'] != data_after['completed']:
        print(f"✅ Total completed mudou de {data_before['completed']} para {data_after['completed']}")
    else:
        print(f"❌ Total completed NÃO mudou! Continua {data_after['completed']}")
    
    # Reverter a mudança para não afetar o estado real
    print(f"\n4️⃣ Revertendo mudança (voltando para 'pending')...")
    result = asset_manager.update_checklist_status(test_asset, 'pending')
    print(f"   Resultado: {'✅ Sucesso' if result else '❌ Falhou'}")
    
    # Verificar caminho
    print(f"\n📂 Informações de debug:")
    print(f"   project_root: {asset_manager.project_root}")
    print(f"   data_path: {asset_manager.data_path}")
    print(f"   json_path exists: {json_path.exists()}")
    print(f"   json_path: {json_path}")

if __name__ == "__main__":
    test_update_checklist()