# ativos_imagens/tools/mascot_animator.py

import os
import subprocess
import tempfile
import shutil
from pathlib import Path

import cv2
from lottie import objects as lottie_objects
from lottie.parsers import svg as lottie_svg
import replicate
import requests

# Importa a ImageGenerator para reutilizar a lógica de geração de PNG e remoção de fundo
from .image_generator import ImageGenerator

class MascotAnimator:
    """
    Ferramenta para criar animações Lottie do mascote "PROF"
    usando um pipeline completo de Imagem-para-Vídeo-para-Vetor.
    """
    VIDEO_GEN_MODEL = "bytedance/seedance-1-lite"

    def _get_transparent_mascot_png(self, prompt_details: dict) -> str:
        """
        Etapa 1 e 2 do pipeline: Gera e obtém um PNG local do mascote com fundo transparente.
        Retorna o caminho do arquivo temporário.
        """
        # Verificar limites de API
        from ..agent import check_api_limit, API_CALL_TRACKER
        
        if not check_api_limit('replicate'):
            raise RuntimeError("Limite de API atingido para geração de imagem do mascote")
        
        generator = ImageGenerator()
        
        print("INFO (MascotAnimator): Etapa 1.1 - Gerando imagem base do mascote...")
        
        # Incrementar contador para geração
        API_CALL_TRACKER['replicate_calls'] += 1
        urls_com_fundo = generator._generate_mascot_image(prompt_details)
        
        # Convertendo o objeto FileOutput para uma string de URL.
        # A biblioteca Replicate retorna uma lista de objetos, então pegamos o primeiro [0]
        # e convertemos para string para obter a URL.
        url_com_fundo_str = str(urls_com_fundo[0])

        print("INFO (MascotAnimator): Etapa 1.2 - Removendo fundo da imagem gerada...")
        
        # Verificar limite novamente para remoção de fundo
        if not check_api_limit('replicate'):
            raise RuntimeError("Limite de API atingido durante remoção de fundo")
        
        API_CALL_TRACKER['replicate_calls'] += 1
        # Agora passamos a string da URL, o que evita o erro de serialização JSON.
        url_sem_fundo_str = generator._remove_background(url_com_fundo_str)
        
        print("INFO (MascotAnimator): Etapa 1.3 - Baixando imagem transparente...")
        response = requests.get(url_sem_fundo_str)
        response.raise_for_status()
        
        # Salva em um arquivo temporário que persistirá até o fim do processo
        fd, temp_png_path = tempfile.mkstemp(suffix=".png", prefix="mascote_transparente_")
        os.close(fd)
        with open(temp_png_path, "wb") as f:
            f.write(response.content)
            
        print(f"INFO (MascotAnimator): PNG transparente salvo localmente em: {temp_png_path}")
        return temp_png_path

    def _generate_video_from_file(self, png_path: str, animation_prompt: str) -> str:
        """Etapa 3: Gera um vídeo a partir de um arquivo de imagem local."""
        from ..agent import check_api_limit, API_CALL_TRACKER
        
        if not check_api_limit('replicate'):
            raise RuntimeError("Limite de API atingido para geração de vídeo")
        
        print(f"INFO (MascotAnimator): Etapa 2 - Gerando vídeo com base em '{os.path.basename(png_path)}'...")
        
        # Logs de debug para troubleshooting
        print(f"DEBUG: Modelo de vídeo: {self.VIDEO_GEN_MODEL}")
        print(f"DEBUG: Prompt de animação: '{animation_prompt}'")
        print(f"DEBUG: Arquivo PNG existe? {os.path.exists(png_path)}")
        print(f"DEBUG: Tamanho do arquivo: {os.path.getsize(png_path)} bytes")
        
        API_CALL_TRACKER['replicate_calls'] += 1
        
        print("DEBUG: Preparando chamada para Replicate API...")
        with open(png_path, "rb") as image_file:
            api_input = {
                "image": image_file,
                "prompt": animation_prompt,
                "duration": 5,  # Seedance aceita apenas 5 ou 10 
                "resolution": "480p", 
                "fps": 24,  # Geramos com mais FPS para ter mais de onde extrair
                "aspect_ratio": "1:1",  # Quadrado para o mascote
                "camera_fixed": False,  # Permitir movimento de câmera
                "seed": 50  # Para reprodutibilidade
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

    def _extract_frames(self, video_path: str, frames_dir: str, target_fps: int = 12) -> int:
        """Etapa 4: Extrai frames do vídeo na taxa de quadros desejada."""
        print(f"INFO (MascotAnimator): Etapa 3 - Extraindo frames para '{frames_dir}' a {target_fps} FPS.")
        cap = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        if video_fps == 0: 
            video_fps = 24  # Fallback

        saved_frame_count = 0
        frame_interval = video_fps / target_fps

        current_frame = 0
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
            
            if current_frame >= saved_frame_count * frame_interval:
                frame_path = os.path.join(frames_dir, f"frame_{saved_frame_count:04d}.png")
                cv2.imwrite(frame_path, image)
                saved_frame_count += 1
            
            current_frame += 1
        
        cap.release()
        print(f"INFO (MascotAnimator): {saved_frame_count} frames extraídos.")
        
        # Validação de frames mínimos
        if saved_frame_count < 12:  # Menos de 1 segundo a 12fps
            raise ValueError(f"Poucos frames extraídos ({saved_frame_count}). Vídeo pode estar corrompido ou muito curto.")
        
        return saved_frame_count

    def _vectorize_frames(self, frames_dir: str, svg_dir: str, frame_count: int) -> None:
        """Etapa 5: Vetoriza cada frame PNG para SVG usando Potrace."""
        print("INFO (MascotAnimator): Etapa 4 - Vetorizando frames para SVG...")
        
        for i in range(frame_count):
            png_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
            pbm_path = os.path.join(frames_dir, f"frame_{i:04d}.pbm")
            svg_path = os.path.join(svg_dir, f"frame_{i:04d}.svg")

            # Converter PNG para PNM primeiro (mkbitmap não aceita PNG)
            pnm_path = os.path.join(frames_dir, f"frame_{i:04d}.pnm")
            
            # Converter PNG para PNM usando ImageMagick ou PIL
            try:
                # Opção 1: Usar ImageMagick convert
                subprocess.run([
                    "convert", png_path, pnm_path
                ], check=True, capture_output=True, text=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Opção 2: Usar PIL/Pillow como fallback
                from PIL import Image
                img = Image.open(png_path)
                img.save(pnm_path, "PPM")
            
            # Agora converter PNM para PBM otimizado
            try:
                result = subprocess.run([
                    "mkbitmap", "-f", "2", "-s", "2", "-t", "0.48", 
                    "-o", pbm_path, pnm_path
                ], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                print(f"ERROR: mkbitmap falhou para frame {i}")
                print(f"ERROR: Return code: {e.returncode}")
                print(f"ERROR: Stdout: {e.stdout}")
                print(f"ERROR: Stderr: {e.stderr}")
                raise
            
            # Vetorizar com parâmetros otimizados
            subprocess.run([
                "potrace", pbm_path, "-s", 
                "-o", svg_path,
                "--turdsize", "10",      # Remove detalhes pequenos
                "--opttolerance", "0.2"  # Otimiza curvas
            ], check=True, capture_output=True)
            
        print("INFO (MascotAnimator): Vetorização de todos os frames concluída.")

    def _compile_lottie(self, svg_dir: str, frame_count: int, fps: int) -> lottie_objects.Animation:
        """Etapa 6: Compila a sequência de SVGs em uma animação Lottie."""
        print("INFO (MascotAnimator): Etapa 5 - Compilando SVGs em uma animação Lottie...")
        
        animation = lottie_objects.Animation(fps, frame_count)
        animation.fr = fps  # Garante FPS correto
        animation.ip = 0    # In-point
        animation.op = frame_count  # Out-point
        
        for i in range(frame_count):
            svg_path = os.path.join(svg_dir, f"frame_{i:04d}.svg")
            
            try:
                layer = lottie_svg.parse_svg_file(svg_path)
                layer.in_point = i
                layer.out_point = i + 1
                layer.ao = 0  # Auto-orient off para otimização
                animation.add_layer(layer)
            except Exception as e:
                print(f"AVISO: Erro ao processar frame {i}: {e}")
                # Continua com os outros frames
                continue
                
        return animation

    def create_mascot_animation(self, prompt_details: dict, animation_prompt: str, output_path: str) -> str:
        """
        Orquestra o pipeline completo para criar uma animação Lottie do mascote.
        """
        print(f"--- Iniciando Pipeline de Animação Lottie para: {os.path.basename(output_path)} ---")
        
        transparent_png_path = None
        video_path = None
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Etapa 1: Gerar PNG transparente do mascote
                transparent_png_path = self._get_transparent_mascot_png(prompt_details)
                
                # Etapa 2: Gerar vídeo a partir da imagem
                video_path = self._generate_video_from_file(transparent_png_path, animation_prompt)
                
                # Etapa 3: Extrair frames do vídeo
                frames_dir = os.path.join(tmpdir, "frames")
                os.makedirs(frames_dir)
                frame_count = self._extract_frames(video_path, frames_dir)
                
                if frame_count == 0:
                    raise RuntimeError("Nenhum frame foi extraído do vídeo.")

                # Etapa 4: Vetorizar frames
                svg_dir = os.path.join(tmpdir, "svgs")
                os.makedirs(svg_dir)
                self._vectorize_frames(frames_dir, svg_dir, frame_count)
                
                # Etapa 5: Compilar Lottie
                animation = self._compile_lottie(svg_dir, frame_count, 12)
                
                # Etapa 6: Salvar arquivo final
                with open(output_path, "w") as f:
                    lottie_objects.script.dump(animation, f)
        
        except Exception as e:
            # Re-raise com contexto adicional
            raise RuntimeError(f"Erro no pipeline de animação: {str(e)}") from e
        
        finally:
            # Limpeza dos arquivos temporários principais
            if transparent_png_path and os.path.exists(transparent_png_path):
                try:
                    os.remove(transparent_png_path)
                except:
                    pass  # Ignore erros de limpeza
            if video_path and os.path.exists(video_path):
                try:
                    os.remove(video_path)
                except:
                    pass  # Ignore erros de limpeza

        print(f"--- Pipeline Lottie concluído! Arquivo salvo em: {output_path} ---")
        return f"Sucesso! Animação Lottie salva em: {output_path}"