#!/usr/bin/env python3
"""
Script de teste específico para a funcionalidade de animação do mascote.
Testa o pipeline completo: PNG → Vídeo → Frames → SVG → Lottie
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ativos_imagens.tools.mascot_animator import MascotAnimator
from ativos_imagens.agent import API_CALL_TRACKER, reset_api_limits

def test_mascot_animation():
    """Testa a criação de uma animação Lottie do mascote."""
    print("🧪 TESTE: Criação de Animação Lottie do Mascote")
    print("="*50)
    
    # Reset contadores
    reset_api_limits()
    
    try:
        # Instanciar animator
        animator = MascotAnimator()
        
        # Preparar dados de teste
        prompt_details = {
            "action": "standing in a friendly pose",
            "objects_location": "with the book held gently under one arm",
            "background_color": "a clean white background"
        }
        
        animation_prompt = "subtle breathing motion, gentle head movement, seamless loop"
        
        # Arquivo de saída de teste
        output_path = "test_mascot_breathing.json"
        
        print("\n📋 Configuração do teste:")
        print(f"  - Prompt do PNG: {prompt_details}")
        print(f"  - Prompt da animação: {animation_prompt}")
        print(f"  - Arquivo de saída: {output_path}")
        
        print("\n🚀 Iniciando pipeline de animação...")
        
        result = animator.create_mascot_animation(
            prompt_details=prompt_details,
            animation_prompt=animation_prompt,
            output_path=output_path
        )
        
        print(f"\n📝 Resultado: {result}")
        
        # Verificar se arquivo foi criado
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / 1024
            print(f"\n✅ TESTE PASSOU!")
            print(f"  - Arquivo criado: {output_path}")
            print(f"  - Tamanho: {file_size:.1f} KB")
            
            # Mostrar primeiras linhas do arquivo
            with open(output_path, 'r') as f:
                content = f.read(200)
                print(f"  - Conteúdo (preview): {content[:100]}...")
        else:
            print("\n❌ TESTE FALHOU: Arquivo não foi criado")
            
    except Exception as e:
        print(f"\n❌ TESTE FALHOU: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Status das chamadas de API
        print(f"\n📊 Chamadas de API utilizadas:")
        print(f"  - Recraft: {API_CALL_TRACKER.get('recraft_calls', 0)}")
        print(f"  - Replicate: {API_CALL_TRACKER.get('replicate_calls', 0)}")
        
        # Limpeza
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                print(f"  - Arquivo de teste removido: {output_path}")
            except:
                pass


def test_basic_imports():
    """Testa se todas as dependências estão disponíveis."""
    print("\n🔍 TESTE: Verificação de Dependências")
    print("="*35)
    
    dependencies = [
        ("opencv-python", "cv2"),
        ("lottie", "lottie.objects"),
        ("potrace", "subprocess"),
        ("requests", "requests"),
        ("replicate", "replicate")
    ]
    
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"  ✅ {name}: OK")
        except ImportError as e:
            print(f"  ❌ {name}: FALTANDO - {e}")
    
    # Testar potrace no sistema
    try:
        import subprocess
        result = subprocess.run(["potrace", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ potrace (sistema): OK")
        else:
            print("  ❌ potrace (sistema): ERRO")
    except:
        print("  ❌ potrace (sistema): NÃO ENCONTRADO")


def main():
    """Executa todos os testes."""
    print("🎭 TESTE COMPLETO: MascotAnimator")
    print("="*40)
    
    # Teste 1: Dependências
    test_basic_imports()
    
    # Teste 2: Funcionalidade completa (se dependências OK)
    print("\n" + "="*50)
    test_mascot_animation()
    
    print("\n🏁 Testes concluídos!")


if __name__ == "__main__":
    main()