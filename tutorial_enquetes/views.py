from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Opcao, Pergunta


class IndexView(generic.ListView):
    template_name = "tutorial_enquetes/index.html"
    context_object_name = "ultimas_perguntas"

    def get_queryset(self):
        """Devolve as cinco enquetes mais recentes já publicadas."""
        return Pergunta.objects.filter(publicada_em__lte=timezone.now())[:5]


class DetalheView(generic.DetailView):
    model = Pergunta
    template_name = "tutorial_enquetes/detalhe.html"

    def get_queryset(self):
        return Pergunta.objects.filter(publicada_em__lte=timezone.now())


class ResultadosView(generic.DetailView):
    model = Pergunta
    template_name = "tutorial_enquetes/resultados.html"


def votar(request, pergunta_id):
    pergunta = get_object_or_404(Pergunta, pk=pergunta_id)
    try:
        opcao = pergunta.opcoes.get(pk=request.POST["opcao"])
    except (KeyError, Opcao.DoesNotExist):
        return render(
            request,
            "tutorial_enquetes/detalhe.html",
            {"pergunta": pergunta, "erro": "Escolha uma opção para votar."},
        )
    opcao.votos = F("votos") + 1
    opcao.save()
    return HttpResponseRedirect(reverse("tutorial_enquetes:resultados", args=(pergunta.id,)))
