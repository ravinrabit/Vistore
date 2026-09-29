from django.contrib import admin

from seguranca.models import Incidente

from .models import ChecklistSeguranca, HistoricoStatus, OrdemServico, Preventiva


class HistoricoInline(admin.TabularInline):
    model = HistoricoStatus
    extra = 0
    readonly_fields = ["status_anterior", "status_novo", "usuario", "data_hora"]
    can_delete = False


class ChecklistInline(admin.StackedInline):
    model = ChecklistSeguranca
    extra = 0


class IncidenteInline(admin.TabularInline):
    model = Incidente
    extra = 0


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "prioridade", "local", "solicitante", "tecnico", "aberta_em"]
    list_filter = ["status", "prioridade", "requer_revisao_seguranca", "local__unidade"]
    search_fields = ["descricao"]
    inlines = [ChecklistInline, IncidenteInline, HistoricoInline]


@admin.register(HistoricoStatus)
class HistoricoStatusAdmin(admin.ModelAdmin):
    list_display = ["ordem", "status_anterior", "status_novo", "usuario", "data_hora"]


@admin.register(ChecklistSeguranca)
class ChecklistSegurancaAdmin(admin.ModelAdmin):
    list_display = ["ordem", "area_isolada", "confirmado_em"]
    filter_horizontal = ["epis_confirmados"]


@admin.register(Preventiva)
class PreventivaAdmin(admin.ModelAdmin):
    list_display = ["equipamento", "tipo_servico", "periodicidade_dias", "proxima_data", "ativa"]
    list_filter = ["ativa"]
