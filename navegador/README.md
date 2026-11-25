# Versão do navegador (GitHub Pages)

O GitHub Pages só serve arquivos estáticos e não roda Python no servidor. Esta pasta publica o
Trilha de outro jeito: o **Django inteiro roda dentro do navegador** do visitante, compilado para
WebAssembly pelo [Pyodide](https://pyodide.org) 314.0.7 (Python 3.14.2).

| Arquivo | Papel |
|---|---|
| `index.html` | Página que carrega o Pyodide e mostra o Trilha num iframe |
| `app.js` | Instala o Django, monta o SQLite sobre o IndexedDB e converte cada clique, formulário ou `fetch` em uma requisição WSGI |
| `ponte.py` | Lado Python: `django.setup()`, `migrate`, `preparar_avaliacao` e o handler WSGI |
| `build.py` | Gera `_site/` com `app.zip`, as wheels e os estáticos (`collectstatic`) |

Configuração própria em `trilha_projeto/settings_navegador.py`.

**Limitações, declaradas.** Cada navegador tem o próprio banco SQLite, salvo no IndexedDB: dados
não são compartilhados entre pessoas nem entre navegadores, e somem se o visitante limpar os dados
do site. O hash de senha usa menos iterações, porque roda em Python puro e a senha não sai do
navegador. A primeira carga baixa cerca de 20 MB (Pyodide e Django).

Gerar e testar localmente:

```bash
python navegador/build.py /tmp/site/gcc265-trilha-django
cd /tmp/site && python -m http.server 8777
# abrir http://localhost:8777/gcc265-trilha-django/
```
