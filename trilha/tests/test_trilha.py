from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from trilha.models import Material

SENHA = "senha-de-teste-123"


def criar_usuario(email):
    return get_user_model().objects.create_user(username=email, email=email, password=SENHA)


class CadastroELoginTests(TestCase):
    def test_cadastro_cria_conta_e_ja_entra(self):
        resposta = self.client.post(
            reverse("trilha:cadastro"),
            {"email": "Ana@Exemplo.com", "password1": SENHA, "password2": SENHA},
        )
        self.assertRedirects(resposta, reverse("trilha:minha_trilha"))
        usuario = get_user_model().objects.get()
        self.assertEqual(usuario.username, "ana@exemplo.com")
        self.assertEqual(usuario.email, "ana@exemplo.com")
        self.assertEqual(int(self.client.session["_auth_user_id"]), usuario.pk)

    def test_cadastro_recusa_email_repetido(self):
        criar_usuario("ana@exemplo.com")
        resposta = self.client.post(
            reverse("trilha:cadastro"),
            {"email": "ANA@exemplo.com", "password1": SENHA, "password2": SENHA},
        )
        self.assertContains(resposta, "Já existe uma conta com este e-mail.")
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_login_com_email(self):
        criar_usuario("ana@exemplo.com")
        resposta = self.client.post(
            reverse("trilha:entrar"), {"username": "Ana@exemplo.com", "password": SENHA}
        )
        self.assertRedirects(resposta, reverse("trilha:minha_trilha"))

    def test_minha_trilha_exige_login(self):
        resposta = self.client.get(reverse("trilha:minha_trilha"))
        self.assertRedirects(
            resposta, f"{reverse('trilha:entrar')}?next={reverse('trilha:minha_trilha')}"
        )


class MaterialTests(TestCase):
    def setUp(self):
        self.ana = criar_usuario("ana@exemplo.com")
        self.client.force_login(self.ana)

    def test_criar_material_e_progresso_persistem(self):
        resposta = self.client.post(
            reverse("trilha:novo"), {"titulo": "Clean Code", "autor": "Robert C. Martin", "progresso": 30}
        )
        self.assertRedirects(resposta, reverse("trilha:minha_trilha"))
        material = Material.objects.get()
        self.assertEqual((material.usuario, material.progresso), (self.ana, 30))

        # "Fechar o navegador e entrar de novo": sessão nova, mesmo usuário.
        self.client.logout()
        self.client.force_login(self.ana)
        resposta = self.client.get(reverse("trilha:minha_trilha"))
        self.assertContains(resposta, "Clean Code")
        self.assertContains(resposta, "30% · em andamento")

    def test_progresso_acima_de_100_e_recusado(self):
        resposta = self.client.post(reverse("trilha:novo"), {"titulo": "Livro", "progresso": 130})
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(Material.objects.exists())

    def test_atualizar_progresso(self):
        material = Material.objects.create(usuario=self.ana, titulo="Clean Code", progresso=30)
        self.client.post(
            reverse("trilha:editar", args=(material.pk,)), {"titulo": "Clean Code", "progresso": 100}
        )
        material.refresh_from_db()
        self.assertEqual(material.progresso, 100)
        self.assertEqual(material.situacao, "concluído")

    def test_resumo_calcula_media_do_progresso(self):
        for titulo, progresso in [("A", 0), ("B", 50), ("C", 100)]:
            Material.objects.create(usuario=self.ana, titulo=titulo, progresso=progresso)
        resumo = self.client.get(reverse("trilha:minha_trilha")).context["resumo"]
        self.assertEqual(resumo["total"], 3)
        self.assertEqual(resumo["media"], 50)
        self.assertEqual(resumo["concluidos"], 1)
        self.assertEqual(resumo["nao_comecados"], 1)

    def test_excluir_material(self):
        material = Material.objects.create(usuario=self.ana, titulo="Clean Code")
        self.client.post(reverse("trilha:excluir", args=(material.pk,)))
        self.assertFalse(Material.objects.exists())


class IsolamentoPorUsuarioTests(TestCase):
    def setUp(self):
        self.ana = criar_usuario("ana@exemplo.com")
        self.bruno = criar_usuario("bruno@exemplo.com")
        self.material_da_ana = Material.objects.create(usuario=self.ana, titulo="Clean Code", progresso=30)
        self.client.force_login(self.bruno)

    def test_segunda_conta_nao_ve_material_da_primeira(self):
        resposta = self.client.get(reverse("trilha:minha_trilha"))
        self.assertNotContains(resposta, "Clean Code")
        self.assertEqual(resposta.context["resumo"]["total"], 0)

    def test_segunda_conta_nao_edita_nem_exclui_material_da_primeira(self):
        pk = self.material_da_ana.pk
        self.assertEqual(self.client.get(reverse("trilha:editar", args=(pk,))).status_code, 404)
        self.assertEqual(
            self.client.post(reverse("trilha:editar", args=(pk,)), {"titulo": "X", "progresso": 0}).status_code,
            404,
        )
        self.assertEqual(self.client.post(reverse("trilha:excluir", args=(pk,))).status_code, 404)
        self.material_da_ana.refresh_from_db()
        self.assertEqual(self.material_da_ana.titulo, "Clean Code")
