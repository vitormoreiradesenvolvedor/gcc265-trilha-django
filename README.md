# Trilha: aprender Django construindo um registro pessoal de estudos

Projeto de portfólio individual de **GCC265 Mentoria Acadêmica I** (Sistemas de Informação,
UFLA, 2026/2, Prof. Dr. Maurício Souza).

O objetivo declarado no Planejamento (instrumento I2) é aprender o framework **Django**, que
eu nunca havia usado, e deixar registrado por escrito como foi aprendê-lo. O repositório tem
duas partes com fronteiras explícitas:

| Diretório | O que é | Autoria |
|---|---|---|
| `tutorial_enquetes/` | Aplicação de estudo construída acompanhando o tutorial oficial do Django | Código derivado da documentação oficial, adaptado para português |
| `trilha/` | Aplicação autoral Trilha (entra no nível esperado, a partir da semana 5) | Autoral |
| `DIARIO.md` | Diário técnico com entradas datadas: o que aprendi, o que travou, como resolvi | Autoral |

## Escopo pactuado

| Nível | Entrega |
|---|---|
| Mínimo viável | Aplicação do tutorial publicada e acessível por link, mais diário com ao menos seis entradas datadas |
| Esperado | Aplicação autoral Trilha: conta de usuário, cadastro manual de materiais, percentual de progresso, duas telas, dados por usuário |
| Ambicioso | Busca na API pública do Google Books e suíte de testes automatizados executada pelo GitHub Actions |

## Roteiro de aceitação do nível mínimo

Executável por terceiro, sem instalar nada, assim que a publicação estiver no ar (semana 3):

1. Abrir o link público.
2. Escolher uma enquete, votar e ver o total de votos mudar.
3. Entrar em `/admin` com o usuário `avaliador` (senha publicada aqui quando a aplicação subir),
   criar uma enquete nova e encontrá-la na página inicial.
4. Conferir que `DIARIO.md` tem seis ou mais entradas datadas, cada uma nomeando um erro ou
   travamento concreto e o que o resolveu.

## Rodar localmente

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser   # usuário de avaliação
.venv/bin/python manage.py runserver
```

Rotas: `/enquetes/` (aplicação do tutorial), `/admin/` (administração).
A raiz `/` redireciona para `/enquetes/`.

### Variáveis de ambiente

| Variável | Padrão local | Para que serve |
|---|---|---|
| `DJANGO_SECRET_KEY` | chave de desenvolvimento | chave de assinatura em produção |
| `DJANGO_DEBUG` | `1` | `0` em produção |
| `DJANGO_ALLOWED_HOSTS` | vazio | host público, separado por vírgula, em produção |

## Cronograma

Oito semanas, de 28/09 a 23/11 de 2026, com checkpoints em 20/10 (nível mínimo fechado) e
17/11 (nível esperado verificado). As semanas de 13/10, 27/10 e 10/11 não têm encontro da
disciplina.

## Licença

MIT. Veja `LICENSE`.
