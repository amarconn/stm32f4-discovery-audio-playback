#!/usr/bin/env python3
"""Normalize a local audio file to the simple WAV expected by MEDIA_USB_KEY.

Requires FFmpeg on PATH. Optional YouTube URL input additionally requires yt-dlp.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

RATE = 44_100
CHANNELS = 2


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def validate(path: Path) -> tuple[float, int]:
    header = path.read_bytes()[:44]
    checks = (
        (header[0:4] == b"RIFF", "RIFF ausente no byte 0"),
        (header[8:12] == b"WAVE", "WAVE ausente no byte 8"),
        (header[12:16] == b"fmt ", "fmt ausente no byte 12"),
        (int.from_bytes(header[16:20], "little") == 16, "fmt size diferente de 16"),
        (int.from_bytes(header[20:22], "little") == 1, "formato diferente de PCM"),
        (int.from_bytes(header[22:24], "little") == CHANNELS, "arquivo não está em estéreo"),
        (int.from_bytes(header[24:28], "little") == RATE, "taxa diferente de 44100 Hz"),
        (int.from_bytes(header[34:36], "little") == 16, "amostra diferente de 16 bits"),
        (header[36:40] == b"data", "chunk data não começa no byte 36"),
    )
    if len(header) != 44:
        raise ValueError("arquivo menor que o cabeçalho WAV de 44 bytes")
    for valid, error in checks:
        if not valid:
            raise ValueError(error)
    with wave.open(str(path), "rb") as wav:
        if wav.getcomptype() != "NONE" or wav.getnchannels() != CHANNELS:
            raise ValueError("WAV não PCM estéreo")
        if wav.getsampwidth() != 2 or wav.getframerate() != RATE:
            raise ValueError("WAV não está em 16 bits/44100 Hz")
        return wav.getnframes() / RATE, path.stat().st_size


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="arquivo de áudio local ou URL do YouTube")
    parser.add_argument("-o", "--output", type=Path, default=Path("audio.wav"),
                        help="WAV de saída (padrão: ./audio.wav)")
    parser.add_argument("--youtube", action="store_true",
                        help="trata input como URL e baixa com yt-dlp")
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        parser.error("FFmpeg não encontrado no PATH; instale FFmpeg e abra novo terminal")
    args.output = args.output.resolve()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    try:
        with tempfile.TemporaryDirectory(prefix="stm32_wav_") as tmp_name:
            tmp = Path(tmp_name)
            source = Path(args.input).expanduser().resolve()
            if args.youtube:
                ytdlp = shutil.which("yt-dlp")
                if not ytdlp:
                    parser.error("yt-dlp ausente; instale com: python -m pip install yt-dlp")
                template = tmp / "source.%(ext)s"
                run([ytdlp, "--no-playlist", "-f", "bestaudio/best", "-o", str(template), args.input])
                candidates = list(tmp.glob("source.*"))
                if not candidates:
                    raise RuntimeError("yt-dlp não gerou arquivo de entrada")
                source = candidates[0]
            if not source.is_file():
                raise FileNotFoundError(f"entrada não encontrada: {source}")
            staged = tmp / "audio.wav"
            run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
                 "-map", "0:a:0", "-vn", "-ac", str(CHANNELS), "-ar", str(RATE),
                 "-c:a", "pcm_s16le", "-map_metadata", "-1", "-fflags", "+bitexact",
                 "-flags:a", "+bitexact", str(staged)])
            duration, size = validate(staged)
            shutil.copy2(staged, args.output)
        print(f"Gerado e validado: {args.output}\n{size} bytes; {duration:.2f} s; PCM estéreo 16 bits/44100 Hz; data@36")
        print("Copie como audio.wav para a raiz do pendrive FAT32.")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
