import datetime

from django.db import models
from django.utils import timezone


class Pergunta(models.Model):
    texto = models.CharField("texto da pergunta", max_length=200)
    publicada_em = models.DateTimeField("data de publicação")

    class Meta:
        verbose_name = "pergunta"
        verbose_name_plural = "perguntas"
        ordering = ["-publicada_em"]

    def __str__(self):
        return self.texto

    def publicada_recentemente(self):
        agora = timezone.now()
        return agora - datetime.timedelta(days=1) <= self.publicada_em <= agora

    publicada_recentemente.boolean = True
    publicada_recentemente.short_description = "publicada nas últimas 24h?"


class Opcao(models.Model):
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE, related_name="opcoes")
    texto = models.CharField("texto da opção", max_length=200)
    votos = models.IntegerField("votos", default=0)

    class Meta:
        verbose_name = "opção"
        verbose_name_plural = "opções"

    def __str__(self):
        return self.texto
