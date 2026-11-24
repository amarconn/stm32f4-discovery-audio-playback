# Prática: reprodução de áudio no STM32F4-Discovery

Este repositório acompanha o [roteiro impresso em PDF](<roteiro discovery audio playback.pdf>). Use esta página como índice dos arquivos e como consulta rápida antes de cada ensaio. Os procedimentos de compilação, gravação e audição devem ser realizados na bancada e anotados na ficha de resultados do roteiro.

Repositório Git: [github.com/amarconn/audio-pendrive-stm32](https://github.com/amarconn/audio-pendrive-stm32).

## Mapa do material

| Pasta/arquivo | O que o aluno encontra |
|---|---|
| `STM32F4-Discovery_FW_V1.1.0/` | Pacote ST original, bibliotecas e projetos Atollic. Não reorganize esta árvore. |
| `STM32F4-Discovery_FW_V1.1.0/Project/Audio_playback_and_record/TrueSTUDIO/MEDIA_InFLASH/` | Exemplo original com áudio embutido na Flash. |
| `STM32F4-Discovery_FW_V1.1.0/Project/Audio_playback_and_record/TrueSTUDIO/MEDIA_USB_KEY/` | Exemplo USB Host para ler arquivo WAV no pendrive. |
| `scripts/` | Um conversor WAV para pendrive e outro para gerar vetor C da Flash. |
| `audio/` | WAVs de entrada e vetor C de demonstração. O WAV convertido para USB é gerado pelo aluno durante a prática. |
| `roteiro discovery audio playback.pdf` | Roteiro de laboratório pronto para leitura/impressão. |
| `referencias/` | Nota de aplicação AN3997 usada como referência técnica. |

O arquivo `audio/smw_course_clear.wav` veio de [The Mushroom Kingdom — Sound Clips](https://themushroomkingdom.net/wav.shtml), site que reúne efeitos sonoros e trechos musicais de jogos do Mario em WAV. O formato original foi verificado: PCM mono, 16 bits, 22.050 Hz, 7,491 s; há um chunk `LIST` no byte 36, por isso ele não deve ser usado diretamente no leitor WAV USB do exemplo.

## O que instalar

- Atollic TrueSTUDIO compatível com os projetos, ST-LINK driver/utilitário e STM32F4-Discovery com STM32F407VG.
- Python 3 e FFmpeg no PATH para os conversores.
- `yt-dlp` é opcional e só é necessário se a entrada de áudio for uma URL: `python -m pip install yt-dlp`.
- Pendrive USB Mass Storage para o ensaio USB. FAT32 é recomendado.

## A. Importar e testar o exemplo original

1. Mantenha a pasta completa `STM32F4-Discovery_FW_V1.1.0`; os projetos usam bibliotecas nas pastas vizinhas.
2. No TrueSTUDIO, use **File > Import > General > Existing Projects into Workspace**. Selecione como raiz `STM32F4-Discovery_FW_V1.1.0/Project/Audio_playback_and_record/TrueSTUDIO`.
3. Importe `MEDIA_InFLASH` sem copiar o projeto para o workspace. Confira se os recursos vinculados aparecem sem erro.
4. Selecione o projeto e execute **Project > Clean**, depois **Build Project**. Guarde o console de compilação.
5. Conecte a placa pelo ST-LINK e use **Debug As > Embedded C/C++ Application** (o texto pode variar com a versão). Permita que o debugger grave o firmware e pressione Resume.
6. Com o firmware original, confira a saída de áudio. Anote o que ocorreu antes de editar qualquer fonte.
7. Repita o processo com `MEDIA_USB_KEY`, mas deixe o pendrive para a etapa D.

Não altere os exemplos originais para fazer o primeiro teste passar. Registre as mensagens e os LEDs observados antes de tentar uma correção.

## B. Gerar vetor para a Flash interna

O projeto Flash usa `src/audio_sample.c` (`AUDIO_SAMPLE[]`) e `AUDIO_FILE_SZE`/`AUIDO_START_ADDRESS` em `src/waveplayer.c`. O código inicia o codec a 48 kHz. Gere o vetor de demonstração com os primeiros cinco segundos:

```powershell
python scripts/wav_to_flash_array.py audio/smw_course_clear.wav --seconds 5 --output audio/smw_course_clear_flash.c
```

O script converte para PCM estéreo, 16 bits, 48.000 Hz e gera um WAV simplificado de 58 bytes dentro da tabela `uint16_t`. Para esta saída, use `AUDIO_FILE_SZE 960000u` e mantenha `AUIDO_START_ADDRESS 58`.

Faça a substituição em uma cópia do projeto `MEDIA_InFLASH`:

1. Copie `audio/smw_course_clear_flash.c` para a pasta `src/` da cópia, com o nome `audio_sample.c`.
2. Em `src/waveplayer.c`, ajuste `AUDIO_FILE_SZE` para `960000u`; deixe `AUIDO_START_ADDRESS` em `58`.
3. Faça Clean e Build. Confira o mapa do linker: o STM32F407VG tem 1 MiB de Flash total, compartilhado entre código e amostras. Se faltar espaço, gere menos segundos com `--seconds`.
4. Grave a cópia do firmware e confira o áudio. Anote se o linker concluiu e o que ouviu.

O arquivo `audio/smw_course_clear_flash.c` já é uma saída de exemplo gerada pelo conversor; não é evidência de reprodução física.

## C. Converter WAV para o pendrive

O leitor USB espera PCM estéreo de 16 bits a 44.100 Hz e um cabeçalho simples de 44 bytes, com `data` iniciando no byte 36. Converta a faixa assim:

```powershell
python scripts/converter_audio_stm32_corrigido.py audio/smw_course_clear.wav -o audio/audio_usb.wav
```

O conversor valida o resultado antes de salvá-lo. Também pode converter outros arquivos de áudio decodificáveis pelo FFmpeg:

```powershell
python scripts/converter_audio_stm32_corrigido.py "minha_musica.mp3" -o audio/audio_usb.wav
```

Não confie apenas na extensão `.wav`: chunks extras como `LIST` ou `JUNK` podem deslocar `data` e o parser ST não percorre chunks de maneira geral.

## D. Preparar o pendrive e reproduzir

1. Formate uma partição primária do pendrive como FAT32.
2. Depois de gerar `audio/audio_usb.wav` na etapa C, copie-o para a raiz do pendrive e renomeie para `audio.wav`. Esse arquivo de saída não acompanha o repositório: ele só aparece quando o aluno executa o conversor.
3. No firmware, confira `WAVE_NAME "0:audio.wav"` em `Project/Audio_playback_and_record/inc/main.h`. `0:` é o volume FatFs; como o caminho não tem subpasta, o WAV fica na raiz.
4. Grave e execute `MEDIA_USB_KEY`. Aguarde o reconhecimento do dispositivo e a montagem do volume. Com `audio.wav` válido na raiz, o comando inicial PLAY tenta iniciar a reprodução.
5. Durante a reprodução, USER alterna para RECORD, interrompendo o áudio; o acionamento seguinte retorna a PLAY. Não deixe a gravação prosseguir sem necessidade. Esse botão não funciona como play/pause no projeto USB.
6. Registre som, LEDs, erros e resposta do botão na ficha do roteiro.

O FatFs incluído configura `_MAX_SS=1024`; as leituras e transferências DMA acontecem em blocos, usando dois buffers alternados. Isso não impõe um limite geral de 1 MB ao tamanho do arquivo. Falha em abrir o volume, falha em abrir `audio.wav` e cabeçalho rejeitado têm indicações diferentes no LED vermelho; o roteiro detalha o diagnóstico.
