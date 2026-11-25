# Trilha: aprender Django construindo um registro pessoal de estudos

Projeto de portfólio individual de **GCC265 Mentoria Acadêmica I** (Sistemas de Informação,
UFLA, 2026/2, Prof. Dr. Maurício Souza).

O objetivo declarado no Planejamento (instrumento I2) é aprender o framework **Django**, que
eu nunca havia usado, e deixar registrado por escrito como foi aprendê-lo. O repositório tem
duas partes com fronteiras explícitas:

| Diretório | O que é | Autoria |
|---|---|---|
| `tutorial_enquetes/` | Aplicação de estudo construída acompanhando o tutorial oficial do Django | Código derivado da documentação oficial, adaptado para português |
| `trilha/` | Aplicação autoral Trilha (níveis esperado e ambicioso) | Autoral, escrita com assistência de IA declarada |
| `DIARIO.md` | Diário técnico com entradas datadas: o que aprendi, o que travou, como resolvi | Autoral |

## Escopo pactuado

| Nível | Entrega |
|---|---|
| Mínimo viável | Aplicação do tutorial publicada e acessível por link, mais diário com ao menos seis entradas datadas |
| Esperado | Aplicação autoral Trilha: conta de usuário, cadastro manual de materiais, percentual de progresso, duas telas, dados por usuário |
| Ambicioso | Busca na API pública do Google Books e suíte de testes automatizados executada pelo GitHub Actions |

## Onde está no ar

**Link público:** https://vitormoreiradesenvolvedor.github.io/gcc265-trilha-django/

Publicado no **GitHub Pages**, com o Django rodando dentro do navegador pelo Pyodide (detalhes e
limitações em [`navegador/README.md`](navegador/README.md)). Os dados ficam no navegador de quem
abre o link. A rota aparece depois do `#`: por exemplo, `.../gcc265-trilha-django/#/trilha/`.

O Planejamento previa o Render (Web Service com PostgreSQL). O Blueprint `render.yaml` continua no
repositório e funciona, mas exige uma conta no Render; a publicação foi feita no GitHub Pages para
não depender de conta de terceiro.

| Rota | O que é |
|---|---|
| `/` | Apresentação do projeto |
| `/enquetes/` | Aplicação do tutorial (nível mínimo viável) |
| `/trilha/` | Aplicação autoral Trilha (níveis esperado e ambicioso) |
| `/admin/` | Administração. Usuário `avaliador`, senha `avaliacao-gcc265`, com permissão só sobre as enquetes |

No GitHub Pages, cada rota vira `#/rota/` (ex.: `#/admin/`).

## Roteiros de aceitação (do Planejamento)

**Mínimo viável.**

1. Abrir o link público, entrar em Enquetes, escolher uma enquete, votar e ver o total mudar.
2. Entrar em `/admin` com `avaliador` / `avaliacao-gcc265`, criar uma enquete nova e encontrá-la
   na lista de enquetes.
3. Conferir que `DIARIO.md` tem seis ou mais entradas datadas, cada uma nomeando um erro ou
   travamento concreto e o que o resolveu.

**Esperado.**

1. Em `/trilha/cadastro/`, criar conta com e-mail e senha.
2. Cadastrar o material "Clean Code" com progresso de 30%; passar pelas duas telas (minha trilha e
   formulário do material).
3. Sair, entrar de novo e encontrar o material em 30%.
4. Criar uma segunda conta: ela não vê nenhum material da primeira.

**Ambicioso.**

1. Na tela de cadastro de material, digitar "clean code", buscar, escolher um resultado e ver
   título e autor preenchidos. Depende de `GOOGLE_BOOKS_API_KEY` no ambiente: sem chave, a cota
   anônima da API é zero e a tela avisa que a busca está indisponível.
2. Na aba Actions do GitHub, a última execução do workflow `testes` aparece com sucesso e o resumo
   informa quantos testes rodaram.

## Rodar localmente

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser   # usuário de avaliação
.venv/bin/python manage.py runserver
```

Testes: `.venv/bin/python manage.py test` (32 testes).
Para popular o usuário avaliador e a enquete de exemplo:
`DJANGO_AVALIADOR_SENHA=... .venv/bin/python manage.py preparar_avaliacao`.

### Variáveis de ambiente

| Variável | Padrão local | Para que serve |
|---|---|---|
| `DJANGO_SECRET_KEY` | chave de desenvolvimento | chave de assinatura em produção |
| `DJANGO_DEBUG` | `1` | `0` em produção |
| `DJANGO_ALLOWED_HOSTS` | vazio | host público, separado por vírgula, em produção (no Render, `RENDER_EXTERNAL_HOSTNAME` entra sozinho) |
| `DATABASE_URL` | SQLite local | PostgreSQL em produção |
| `DJANGO_AVALIADOR_SENHA` | ausente | senha do usuário `avaliador`, criado por `preparar_avaliacao` |
| `GOOGLE_BOOKS_API_KEY` | ausente | chave da API do Google Books (busca do nível ambicioso) |

## Estado atual

| Semana | Período | Estado |
|---|---|---|
| S1 | 28/09 a 04/10 | não executada; trabalho feito em 05/10 (ver correção de datas no diário) |
| S2 | 05/10 a 11/10 | executada em 05/10: tutorial partes 1 a 4, diário entradas 1 e 2 |
| S3 a S8 | 12/10 a 22/11 | não executadas: nenhum commit entre 05/10 e 24/11 (diário, entrada 3) |
| Após o prazo | 24/11 | tutorial partes 5 e 6, Trilha (esperado), busca no Google Books e GitHub Actions (ambicioso), publicação no GitHub Pages com Pyodide, diário entradas 3 a 8 |

O comparativo entre o pactuado e o entregue está no Relatório Final (instrumento I4).

## Cronograma

Oito semanas, de 28/09 a 23/11 de 2026, com checkpoints em 20/10 (nível mínimo fechado) e
17/11 (nível esperado verificado). As semanas de 13/10, 27/10 e 10/11 não têm encontro da
disciplina.

## Licença

MIT. Veja `LICENSE`.
