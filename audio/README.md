# Arquivos de áudio

- `smw_course_clear.wav`: entrada recebida do site [The Mushroom Kingdom — Sound Clips](https://themushroomkingdom.net/wav.shtml). WAV PCM mono, 16 bits, 22.050 Hz, 7,491 s. Tem chunk `LIST` no byte 36; converta antes de usar no USB.
- `robocop.wav`: outra faixa de entrada disponível para os exemplos de conversão.
- `smw_course_clear_flash.c`: tabela `uint16_t` gerada com os primeiros 5 s da faixa Mario, em PCM estéreo 16 bits a 48 kHz. É material para substituir `audio_sample.c` em uma cópia do projeto Flash; a reprodução física ainda precisa ser verificada.
- `audio_usb.wav`: arquivo intermediário que o aluno gera com o conversor USB. Renomeie para `audio.wav` ao copiá-lo para a raiz do pendrive.

Use os scripts em `../scripts/README.md` para gerar os formatos de cada projeto.
