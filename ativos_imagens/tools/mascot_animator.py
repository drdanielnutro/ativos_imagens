# ativos_imagens/tools/mascot_animator.py

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import zipfile
import json

import cv2
from lottie import objects as lottie_objects
from lottie.parsers import svg as lottie_svg
from lottie import exporters
import replicate
import requests

import sys
from PIL import Image

# Importa a ImageGenerator para reutilizar a lógica de geração de PNG e remoção de fundo
from .image_generator import ImageGenerator

class MascotAnimator:
    """
    Ferramenta para criar animações Lottie do mascote "PROF"
    usando um pipeline completo de Imagem-para-Vídeo-para-Vetor.
    """
    VIDEO_GEN_MODEL = "bytedance/seedance-1-lite"
    DEFAULT_BMP_COLORS = "8"  # Número padrão de cores para vetorização

    VERBOSE_SUBPROCESS = True  # Exibir stdout/stderr das ferramentas externas

    # Helper para rodar comandos e printar saída
    def _run_cmd(self, cmd: list[str]):
        """Executa subprocess.run exibindo stdout/stderr se VERBOSE_SUBPROCESS."""
        import subprocess, shlex
        print(f"EXEC ⟩ {shlex.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if self.VERBOSE_SUBPROCESS:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        return result

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
                "prompt": f"{animation_prompt}, solid blue background color #0047bb",
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

    def _subsample_every_other_frame(self, frames_dir: str, frame_count: int) -> int:
        """
        Remove metade dos frames mantendo apenas os de índice ímpar (ou par),
        renomeando os remanescentes para que a sequência continue contígua
        (frame_0000.png, frame_0001.png, ...).

        Args:
            frames_dir: diretório onde estão os PNGs extraídos.
            frame_count: número total de frames atuais.

        Returns:
            Novo número de frames após subsampling.
        """
        print("INFO (MascotAnimator): Realizando subsampling – mantendo apenas metade dos frames…")

        kept_index = 0
        for original_idx in range(frame_count):
            png_path = os.path.join(frames_dir, f"frame_{original_idx:04d}.png")
            if not os.path.exists(png_path):
                # Já pode ter sido removido/renomeado em iterações anteriores
                continue

            # Manter apenas os frames de índice ímpar (alternando)
            if original_idx % 2 == 0:
                # Remove este frame
                os.remove(png_path)
            else:
                # Renomeia para posição compactada
                new_path = os.path.join(frames_dir, f"frame_{kept_index:04d}.png")
                os.rename(png_path, new_path)
                kept_index += 1

        print(f"INFO (MascotAnimator): Subsampling concluído. {kept_index} frames restantes.")
        if kept_index < 6:
            raise ValueError("Subsampling resultou em poucos frames; a animação pode ficar truncada.")
        return kept_index

    def _vectorize_frames(self, frames_dir: str, svg_dir: str, frame_count: int) -> None:
        """Etapa 4: Vetoriza cada frame PNG para SVG usando Potrace."""
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
                self._run_cmd(["convert", png_path, pnm_path])
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Opção 2: Usar PIL/Pillow como fallback
                from PIL import Image
                img = Image.open(png_path)
                img.save(pnm_path, "PPM")
            
            # Agora converter PNM para PBM otimizado
            try:
                self._run_cmd(["mkbitmap", "-f", "2", "-s", "2", "-t", "0.48", "-o", pbm_path, pnm_path])
            except subprocess.CalledProcessError as e:
                print(f"ERROR: mkbitmap falhou para frame {i}")
                print(f"ERROR: Return code: {e.returncode}")
                print(f"ERROR: Stdout: {e.stdout}")
                print(f"ERROR: Stderr: {e.stderr}")
                raise
            
            # Vetorizar com parâmetros otimizados
            self._run_cmd([
                "potrace", pbm_path, "-s", 
                "-o", svg_path,
                "--turdsize", "10",      # Remove detalhes pequenos
                "--opttolerance", "0.2"  # Otimiza curvas
            ])
            
            # Otimizar SVG com SVGO (se instalado)
            try:
                self._run_cmd(["svgo", "--multipass", svg_path])
            except FileNotFoundError:
                print("WARN: SVGO não encontrado. Pulando otimização de SVG.")
            
        print("INFO (MascotAnimator): Vetorização de todos os frames concluída.")

    def _compile_lottie(self, svg_dir: str, frame_count: int, fps: int) -> lottie_objects.Animation:
        """Etapa 6: Compila a sequência de SVGs em uma animação Lottie."""
        print("INFO (MascotAnimator): Etapa 5 - Compilando SVGs em uma animação Lottie...")
        
        animation = lottie_objects.Animation(n_frames=frame_count, framerate=fps)
        animation.frame_rate = fps  # Garante FPS correto
        animation.in_point = 0    # In-point
        animation.out_point = frame_count  # Out-point
        
        for i in range(frame_count):
            svg_path = os.path.join(svg_dir, f"frame_{i:04d}.svg")
            
            try:
                # parse_svg_file retorna um objeto Animation, precisamos de suas camadas
                parsed_animation = lottie_svg.parse_svg_file(svg_path)
                for layer in parsed_animation.layers:
                    layer.in_point = i
                    layer.out_point = i + 1
                    layer.ao = 0  # Auto-orient off para otimização
                    animation.add_layer(layer)
            except Exception as e:
                print(f"AVISO: Erro ao processar frame {i}: {e}")
                # Continua com os outros frames
                continue
                
        return animation

    def _optimize_json(self, json_path: str, level: int = 2) -> str:
        """Aplica python-lottie --optimize ao JSON gerado."""
        import subprocess, sys, os, shutil

        lottie_convert_path = os.path.join(os.path.dirname(sys.executable), "lottie_convert.py")
        if not os.path.exists(lottie_convert_path):
            print("WARN: lottie_convert.py não encontrado. Pulando otimização JSON.")
            return json_path

        temp_out = json_path.replace(".json", "_opt.json")
        try:
            self._run_cmd([
                lottie_convert_path, json_path, temp_out,
                "--input-format", "lottie",
                "--output-format", "lottie",
                "--optimize", str(level)
            ])

            shutil.move(temp_out, json_path)
            print("INFO (MascotAnimator): JSON otimizado com python-lottie (level %s)." % level)
        except subprocess.CalledProcessError as e:
            print(f"WARN: Otimização JSON falhou: {e.stderr}\nContinuando com arquivo original.")
        return json_path

    def _create_dotlottie(self, json_path: str) -> str:
        """
        Converte JSON para formato .lottie (ZIP comprimido) com otimizações máximas.
        
        Args:
            json_path: Caminho do arquivo JSON Lottie
            
        Returns:
            Caminho do arquivo .lottie criado
        """
        print("INFO (MascotAnimator): Iniciando conversão para formato .lottie...")

        lottie_path = json_path.replace('.json', '.lottie')

        try:
            # Passo 1: Ler e minificar o JSON
            print("  - Lendo e minificando JSON...")
            with open(json_path, 'r') as f:
                animation_data = json.load(f)

            minified_json = json.dumps(animation_data, separators=(',', ':'))

            # Passo 2: Criar estrutura do dotLottie
            print("  - Criando estrutura dotLottie...")
            manifest = {
                "animations": [{
                    "id": "a",
                    "path": "a.json"
                }],
                "version": "1.0"
            }

            # Passo 3: Criar arquivo ZIP com compressão máxima
            print("  - Comprimindo com ZIP_DEFLATED nível 9...")
            with zipfile.ZipFile(
                lottie_path,
                'w',
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=9
            ) as zf:
                zf.writestr(
                    'manifest.json',
                    json.dumps(manifest, separators=(',', ':')),
                    compress_type=zipfile.ZIP_DEFLATED
                )
                zf.writestr(
                    'a.json',
                    minified_json,
                    compress_type=zipfile.ZIP_DEFLATED
                )

            # Passo 4: Análise detalhada de tamanhos
            original_size = os.path.getsize(json_path)
            compressed_size = os.path.getsize(lottie_path)

            print(f"\n Análise de Compressão:")
            print(f"  - JSON original: {original_size:,} bytes ({original_size/1024:.1f} KB)")
            print(f"  - JSON minificado: {len(minified_json):,} bytes ({len(minified_json)/1024:.1f} KB)")
            print(f"  - .lottie final: {compressed_size:,} bytes ({compressed_size/1024:.1f} KB)")

            reduction_percent = ((original_size - compressed_size) / original_size) * 100
            print(f"  - Redução total: {reduction_percent:.1f}%")

            # Passo 5: Validação do objetivo
            size_kb = compressed_size / 1024
            if size_kb <= 100:
                print(f"\n✅ SUCESSO: Arquivo .lottie com {size_kb:.1f} KB (< 100 KB)")
            else:
                print(f"\n⚠️ AVISO: Arquivo ainda grande: {size_kb:.1f} KB")
                print("  Sugestões para reduzir mais:")
                print("  - Diminuir --bmp-n-colors para 4 ou 2")
                print("  - Reduzir número de frames")
                print("  - Simplificar a animação")

            return lottie_path

        except Exception as e:
            print(f"❌ ERRO ao criar .lottie: {str(e)}")
            import traceback
            traceback.print_exc()
            return json_path

    def create_mascot_animation_v2(self, prompt_details: dict, animation_prompt: str, output_path: str, output_format: str = "lottie") -> str:
        """
        Pipeline otimizado usando lottie_convert.py com modo polygon (Potrace) para vetorização.
        """
        print(f"--- Iniciando Pipeline v2 de Animação Lottie (modo polygon) para: {os.path.basename(output_path)} ---")

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
                
                # Subsampling: manter somente metade dos frames
                frame_count = self._subsample_every_other_frame(frames_dir, frame_count)
                
                if frame_count == 0:
                    raise RuntimeError("Nenhum frame foi extraído do vídeo.")
                
                # Etapa 4: Usar lottie_convert.py com modo polygon
                print("INFO (MascotAnimator): Etapa 4 - Vetorizando com lottie_convert.py (modo polygon)...")
                
                # Verificar disponibilidade do modo polygon (deve existir por padrão)
                lottie_convert_path = os.path.join(os.path.dirname(sys.executable), "lottie_convert.py")
                check_cmd = [lottie_convert_path, "--help"]
                check_result = self._run_cmd(check_cmd)
                if "polygon" not in check_result.stdout:
                    print("⚠️  AVISO: Flag '--bmp-mode polygon' não encontrada na ajuda do lottie_convert.py. Verifique a instalação da biblioteca 'lottie'.")
                
                # Coletar todos os frames
                frame_files = []
                for i in range(frame_count):
                    frame_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
                    if os.path.exists(frame_path):
                        frame_files.append(frame_path)
                
                if not frame_files:
                    raise ValueError("Nenhum frame encontrado para processar")
                
                # Criar GIF temporário com todos os frames
                temp_gif = os.path.join(tmpdir, "all_frames.gif")
                print(f"INFO: Criando GIF temporário com {len(frame_files)} frames...")
                
                # Usar PIL para criar o GIF
                pil_images = []
                for frame_path in frame_files:
                    img = Image.open(frame_path)
                    pil_images.append(img)
                
                # Salvar como GIF animado
                pil_images[0].save(
                    temp_gif,
                    save_all=True,
                    append_images=pil_images[1:],
                    duration=83,  # ~12 FPS (1000ms / 12fps = 83ms por frame)
                    loop=0,
                    optimize=False  # Não otimizar GIF, queremos qualidade máxima
                )
                
                print(f"GIF criado: {temp_gif} ({os.path.getsize(temp_gif) / 1024:.1f} KB)")
                
                # Criar Lottie temporário
                temp_lottie = os.path.join(tmpdir, "animation_temp.json")
                
                # Comando para converter GIF em Lottie com vetorização polygon
                cmd = [
                    lottie_convert_path,         # Usar caminho completo
                    temp_gif,                    # Entrada: GIF com todos os frames
                    temp_lottie,                 # Saída: arquivo JSON Lottie
                    "--input-format", "bmp",     # Formato de entrada (funciona para GIF também)
                    "--output-format", "lottie", # Formato de saída
                    "--bmp-mode", "polygon",     # Modo polygon com Potrace para vetorização suave
                    "--bmp-n-colors", self.DEFAULT_BMP_COLORS,       # Limitar paleta
                    "--optimize", "2",           # Otimização máxima do JSON
                ]
                
                print(f"Executando comando de vetorização com modo polygon...")
                print(f"Comando: {' '.join(cmd)}")
                result = self._run_cmd(cmd)
                
                if result.returncode != 0:
                    print(f"ERRO: {result.stderr}")
                    raise RuntimeError(f"Erro na vetorização: {result.stderr}")
                
                print("Vetorização com modo polygon concluída com sucesso!")
                
                # Copiar para o destino
                shutil.copy2(temp_lottie, output_path)
                
                # Log do tamanho
                json_size = os.path.getsize(output_path) / 1024
                print(f"Tamanho do JSON gerado: {json_size:.1f} KB")
                
                # Converter para formato .lottie se solicitado
                if output_format == "lottie":
                    final_path = self._create_dotlottie(output_path)
                    # Mantemos o JSON original para inspeção
                    print(f"--- Pipeline v2 concluído! Arquivo salvo em: {final_path} ---")
                    return final_path
                
                print(f"--- Pipeline v2 concluído! Arquivo JSON salvo em: {output_path} ---")
                return output_path
        
        except Exception as e:
            # Re-raise com contexto adicional
            raise RuntimeError(f"Erro no pipeline v2 de animação: {str(e)}") from e
        
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

    def create_mascot_animation(self, prompt_details: dict, animation_prompt: str, output_path: str, output_format: str = "lottie") -> str:
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
                
                # Subsampling: manter somente metade dos frames
                frame_count = self._subsample_every_other_frame(frames_dir, frame_count)
                
                if frame_count == 0:
                    raise RuntimeError("Nenhum frame foi extraído do vídeo.")

                # Etapa 4: Vetorizar frames
                svg_dir = os.path.join(tmpdir, "svgs")
                os.makedirs(svg_dir)
                self._vectorize_frames(frames_dir, svg_dir, frame_count)
                
                # Etapa 5: Compilar Lottie
                animation = self._compile_lottie(svg_dir, frame_count, 12)
                
                # Etapa 6: Salvar arquivo final
                exporters.export_lottie(animation, output_path)
                
                # Otimizar JSON gerado com python-lottie (level 2)
                self._optimize_json(output_path, level=2)
                
                # Converter para formato .lottie se solicitado
                if output_format == "lottie":
                    final_path = self._create_dotlottie(output_path)
                    # Mantemos o JSON original para inspeção
                    print(f"--- Pipeline Lottie concluído! Arquivo salvo em: {final_path} ---")
                    return final_path
                
                print(f"--- Pipeline Lottie concluído! Arquivo salvo em: {output_path} ---")
                return output_path
        
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

        # Note: output_path pode ter sido modificado para .lottie
        # A mensagem final e retorno são tratados dentro do try block