# Instagram Question Sticker Spike

Experimento isolado para investigar publicacao de Story com caixinha de perguntas
via Instagram Private API.

## Contexto

O Instagram Graph API oficial publica Stories, mas nao suporta stickers nativos
interativos como caixinha de perguntas. Este spike usa `instagrapi`, que opera via
Private API/mobile API. Isso pode gerar challenge, bloqueio de sessao ou risco para
a conta. Use somente com conta secundaria ate validar estabilidade.

## Hipotese tecnica

`instagrapi` permite enviar `StorySticker` customizado para `media/configure_to_story/`.
Ele ja usa o mesmo mecanismo para link stickers e polls:

- `tap_models`
- `story_sticker_ids`
- campos extras por sticker

A caixinha de perguntas aparece nas respostas da API como `story_questions` com
um objeto `question_sticker`. O payload exato de criacao nao esta documentado.
Este spike testa variantes provaveis.

## Setup

```bash
cd /root/projetos/carousel-api/experiments/ig-question-sticker
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Crie um arquivo `.env` local:

```env
IG_USERNAME=conta_teste
IG_PASSWORD=senha_teste
```

## Uso

Renderize/crie uma imagem 1080x1920 e rode:

```bash
. .venv/bin/activate
python question_sticker_spike.py login
python question_sticker_spike.py tray
python question_sticker_spike.py post \
  --image /tmp/story_seq_01.jpg \
  --question "Qual handoff mais trava sua empresa hoje?" \
  --variant question_sticker
```

Variantes disponiveis:

- `question_sticker`
- `questions_sticker`
- `story_question`
- `raw_story_questions`

Depois de postar, abra no app do Instagram e veja se:

1. o story publicou;
2. o sticker apareceu visualmente;
3. o sticker ficou interativo;
4. as respostas aparecem nos insights do story.

## Criterio de sucesso

So integrar no app principal se uma variante funcionar em conta secundaria por
varios testes e sem challenge recorrente.
