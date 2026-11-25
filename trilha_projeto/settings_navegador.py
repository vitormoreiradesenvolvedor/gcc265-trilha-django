"""Configuração da versão que roda no navegador (GitHub Pages + Pyodide).

O GitHub Pages só serve arquivos estáticos. Nesta versão o Django inteiro roda dentro do
navegador do visitante, compilado para WebAssembly pelo Pyodide, e o banco SQLite fica salvo no
IndexedDB desse navegador. Cada visitante tem o próprio banco: nada é compartilhado entre pessoas.
"""

import os

from .settings import *  # noqa: F401,F403
from .settings import MIDDLEWARE

DEBUG = False
ALLOWED_HOSTS = ["localhost"]
CSRF_TRUSTED_ORIGINS = []

# Não há HTTPS entre a página e o Django: as requisições não saem do navegador.
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# /dados é montado sobre o IndexedDB pelo carregador (navegador/app.js).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/dados/db.sqlite3",
    }
}

MIDDLEWARE = [m for m in MIDDLEWARE if not m.startswith("whitenoise.")]

# Os estáticos são servidos pelo próprio GitHub Pages, gerados por collectstatic no build.
STATIC_URL = os.environ.get("TRILHA_STATIC_URL", "/static/")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# PBKDF2 com o número padrão de iterações leva segundos em WebAssembly; aqui a senha nunca
# sai do navegador de quem a digitou, então um custo menor não expõe nada a terceiros.
PASSWORD_HASHERS = ["trilha.hashers.PBKDF2Navegador"]

# Erros 500 aparecem no console do navegador (F12), já que não há log de servidor.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"django.request": {"handlers": ["console"], "level": "ERROR"}},
}
