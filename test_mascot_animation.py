import os
import sys

# Adiciona o diretório pai ao sys.path para permitir importações relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ativos_imagens')))

from ativos_imagens.tools.mascot_animator import MascotAnimator

# Configurar o token da API da Replicate (substitua pelo seu token real)
# É altamente recomendado usar variáveis de ambiente para tokens de API
# Ex: export REPLICATE_API_TOKEN="seu_token_aqui"
# os.environ["REPLICATE_API_TOKEN"] = "seu_token_aqui"

if __name__ == "__main__":
    input_video = "/Users/institutorecriare/VSCodeProjects/criador_agentes/ativos_imagens/testes/testes_de_lottie/videos_mascote/prof.mp4"
    output_webp = "/Users/institutorecriare/VSCodeProjects/criador_agentes/ativos_imagens/output/prof_animation_rembg.webp"

    animator = MascotAnimator()

    print(f"Iniciando teste de animação com remoção de fundo para: {input_video}")
    try:
        final_path = animator.create_mascot_animation(
            input_video_path=input_video,
            output_path=output_webp,
            remove_background=True, # Testando com remoção de fundo
            fps=12,
            scale=256
        )
        print(f"Animação WebP gerada com sucesso em: {final_path}")
    except Exception as e:
        print(f"Erro durante a geração da animação: {e}")
        import traceback
        traceback.print_exc()
