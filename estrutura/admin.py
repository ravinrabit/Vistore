from django.contrib import admin

from .models import Equipamento, Local, Unidade


@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ["nome", "endereco", "ativa"]
    list_filter = ["ativa"]
    search_fields = ["nome"]


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = ["unidade", "bloco", "andar", "sala", "tipo_ambiente"]
    list_filter = ["unidade", "tipo_ambiente"]
    search_fields = ["bloco", "sala"]


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ["nome", "patrimonio", "local"]
    list_filter = ["local__unidade"]
    search_fields = ["nome", "patrimonio"]
