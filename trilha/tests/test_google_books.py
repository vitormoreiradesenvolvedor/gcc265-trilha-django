from unittest import mock

import requests
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from trilha.google_books import BuscaIndisponivel, buscar_livros


def resposta_falsa(json=None, status=200):
    resposta = mock.Mock(status_code=status)
    resposta.json.return_value = json
    if status >= 400:
        resposta.raise_for_status.side_effect = requests.HTTPError(f"{status}")
    return resposta


class BuscarLivrosTests(SimpleTestCase):
    @mock.patch("trilha.google_books.requests.get")
    def test_extrai_titulo_e_autores(self, get):
        get.return_value = resposta_falsa({"items": [
            {"volumeInfo": {"title": "Clean Code", "subtitle": "A Handbook of Agile Software Craftsmanship",
                            "authors": ["Robert C. Martin"]}},
            {"volumeInfo": {"title": "Refactoring", "authors": ["Martin Fowler", "Kent Beck"]}},
        ]})
        self.assertEqual(buscar_livros("clean code"), [
            {"titulo": "Clean Code: A Handbook of Agile Software Craftsmanship", "autor": "Robert C. Martin"},
            {"titulo": "Refactoring", "autor": "Martin Fowler, Kent Beck"},
        ])
        self.assertEqual(get.call_args.kwargs["params"]["q"], "clean code")

    @mock.patch("trilha.google_books.requests.get")
    def test_campos_ausentes_nao_quebram(self, get):
        get.return_value = resposta_falsa({"items": [
            {"volumeInfo": {"title": "Sem autor"}},
            {"volumeInfo": {"authors": ["Sem título"]}},
            {},
        ]})
        self.assertEqual(buscar_livros("x"), [{"titulo": "Sem autor", "autor": ""}])

    @mock.patch("trilha.google_books.requests.get")
    def test_sem_resultados(self, get):
        get.return_value = resposta_falsa({})
        self.assertEqual(buscar_livros("xyzxyz"), [])

    @mock.patch("trilha.google_books.requests.get")
    def test_termo_vazio_nem_consulta(self, get):
        self.assertEqual(buscar_livros("   "), [])
        get.assert_not_called()

    @mock.patch("trilha.google_books.requests.get")
    def test_cota_esgotada_vira_busca_indisponivel(self, get):
        get.return_value = resposta_falsa({"error": {"code": 429}}, status=429)
        with self.assertRaises(BuscaIndisponivel):
            buscar_livros("clean code")

    @mock.patch("trilha.google_books.requests.get", side_effect=requests.Timeout("lento"))
    def test_timeout_vira_busca_indisponivel(self, get):
        with self.assertRaises(BuscaIndisponivel):
            buscar_livros("clean code")

    @mock.patch.dict("os.environ", {"GOOGLE_BOOKS_API_KEY": "chave-teste"})
    @mock.patch("trilha.google_books.requests.get")
    def test_chave_vai_na_consulta_quando_definida(self, get):
        get.return_value = resposta_falsa({})
        buscar_livros("clean code")
        self.assertEqual(get.call_args.kwargs["params"]["key"], "chave-teste")


class BuscarViewTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(username="ana@exemplo.com", password="x")
        self.client.force_login(usuario)

    @mock.patch("trilha.views.buscar_livros", return_value=[{"titulo": "Clean Code", "autor": "Robert C. Martin"}])
    def test_devolve_json(self, buscar):
        resposta = self.client.get(reverse("trilha:buscar"), {"q": "clean code"})
        self.assertEqual(resposta.json(), {"resultados": [{"titulo": "Clean Code", "autor": "Robert C. Martin"}]})

    @mock.patch("trilha.views.buscar_livros", side_effect=BuscaIndisponivel("429"))
    def test_falha_devolve_503_com_mensagem(self, buscar):
        resposta = self.client.get(reverse("trilha:buscar"), {"q": "clean code"})
        self.assertEqual(resposta.status_code, 503)
        self.assertIn("manualmente", resposta.json()["erro"])

    def test_exige_login(self):
        self.client.logout()
        resposta = self.client.get(reverse("trilha:buscar"), {"q": "x"})
        self.assertEqual(resposta.status_code, 302)
