from django import forms

from contas.forms import EstiloBootstrapMixin

from .models import Equipamento, Local, Unidade


class UnidadeForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Unidade
        fields = ["nome", "endereco", "ativa"]


class LocalForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Local
        fields = ["unidade", "bloco", "andar", "sala", "tipo_ambiente"]

    def __init__(self, *args, usuario, **kwargs):
        super().__init__(*args, **kwargs)
        campo = self.fields["unidade"]
        campo.queryset = Unidade.objects.filter(ativa=True)
        if not usuario.eh_admin:

            campo.disabled = True
            campo.initial = usuario.unidade


class EquipamentoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = ["nome", "patrimonio", "local", "descricao"]
        widgets = {"descricao": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, usuario, **kwargs):
        super().__init__(*args, **kwargs)
        locais = Local.objects.select_related("unidade")
        if not usuario.eh_admin:
            locais = locais.filter(unidade=usuario.unidade)
        self.fields["local"].queryset = locais
