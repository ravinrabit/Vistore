from django.test import TestCase
from django.urls import reverse

from contas.models import Perfil, Usuario
from estrutura.models import Unidade


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade = Unidade.objects.create(nome="Taguatinga")
        cls.usuario = Usuario.objects.create_user(
            email="ana@senacdf.edu.br", password="senha-forte-123", nome="Ana Souza",
            perfil=Perfil.SOLICITANTE, unidade=cls.unidade,
        )

    def test_login_com_email(self):
        resposta = self.client.post(
            reverse("contas:login"), {"username": "ana@senacdf.edu.br", "password": "senha-forte-123"}
        )
        self.assertRedirects(resposta, reverse("contas:painel"))

    def test_senha_errada_nao_entra(self):
        resposta = self.client.post(
            reverse("contas:login"), {"username": "ana@senacdf.edu.br", "password": "errada"}
        )
        self.assertContains(resposta, "E-mail ou senha incorretos")

    def test_usuario_desativado_nao_entra(self):
        """RN10: usuário desativado não entra no sistema."""
        self.usuario.is_active = False
        self.usuario.save()
        entrou = self.client.login(email="ana@senacdf.edu.br", password="senha-forte-123")
        self.assertFalse(entrou)

    def test_painel_exige_login(self):
        resposta = self.client.get(reverse("contas:painel"))
        self.assertRedirects(resposta, f"{reverse('contas:login')}?next=/")

    def test_logout(self):
        self.client.force_login(self.usuario)
        resposta = self.client.post(reverse("contas:logout"))
        self.assertRedirects(resposta, reverse("contas:login"))


class PainelPorPerfilTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade = Unidade.objects.create(nome="Taguatinga")

    def _usuario(self, perfil):
        return Usuario.objects.create_user(
            email=f"{perfil.lower()}@teste.com", password="x", nome=perfil.title(),
            perfil=perfil, unidade=self.unidade,
        )

    def test_cada_perfil_ve_seu_painel(self):
        for perfil in Perfil.values:
            with self.subTest(perfil=perfil):
                self.client.force_login(self._usuario(perfil))
                resposta = self.client.get(reverse("contas:painel"))
                self.assertTemplateUsed(resposta, f"contas/painel/{perfil.lower()}.html")

    def test_usuario_sem_unidade_invalido_exceto_admin(self):
        from django.core.exceptions import ValidationError

        tecnico = Usuario(email="t@t.com", nome="T", perfil=Perfil.TECNICO)
        with self.assertRaises(ValidationError):
            tecnico.full_clean(exclude=["password"])
        admin = Usuario(email="a@a.com", nome="A", perfil=Perfil.ADMIN)
        admin.full_clean(exclude=["password"])  # não levanta erro
