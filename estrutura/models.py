from django.db import models


class Unidade(models.Model):
    """Unidade do SENAC-DF (ex.: Taguatinga, Ennius Muniz)."""

    nome = models.CharField("nome", max_length=100, unique=True)
    endereco = models.CharField("endereço", max_length=255, blank=True)
    ativa = models.BooleanField("ativa", default=True)

    class Meta:
        verbose_name = "unidade"
        verbose_name_plural = "unidades"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class TipoAmbiente(models.TextChoices):
    SALA_AULA = "SALA_AULA", "Sala de aula"
    LABORATORIO = "LABORATORIO", "Laboratório"
    ADMINISTRATIVO = "ADMINISTRATIVO", "Administrativo"
    AUDITORIO = "AUDITORIO", "Auditório"
    COZINHA = "COZINHA", "Cozinha"
    BANHEIRO = "BANHEIRO", "Banheiro"
    AREA_EXTERNA = "AREA_EXTERNA", "Área externa"
    TECNICO = "TECNICO", "Área técnica"
    OUTRO = "OUTRO", "Outro"


class Local(models.Model):

    unidade = models.ForeignKey(
        Unidade, verbose_name="unidade", on_delete=models.PROTECT, related_name="locais"
    )
    bloco = models.CharField("bloco", max_length=50)
    andar = models.CharField("andar", max_length=30)
    sala = models.CharField("sala", max_length=50)
    tipo_ambiente = models.CharField(
        "tipo de ambiente", max_length=20, choices=TipoAmbiente.choices, default=TipoAmbiente.SALA_AULA
    )

    class Meta:
        verbose_name = "local"
        verbose_name_plural = "locais"
        ordering = ["unidade__nome", "bloco", "andar", "sala"]
        constraints = [
            models.UniqueConstraint(
                fields=["unidade", "bloco", "andar", "sala"], name="local_unico_por_unidade"
            ),
        ]

    def __str__(self):
        return f"{self.unidade} — Bloco {self.bloco}, {self.andar}, {self.sala}"


class Equipamento(models.Model):

    local = models.ForeignKey(
        Local, verbose_name="local", on_delete=models.PROTECT, related_name="equipamentos"
    )
    nome = models.CharField("nome", max_length=100)
    patrimonio = models.CharField("nº de patrimônio", max_length=50, unique=True)
    descricao = models.TextField("descrição", blank=True)

    class Meta:
        verbose_name = "equipamento"
        verbose_name_plural = "equipamentos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.patrimonio})"
