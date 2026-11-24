# Ferramentas de conversão

Execute os comandos a partir da raiz do repositório para que os caminhos relativos coincidam com os exemplos do roteiro. Requisitos comuns: Python 3 e FFmpeg acessível pelo `PATH`.

## WAV para o pendrive (`MEDIA_USB_KEY`)

```powershell
python scripts/converter_audio_stm32_corrigido.py audio/smw_course_clear.wav -o audio/audio_usb.wav
```

Saída: PCM estéreo, 16 bits, 44.100 Hz, cabeçalho WAV de 44 bytes e chunk `data` no byte 36. O script valida o cabeçalho. O firmware espera o arquivo com nome `audio.wav` na raiz do pendrive; renomeie/copiei `audio/audio_usb.wav` para esse destino.

## Vetor C para Flash (`MEDIA_InFLASH`)

```powershell
python scripts/wav_to_flash_array.py audio/smw_course_clear.wav --seconds 5 --output audio/smw_course_clear_flash.c
```

Saída: `uint16_t AUDIO_SAMPLE[]`, PCM estéreo, 16 bits, 48.000 Hz, até cinco segundos por padrão. Para esse exemplo, atualize `AUDIO_FILE_SZE` para `960000u` e mantenha `AUIDO_START_ADDRESS` em `58`. Copie o vetor apenas para uma cópia do projeto original. O linker map deve confirmar que o programa e a tabela cabem na Flash.

Os conversores têm finalidades diferentes: um grava um WAV simples para FatFs; o outro emite código C para compilar junto com o firmware Flash. A conversão não substitui o ensaio de áudio na placa.
