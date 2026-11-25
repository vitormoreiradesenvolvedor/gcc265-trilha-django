"""URLs do projeto Trilha.

A raiz apresenta o projeto. A aplicação de estudo do tutorial oficial do Django responde
em /enquetes/ (nível mínimo viável) e a aplicação autoral Trilha em /trilha/ (nível esperado).
"""

from django.contrib import admin
from django.urls import include, path

from trilha import views as trilha_views

urlpatterns = [
    path("", trilha_views.inicio, name="inicio"),
    path("enquetes/", include("tutorial_enquetes.urls")),
    path("trilha/", include("trilha.urls")),
    path("admin/", admin.site.urls),
]
