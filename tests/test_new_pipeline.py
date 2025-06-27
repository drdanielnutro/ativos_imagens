#!/usr/bin/env python3
"""Script para testar o novo pipeline de geração Lottie com vetorização otimizada."""

import os
import sys
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent))

from ativos_imagens.tools.mascot_animator import MascotAnimator
from ativos_imagens.agent import check_api_limit, API_CALL_TRACKER

def test_new_pipeline():
    """Testa o pipeline v2 com lottie_convert.py e trace mode."""
    
    print("=== Teste do Pipeline V2 de Animação Lottie ===")
    print()
    
    # Verificar limite de API
    if not check_api_limit('replicate'):
        print("❌ Limite de API atingido. Abortando teste.")
        return
    
    # Configurar detalhes do mascote
    prompt_details = {
        "character": "PROF",
        "expression": "friendly",
        "pose": "standing",
        "accessories": ["blue academic cap"],
        "description": "PROF mascot with academic cap, clean cartoon style"
    }
    
    # Prompt de animação
    animation_prompt = "standing still, breathing gently, slight idle movement"
    
    # Criar pasta de saída
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Arquivo de saída
    output_path = output_dir / "mascot_idle_v2_test.json"
    
    try:
        # Criar instância do animador
        animator = MascotAnimator()
        
        print(f"📁 Arquivo de saída: {output_path}")
        print(f"🎬 Prompt de animação: {animation_prompt}")
        print()
        print("Iniciando geração...")
        print()
        
        # Executar pipeline v2
        result = animator.create_mascot_animation_v2(
            prompt_details=prompt_details,
            animation_prompt=animation_prompt,
            output_path=str(output_path),
            output_format="lottie"  # Vai gerar .lottie comprimido
        )
        
        print()
        print("✅ Pipeline concluído!")
        print(f"📂 Arquivo gerado: {result}")
        
        # Verificar tamanho
        if os.path.exists(result):
            size_bytes = os.path.getsize(result)
            size_kb = size_bytes / 1024
            size_mb = size_kb / 1024
            
            print()
            print("📊 Análise do arquivo:")
            print(f"   - Tamanho: {size_bytes:,} bytes")
            print(f"   - Tamanho: {size_kb:.2f} KB")
            print(f"   - Tamanho: {size_mb:.2f} MB")
            
            if size_kb < 100:
                print("   ✅ SUCESSO: Arquivo menor que 100KB!")
            else:
                print(f"   ⚠️  AVISO: Arquivo ainda grande ({size_kb:.2f} KB)")
        
        # Mostrar estatísticas de API
        print()
        print("📈 Estatísticas de API:")
        print(f"   - Chamadas Replicate: {API_CALL_TRACKER['replicate_calls']}")
        print(f"   - Chamadas Recraft: {API_CALL_TRACKER['recraft_calls']}")
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_pipeline()