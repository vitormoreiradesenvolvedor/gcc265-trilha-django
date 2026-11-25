"""Monta o site estático da versão do navegador.

Uso: python navegador/build.py _site

Gera em _site/: index.html e app.js (carregador), app.zip (código do projeto e ponte.py),
wheels/ (Django e dependências puras em Python, com manifesto.json) e static/ (collectstatic).
"""

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AQUI = Path(__file__).resolve().parent

# Dependências puras em Python instaladas por micropip. requests e pyodide-http vêm do Pyodide.
WHEELS = ["Django", "asgiref", "sqlparse", "dj-database-url"]
PASTAS_DO_PROJETO = ["trilha_projeto", "tutorial_enquetes", "trilha"]


def versoes_fixadas():
    fixadas = {}
    for linha in (RAIZ / "requirements.txt").read_text().splitlines():
        if "==" in linha:
            nome, versao = linha.strip().split("==")
            fixadas[nome.lower()] = versao
    return [f"{nome}=={fixadas[nome.lower()]}" for nome in WHEELS]


def main(destino):
    destino = Path(destino).resolve()
    shutil.rmtree(destino, ignore_errors=True)
    destino.mkdir(parents=True)

    for nome in ["index.html", "app.js"]:
        shutil.copy(AQUI / nome, destino / nome)
    (destino / ".nojekyll").touch()

    with zipfile.ZipFile(destino / "app.zip", "w", zipfile.ZIP_DEFLATED) as zipado:
        zipado.write(AQUI / "ponte.py", "ponte.py")
        for pasta in PASTAS_DO_PROJETO:
            for arquivo in sorted((RAIZ / pasta).rglob("*")):
                if arquivo.is_file() and "__pycache__" not in arquivo.parts and "tests" not in arquivo.parts:
                    zipado.write(arquivo, arquivo.relative_to(RAIZ))

    pasta_wheels = destino / "wheels"
    subprocess.run(
        [sys.executable, "-m", "pip", "download", "--quiet", "--no-deps", "--only-binary=:all:",
         "--dest", str(pasta_wheels), *versoes_fixadas()],
        check=True,
    )
    manifesto = sorted(p.name for p in pasta_wheels.glob("*.whl"))
    (pasta_wheels / "manifesto.json").write_text(json.dumps(manifesto, indent=2))

    ambiente = dict(os.environ, DJANGO_SETTINGS_MODULE="trilha_projeto.settings", DJANGO_DEBUG="1")
    subprocess.run(
        [sys.executable, "-c",
         "import django, sys; from django.conf import settings; django.setup(); "
         "from django.core.management import call_command; "
         f"settings.STATIC_ROOT = {str(destino / 'static')!r}; "
         "call_command('collectstatic', interactive=False, verbosity=0)"],
        cwd=RAIZ, env=ambiente, check=True,
    )
    print(f"Site gerado em {destino}: {len(manifesto)} wheels, app.zip e static/.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "_site")
