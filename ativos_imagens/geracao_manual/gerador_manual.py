# gerador_manual.py
"""
Script de Geração Manual de Ativos

Este script permite gerar ativos específicos do projeto "Professor Virtual"
de forma manual, fornecendo seus IDs como argumentos de linha de comando.

Uso:
  python -m ativos_imagens.geracao_manual.gerador_manual <ASSET_ID_1> <ASSET_ID_2> ...

Exemplo:
  python -m ativos_imagens.geracao_manual.gerador_manual SFX-01 MAS-06 UI-01
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz do projeto ao sys.path para importações relativas
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from ativos_imagens.tools.asset_manager import AssetManager
from ativos_imagens.tools.image_generator import ImageGenerator
from ativos_imagens.tools.lottie_programmatic import LottieProgrammaticGenerator
from ativos_imagens.tools.mascot_animator import MascotAnimator
from ativos_imagens.tools.svg_generator import SVGGenerator
from ativos_imagens.tools.audio_generator import AudioEffectGenerator

# Mapeamento de nomes de ferramentas para as classes geradoras correspondentes
GENERATOR_MAP = {
    "image_generator": ImageGenerator,
    "lottie_programmatic": LottieProgrammaticGenerator,
    "mascot_animator": MascotAnimator,
    "svg_generator": SVGGenerator,
    "audio_generator": AudioEffectGenerator,
}

# Mapeamento de ferramentas para os métodos de geração específicos
METHOD_MAP = {
    "image_generator": "generate_png",
    "lottie_programmatic": "generate_animation",
    "mascot_animator": "create_mascot_animation",
    "svg_generator": "generate_svg",
    "audio_generator": "generate_sound_effect",
}

def main():
    """
    Função principal que orquestra a geração dos ativos.
    """
    asset_ids = sys.argv[1:]
    if not asset_ids:
        print("Uso: python -m ativos_imagens.geracao_manual.gerador_manual <ASSET_ID_1> <ASSET_ID_2> ...")
        sys.exit(1)

    asset_manager = AssetManager(project_root=str(project_root))
    asset_manager.load_specifications()
    asset_manager.load_checklist_status()

    print(f"Solicitados {len(asset_ids)} ativos para geração: {', '.join(asset_ids)}")

    for asset_id in asset_ids:
        print(f"\n--- Iniciando geração para: {asset_id} ---")
        
        spec = asset_manager.get_specification(asset_id)
        if not spec:
            print(f"ERRO: Especificação para o ativo '{asset_id}' não encontrada. Pulando.")
            continue

        tool_name = spec.get("tool")
        params = spec.get("params", {})

        output_path_obj = asset_manager.get_asset_path(asset_id)
        if not output_path_obj:
            print(f"ERRO: Não foi possível determinar o caminho de saída para '{asset_id}'. Pulando.")
            continue
        
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        output_path = str(output_path_obj)

        # Força a extensão para .webp se a ferramenta for mascot_animator
        if tool_name == "mascot_animator":
            output_path = str(Path(output_path).with_suffix(".webp"))

        try:
            generator_class = GENERATOR_MAP.get(tool_name)
            if not generator_class:
                print(f"AVISO: Ferramenta '{tool_name}' não mapeada. Pulando '{asset_id}'.")
                continue

            # Instanciar o gerador
            if tool_name in ["svg_generator", "lottie_programmatic"]:
                generator = generator_class(output_dir=str(output_path_obj.parent))
            else:
                generator = generator_class()

            generation_method_name = METHOD_MAP.get(tool_name)
            generation_method = getattr(generator, generation_method_name)

            print(f"INFO: Ferramenta '{tool_name}', Método '{generation_method_name}'.")
            print(f"INFO: Parâmetros: {params}")
            print(f"INFO: Caminho de saída: {output_path}")

            # Adicionar parâmetros que são derivados e não estão no JSON
            if tool_name == "audio_generator":
                params['output_dir'] = str(output_path_obj.parent)
            elif tool_name == "image_generator":
                params['output_path'] = output_path
                # prompt_details['filename_base'] não é mais necessário aqui, pois o output_path já contém o nome do arquivo
                # params['prompt_details']['filename_base'] = output_path_obj.stem
                # params['remove_bg'] = True # remove_bg já deve vir do JSON
            elif tool_name == "mascot_animator":
                params['output_path'] = output_path
                # Os parâmetros input_video_path, remove_background, fps, scale
                # devem vir diretamente da especificação do ativo (params)

            # Chamar o método de geração com os parâmetros desempacotados
            generation_method(**params)

            print(f"SUCESSO: Ativo '{asset_id}' gerado em '{output_path}'")
            
            asset_manager.update_checklist_status(asset_id, 'completed')
            print(f"INFO: Checklist atualizado para '{asset_id}'.")

        except Exception as e:
            print(f"ERRO FATAL ao gerar '{asset_id}': {e}")
            import traceback
            traceback.print_exc()
            asset_manager.update_checklist_status(asset_id, 'error')

if __name__ == "__main__":
    main()