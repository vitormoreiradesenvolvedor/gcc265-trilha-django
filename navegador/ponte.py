"""Ponte entre o carregador JavaScript e o Django rodando no Pyodide.

O JavaScript chama `iniciar()` uma vez e `requisitar()` a cada navegação, envio de formulário
ou fetch da página. `requisitar()` monta um ambiente WSGI e chama o mesmo handler que o gunicorn
chamaria no servidor.
"""

import io
import os
import sys


def iniciar(static_url):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trilha_projeto.settings_navegador")
    os.environ["TRILHA_STATIC_URL"] = static_url
    os.environ.setdefault("DJANGO_AVALIADOR_SENHA", "avaliacao-gcc265")
    # O Pyodide mantém um event loop sempre ativo, e o Django recusa ORM síncrono quando vê um.
    # Aqui não há threads nem concorrência: cada requisição roda inteira antes da próxima.
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

    import pyodide_http

    pyodide_http.patch_all()  # requests passa a usar XMLHttpRequest (busca no Google Books)

    import django
    from django.core.management import call_command

    django.setup()
    call_command("migrate", verbosity=0, interactive=False)
    call_command("preparar_avaliacao", verbosity=0)

    global _handler
    from django.core.handlers.wsgi import WSGIHandler

    _handler = WSGIHandler()


def requisitar(metodo, caminho, consulta, corpo, tipo, cookie):
    corpo = (corpo or "").encode("utf-8")
    environ = {
        "REQUEST_METHOD": metodo,
        "PATH_INFO": caminho,
        "QUERY_STRING": consulta or "",
        "CONTENT_TYPE": tipo or "",
        "CONTENT_LENGTH": str(len(corpo)),
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "80",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "HTTP_HOST": "localhost",
        "HTTP_COOKIE": cookie or "",
        "HTTP_ACCEPT": "text/html,application/json",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": io.BytesIO(corpo),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }
    resposta = {}

    def start_response(status, cabecalhos, exc_info=None):
        resposta["status"] = int(status.split()[0])
        resposta["cabecalhos"] = [list(c) for c in cabecalhos]

    partes = _handler(environ, start_response)
    try:
        resposta["corpo"] = b"".join(partes).decode("utf-8", errors="replace")
    finally:
        if hasattr(partes, "close"):
            partes.close()
    return resposta
