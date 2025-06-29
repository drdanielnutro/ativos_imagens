#!/usr/bin/env python
"""
Script de teste: geração de áudio MP3 a partir de um prompt de texto.

Uso:
    python gerar_audio.py "clique suave de botão" --duracao 0.5 --output button_tap.mp3

Pré-requisitos:
    1. Defina a variável de ambiente REPLICATE_API_TOKEN com seu token da Replicate.
    2. Instale dependências:
        pip install replicate requests pydub ffmpeg-python
    3. FFmpeg deve estar disponível no PATH (necessário para exportar MP3 via PyDub).

Este script segue o pipeline descrito em docs/definicoes/pipeline_completo.md e
em docs/deep_research/deep_research_ideia/GERAÇÃO DE ÁUDIO MP3.txt:
    • Geração de WAV via modelo stackadoc/stable-audio-open-1.0:9aff84a639f96d0f7e6081cdea002d15133d0043727f849c40abdd166b7c75a8 (ou alternativos).
    • Download temporário.
    • Conversão/normalização para MP3 128 kbps, 44.1 kHz, estéreo, fade 10 ms.
"""

import argparse
import os
import sys
import tempfile
from typing import List

import requests
import replicate  # type: ignore
from pydub import AudioSegment  # type: ignore

# -----------------------------------------------------------------------------
# Funções utilitárias
# -----------------------------------------------------------------------------

def _normalize_to_peak(audio: AudioSegment, target_db: float = -3.0) -> AudioSegment:
    """Normaliza o áudio para que o pico atinja o nível target_db (dBFS)."""
    gain_needed = target_db - audio.max_dBFS
    return audio.apply_gain(gain_needed)


def _process_audio(input_file: str, output_filename: str, target_duration: float) -> str:
    """Converte WAV para MP3 final, ajustando specs do projeto."""
    audio = AudioSegment.from_file(input_file)

    # Garantir estéreo e 44.1 kHz
    audio = audio.set_channels(2)
    audio = audio.set_frame_rate(44100)

    # Ajustar duração
    target_ms = int(target_duration * 1000)
    if len(audio) > target_ms:
        audio = audio[:target_ms]
    elif len(audio) < target_ms:
        loops = (target_ms // len(audio)) + 1
        audio = (audio * loops)[:target_ms]

    # Normalizar e aplicar fades
    audio = _normalize_to_peak(audio, -3.0)
    audio = audio.fade_in(10).fade_out(10)

    # Exportar em MP3 128 kbps CBR
    audio.export(
        output_filename,
        format="mp3",
        bitrate="128k",
        parameters=["-ac", "2", "-ar", "44100"],
    )
    return output_filename


def _download(url: str) -> str:
    """Baixa o arquivo de áudio da URL para um arquivo temporário e retorna o caminho."""
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(response.content)
    tmp.close()
    return tmp.name


def _call_replicate(prompt: str, duration: float, model: str) -> str:
    """Invoca o modelo da Replicate e retorna a URL do WAV gerado."""
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print("Erro: defina REPLICATE_API_TOKEN no ambiente.", file=sys.stderr)
        sys.exit(1)

    client = replicate.Client(api_token=token)

    if model == "stable-audio":
        output = client.run(
            "stackadoc/stable-audio-open-1.0:9aff84a639f96d0f7e6081cdea002d15133d0043727f849c40abdd166b7c75a8",
            input={
                "prompt": prompt,
                "duration": int(duration),
                "seconds_total": int(duration),
                "steps": 100,
                "cfg_scale": 6,
            },
        )
    elif model == "musicgen":
        output = client.run(
            "meta/musicgen",
            input={
                "prompt": prompt,
                "duration": int(duration),
                "model_version": "stereo-melody-large",
                "output_format": "wav",
            },
        )
    else:  # "magnet"
        output = client.run(
            "lucataco/magnet",
            input={
                "prompt": prompt,
                "model": "facebook/magnet-small-10secs",
            },
        )

    # A Replicate pode retornar list ou string; padronizamos para str
    if isinstance(output, list):
        return output[0]
    return str(output)

# -----------------------------------------------------------------------------
# Função principal (CLI)
# -----------------------------------------------------------------------------

def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Gera um efeito sonoro (MP3) a partir de um prompt de texto usando a API Replicate.",
    )
    parser.add_argument("prompt", help="Descrição textual do som a ser gerado (entre aspas)")
    parser.add_argument(
        "--duracao",
        type=float,
        default=1.5,
        help="Duração desejada em segundos (padrão: 1.5)",
    )
    parser.add_argument(
        "--output",
        default="output.mp3",
        help="Nome/path do arquivo MP3 de saída (padrão: output.mp3)",
    )
    parser.add_argument(
        "--modelo",
        choices=["stable-audio", "musicgen", "magnet"],
        default="stable-audio",
        help="Modelo Replicate a usar (padrão: stable-audio-open-1.0)",
    )

    args = parser.parse_args(argv)

    print("[1/4] Enviando prompt para o modelo Replicate…")
    wav_url = _call_replicate(args.prompt, args.duracao, args.modelo)

    print("[2/4] Baixando arquivo WAV temporário…")
    tmp_wav = _download(wav_url)

    try:
        print("[3/4] Processando e convertendo para MP3…")
        mp3_path = _process_audio(tmp_wav, args.output, args.duracao)
    finally:
        os.unlink(tmp_wav)  # Limpa arquivo temporário

    print(f"[4/4] Concluído! Arquivo salvo em: {mp3_path}")


if __name__ == "__main__":
    main() 