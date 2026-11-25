from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import EntrarForm

app_name = "trilha"
urlpatterns = [
    path("", views.MinhaTrilhaView.as_view(), name="minha_trilha"),
    path("novo/", views.MaterialCreateView.as_view(), name="novo"),
    path("<int:pk>/editar/", views.MaterialUpdateView.as_view(), name="editar"),
    path("<int:pk>/excluir/", views.MaterialDeleteView.as_view(), name="excluir"),
    path("buscar/", views.buscar, name="buscar"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path(
        "entrar/",
        auth_views.LoginView.as_view(authentication_form=EntrarForm, redirect_authenticated_user=True),
        name="entrar",
    ),
    path("sair/", auth_views.LogoutView.as_view(), name="sair"),
]
