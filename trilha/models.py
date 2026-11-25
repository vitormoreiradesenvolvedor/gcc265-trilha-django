from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models


class Material(models.Model):
    """Um item que a pessoa pretende estudar: livro, curso, vídeo, artigo."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="materiais"
    )
    titulo = models.CharField("título", max_length=200)
    autor = models.CharField("autor", max_length=200, blank=True)
    progresso = models.PositiveSmallIntegerField(
        "progresso (%)", default=0, validators=[MaxValueValidator(100)]
    )
    criado_em = models.DateTimeField("criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "material"
        verbose_name_plural = "materiais"
        ordering = ["-atualizado_em"]

    def __str__(self):
        return self.titulo

    @property
    def situacao(self):
        if self.progresso == 0:
            return "não começado"
        if self.progresso == 100:
            return "concluído"
        return "em andamento"
