#!/usr/bin/env bash
# Build do Render: dependências, estáticos, migrations e dados de avaliação.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py preparar_avaliacao
