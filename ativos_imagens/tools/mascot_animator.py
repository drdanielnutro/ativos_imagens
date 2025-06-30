# ativos_imagens/tools/mascot_animator.py

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import json
import replicate
import requests
import sys

# Importa a ImageGenerator para reutilizar a lógica de geração de PNG e remoção de fundo
from .image_generator import ImageGenerator

class MascotAnimator:
    VIDEO_GEN_MODEL = "bytedance/seedance-1-lite"

    """
    Ferramenta para processar vídeos de mascotes, opcionalmente remover o fundo
    e converter para o formato WebP otimizado para uso em aplicativos mobile.
    """
    VERBOSE_SUBPROCESS = True  # Exibir stdout/stderr das ferramentas externas

    def _run_cmd(self, cmd: list[str]):
        """Executa comandos externos, exibindo saída em tempo real se VERBOSE_SUBPROCESS."""
        import subprocess, shlex
        print(f"EXEC ⟩ {shlex.join(cmd)}")
        if self.VERBOSE_SUBPROCESS:
            process = subprocess.Popen(cmd)
            code = process.wait()
            if code != 0:
                raise subprocess.CalledProcessError(code, cmd)
            return subprocess.CompletedProcess(cmd, code)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
            return result

    def _get_transparent_mascot_png(self, prompt_details: dict) -> str:
        """
        Gera e obtém um PNG local do mascote com fundo transparente.
        Retorna o caminho do arquivo temporário.
        """
        try:
            from ..agent import check_api_limit, API_CALL_TRACKER
        except ModuleNotFoundError:
            print("AVISO: Módulo 'agent' não encontrado. Usando funções dummy para controle de API.")
            check_api_limit = lambda x: True
            API_CALL_TRACKER = {'replicate_calls': 0} # Dicionário dummy
        
        if not check_api_limit('replicate'):
            raise RuntimeError("Limite de API atingido para geração de imagem do mascote")
        
        generator = ImageGenerator()
        
        print("INFO (MascotAnimator): Gerando imagem base do mascote...")
        
        API_CALL_TRACKER['replicate_calls'] += 1
        urls_com_fundo = generator._generate_mascot_image(prompt_details)
        
        url_com_fundo_str = str(urls_com_fundo[0])

        # A remoção de fundo da imagem inicial foi desativada conforme solicitado.
        # A imagem será baixada com o fundo original.
        print("INFO (MascotAnimator): Baixando imagem gerada (com fundo original)...")
        response = requests.get(url_com_fundo_str)
        response.raise_for_status()
        
        fd, temp_png_path = tempfile.mkstemp(suffix=".png", prefix="mascote_transparente_")
        os.close(fd)
        with open(temp_png_path, "wb") as f:
            f.write(response.content)
            
        print(f"INFO (MascotAnimator): PNG transparente salvo localmente em: {temp_png_path}")
        return temp_png_path

    def _generate_video_from_file(self, png_path: str, animation_prompt: str) -> str:
        """Gera um vídeo a partir de um arquivo de imagem local."""
        try:
            from ..agent import check_api_limit, API_CALL_TRACKER
        except ModuleNotFoundError:
            check_api_limit = lambda x: True
            API_CALL_TRACKER = {'replicate_calls': 0} # Dicionário dummy
        
        if not check_api_limit('replicate'):
            raise RuntimeError("Limite de API atingido para geração de vídeo")
        
        print(f"INFO (MascotAnimator): Gerando vídeo com base em '{os.path.basename(png_path)}'...")
        
        API_CALL_TRACKER['replicate_calls'] += 1
        
        print("DEBUG: Preparando chamada para Replicate API...")
        with open(png_path, "rb") as image_file:
            api_input = {
                "image": image_file,
                "prompt": self._enrich_animation_prompt(animation_prompt),
                "duration": 5,
                "resolution": "480p",
                "fps": 24,
                "aspect_ratio": "1:1",
                "camera_fixed": False,
                "seed": 50
            }
            try:
                print("DEBUG: Chamando replicate.run()...")
                output = replicate.run(self.VIDEO_GEN_MODEL, input=api_input)
                print(f"DEBUG: Resposta recebida com sucesso. Tipo: {type(output)}")
                video_url = output[0] if isinstance(output, list) else output
                print(f"DEBUG: URL do vídeo gerado: {video_url}")
            except Exception as e:
                print(f"ERROR: Falha ao chamar Replicate API")
                print(f"ERROR: Tipo do erro: {type(e).__name__}")
                print(f"ERROR: Mensagem: {str(e)}")
                if hasattr(e, 'response'):
                    print(f"ERROR: Response status: {getattr(e.response, 'status_code', 'N/A')}")
                    print(f"ERROR: Response body: {getattr(e.response, 'text', 'N/A')}")
                if hasattr(e, '__dict__'):
                    print(f"ERROR: Detalhes completos: {e.__dict__}")
                raise

            response = requests.get(video_url)
            response.raise_for_status()
            
            fd, video_temp_path = tempfile.mkstemp(suffix=".mp4", prefix="temp_animation_")
            os.close(fd)
            with open(video_temp_path, "wb") as f:
                f.write(response.content)
            
            return video_temp_path
    
    def _enrich_animation_prompt(self, base_prompt: str) -> str:
        """
        Enriquece o prompt de animação com contexto do Professor Virtual.
        Baseado nas especificações do agente gerador de prompts.
        """
        context = "Educational owl mascot animation for Brazilian children's learning app Professor Virtual"
        mascot_details = "friendly owl character with round shapes, large expressive eyes, warm blue (#4A90F2) and orange (#FF8A3D) colors"
        animation_style = "smooth child-friendly animation, gentle movements, encouraging gestures, educational context"
        background = "solid blue background color #0047bb matching Professor Virtual brand"
        enrichments = {
            "breathing": "subtle chest movement, natural idle animation, alive and friendly presence",
            "wave": "welcoming gesture, warm greeting for children, friendly teacher-like wave",
            "jump": "playful bounce with squash and stretch, excited but controlled movement",
            "thinking": "thoughtful expression, educational moment, lightbulb moment visualization",
            "celebration": "joyful but not overwhelming, positive reinforcement, learning achievement celebration"
        }
        
        specific_enrichment = ""
        for key, value in enrichments.items():
            if key in base_prompt.lower():
                specific_enrichment = f", {value}"
                break
        
        enriched_prompt = f"{context}: {base_prompt}"
        enriched_prompt += f", {mascot_details}"
        enriched_prompt += f", {animation_style}"
        enriched_prompt += specific_enrichment
        enriched_prompt += f", {background}"
        enriched_prompt += ", suitable for 7-11 year old children"
        enriched_prompt += ", professional educational quality"
        
        return enriched_prompt

    def _remove_video_background(self, input_video_path: str, output_video_path: str, transparent_color: str = "#00000000") -> str:
        """
        Remove o fundo de um vídeo usando a API da Replicate (lucataco/rembg-video).
        Args:
            input_video_path: Caminho absoluto para o vídeo de entrada.
            output_video_path: Caminho absoluto para salvar o vídeo com fundo removido.
            transparent_color: Cor a ser usada como transparente (ex: "#00000000" para preto transparente).
        Returns:
            Caminho absoluto para o vídeo com fundo removido.
        """
        print(f"INFO (MascotAnimator): Removendo fundo do vídeo: {input_video_path}")

        # Replicate API para rembg-video espera uma URL. 
        # Para simplificar, vamos assumir que o input_video_path pode ser usado diretamente
        # se a biblioteca replicate.run puder lidar com caminhos de arquivo locais.
        # Se não, um passo de upload temporário será necessário.
        # Por enquanto, vamos tentar passar o caminho do arquivo.

        # Nota: A API da Replicate para rembg-video não tem um parâmetro 'color' direto para o fundo.
        # Ela remove o fundo e o torna transparente. O 'transparent_color' seria mais para
        # um cenário onde você quer substituir o fundo por uma cor específica, não para a remoção.
        # A remoção de fundo já implica em transparência.

        try:
            # A API da Replicate para rembg-video espera uma URL.
            # Para testar localmente, podemos usar um serviço como ngrok ou um servidor local
            # para expor o arquivo, ou usar um arquivo já hospedado.
            # No uso real, você precisaria de um mecanismo para fazer o upload do vídeo
            # para um local acessível pela Replicate (ex: S3, Google Cloud Storage, etc.)
            # e passar a URL para a API.

            # Placeholder para o upload:
            # video_url = "URL_DO_SEU_VIDEO_HOSPEDADO"
            # Ou, se replicate.run aceitar File objects:
            with open(input_video_path, "rb") as video_file:
                api_input = {
                    "mode": "Normal", # Conforme solicitado
                    "video": video_file # Tentando passar o objeto File
                }
                print("DEBUG: Chamando replicate.run para remoção de fundo...")
                output = replicate.run(
                    "lucataco/rembg-video:c18392381d1b5410b5a76b9b0c58db132526d3f79fe602e04e0d80cb668df509",
                    input=api_input
                )
                print(f"DEBUG: Saída da Replicate API: {output}")

                # A saída é uma URL para o vídeo com fundo removido
                video_with_bg_removed_url = output

                print(f"INFO (MascotAnimator): Baixando vídeo com fundo removido de: {video_with_bg_removed_url}")
                response = requests.get(video_with_bg_removed_url, stream=True)
                response.raise_for_status()

                with open(output_video_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"INFO (MascotAnimator): Vídeo com fundo removido salvo em: {output_video_path}")
                return output_video_path

        except Exception as e:
            print(f"ERROR: Falha ao remover fundo do vídeo: {str(e)}")
            raise

    def _convert_to_webp(self, input_video_path: str, output_webp_path: str, fps: int = 12, scale: int = 256) -> str:
        """
        Converte um vídeo para o formato WebP otimizado usando FFmpeg.
        Args:
            input_video_path: Caminho absoluto para o vídeo de entrada.
            output_webp_path: Caminho absoluto para salvar o arquivo WebP.
            fps: Frames por segundo para o WebP.
            scale: Largura máxima para o vídeo (altura será ajustada proporcionalmente).
        Returns:
            Caminho absoluto para o arquivo WebP gerado.
        """
        print(f"INFO (MascotAnimator): Convertendo vídeo para WebP: {input_video_path} -> {output_webp_path}")
        cmd = [
            "ffmpeg",
            "-v", "warning",
            "-i", input_video_path,
            "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos",
            "-loop", "0",
            "-q:v", "80", # Qualidade de vídeo (0-100, 80 é um bom equilíbrio)
            "-compression_level", "6", # Nível de compressão (0-6, 6 é o máximo)
            "-y", # Sobrescrever arquivo de saída se existir
            output_webp_path
        ]
        try:
            self._run_cmd(cmd)
            print(f"INFO (MascotAnimator): Arquivo WebP gerado: {output_webp_path}")
            return output_webp_path
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Falha ao converter para WebP: {e}")
            raise

    def create_mascot_animation(self, output_path: str, input_video_path: str = None, remove_background: bool = False, fps: int = 12, scale: int = 256, prompt_details: dict = None, animation_prompt: str = None) -> str:
        """
        Orquestra o pipeline para criar uma animação de mascote.
        Pode gerar o vídeo do zero (a partir de prompt) ou processar um vídeo existente.
        Opcionalmente remove o fundo e converte para WebP.

        Args:
            output_path: Caminho absoluto para salvar o arquivo WebP final.
            input_video_path: (Opcional) Caminho absoluto para um vídeo de entrada existente.
            remove_background: Se True, remove o fundo do vídeo usando a API da Replicate.
            fps: Frames por segundo para o WebP final.
            scale: Largura máxima para o vídeo WebP final.
            prompt_details: (Opcional) Dicionário com detalhes do prompt para gerar a imagem do mascote.
            animation_prompt: (Opcional) String com o prompt para animar o mascote.

        Returns:
            Caminho absoluto para o arquivo WebP gerado.
        """
        print(f"--- Iniciando Pipeline de Animação de Mascote para: {os.path.basename(output_path)} ---")

        video_to_process_path = None
        temp_png_path = None
        temp_video_generated = None
        temp_video_with_bg_removed = None

        try:
            if input_video_path:
                video_to_process_path = input_video_path
                print(f"INFO (MascotAnimator): Usando vídeo de entrada existente: {input_video_path}")
            elif prompt_details and animation_prompt:
                print("INFO (MascotAnimator): Gerando vídeo a partir de prompts...")
                temp_png_path = self._get_transparent_mascot_png(prompt_details)
                temp_video_generated = self._generate_video_from_file(temp_png_path, animation_prompt)
                video_to_process_path = temp_video_generated
            else:
                raise ValueError("É necessário fornecer 'input_video_path' OU 'prompt_details' e 'animation_prompt'.")

            if remove_background:
                fd, temp_video_with_bg_removed = tempfile.mkstemp(suffix=".mp4", prefix="mascot_rembg_")
                os.close(fd)
                video_to_process_path = self._remove_video_background(video_to_process_path, temp_video_with_bg_removed)

            final_webp_path = self._convert_to_webp(video_to_process_path, output_path, fps, scale)

            print(f"--- Pipeline de Animação de Mascote concluído! Arquivo salvo em: {final_webp_path} ---")
            return final_webp_path

        except Exception as e:
            raise RuntimeError(f"Erro no pipeline de animação de mascote: {str(e)}") from e
        finally:
            # Limpeza de arquivos temporários
            if temp_png_path and os.path.exists(temp_png_path):
                try:
                    os.remove(temp_png_path)
                except Exception as e:
                    print(f"WARN: Falha ao remover arquivo temporário {temp_png_path}: {e}")
            if temp_video_generated and os.path.exists(temp_video_generated):
                try:
                    os.remove(temp_video_generated)
                except Exception as e:
                    print(f"WARN: Falha ao remover arquivo temporário {temp_video_generated}: {e}")
            if temp_video_with_bg_removed and os.path.exists(temp_video_with_bg_removed):
                try:
                    os.remove(temp_video_with_bg_removed)
                except Exception as e:
                    print(f"WARN: Falha ao remover arquivo temporário {temp_video_with_bg_removed}: {e}")
        """
        Orquestra o pipeline para processar um vídeo de mascote.
        Opcionalmente remove o fundo e converte para WebP.
        Args:
            input_video_path: Caminho absoluto para o vídeo de entrada.
            output_path: Caminho absoluto para salvar o arquivo WebP final.
            remove_background: Se True, remove o fundo do vídeo usando a API da Replicate.
            fps: Frames por segundo para o WebP final.
            scale: Largura máxima para o vídeo WebP final.
        Returns:
            Caminho absoluto para o arquivo WebP gerado.
        """
        print(f"--- Iniciando Pipeline de Animação de Mascote para: {os.path.basename(output_path)} ---")

        processed_video_path = input_video_path
        temp_video_with_bg_removed = None

        try:
            if remove_background:
                # Cria um arquivo temporário para o vídeo com fundo removido
                fd, temp_video_with_bg_removed = tempfile.mkstemp(suffix=".mp4", prefix="mascot_rembg_")
                os.close(fd)
                processed_video_path = self._remove_video_background(input_video_path, temp_video_with_bg_removed)

            final_webp_path = self._convert_to_webp(processed_video_path, output_path, fps, scale)

            print(f"--- Pipeline de Animação de Mascote concluído! Arquivo salvo em: {final_webp_path} ---")
            return final_webp_path

        except Exception as e:
            raise RuntimeError(f"Erro no pipeline de animação de mascote: {str(e)}") from e
        finally:
            # Limpeza de arquivos temporários
            if temp_video_with_bg_removed and os.path.exists(temp_video_with_bg_removed):
                try:
                    os.remove(temp_video_with_bg_removed)
                except Exception as e:
                    print(f"WARN: Falha ao remover arquivo temporário {temp_video_with_bg_removed}: {e}")
