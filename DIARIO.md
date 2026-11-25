# Diário técnico

Registro datado do aprendizado de Django. Uma entrada por sessão de trabalho: o que fiz, o que
travou e como resolvi. Meta do nível mínimo viável: pelo menos seis entradas datadas até 20/10.

> **Correção de datas (24/11/2026).** As entradas 1 e 2 foram originalmente datadas de 03/10/2026,
> e os seis primeiros commits do repositório tiveram as datas reescritas com `git filter-branch`
> para o mesmo dia. A data real do trabalho é **05/10/2026**, entre 23h32 e 23h33 no horário dos
> commits originais. O histórico reescrito foi mantido como está, sem novo force-push, e a
> discrepância está declarada aqui e no Relatório Final.

---

## Entrada 1: 05/10/2026, ambiente e primeiro projeto no ar localmente

**O que fiz.** Criei o repositório, o ambiente virtual com Python 3.14.7 e Django 6.1.1, o
projeto `trilha_projeto` e a aplicação `tutorial_enquetes`. Segui as partes 1 a 4 do tutorial
oficial do Django: modelos `Pergunta` e `Opcao`, migrations, registro no Admin com inline de
opções, views genéricas `ListView` e `DetailView`, formulário de voto com CSRF e templates.

**Decisões.**

- Traduzi os nomes do tutorial (`Question`/`Choice` viraram `Pergunta`/`Opcao`, `polls` virou
  `enquetes`). O código continua derivado da documentação oficial, e por isso ficou isolado no
  diretório `tutorial_enquetes/`. A aplicação autoral entra depois em `trilha/`. Essa fronteira
  é a mesma que declarei no Planejamento, na declaração de reuso: o que se avalia é o
  incremento autoral, então a divisão precisa estar visível no repositório, não só no texto.
- `related_name="opcoes"` no `ForeignKey`, para o template escrever `pergunta.opcoes.all` em vez
  de `pergunta.opcao_set.all`. Vindo de Laravel, essa é a primeira diferença que me pegou: no
  Eloquent eu declaro o método da relação; no Django ORM a relação inversa é gerada e o nome
  dela é configuração do campo.
- O voto usa `F("votos") + 1` em vez de ler o inteiro em Python e somar. A soma vira expressão
  SQL e o banco resolve, o que evita perder voto quando dois acessos salvam ao mesmo tempo.

**O que travou.** Nada bloqueante nesta primeira sessão. O custo foi de vocabulário: o Django
separa `urls.py` por aplicação com `app_name` e namespace, e a referência no template é
`{% url 'tutorial_enquetes:detalhe' pergunta.id %}`. Errei o namespace duas vezes antes de
entender que `app_name` e o `include()` precisam concordar.

**Início tardio.** O Planejamento prevê o início em 28/09, e eu comecei em 05/10, já na
semana 2 do cronograma. A semana 1 inteira foi perdida e ficam registrados aqui: a comparação
honesta entre o pactuado e o entregue vale nota no Relatório Final, e o histórico do
repositório é a evidência que sustenta o que eu declarar lá.

---

## Entrada 2: 05/10/2026, ALLOWED_HOSTS derrubou o acesso local

**O problema.** Depois de passar `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS` para variáveis de
ambiente, pensando já na publicação no Render, a aplicação parou de responder na verificação
local. Erro exato:

```
django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'testserver'.
You may need to add 'testserver' to ALLOWED_HOSTS.
```

**A causa.** Eu havia escrito `ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS",
"127.0.0.1,localhost").split(",")`. Parecia inofensivo, mas desligou um comportamento do
framework: com `DEBUG = True` **e a lista vazia**, o Django libera sozinho `localhost`,
`127.0.0.1` e `testserver`. Ao preencher a lista com um padrão, eu assumi a responsabilidade
por todos os hosts, inclusive os que o próprio Django trataria.

**A solução.** Deixar a lista vazia por padrão e preenchê-la apenas em produção:

```python
_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(",") if h.strip()]
```

**Um segundo detalhe no caminho.** Para verificar o fluxo sem abrir o navegador, usei o
`django.test.Client` em um script avulso e tomei o mesmo `DisallowedHost`. O `testserver` só é
liberado quando o ambiente de teste está preparado: fora do `manage.py test` é preciso chamar
`django.test.utils.setup_test_environment()` antes. O script de verificação é descartável e não
está versionado; os testes automatizados de verdade pertencem ao nível ambicioso.

**Verificação executada.** Listar enquetes devolveu 200, a página de detalhe devolveu 200, o
voto redirecionou e foi contabilizado (`votos == 1`) e o voto sem opção escolhida devolveu a
mensagem de erro em vez de quebrar.

**Aprendizado que levo.** Configuração que "parece boa prática" pode desligar um padrão seguro
do framework. Antes de trocar um padrão do Django por variável de ambiente, vale ler o que o
padrão já fazia.

---

> **Sobre as entradas 3 a 7.** Foram escritas em 24/11/2026, um dia depois do prazo do Relatório
> Final (23/11), numa única sessão de trabalho. O código dessa sessão foi escrito com o Claude
> Code (modelo Opus 5.5), conduzido e revisado por mim; os erros registrados abaixo são os que
> apareceram de fato nessa sessão, com a mensagem exata quando houve uma. O uso de IA no produto
> está descrito no Relatório Final.

## Entrada 3: 24/11/2026, retomada depois de sete semanas parado

**O que aconteceu entre 05/10 e 24/11.** Nenhum commit. A carga de trabalho fixo de 40 horas, a
demanda de freelance e as entregas e provas do segundo bimestre ocuparam as horas que o
Planejamento reservava ao projeto. Os gatilhos do risco R1 ("demanda de freelance acima de 8 horas
em uma semana" e "sete dias corridos sem commit no repositório") foram atingidos já em outubro, e a
resposta planejada, registrar a decisão neste diário no mesmo dia e usar a janela de
renegociação de 20/10, **não foi executada**. Não houve renegociação de escopo.

**Correção de datas.** Os seis primeiros commits foram feitos em 05/10 e tiveram as datas
reescritas para 03/10. Corrigi as entradas 1 e 2 e declarei a reescrita no topo deste diário. Não
reescrevi o histórico publicado de novo.

**O que fiz.** Partes 5 e 6 do tutorial oficial: 11 testes (`publicada_recentemente`, listagem que
esconde enquete futura, 404 no detalhe de enquete futura, voto) e o CSS movido para `static/`.

## Entrada 4: 24/11/2026, testes quebrando depois de configurar o WhiteNoise

**O problema.** Depois de preparar a publicação (gunicorn, WhiteNoise, `dj-database-url`), 9 dos
11 testes das enquetes passaram a falhar com:

```
ValueError: Missing staticfiles manifest entry for 'tutorial_enquetes/estilo.css'
```

**A causa.** `CompressedManifestStaticFilesStorage` resolve `{% static %}` por um manifest que só
existe depois de `collectstatic`. Na primeira rodada os testes passaram porque eu tinha acabado de
rodar `collectstatic` e a pasta `staticfiles/` estava lá; quando ela foi apagada, o erro apareceu.
Teste verde por acidente do ambiente local.

**A solução.** Usar o storage com manifest só com `DEBUG=0`. Local e no CI, o Django serve os
estáticos direto das pastas `static/` das aplicações. Commit próprio (`fix(build)`).

## Entrada 5: 24/11/2026, conta por e-mail e isolamento por usuário

**Decisões.**

- O critério do nível esperado pede conta "com e-mail e senha", mas o `User` padrão do Django
  entra por `username`. Em vez de trocar o modelo de usuário no meio do projeto (o que exige
  migrations desde o início), o formulário de cadastro normaliza o e-mail em minúsculas e grava
  nele o `username`. O `LoginView` padrão continua funcionando.
- Isolamento: todas as views do material herdam um mixin cujo `get_queryset()` filtra por
  `request.user`. Material de outra conta não aparece na lista e devolve 404 em editar e excluir,
  sem precisar checar dono em cada view. Vindo do Laravel, é o equivalente a um global scope.

**Verificação.** 11 testes do Trilha, incluindo os dois do critério de aceitação: material em 30%
continua em 30% depois de sair e entrar de novo, e a segunda conta não vê nem edita o material da
primeira.

## Entrada 6: 24/11/2026, Google Books devolveu 429 com cota zero

**O problema.** Antes de escrever a busca, consultei a API sem chave para ver o formato da
resposta e recebi:

```
"code": 429, "status": "RESOURCE_EXHAUSTED", "quota_limit_value": "0"
```

A cota anônima por dia era zero: sem chave de API, a busca não funciona.

**A solução.** A chave entra por variável de ambiente (`GOOGLE_BOOKS_API_KEY`), nunca no código.
Qualquer falha (erro HTTP, timeout de 5 s, JSON inválido) vira `BuscaIndisponivel`, o endpoint
responde 503 com mensagem, e a tela avisa e segue aceitando preenchimento manual. Os 10 testes da
busca simulam o `requests.get`, então a suíte não depende da cota da API.

**Pendente.** Sem a chave configurada no Render, o critério de aceitação do ambicioso ("digitar
clean code e ver título e autor preenchidos sozinhos") não passa em produção.

## Entrada 7: 24/11/2026, roteiro de aceitação em navegador real

**O que fiz.** Rodei a aplicação com `gunicorn` e `DJANGO_DEBUG=0`, como roda no Render, e executei
os roteiros de aceitação do Planejamento num Chrome headless (Playwright): voto contabilizado,
enquete criada pelo usuário `avaliador` no Admin aparecendo na página inicial, conta criada,
Clean Code em 30% depois de sair e entrar, segunda conta sem acesso (404) ao material da primeira.

**O que travou.** O resumo mostrava "3 materialis". O filtro `pluralize:"is"` só acrescenta o
sufixo, e "material" tem plural irregular. Trocado por `{% if %}`. O campo de busca também estava
sem estilo, porque fica fora do `<form>` e o seletor do CSS era `form input`.
