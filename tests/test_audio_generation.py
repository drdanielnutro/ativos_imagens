"""
Script de teste para geração de áudio
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ativos_imagens.tools.audio_generator import AudioEffectGenerator
from ativos_imagens.tools.asset_manager import AssetManager


def test_audio_configs():
    """Testa se as configurações de áudio estão corretas"""
    print("=== Testando Configurações de Áudio ===")
    
    generator = AudioEffectGenerator()
    
    print("\nAtivos de áudio configurados:")
    for asset_id, config in generator.AUDIO_CONFIGS.items():
        print(f"\n{asset_id}:")
        print(f"  - Arquivo: {config['filename']}")
        print(f"  - Duração: {config['duration']}s")
        print(f"  - Modelo: {config['model']}")
        print(f"  - Prompt: {config['prompt'][:60]}...")


def test_asset_manager_integration():
    """Testa integração com AssetManager"""
    print("\n\n=== Testando Integração com AssetManager ===")
    
    manager = AssetManager()
    manager.load_asset_inventory()
    
    # Verificar se os ativos SFX são reconhecidos
    audio_assets = []
    for asset_id, spec in manager.asset_specs.items():
        if spec.get('type') == 'audio':
            audio_assets.append(asset_id)
    
    print(f"\nAtivos de áudio encontrados no inventário: {len(audio_assets)}")
    for asset_id in sorted(audio_assets):
        spec = manager.asset_specs[asset_id]
        print(f"  - {asset_id}: {spec.get('filename')} - {spec.get('description')}")


def test_single_audio_generation():
    """Testa a geração de um único áudio"""
    print("\n\n=== Testando Geração de Áudio Individual ===")
    
    # Verifica se o token está configurado
    if not os.getenv('REPLICATE_API_TOKEN') or os.getenv('REPLICATE_API_TOKEN') == 'sua_chave_replicate_aqui':
        print("❌ REPLICATE_API_TOKEN não configurado no .env")
        print("   Configure sua chave antes de testar a geração real")
        return
    
    try:
        generator = AudioEffectGenerator()
        
        # Testar com o primeiro áudio (button_tap)
        asset_id = "SFX-01"
        print(f"\nTentando gerar {asset_id}...")
        
        output_path = generator.generate_sound_effect(
            asset_id=asset_id,
            output_dir="test_output"
        )
        
        if output_path:
            print(f"✅ Áudio gerado com sucesso: {output_path}")
            print(f"   Tamanho: {os.path.getsize(output_path) / 1024:.1f} KB")
        else:
            print("❌ Falha na geração do áudio")
            
    except Exception as e:
        print(f"❌ Erro: {e}")


def main():
    """Executa todos os testes"""
    print("🎵 Teste do Sistema de Geração de Áudio 🎵\n")
    
    test_audio_configs()
    test_asset_manager_integration()
    test_single_audio_generation()
    
    print("\n\n✅ Testes concluídos!")


if __name__ == "__main__":
    main()