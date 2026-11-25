"""Busca de livros na API pública do Google Books.

Sem chave, a cota anônima da API pode ser zero (resposta 429 RESOURCE_EXHAUSTED);
com GOOGLE_BOOKS_API_KEY definida, a chave vai na consulta. Qualquer falha vira
BuscaIndisponivel, e a tela segue aceitando o preenchimento manual.
"""

import os

import requests

URL = "https://www.googleapis.com/books/v1/volumes"
TIMEOUT_SEGUNDOS = 5
MAX_RESULTADOS = 5


class BuscaIndisponivel(Exception):
    pass


def buscar_livros(termo):
    """Devolve até MAX_RESULTADOS dicionários {"titulo", "autor"} para o termo."""
    termo = (termo or "").strip()
    if not termo:
        return []

    parametros = {
        "q": termo,
        "maxResults": MAX_RESULTADOS,
        "printType": "books",
        "fields": "items(volumeInfo(title,subtitle,authors))",
    }
    chave = os.environ.get("GOOGLE_BOOKS_API_KEY")
    if chave:
        parametros["key"] = chave

    try:
        resposta = requests.get(URL, params=parametros, timeout=TIMEOUT_SEGUNDOS)
        resposta.raise_for_status()
        dados = resposta.json()
    except (requests.RequestException, ValueError) as erro:
        raise BuscaIndisponivel(str(erro)) from erro

    resultados = []
    for item in dados.get("items", []):
        info = item.get("volumeInfo") or {}
        titulo = info.get("title")
        if not titulo:
            continue
        if info.get("subtitle"):
            titulo = f"{titulo}: {info['subtitle']}"
        resultados.append({"titulo": titulo, "autor": ", ".join(info.get("authors") or [])})
    return resultados
