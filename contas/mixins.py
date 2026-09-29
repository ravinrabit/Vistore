
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class PerfilRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):

    perfis_permitidos = []

    def test_func(self):
        usuario = self.request.user
        return usuario.eh_admin or usuario.perfil in self.perfis_permitidos


class GestaoMixin(PerfilRequeridoMixin):


    perfis_permitidos = ["GESTOR"]


class SomenteAdminMixin(PerfilRequeridoMixin):


    perfis_permitidos = []


class FiltroUnidadeMixin:

    campo_unidade = "unidade"

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario = self.request.user
        if usuario.eh_admin:
            return queryset
        return queryset.filter(**{self.campo_unidade: usuario.unidade_id})
