from django.contrib import admin

from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["titulo", "autor", "usuario", "progresso", "atualizado_em"]
    list_filter = ["atualizado_em"]
    search_fields = ["titulo", "autor", "usuario__username"]
