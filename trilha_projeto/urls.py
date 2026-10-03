"""URLs do projeto Trilha.

A aplicação de estudo do tutorial oficial do Django responde em /enquetes/.
A aplicação autoral Trilha entra em /trilha/ a partir do nível esperado.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="tutorial_enquetes:index", permanent=False)),
    path("enquetes/", include("tutorial_enquetes.urls")),
    path("admin/", admin.site.urls),
]
