from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic

from .forms import CadastroForm, MaterialForm
from .models import Material


def inicio(request):
    return render(request, "trilha/inicio.html")


def cadastro(request):
    if request.user.is_authenticated:
        return redirect("trilha:minha_trilha")
    form = CadastroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, "Conta criada. Cadastre o primeiro material da sua trilha.")
        return redirect("trilha:minha_trilha")
    return render(request, "registration/cadastro.html", {"form": form})


class MateriaisDoUsuarioMixin(LoginRequiredMixin):
    """Toda consulta parte do usuário logado: material de outra conta devolve 404."""

    model = Material

    def get_queryset(self):
        return Material.objects.filter(usuario=self.request.user)


class MinhaTrilhaView(MateriaisDoUsuarioMixin, generic.ListView):
    template_name = "trilha/minha_trilha.html"
    context_object_name = "materiais"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["resumo"] = self.get_queryset().aggregate(
            total=Count("id"),
            media=Avg("progresso"),
            concluidos=Count("id", filter=Q(progresso=100)),
            nao_comecados=Count("id", filter=Q(progresso=0)),
        )
        return contexto


class MaterialFormMixin(MateriaisDoUsuarioMixin):
    form_class = MaterialForm
    template_name = "trilha/material_form.html"
    success_url = reverse_lazy("trilha:minha_trilha")


class MaterialCreateView(MaterialFormMixin, generic.CreateView):
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, f"“{form.instance.titulo}” entrou na sua trilha.")
        return super().form_valid(form)


class MaterialUpdateView(MaterialFormMixin, generic.UpdateView):
    def form_valid(self, form):
        messages.success(self.request, f"Progresso de “{form.instance.titulo}” atualizado.")
        return super().form_valid(form)


class MaterialDeleteView(MateriaisDoUsuarioMixin, generic.DeleteView):
    template_name = "trilha/material_confirmar_exclusao.html"
    success_url = reverse_lazy("trilha:minha_trilha")

    def form_valid(self, form):
        messages.success(self.request, f"“{self.object.titulo}” saiu da sua trilha.")
        return super().form_valid(form)
