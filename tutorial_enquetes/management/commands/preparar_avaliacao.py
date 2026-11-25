"""Prepara o ambiente publicado para o roteiro de aceitação do nível mínimo.

Cria (ou atualiza) o usuário `avaliador`, com acesso ao Admin restrito às enquetes,
e publica uma enquete de exemplo se ainda não houver nenhuma. Pode rodar a cada deploy.
"""

import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.utils import timezone

from tutorial_enquetes.models import Pergunta


class Command(BaseCommand):
    help = "Cria o usuário avaliador e uma enquete de exemplo."

    def handle(self, *args, **options):
        senha = os.environ.get("DJANGO_AVALIADOR_SENHA")
        if senha:
            usuario, _ = get_user_model().objects.get_or_create(username="avaliador")
            usuario.is_staff = True
            usuario.is_superuser = False
            usuario.set_password(senha)
            usuario.save()
            usuario.user_permissions.set(
                Permission.objects.filter(content_type__app_label="tutorial_enquetes")
            )
            self.stdout.write("Usuário avaliador pronto.")
        else:
            self.stdout.write("DJANGO_AVALIADOR_SENHA ausente: usuário avaliador não criado.")

        if not Pergunta.objects.exists():
            pergunta = Pergunta.objects.create(
                texto="Qual framework web você quer aprender a seguir?",
                publicada_em=timezone.now(),
            )
            for texto in ["Django", "Laravel", "Next.js"]:
                pergunta.opcoes.create(texto=texto)
            self.stdout.write("Enquete de exemplo publicada.")
