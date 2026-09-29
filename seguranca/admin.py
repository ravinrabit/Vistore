from django.contrib import admin

from .models import EPI, Incidente, TipoServico, Treinamento, TreinamentoTecnico


@admin.register(Treinamento)
class TreinamentoAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nome", "validade_meses"]
    search_fields = ["codigo", "nome"]


@admin.register(TreinamentoTecnico)
class TreinamentoTecnicoAdmin(admin.ModelAdmin):
    list_display = ["tecnico", "treinamento", "data_realizacao", "data_validade"]
    list_filter = ["treinamento", "tecnico__unidade"]
    search_fields = ["tecnico__nome"]


@admin.register(EPI)
class EPIAdmin(admin.ModelAdmin):
    list_display = ["nome", "numero_ca"]
    search_fields = ["nome", "numero_ca"]


@admin.register(TipoServico)
class TipoServicoAdmin(admin.ModelAdmin):
    list_display = ["nome", "eletrico", "trabalho_em_altura"]
    list_filter = ["eletrico", "trabalho_em_altura"]
    filter_horizontal = ["treinamentos_exigidos", "epis_exigidos"]


@admin.register(Incidente)
class IncidenteAdmin(admin.ModelAdmin):
    list_display = ["ordem", "gravidade", "houve_lesao", "houve_afastamento", "registrado_por", "data_hora"]
    list_filter = ["gravidade", "houve_lesao", "houve_afastamento"]
