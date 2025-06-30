import io
import os
from typing import Dict, Literal

import PIL.Image as Image
import requests
import replicate

# --- Constantes do Modelo Mascote ---
FINE_TUNED_MASCOT_MODEL_ID = "drdanielnutro/prof:9023328b0f41ca5a47381d06a1bbaab03294d1ea4b03d3f92449fae5081dc47c"

MASCOT_PROMPT_TEMPLATE = """
Illustration of "PROF" {action}. The yellow book and yellow pencil {objects_location}.
Colors: Head, neck, arms and legs wear a friendly light-green (#84B864);
the plastron on his chest glows bright yellow (#FFCC33);
the smooth back shell is a deep forest-green (#336655);
two slim brown eyebrows (#966953) hover above his large black eyes (#1E1E1E),
while soft coral-pink cheeks (#E5988E) add warmth,
and a sturdy blue-gray glasses frame (#4C5F7A) completes the look.
The background should be {background_color}.
"""

MASCOT_API_PARAMS = {
    "seed": 50, "model": "dev", "go_fast": False, "lora_scale": 1.5,
    "megapixels": "1", "num_outputs": 1, "aspect_ratio": "1:1",
    "output_format": "png", "guidance_scale": 3, "output_quality": 80,
    "prompt_strength": 0.55, "extra_lora_scale": 1, "num_inference_steps": 28
}


class ImageGenerator:
    """Ferramenta para gerar imagens PNG usando a API da Replicate."""

    def _generate_mascot_image(self, prompt_details: Dict[str, str]) -> list:
        """Lida com a geração específica do mascote."""
        final_prompt = MASCOT_PROMPT_TEMPLATE.format(
            action=prompt_details.get('action', 'in a neutral pose'),
            objects_location=prompt_details.get('objects_location', 'nearby'),
            background_color=prompt_details.get('background_color', 'a clean white background')
        ).strip().replace('\n', ' ')

        api_input = MASCOT_API_PARAMS.copy()
        api_input["prompt"] = final_prompt

        print(f"INFO: Usando modelo mascote treinado: '{FINE_TUNED_MASCOT_MODEL_ID}'")
        print(f"INFO: Gerando imagem com prompt: '{final_prompt[:100]}...'")

        return replicate.run(FINE_TUNED_MASCOT_MODEL_ID, input=api_input)

    def _generate_generic_image(self, prompt: str, model_name: str) -> list:
        """Lida com a geração de imagens genéricas."""
        print(f"INFO: Usando modelo genérico: '{model_name}'")
        print(f"INFO: Gerando imagem com prompt: '{prompt[:100]}...'")
        
        return replicate.run(model_name, input={"prompt": prompt})

    def _remove_background(self, image_url: str) -> str:
        """
        Remove o fundo de uma imagem usando a API da Replicate.

        Args:
            image_url: A URL da imagem original com fundo.

        Returns:
            A URL da nova imagem com fundo transparente.
        """
        import tempfile

        # Modelo lucataco/remove-bg - mais estável e simples
        model_id = "lucataco/remove-bg:95fcc2a26d3899cd6c2691c900465aaeff466285a65c14638cc5f36f34befaf1"
        print(f"INFO: Removendo fundo da imagem: {image_url}")

        # Baixar a imagem para um arquivo temporário
        response = requests.get(image_url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image_file:
            temp_image_file.write(response.content)
            temp_image_path = temp_image_file.name

        try:
            with open(temp_image_path, "rb") as f:
                api_input = {
                    "image": f
                }
                result = replicate.run(model_id, input=api_input)
            
            # Tratar FileOutput para extrair URL
            if hasattr(result, 'url'):
                return result.url
            elif isinstance(result, str):
                return result
            else:
                return str(result)
        finally:
            # Garantir que o arquivo temporário seja removido
            os.unlink(temp_image_path)

    def generate_png(self, asset_type: Literal['mascote', 'generico'], prompt_details: Dict[str, str], output_path: str, model_name: str = "stability-ai/sdxl", remove_bg: bool = False) -> str:
        """Gera uma imagem PNG, opcionalmente remove o fundo, e a salva em disco."""
        try:
            # Importar função de verificação do agent (se disponível)
            from ..agent import check_api_limit, API_CALL_TRACKER
        except ModuleNotFoundError:
            # Fallback para uso manual: funções dummy
            print("AVISO: Módulo 'agent' não encontrado. Usando funções dummy para controle de API.")
            check_api_limit = lambda x: True
            API_CALL_TRACKER = {'replicate_calls': 0} # Dicionário dummy
        
        # Verificar limite de API
        if not check_api_limit('replicate'):
            raise RuntimeError("Limite de chamadas de API atingido. Operação cancelada.")
            
        try:
            # Incrementar contador
            API_CALL_TRACKER['replicate_calls'] += 1
            
            # ETAPA 1: Geração da imagem com fundo
            if asset_type == 'mascote':
                initial_output_urls = self._generate_mascot_image(prompt_details)
            else:
                description = prompt_details.get('description', 'a simple sphere')
                initial_output_urls = self._generate_generic_image(description, model_name)

            image_with_bg_url = initial_output_urls[0]

            # --- NOVA ETAPA 2: Remoção do Fundo ---
            if remove_bg:
                print("INFO: Iniciando a etapa de remoção de fundo...")
                # Verificar limite novamente para remoção de fundo
                if not check_api_limit('replicate'):
                    raise RuntimeError("Limite de API atingido durante remoção de fundo.")
                API_CALL_TRACKER['replicate_calls'] += 1
                image_no_bg_url = self._remove_background(image_with_bg_url)
                print("INFO: Remoção de fundo concluída.")
            else:
                print("INFO: Etapa de remoção de fundo pulada.")
                image_no_bg_url = image_with_bg_url
            # ----------------------------------------

            # ETAPA 3: Download e salvamento da imagem final (já sem fundo)
            print(f"INFO: Baixando imagem final de: {image_no_bg_url}")
            response = requests.get(image_no_bg_url)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))
            
            # Salvar no caminho de saída fornecido
            img.save(output_path)

            return output_path

        except Exception as e:
            error_message = f"ERRO: Pipeline de geração de PNG falhou. Detalhes: {e}"
            if hasattr(e, 'response') and e.response is not None and '402' in str(e.response.status_code):
                error_message += "\n(Causa provável: Créditos insuficientes na Replicate)"
            raise RuntimeError(error_message) from e 