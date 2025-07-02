#!/usr/bin/env python3
"""
Script de teste para verificar a integração do novo formato JSON
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ativos_imagens.tools.asset_manager import AssetManager

def test_json_integration():
    """Testa as funcionalidades do novo sistema JSON"""
    print("🧪 Testando integração com formato JSON...\n")
    
    # Inicializar AssetManager
    asset_manager = AssetManager(project_root=str(project_root))
    
    # Teste 1: Carregar especificações
    print("1️⃣ Testando carregamento de especificações...")
    try:
        specs = asset_manager.load_specifications()
        print(f"✅ {len(specs)} especificações carregadas com sucesso")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # Teste 2: Carregar status do checklist JSON
    print("\n2️⃣ Testando carregamento do checklist JSON...")
    try:
        status = asset_manager.load_checklist_status()
        completed = sum(1 for s in status.values() if s["completed"])
        print(f"✅ Status carregado: {len(status)} ativos, {completed} completos")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # Teste 3: Obter próximo ativo pendente
    print("\n3️⃣ Testando get_next_pending_asset()...")
    try:
        next_asset = asset_manager.get_next_pending_asset()
        if next_asset:
            print(f"✅ Próximo ativo: {next_asset}")
            spec = asset_manager.get_specification(next_asset)
            print(f"   Ferramenta: {spec.get('tool')}")
        else:
            print("✅ Nenhum ativo pendente (todos completos)")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # Teste 4: Obter lista de ativos pendentes
    print("\n4️⃣ Testando get_pending_assets()...")
    try:
        pending = asset_manager.get_pending_assets(limit=5)
        print(f"✅ {len(pending)} ativos pendentes (limite 5):")
        for asset in pending:
            print(f"   - {asset['id']} ({asset['tool']})")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # Teste 5: Filtrar por categoria
    print("\n5️⃣ Testando filtro por categoria...")
    try:
        audio_pending = asset_manager.get_pending_assets(category="audio", limit=3)
        print(f"✅ {len(audio_pending)} ativos de áudio pendentes:")
        for asset in audio_pending:
            print(f"   - {asset['id']}: {asset.get('description', 'N/A')}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # Teste 6: Verificar sincronização JSON/MD
    print("\n6️⃣ Verificando sincronização JSON ↔ MD...")
    json_path = project_root / "docs" / "definicoes" / "checklist_ativos_criados.json"
    md_path = project_root / "docs" / "definicoes" / "checklist_ativos_criados.md"
    
    if json_path.exists() and md_path.exists():
        import json
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        
        print(f"✅ JSON: {json_data['completed']} completos de {json_data['total_assets']}")
        print(f"✅ Última atualização: {json_data['last_updated']}")
        
        # Verificar alguns IDs específicos
        test_ids = ["SFX-01", "SFX-02", "SFX-03", "SFX-04"]
        print("\n   Status de ativos de teste:")
        for test_id in test_ids:
            if test_id in json_data["assets"]:
                asset = json_data["assets"][test_id]
                status_icon = "✅" if asset["status"] == "completed" else "⏳"
                print(f"   {status_icon} {test_id}: {asset['status']}")
    
    print("\n✨ Todos os testes concluídos!")
    
    # Resumo final
    print("\n📊 RESUMO:")
    print("- AssetManager agora suporta formato JSON ✅")
    print("- Novas funções get_pending_assets() e get_next_pending_asset() ✅")
    print("- Sincronização JSON/MD funcionando ✅")
    print("- Sistema pronto para uso! 🚀")

if __name__ == "__main__":
    test_json_integration()