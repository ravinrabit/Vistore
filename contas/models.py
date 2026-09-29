from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


class Perfil(models.TextChoices):
    SOLICITANTE = "SOLICITANTE", "Solicitante"
    TECNICO = "TECNICO", "Técnico"
    GESTOR = "GESTOR", "Gestor de Segurança"
    ADMIN = "ADMIN", "Administrador"


class UsuarioManager(BaseUserManager):

    use_in_migrations = True

    def _criar_usuario(self, email, password, **extra):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra)
        usuario.set_password(password)  # guarda só o hash, nunca a senha pura
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._criar_usuario(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("perfil", Perfil.ADMIN)
        if not extra["is_staff"] or not extra["is_superuser"]:
            raise ValueError("Superusuário precisa de is_staff=True e is_superuser=True.")
        return self._criar_usuario(email, password, **extra)


class Usuario(AbstractUser):

    username = None
    first_name = None
    last_name = None

    nome = models.CharField("nome", max_length=150)
    email = models.EmailField("e-mail", unique=True)
    perfil = models.CharField(
        "perfil", max_length=20, choices=Perfil.choices, default=Perfil.SOLICITANTE
    )
    unidade = models.ForeignKey(
        "estrutura.Unidade",
        verbose_name="unidade",
        on_delete=models.PROTECT,  
        related_name="usuarios",
        null=True,
        blank=True, 
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.get_perfil_display()})"

    def clean(self):
        super().clean()
        if self.perfil != Perfil.ADMIN and not self.unidade_id:
            raise ValidationError({"unidade": "Todo usuário, exceto o Administrador, precisa de uma unidade."})

    def get_full_name(self):
        return self.nome

    def get_short_name(self):
        return self.nome.split(" ")[0] if self.nome else self.email


    @property
    def eh_admin(self):
        return self.perfil == Perfil.ADMIN or self.is_superuser

    @property
    def eh_gestor(self):
        return self.perfil == Perfil.GESTOR

    @property
    def eh_tecnico(self):
        return self.perfil == Perfil.TECNICO

    @property
    def eh_solicitante(self):
        return self.perfil == Perfil.SOLICITANTE
