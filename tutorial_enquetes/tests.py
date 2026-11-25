import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Pergunta


def criar_pergunta(texto, dias):
    """Cria uma pergunta publicada com deslocamento de `dias` em relação a agora
    (negativo para o passado, positivo para o futuro)."""
    momento = timezone.now() + datetime.timedelta(days=dias)
    return Pergunta.objects.create(texto=texto, publicada_em=momento)


class PerguntaModelTests(TestCase):
    def test_publicada_recentemente_com_pergunta_futura(self):
        futura = Pergunta(publicada_em=timezone.now() + datetime.timedelta(days=30))
        self.assertIs(futura.publicada_recentemente(), False)

    def test_publicada_recentemente_com_pergunta_antiga(self):
        antiga = Pergunta(publicada_em=timezone.now() - datetime.timedelta(days=1, seconds=1))
        self.assertIs(antiga.publicada_recentemente(), False)

    def test_publicada_recentemente_com_pergunta_recente(self):
        recente = Pergunta(publicada_em=timezone.now() - datetime.timedelta(hours=23, minutes=59))
        self.assertIs(recente.publicada_recentemente(), True)


class IndexViewTests(TestCase):
    def test_sem_perguntas(self):
        resposta = self.client.get(reverse("tutorial_enquetes:index"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Nenhuma enquete publicada ainda.")
        self.assertQuerySetEqual(resposta.context["ultimas_perguntas"], [])

    def test_pergunta_passada_aparece(self):
        pergunta = criar_pergunta("Pergunta passada.", dias=-30)
        resposta = self.client.get(reverse("tutorial_enquetes:index"))
        self.assertQuerySetEqual(resposta.context["ultimas_perguntas"], [pergunta])

    def test_pergunta_futura_nao_aparece(self):
        criar_pergunta("Pergunta futura.", dias=30)
        resposta = self.client.get(reverse("tutorial_enquetes:index"))
        self.assertContains(resposta, "Nenhuma enquete publicada ainda.")

    def test_passada_e_futura_so_mostra_passada(self):
        pergunta = criar_pergunta("Pergunta passada.", dias=-30)
        criar_pergunta("Pergunta futura.", dias=30)
        resposta = self.client.get(reverse("tutorial_enquetes:index"))
        self.assertQuerySetEqual(resposta.context["ultimas_perguntas"], [pergunta])


class DetalheViewTests(TestCase):
    def test_pergunta_futura_devolve_404(self):
        futura = criar_pergunta("Pergunta futura.", dias=5)
        resposta = self.client.get(reverse("tutorial_enquetes:detalhe", args=(futura.id,)))
        self.assertEqual(resposta.status_code, 404)

    def test_pergunta_passada_mostra_texto(self):
        passada = criar_pergunta("Pergunta passada.", dias=-5)
        resposta = self.client.get(reverse("tutorial_enquetes:detalhe", args=(passada.id,)))
        self.assertContains(resposta, passada.texto)


class VotarTests(TestCase):
    def test_voto_soma_e_redireciona(self):
        pergunta = criar_pergunta("Qual framework?", dias=-1)
        opcao = pergunta.opcoes.create(texto="Django")
        resposta = self.client.post(
            reverse("tutorial_enquetes:votar", args=(pergunta.id,)), {"opcao": opcao.id}
        )
        self.assertRedirects(resposta, reverse("tutorial_enquetes:resultados", args=(pergunta.id,)))
        opcao.refresh_from_db()
        self.assertEqual(opcao.votos, 1)

    def test_voto_sem_opcao_mostra_erro(self):
        pergunta = criar_pergunta("Qual framework?", dias=-1)
        resposta = self.client.post(reverse("tutorial_enquetes:votar", args=(pergunta.id,)))
        self.assertContains(resposta, "Escolha uma opção para votar.")
