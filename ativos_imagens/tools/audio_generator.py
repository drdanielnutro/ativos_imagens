"""
Ferramenta para geração de efeitos sonoros usando modelos de IA.
Implementa estratégia híbrida: stable-audio para SFX, musicgen para tons musicais.
"""

import replicate
import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis do .env
from pydub import AudioSegment
import tempfile
from typing import Optional, Dict, Union

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class AudioEffectGenerator:
    """
    Gera e processa efeitos sonoros usando modelos de IA da Replicate.
    Suporta uma estratégia híbrida para selecionar o melhor modelo por tipo de som
    e inclui processamento avançado para conformidade com especificações exatas.
    """
    
    MODELS = {
        "stable-audio": {
            "identifier": "stackadoc/stable-audio-open-1.0:9aff84a639f96d0f7e6081cdea002d15133d0043727f849c40abdd166b7c75a8",
            "type": "sfx"
        }
    }
    
    

    def __init__(self, replicate_token: Optional[str] = None):
        """
        Inicializa o gerador de efeitos sonoros.
        
        Args:
            replicate_token: Token da API da Replicate. Se não fornecido, tenta usar variável de ambiente.
        """
        self.replicate_token = replicate_token or os.getenv('REPLICATE_API_TOKEN')
        if not self.replicate_token:
            raise ValueError("Token da API da Replicate é obrigatório. Configure REPLICATE_API_TOKEN no .env")
        
        self.client = replicate.Client(api_token=self.replicate_token)

    def generate_sound_effect(self, filename: str, duration: float, model: str, prompt: str, negative_prompt: str = "", output_dir: str = "generated_audio") -> str:
        """
        Gera um efeito sonoro com base nos parâmetros fornecidos.
        
        Args:
            filename: Nome do arquivo de saída (ex: 'button_tap.mp3')
            duration: Duração desejada do áudio em segundos.
            model: Modelo de IA a ser usado ('stable-audio' ou 'musicgen').
            prompt: Prompt de texto para a geração do áudio.
            negative_prompt: Prompt negativo para a geração do áudio (opcional).
            output_dir: Diretório onde salvar o arquivo gerado.
            
        Returns:
            str: Caminho do arquivo gerado ou string vazia se falhar.
        """
        output_filename = os.path.join(output_dir, filename)
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        logging.info(f"Iniciando geração para '{filename}' usando modelo '{model}'")
        
        try:
            # 1. Chamar a API da Replicate
            raw_audio_url = self._call_replicate_model(
                prompt=prompt,
                duration=duration,
                model_choice=model,
                negative_prompt=negative_prompt
            )
            
            if not raw_audio_url:
                logging.error(f"Falha ao obter URL de áudio da Replicate para '{filename}'")
                return ""
            
            # 2. Baixar o arquivo gerado para um local temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = os.path.join(temp_dir, "raw_audio.wav")
                self._download_audio(raw_audio_url, temp_file_path)
                
                # 3. Processar conforme especificações
                # Para processing_loop, criar versão seamless
                # A lógica para SFX-09 agora é baseada no filename
                if "processing_loop" in filename: # Assumindo que SFX-09 é o único com "processing_loop" no nome
                    processed_file_path = self.create_seamless_loop(
                        temp_file_path, 
                        output_filename, 
                        duration
                    )
                else:
                    processed_file_path = self._process_audio(
                        temp_file_path, 
                        output_filename, 
                        duration
                    )
                
                logging.info(f"Arquivo '{processed_file_path}' gerado e processado com sucesso")
                return processed_file_path

        except Exception as e:
            logging.error(f"Erro ao gerar '{filename}': {e}", exc_info=True)
            return ""

    def _call_replicate_model(self, prompt: str, duration: float, model_choice: str, negative_prompt: str = "") -> str:
        """Chama o modelo Replicate apropriado com tratamento de erros."""
        model_info = self.MODELS["stable-audio"] # Força o uso de stable-audio
        logging.info(f"Chamando modelo 'stable-audio' com prompt: '{prompt[:80]}...'")

        try:
            input_params = {
                "prompt": prompt,
                "seconds_total": int(duration),
                "seconds_start": 0,
                "cfg_scale": 7.0,
                "steps": 100,
                "seed": -1
            }
            if negative_prompt:
                input_params["negative_prompt"] = negative_prompt
            
            output = self.client.run(model_info["identifier"], input=input_params)
            
            # A saída pode ser um objeto FileOutput, uma lista ou string
            if isinstance(output, replicate.helpers.FileOutput):
                return str(output) # Converte FileOutput para string (URL)
            elif isinstance(output, list) and len(output) > 0:
                return str(output[0]) # Converte o primeiro item da lista para string (URL)
            elif isinstance(output, str):
                return output
            else:
                logging.error(f"Formato de saída inesperado: {type(output)}")
                return ""

        except replicate.exceptions.ReplicateError as e:
            logging.error(f"Erro na API da Replicate: {e}")
            return ""

    def _download_audio(self, url: str, temp_path: str):
        """Baixa o áudio da URL para um arquivo temporário com tratamento de erros."""
        logging.info(f"Baixando áudio...")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            logging.info(f"Áudio baixado com sucesso")

        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao baixar áudio: {e}")
            raise

    def _process_audio(self, input_file: str, output_filename: str, target_duration: float) -> str:
        """
        Processa o áudio para atender às especificações:
        - Formato: MP3, 44.1kHz, Estéreo, 128 kbps CBR
        - Normalização: pico de -3dB
        - Fade: 10ms in/out
        - Duração precisa
        """
        logging.info(f"Processando áudio para especificações finais...")
        
        try:
            audio = AudioSegment.from_file(input_file)
            
            # Ajustar duração (crucial para stable-audio que retorna ~47s)
            target_duration_ms = int(target_duration * 1000)
            if len(audio) > target_duration_ms:
                audio = audio[:target_duration_ms]
            elif len(audio) < target_duration_ms and len(audio) > 0:
                # Preenche com o próprio áudio se for mais curto
                loops_needed = (target_duration_ms // len(audio)) + 1
                audio = audio * loops_needed
                audio = audio[:target_duration_ms]

            # Garantir estéreo e taxa de amostragem
            audio = audio.set_channels(2).set_frame_rate(44100)
            
            # Normalizar para pico de -3dB
            audio = self._normalize_to_peak(audio, -3.0)
            
            # Aplicar fade de 10ms
            audio = audio.fade_in(10).fade_out(10)
            
            # Exportar como MP3 com especificações exatas
            audio.export(
                output_filename,
                format="mp3",
                bitrate="128k",
                parameters=["-ac", "2", "-ar", "44100", "-b:a", "128k"]
            )
            
            return output_filename
            
        except Exception as e:
            logging.error(f"Falha ao processar áudio: {e}")
            raise

    def _normalize_to_peak(self, audio: AudioSegment, target_db: float) -> AudioSegment:
        """Normaliza o áudio para um nível de pico específico em dBFS."""
        if audio.max_dBFS == float('-inf'):  # Evita erro em áudio silencioso
            return audio
        change_in_db = target_db - audio.max_dBFS
        return audio.apply_gain(change_in_db)

    def create_seamless_loop(self, input_file: str, output_file: str,
                           loop_duration: float = 3.0, crossfade_duration_ms: int = 100) -> str:
        """
        Cria um loop contínuo usando crossfade de potência constante.
        Usado especialmente para processing_loop.mp3.
        """
        logging.info(f"Criando loop contínuo...")
        
        try:
            audio = AudioSegment.from_file(input_file)
            
            # Garante que o áudio tenha a duração de loop desejada
            loop_duration_ms = int(loop_duration * 1000)
            if len(audio) > loop_duration_ms:
                audio = audio[:loop_duration_ms]
            elif len(audio) < loop_duration_ms and len(audio) > 0:
                loops_needed = (loop_duration_ms // len(audio)) + 1
                audio = audio * loops_needed
                audio = audio[:loop_duration_ms]

            # Cria overlap para crossfade
            overlap_start = audio[-crossfade_duration_ms:]
            overlap_end = audio[:crossfade_duration_ms]
            
            # Aplica fade out no final e fade in no início
            overlap_start = overlap_start.fade_out(crossfade_duration_ms)
            overlap_end = overlap_end.fade_in(crossfade_duration_ms)
            
            # Combina os overlaps
            crossfaded = overlap_start.overlay(overlap_end)
            
            # Reconstrói o loop
            middle = audio[crossfade_duration_ms:-crossfade_duration_ms]
            seamless_loop = crossfaded + middle
            
            # Aplica o mesmo processamento dos outros efeitos
            seamless_loop = seamless_loop.set_channels(2).set_frame_rate(44100)
            seamless_loop = self._normalize_to_peak(seamless_loop, -3.0)
            
            # Exporta com especificações
            seamless_loop.export(
                output_file,
                format="mp3",
                bitrate="128k",
                parameters=["-ac", "2", "-ar", "44100", "-b:a", "128k"]
            )
            
            return output_file
            
        except Exception as e:
            logging.error(f"Falha ao criar loop contínuo: {e}")
            raise

    