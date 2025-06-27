#!/usr/bin/env python3
"""
Script de teste específico para validar o pipeline com vetorização direta.
Executa verificações detalhadas e fornece diagnóstico completo.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Adicionar diretório do projeto ao Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def check_environment():
    """Verifica se o ambiente está configurado corretamente para a vetorização direta."""
    print("=== VERIFICAÇÃO DO AMBIENTE ===\n")

    issues = []
    venv_python = "/Users/institutorecriare/VSCodeProjects/criador_agentes/ativos_imagens/.venv/bin/python"

    # 1. Verificar python-lottie
    try:
        import lottie
        print(f"✅ python-lottie instalado: versão {lottie.__version__}")
    except ImportError:
        print("❌ python-lottie NÃO instalado")
        issues.append(f"{venv_python} -m pip install lottie")

    # 2. Verificar Pillow
    try:
        from PIL import Image
        print("✅ Pillow instalado")
    except ImportError:
        print("❌ Pillow NÃO instalado")
        issues.append(f"{venv_python} -m pip install Pillow")

    # 3. Verificar potrace no sistema
    potrace_result = subprocess.run(
        ["which", "potrace"],
        capture_output=True,
        text=True
    )
    if potrace_result.returncode == 0:
        print(f"✅ Potrace instalado: {potrace_result.stdout.strip()}")
    else:
        print("❌ Potrace NÃO encontrado no sistema")
        issues.append("brew install potrace")

    # 4. Verificar mkbitmap no sistema
    mkbitmap_result = subprocess.run(
        ["which", "mkbitmap"],
        capture_output=True,
        text=True
    )
    if mkbitmap_result.returncode == 0:
        print(f"✅ mkbitmap instalado: {mkbitmap_result.stdout.strip()}")
    else:
        print("❌ mkbitmap NÃO encontrado no sistema")
        issues.append("brew install potrace") # mkbitmap vem com potrace

    # 5. Verificar ImageMagick (convert) como fallback
    convert_result = subprocess.run(
        ["which", "convert"],
        capture_output=True,
        text=True
    )
    if convert_result.returncode == 0:
        print(f"✅ ImageMagick (convert) instalado: {convert_result.stdout.strip()}")
    else:
        print("⚠️ ImageMagick (convert) NÃO encontrado. Usará Pillow como fallback para PNG->PNM.")
        # Não é um erro crítico, apenas um aviso

    if issues:
        print(f"\n❌ PROBLEMAS ENCONTRADOS. Execute:")
        for issue in issues:
            print(f"   {issue}")
        return False

    print("\n✅ Ambiente configurado corretamente!")
    return True

def test_pipeline_with_trace():
    """Testa o pipeline completo com vetorização direta."""
    print("\n=== TESTE DO PIPELINE COM VETORIZAÇÃO DIRETA ===\n")

    from ativos_imagens.tools.mascot_animator import MascotAnimator
    from ativos_imagens.agent import check_api_limit, API_CALL_TRACKER

    # Verificar limites de API
    if not check_api_limit('replicate'):
        print("❌ Limite de API atingido")
        return False

    # Configuração do teste
    prompt_details = {
        "character": "PROF",
        "expression": "friendly",
        "pose": "standing",
        "accessories": ["blue academic cap"],
        "description": "PROF mascot with academic cap, clean cartoon style, simple shapes"
    }

    animation_prompt = "standing still, breathing gently, minimal movement"

    # Criar diretório de saída
    output_dir = Path("test_trace_output")
    output_dir.mkdir(exist_ok=True)

    # Arquivos de saída
    json_path = output_dir / "mascot_trace.json"

    try:
        # Executar pipeline
        animator = MascotAnimator()
        print(f"Iniciando geração da animação...")
        print(f"Saída esperada: {json_path}")

        result_path = animator.create_mascot_animation_v2(
            prompt_details=prompt_details,
            animation_prompt=animation_prompt,
            output_path=str(json_path),
            output_format="lottie"  # Vai gerar .lottie
        )

        print(f"\nPipeline concluído!")
        print(f"Arquivo gerado: {result_path}")

        # Análise do resultado
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            size_kb = file_size / 1024
            size_mb = size_kb / 1024

            print(f"\n ANÁLISE DO RESULTADO:")
            print(f"  Tipo: {'.lottie' if result_path.endswith('.lottie') else '.json'}")
            print(f"  Tamanho: {file_size:,} bytes")
            print(f"  Tamanho: {size_kb:.2f} KB")
            if size_mb >= 1:
                print(f"  Tamanho: {size_mb:.2f} MB")

            # Verificar objetivo
            if size_kb < 100:
                print(f"\n✅ SUCESSO TOTAL: {size_kb:.2f} KB < 100 KB")
                return True
            else:
                print(f"\n❌ FALHA: {size_kb:.2f} KB > 100 KB")

                # Diagnóstico adicional
                if result_path.endswith('.json'):
                    print("\n DIAGNÓSTICO:")
                    print("  - Arquivo não foi convertido para .lottie")
                    print("  - Verificar método _create_dotlottie")

                # Tentar analisar o JSON
                if result_path.endswith('.json'):
                    with open(result_path, 'r') as f:
                        data = json.load(f)
                        frame_count = data.get('op', 0)  # outPoint = total frames
                        print(f"  - Total de frames: {frame_count}")
                        if frame_count > 60:
                            print("  - Muitos frames! Considere reduzir para 30-40")

                return False
        else:
            print(f"\n❌ ERRO: Arquivo não foi criado")
            return False

    except Exception as e:
        print(f"\n❌ ERRO NO PIPELINE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Mostrar uso de API
        print(f"\n USO DE API:")
        print(f"  Replicate: {API_CALL_TRACKER.get('replicate_calls', 0)} chamadas")

def main():
    """Função principal."""
    print("TESTE DO PIPELINE LOTTIE COM VETORIZAÇÃO DIRETA")
    print("=" * 50)

    # Verificar ambiente
    if not check_environment():
        print("\n❌ Corrija os problemas acima antes de continuar.")
        return 1

    # Executar teste
    if test_pipeline_with_trace():
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        return 0
    else:
        print("\n❌ TESTE FALHOU - Verifique os logs acima")
        return 1

if __name__ == "__main__":
    sys.exit(main())