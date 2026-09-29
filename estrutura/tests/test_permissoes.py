"""Testes das permissões do CRUD: Admin vê tudo, Gestor só a própria unidade."""

from django.test import TestCase
from django.urls import reverse

from contas.models import Perfil, Usuario
from estrutura.models import Equipamento, Local, Unidade


class PermissoesEstruturaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.taguatinga = Unidade.objects.create(nome="Taguatinga")
        cls.ennius = Unidade.objects.create(nome="Ennius Muniz")

        cls.local_tag = Local.objects.create(unidade=cls.taguatinga, bloco="A", andar="Térreo", sala="101")
        cls.local_enn = Local.objects.create(unidade=cls.ennius, bloco="B", andar="1º", sala="201")
        cls.equip_tag = Equipamento.objects.create(local=cls.local_tag, nome="Ar-condicionado", patrimonio="T-001")
        cls.equip_enn = Equipamento.objects.create(local=cls.local_enn, nome="Quadro elétrico", patrimonio="E-001")

        def criar(email, perfil, unidade=None):
            return Usuario.objects.create_user(email=email, password="x", nome=email, perfil=perfil, unidade=unidade)

        cls.admin = criar("admin@t.com", Perfil.ADMIN)
        cls.gestor = criar("gestor@t.com", Perfil.GESTOR, cls.taguatinga)
        cls.tecnico = criar("tecnico@t.com", Perfil.TECNICO, cls.taguatinga)
        cls.solicitante = criar("solic@t.com", Perfil.SOLICITANTE, cls.taguatinga)

    # --- Listagens ---------------------------------------------------------

    def test_admin_ve_locais_de_todas_as_unidades(self):
        self.client.force_login(self.admin)
        resposta = self.client.get(reverse("estrutura:local_lista"))
        self.assertCountEqual(resposta.context["object_list"], [self.local_tag, self.local_enn])

    def test_gestor_ve_so_locais_da_sua_unidade(self):
        self.client.force_login(self.gestor)
        resposta = self.client.get(reverse("estrutura:local_lista"))
        self.assertEqual(list(resposta.context["object_list"]), [self.local_tag])

    def test_gestor_ve_so_equipamentos_da_sua_unidade(self):
        self.client.force_login(self.gestor)
        resposta = self.client.get(reverse("estrutura:equipamento_lista"))
        self.assertEqual(list(resposta.context["object_list"]), [self.equip_tag])

    def test_gestor_ve_so_a_propria_unidade(self):
        self.client.force_login(self.gestor)
        resposta = self.client.get(reverse("estrutura:unidade_lista"))
        self.assertEqual(list(resposta.context["object_list"]), [self.taguatinga])

    def test_busca_filtra_listagem(self):
        self.client.force_login(self.admin)
        resposta = self.client.get(reverse("estrutura:equipamento_lista"), {"q": "quadro"})
        self.assertEqual(list(resposta.context["object_list"]), [self.equip_enn])

    # --- Acesso negado -----------------------------------------------------

    def test_tecnico_e_solicitante_nao_acessam_cadastros(self):
        for usuario in [self.tecnico, self.solicitante]:
            self.client.force_login(usuario)
            for rota in ["estrutura:unidade_lista", "estrutura:local_lista", "estrutura:equipamento_lista"]:
                with self.subTest(usuario=usuario.email, rota=rota):
                    self.assertEqual(self.client.get(reverse(rota)).status_code, 403)

    def test_gestor_nao_cria_nem_exclui_unidade(self):
        self.client.force_login(self.gestor)
        self.assertEqual(self.client.get(reverse("estrutura:unidade_nova")).status_code, 403)
        url = reverse("estrutura:unidade_excluir", args=[self.taguatinga.pk])
        self.assertEqual(self.client.post(url).status_code, 403)

    def test_gestor_nao_edita_registro_de_outra_unidade(self):
        self.client.force_login(self.gestor)
        urls = [
            reverse("estrutura:unidade_editar", args=[self.ennius.pk]),
            reverse("estrutura:local_editar", args=[self.local_enn.pk]),
            reverse("estrutura:equipamento_editar", args=[self.equip_enn.pk]),
            reverse("estrutura:equipamento_excluir", args=[self.equip_enn.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    # --- Cadastro ----------------------------------------------------------

    def test_gestor_cria_local_sempre_na_propria_unidade(self):
        self.client.force_login(self.gestor)
        self.client.post(reverse("estrutura:local_novo"), {
            "unidade": self.ennius.pk, "bloco": "C", "andar": "2º", "sala": "305", "tipo_ambiente": "LABORATORIO",
        })
        local = Local.objects.get(sala="305")
        self.assertEqual(local.unidade, self.taguatinga)

    def test_gestor_nao_cadastra_equipamento_em_local_de_outra_unidade(self):
        self.client.force_login(self.gestor)
        resposta = self.client.post(reverse("estrutura:equipamento_novo"), {
            "nome": "Bomba", "patrimonio": "X-9", "local": self.local_enn.pk,
        })
        self.assertEqual(resposta.status_code, 200)  # formulário volta com erro
        self.assertFalse(Equipamento.objects.filter(patrimonio="X-9").exists())

    def test_local_duplicado_na_mesma_unidade_e_recusado(self):
        self.client.force_login(self.gestor)
        resposta = self.client.post(reverse("estrutura:local_novo"), {
            "bloco": "A", "andar": "Térreo", "sala": "101", "tipo_ambiente": "SALA_AULA",
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Local.objects.filter(sala="101").count(), 1)

    def test_admin_cria_unidade(self):
        self.client.force_login(self.admin)
        resposta = self.client.post(reverse("estrutura:unidade_nova"), {"nome": "Gama", "ativa": "on"})
        self.assertRedirects(resposta, reverse("estrutura:unidade_lista"))
        self.assertTrue(Unidade.objects.filter(nome="Gama").exists())

    # --- Exclusão ----------------------------------------------------------

    def test_exclusao_protegida_mostra_mensagem(self):
        self.client.force_login(self.gestor)
        resposta = self.client.post(reverse("estrutura:local_excluir", args=[self.local_tag.pk]), follow=True)
        self.assertTrue(Local.objects.filter(pk=self.local_tag.pk).exists())
        self.assertContains(resposta, "não pode ser excluído")

    def test_gestor_exclui_equipamento_da_sua_unidade(self):
        self.client.force_login(self.gestor)
        self.client.post(reverse("estrutura:equipamento_excluir", args=[self.equip_tag.pk]))
        self.assertFalse(Equipamento.objects.filter(pk=self.equip_tag.pk).exists())
