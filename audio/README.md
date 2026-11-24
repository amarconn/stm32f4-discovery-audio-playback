# Arquivos de áudio

- `smw_course_clear.wav`: entrada recebida do site [The Mushroom Kingdom — Sound Clips](https://themushroomkingdom.net/wav.shtml). WAV PCM mono, 16 bits, 22.050 Hz, 7,491 s. Tem chunk `LIST` no byte 36; converta antes de usar no USB.
- `robocop.wav`: outra faixa de entrada. Para usar no pendrive, passe-a pelo conversor USB e confira o cabeçalho gerado antes de copiá-la.
- `smw_course_clear_flash.c`: tabela `uint16_t` gerada com os primeiros 5 s da faixa Mario, em PCM estéreo 16 bits a 48 kHz. Foi usada para substituir `audio_sample.c` em uma cópia de `MEDIA_InFLASH`, recompilada e validada em reprodução.
- `audio_usb.wav`: **não está incluído inicialmente**. O aluno o gera na etapa USB executando `python scripts/converter_audio_stm32_corrigido.py audio/smw_course_clear.wav -o audio/audio_usb.wav`. Só depois da conversão esse arquivo passa a existir; copie-o para a raiz do pendrive com o nome `audio.wav`.

Use os scripts em `../scripts/README.md` para gerar os formatos de cada projeto.
