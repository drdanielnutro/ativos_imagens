# ativos_imagens/tools/mascot_animator_v2.py

import os
import subprocess
import tempfile
import shutil
import sys
from pathlib import Path

import cv2
from lottie import objects as lottie_objects
from lottie.parsers import svg as lottie_svg
import replicate
import requests

# Importa a ImageGenerator para reutilizar a lógica de geração de PNG 
from .image_generator import ImageGenerator

class MascotAnimatorV2:
    """
    Versão melhorada do MascotAnimator que usa isolamento de processos
    para evitar problemas de serialização JSON no Replicate.
    """
    VIDEO_GEN_MODEL = "kwaivgi/kling-v2.0"

    def _isolated_bg_removal(self, image_url: str) -> str:
        """
        Executa remoção de fundo em processo isolado para evitar problemas de serialização JSON.
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
                timeout=120,  # 2 minutos timeout
                cwd=os.getcwd()  # Garantir diretório correto
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

    def _get_transparent_mascot_png(self, prompt_details: dict) -> str:
        """
        Etapa 1 e 2 do pipeline: Gera e obtém um PNG local do mascote com fundo transparente.
        Versão com isolamento de processos.
        """
        # Verificar limites de API
        from ..agent import check_api_limit, API_CALL_TRACKER
        
        if not check_api_limit('replicate'):
            raise RuntimeError("Limite de API atingido para geração de imagem do mascote")
        
        generator = ImageGenerator()
        
        print("INFO (MascotAnimatorV2): Etapa 1.1 - Gerando imagem base do mascote...")
        
        # Incrementar contador para geração
        API_CALL_TRACKER['replicate_calls'] += 1
        urls_com_fundo = generator._generate_mascot_image(prompt_details)
        url_com_fundo = urls_com_fundo[0]

        print("INFO (MascotAnimatorV2): Etapa 1.2 - Removendo fundo (processo isolado)...")
        
        # Verificar limite novamente para remoção de fundo
        if not check_api_limit('replicate'):
            raise RuntimeError("Limite de API atingido durante remoção de fundo")
        
        API_CALL_TRACKER['replicate_calls'] += 1
        
        # USAR ISOLAMENTO DE PROCESSOS
        url_sem_fundo = self._isolated_bg_removal(url_com_fundo)
        
        print("INFO (MascotAnimatorV2): Etapa 1.3 - Baixando imagem transparente...")
        response = requests.get(url_sem_fundo)
        response.raise_for_status()
        
        # Salva em um arquivo temporário que persistirá até o fim do processo
        fd, temp_png_path = tempfile.mkstemp(suffix=".png", prefix="mascote_transparente_")
        os.close(fd)
        with open(temp_png_path, "wb") as f:
            f.write(response.content)
            
        print(f"INFO (MascotAnimatorV2): PNG transparente salvo localmente em: {temp_png_path}")
        return temp_png_path

    def _generate_video_from_file(self, png_path: str, animation_prompt: str) -> str:
        """Etapa 3: Gera um vídeo a partir de um arquivo de imagem local."""
        from ..agent import check_api_limit, API_CALL_TRACKER
        
        if not check_api_limit('replicate'):
            raise RuntimeError("Limite de API atingido para geração de vídeo")
        
        print(f"INFO (MascotAnimatorV2): Etapa 2 - Gerando vídeo com base em '{os.path.basename(png_path)}'...")
        
        API_CALL_TRACKER['replicate_calls'] += 1
        
        with open(png_path, "rb") as image_file:
            api_input = {
                "prompt": animation_prompt,
                "start_image": image_file,  # Usar imagem como frame inicial
                "duration": 5,              # 5 segundos de vídeo
                "cfg_scale": 0.7,          # Seguir prompt moderadamente
                "aspect_ratio": "1:1",     # Formato quadrado para mascote
                "negative_prompt": "blurry, low quality, distorted"
            }
            output = replicate.run(self.VIDEO_GEN_MODEL, input=api_input)
            video_url = output[0] if isinstance(output, list) else output

            response = requests.get(video_url)
            response.raise_for_status()
            
            fd, video_temp_path = tempfile.mkstemp(suffix=".mp4", prefix="temp_animation_")
            os.close(fd)
            with open(video_temp_path, "wb") as f:
                f.write(response.content)
            
            return video_temp_path

    def _extract_frames(self, video_path: str, frames_dir: str, target_fps: int = 12) -> int:
        """Etapa 4: Extrai frames do vídeo na taxa de quadros desejada."""
        print(f"INFO (MascotAnimatorV2): Etapa 3 - Extraindo frames para '{frames_dir}' a {target_fps} FPS.")
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
        print(f"INFO (MascotAnimatorV2): {saved_frame_count} frames extraídos.")
        
        # Validação de frames mínimos
        if saved_frame_count < 12:  # Menos de 1 segundo a 12fps
            raise ValueError(f"Poucos frames extraídos ({saved_frame_count}). Vídeo pode estar corrompido ou muito curto.")
        
        return saved_frame_count

    def _vectorize_frames(self, frames_dir: str, svg_dir: str, frame_count: int) -> None:
        """Etapa 5: Vetoriza cada frame PNG para SVG usando Potrace."""
        print("INFO (MascotAnimatorV2): Etapa 4 - Vetorizando frames para SVG...")
        
        for i in range(frame_count):
            png_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
            pbm_path = os.path.join(frames_dir, f"frame_{i:04d}.pbm")
            svg_path = os.path.join(svg_dir, f"frame_{i:04d}.svg")

            # Converter para PBM primeiro
            subprocess.run([
                "mkbitmap", "-f", "2", "-s", "2", "-t", "0.48", 
                "-o", pbm_path, png_path
            ], check=True, capture_output=True)
            
            # Vetorizar com parâmetros otimizados
            subprocess.run([
                "potrace", pbm_path, "-s", 
                "-o", svg_path,
                "--turdsize", "10",      # Remove detalhes pequenos
                "--opttolerance", "0.2"  # Otimiza curvas
            ], check=True, capture_output=True)
            
        print("INFO (MascotAnimatorV2): Vetorização de todos os frames concluída.")

    def _compile_lottie(self, svg_dir: str, frame_count: int, fps: int) -> lottie_objects.Animation:
        """Etapa 6: Compila a sequência de SVGs em uma animação Lottie."""
        print("INFO (MascotAnimatorV2): Etapa 5 - Compilando SVGs em uma animação Lottie...")
        
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
        Versão com isolamento de processos para evitar problemas de serialização JSON.
        """
        print(f"--- Iniciando Pipeline V2 de Animação Lottie para: {os.path.basename(output_path)} ---")
        
        transparent_png_path = None
        video_path = None
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Etapa 1: Gerar PNG transparente do mascote (COM ISOLAMENTO)
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
            raise RuntimeError(f"Erro no pipeline de animação V2: {str(e)}") from e
        
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

        print(f"--- Pipeline Lottie V2 concluído! Arquivo salvo em: {output_path} ---")
        return f"Sucesso! Animação Lottie V2 salva em: {output_path}"