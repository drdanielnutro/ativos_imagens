"""
Ferramenta para geração de efeitos sonoros usando modelos de IA.
Implementa estratégia híbrida: stable-audio para SFX, musicgen para tons musicais.
"""

import replicate
import requests
import os
import logging
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
        },
        "musicgen": {
            "identifier": "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb",
            "type": "tonal"
        }
    }
    
    # Mapeamento de IDs de ativos para configurações com prompts otimizados
    # Baseado nas especificações do Professor Virtual para crianças brasileiras 7-11 anos
    AUDIO_CONFIGS = {
        "SFX-01": {
            "filename": "button_tap.mp3",
            "duration": 0.5,
            "model": "stable-audio",
            "prompt": "Professional sound design for children's educational app: gentle satisfying button tap sound, Material Design inspired UI feedback, soft but crisp tactile response, warm wooden percussion quality, child-friendly mobile interface sound, exactly 0.5 seconds, non-startling, encouraging interaction",
            "negative_prompt": "loud, sharp, metallic, echo, harsh, aggressive, annoying, repetitive fatigue"
        },
        "SFX-02": {
            "filename": "success.mp3",
            "duration": 1.5,
            "model": "musicgen",
            "prompt": "Children's educational app success sound: bright cheerful completion chime, celebratory but not overwhelming, harmonious major chord progression, magical sparkle quality like Mario coin collection, Brazilian warmth and joy, encouraging achievement feeling, 1.5 seconds duration, mobile-optimized"
        },
        "SFX-03": {
            "filename": "error_gentle.mp3",
            "duration": 1.0,
            "model": "musicgen",
            "prompt": "Educational app gentle error indication: soft musical warning for children 7-11 years, helpful not startling, descending two-note melody with rounded smooth tone, xylophone or marimba quality, encouraging to try again, non-alarming supportive feedback, exactly 1 second"
        },
        "SFX-04": {
            "filename": "notification.mp3",
            "duration": 1.0,
            "model": "musicgen",
            "prompt": "Child-friendly notification bell for educational app: gentle school bell inspired but softer, pleasant triangular chime, warm resonance, attention-getting without startling, Brazilian school context, friendly reminder quality, exactly 1 second duration"
        },
        "SFX-05": {
            "filename": "achievement.mp3",
            "duration": 2.5,
            "model": "musicgen",
            "prompt": "Educational achievement celebration fanfare: triumphant orchestral sound for children, brief celebratory fanfare, positive reinforcement for learning milestones, uplifting major key progression, Brazilian festive spirit without stereotypes, encouraging continued learning, 2.5 seconds duration"
        },
        "SFX-06": {
            "filename": "camera_shutter.mp3",
            "duration": 0.5,
            "model": "stable-audio",
            "prompt": "Modern smartphone camera capture sound for kids app: contemporary digital camera shutter click, crisp but not mechanical, friendly photo-taking feedback, familiar mobile phone camera sound, clean and satisfying, exactly 0.5 seconds",
            "negative_prompt": "old mechanical camera, film advance, electronic beep, harsh click"
        },
        "SFX-07": {
            "filename": "page_transition.mp3",
            "duration": 0.5,
            "model": "stable-audio",
            "prompt": "Smooth page turn transition for educational app: gentle paper sliding swoosh, airy page flip sound, book page turning quality, light and swift movement, story-time feeling, non-distracting navigation feedback, exactly 0.5 seconds",
            "negative_prompt": "harsh whoosh, windy, noisy, heavy bass, sharp swoosh"
        },
        "SFX-08": {
            "filename": "pop_up.mp3",
            "duration": 0.5,
            "model": "stable-audio",
            "prompt": "Playful bubble pop for children's interface: cartoon soap bubble bursting, light and delightful pop sound, fun interaction feedback, bouncy and soft quality, game-like satisfaction, child-appropriate playfulness, exactly 0.5 seconds",
            "negative_prompt": "loud pop, aggressive burst, sharp crack, balloon pop"
        },
        "SFX-09": {
            "filename": "processing_loop.mp3",
            "duration": 3.0,
            "model": "stable-audio",
            "prompt": "Ambient thinking/processing loop for educational app: soft electronic thinking sound, gentle pulsing hum, AI assistant processing indication, soothing continuous background, seamless 3-second loop, calming waiting music, child-friendly technology sound",
            "negative_prompt": "harsh buzz, loud hum, distracting, annoying, anxiety-inducing"
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

    def generate_sound_effect(self, asset_id: str, output_dir: str = "generated_audio") -> str:
        """
        Gera um efeito sonoro baseado no ID do ativo.
        
        Args:
            asset_id: ID do ativo (ex: 'SFX-01', 'SFX-02')
            output_dir: Diretório onde salvar o arquivo gerado
            
        Returns:
            str: Caminho do arquivo gerado ou string vazia se falhar
        """
        if asset_id not in self.AUDIO_CONFIGS:
            logging.error(f"ID de ativo '{asset_id}' não encontrado nas configurações")
            return ""
        
        config = self.AUDIO_CONFIGS[asset_id]
        output_filename = os.path.join(output_dir, config["filename"])
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        logging.info(f"Iniciando geração para '{asset_id}' ({config['filename']}) usando modelo '{config['model']}'")
        
        try:
            # 1. Chamar a API da Replicate
            raw_audio_url = self._call_replicate_model(
                prompt=config["prompt"],
                duration=config["duration"],
                model_choice=config["model"],
                negative_prompt=config.get("negative_prompt", "")
            )
            
            if not raw_audio_url:
                logging.error(f"Falha ao obter URL de áudio da Replicate para '{asset_id}'")
                return ""
            
            # 2. Baixar o arquivo gerado para um local temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = os.path.join(temp_dir, "raw_audio.wav")
                self._download_audio(raw_audio_url, temp_file_path)
                
                # 3. Processar conforme especificações
                # Para processing_loop, criar versão seamless
                if asset_id == "SFX-09":
                    processed_file_path = self.create_seamless_loop(
                        temp_file_path, 
                        output_filename, 
                        config["duration"]
                    )
                else:
                    processed_file_path = self._process_audio(
                        temp_file_path, 
                        output_filename, 
                        config["duration"]
                    )
                
                logging.info(f"Arquivo '{processed_file_path}' gerado e processado com sucesso")
                return processed_file_path

        except Exception as e:
            logging.error(f"Erro ao gerar '{asset_id}': {e}", exc_info=True)
            return ""

    def _call_replicate_model(self, prompt: str, duration: float, model_choice: str, negative_prompt: str = "") -> str:
        """Chama o modelo Replicate apropriado com tratamento de erros."""
        if model_choice not in self.MODELS:
            raise ValueError(f"Modelo '{model_choice}' não suportado")

        model_info = self.MODELS[model_choice]
        logging.info(f"Chamando modelo '{model_choice}' com prompt: '{prompt[:80]}...'")

        try:
            if model_choice == "stable-audio":
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
                    
            elif model_choice == "musicgen":
                input_params = {
                    "prompt": prompt,
                    "duration": int(max(duration, 1)),  # musicgen mínimo 1s
                    "model_version": "stereo-melody-large",
                    "output_format": "wav",
                    "normalization_strategy": "loudness",
                    "temperature": 1,
                    "top_k": 250,
                    "top_p": 0,
                    "classifier_free_guidance": 3
                }
            
            output = self.client.run(model_info["identifier"], input=input_params)
            
            # A saída pode ser uma lista ou string
            if isinstance(output, list) and len(output) > 0:
                return output[0]
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

    def get_asset_info(self, asset_id: str) -> Dict[str, Union[str, float]]:
        """
        Retorna informações sobre um ativo de áudio.
        
        Args:
            asset_id: ID do ativo
            
        Returns:
            Dict com informações do ativo ou dict vazio se não encontrado
        """
        return self.AUDIO_CONFIGS.get(asset_id, {})