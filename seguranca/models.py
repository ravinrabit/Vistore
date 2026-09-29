import calendar
from datetime import date

from django.conf import settings
from django.db import models


def somar_meses(data, meses):

    mes_total = data.month - 1 + meses
    ano = data.year + mes_total // 12
    mes = mes_total % 12 + 1
    dia = min(data.day, calendar.monthrange(ano, mes)[1])
    return date(ano, mes, dia)


class Treinamento(models.Model):


    codigo = models.CharField("código", max_length=20, unique=True)
    nome = models.CharField("nome", max_length=150)
    validade_meses = models.PositiveSmallIntegerField("validade (meses)")

    class Meta:
        verbose_name = "treinamento"
        verbose_name_plural = "treinamentos"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} — {self.nome}"


class TreinamentoTecnico(models.Model):

    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="técnico",
        on_delete=models.PROTECT,
        related_name="treinamentos",
        limit_choices_to={"perfil": "TECNICO"},
    )
    treinamento = models.ForeignKey(
        Treinamento, verbose_name="treinamento", on_delete=models.PROTECT, related_name="realizacoes"
    )
    data_realizacao = models.DateField("data de realização")
    data_validade = models.DateField(
        "data de validade", blank=True, help_text="Se vazio, é calculada pela validade do treinamento."
    )

    class Meta:
        verbose_name = "treinamento do técnico"
        verbose_name_plural = "treinamentos dos técnicos"
        ordering = ["-data_validade"]

    def __str__(self):
        return f"{self.tecnico.nome} — {self.treinamento.codigo} (válido até {self.data_validade:%d/%m/%Y})"

    def save(self, *args, **kwargs):
        if not self.data_validade:
            self.data_validade = somar_meses(self.data_realizacao, self.treinamento.validade_meses)
        super().save(*args, **kwargs)

    def valido_em(self, data):
        return self.data_realizacao <= data <= self.data_validade


class EPI(models.Model):

    nome = models.CharField("nome", max_length=100)
    numero_ca = models.CharField("nº do CA", max_length=20, unique=True)
    descricao = models.TextField("descrição", blank=True)

    class Meta:
        verbose_name = "EPI"
        verbose_name_plural = "EPIs"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} (CA {self.numero_ca})"


class TipoServico(models.Model):


    nome = models.CharField("nome", max_length=100, unique=True)
    descricao = models.TextField("descrição", blank=True)
    eletrico = models.BooleanField("serviço elétrico", default=False, help_text="Exige NR-10.")
    trabalho_em_altura = models.BooleanField(
        "trabalho acima de 2 m", default=False, help_text="Exige NR-35."
    )
    treinamentos_exigidos = models.ManyToManyField(
        Treinamento, verbose_name="treinamentos exigidos", blank=True, related_name="tipos_servico"
    )
    epis_exigidos = models.ManyToManyField(
        EPI, verbose_name="EPIs exigidos", blank=True, related_name="tipos_servico"
    )

    class Meta:
        verbose_name = "tipo de serviço"
        verbose_name_plural = "tipos de serviço"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Gravidade(models.TextChoices):
    LEVE = "LEVE", "Leve"
    MODERADA = "MODERADA", "Moderada"
    GRAVE = "GRAVE", "Grave"


class Incidente(models.Model):

    ordem = models.ForeignKey(
        "ordens.OrdemServico", verbose_name="ordem de serviço", on_delete=models.CASCADE,
        related_name="incidentes",
    )
    descricao = models.TextField("descrição")
    gravidade = models.CharField("gravidade", max_length=10, choices=Gravidade.choices)
    houve_lesao = models.BooleanField("houve lesão", default=False)
    houve_afastamento = models.BooleanField("houve afastamento", default=False)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="registrado por", on_delete=models.PROTECT,
        related_name="incidentes_registrados",
    )
    data_hora = models.DateTimeField("data e hora", auto_now_add=True)

    class Meta:
        verbose_name = "incidente"
        verbose_name_plural = "incidentes"
        ordering = ["-data_hora"]

    def __str__(self):
        return f"Incidente {self.get_gravidade_display().lower()} na OS #{self.ordem_id}"
