from django.contrib import admin

from .models import Opcao, Pergunta


class OpcaoInline(admin.TabularInline):
    model = Opcao
    extra = 3


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["texto"]}),
        ("Publicação", {"fields": ["publicada_em"]}),
    ]
    inlines = [OpcaoInline]
    list_display = ["texto", "publicada_em", "publicada_recentemente"]
    list_filter = ["publicada_em"]
    search_fields = ["texto"]
