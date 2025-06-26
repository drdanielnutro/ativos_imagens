#!/usr/bin/env python3
"""
Teste isolado de remoção de fundo usando subprocess
para evitar problemas de serialização JSON no contexto principal
"""

import subprocess
import sys
import json
import tempfile
import os

def isolated_bg_removal(image_url: str) -> str:
    """
    Executa remoção de fundo em processo isolado
    """
    script_content = f'''
import sys
sys.path.append('.')

from dotenv import load_dotenv
load_dotenv()

from ativos_imagens.tools.image_generator import ImageGenerator

try:
    generator = ImageGenerator()
    result_url = generator._remove_background("{image_url}")
    print("SUCCESS:" + result_url)
except Exception as e:
    print("ERROR:" + str(e))
'''
    
    # Criar script temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        script_path = f.name
    
    try:
        # Executar em subprocess
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Processar resultado
        if result.returncode == 0:
            output = result.stdout.strip()
            # Buscar linha que começa com SUCCESS:
            for line in output.split('\n'):
                if line.startswith("SUCCESS:"):
                    return line[8:]  # Remove "SUCCESS:"
                elif line.startswith("ERROR:"):
                    raise RuntimeError(line[6:])  # Remove "ERROR:"
            
            raise RuntimeError(f"Não encontrou SUCCESS ou ERROR na saída: {output}")
        else:
            raise RuntimeError(f"Processo falhou: {result.stderr}")
            
    finally:
        # Limpar arquivo temporário
        try:
            os.unlink(script_path)
        except:
            pass

if __name__ == "__main__":
    print("=== TESTE ISOLADO DE REMOÇÃO DE FUNDO ===")
    print()
    
    test_url = "https://replicate.delivery/xezq/dBsB6i2PSyIfAKtv00GV1xCxdDGGqD7ZeGFFmwAjQ1N6ud6UA/out-0.png"
    
    print(f"🖼️ URL de teste: {test_url}")
    print("🔄 Executando remoção de fundo em processo isolado...")
    print()
    
    try:
        result = isolated_bg_removal(test_url)
        print("✅ SUCESSO!")
        print(f"🔗 URL resultado: {result}")
        print(f"📊 Tipo: {type(result)}")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()