# Diário técnico

Registro datado do aprendizado de Django. Uma entrada por sessão de trabalho: o que fiz, o que
travou e como resolvi. Meta do nível mínimo viável: pelo menos seis entradas datadas até 20/10.

---

## Entrada 1: 03/10/2026, ambiente e primeiro projeto no ar localmente

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

**Início tardio.** O Planejamento prevê o início em 28/09, e eu comecei em 03/10, no fim da
semana 1 do cronograma. Os primeiros dias foram perdidos e ficam registrados aqui: a comparação
honesta entre o pactuado e o entregue vale nota no Relatório Final, e o histórico do
repositório é a evidência que sustenta o que eu declarar lá.

---

## Entrada 2: 03/10/2026, ALLOWED_HOSTS derrubou o acesso local

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
