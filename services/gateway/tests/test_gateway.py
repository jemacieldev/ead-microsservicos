"""Testes do API Gateway com os microsserviços simulados (mocks)."""
import pytest
import requests

import app as gateway


class RespostaFalsa:
    def __init__(self, status_code=200, dados=None):
        self.status_code = status_code
        self._dados = dados or {}
        self.ok = status_code < 400
        self.content = b'{"fake": true}'
        self.headers = {"Content-Type": "application/json"}

    def json(self):
        return self._dados


@pytest.fixture
def cliente():
    return gateway.criar_app().test_client()


def test_health_com_todos_os_servicos_ok(cliente, monkeypatch):
    monkeypatch.setattr(requests, "get", lambda url, timeout: RespostaFalsa(200))
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    assert resposta.get_json()["status"] == "ok"


def test_health_degradado_quando_um_servico_cai(cliente, monkeypatch):
    def get_falso(url, timeout):
        if "5003" in url:  # avaliacoes fora do ar
            raise requests.ConnectionError()
        return RespostaFalsa(200)

    monkeypatch.setattr(requests, "get", get_falso)
    resposta = cliente.get("/health")
    assert resposta.status_code == 503
    assert resposta.get_json()["servicos"]["avaliacoes"] == "indisponivel"


def test_roteia_para_o_servico_correto(cliente, monkeypatch):
    chamadas = []

    def request_falso(metodo, url, **kwargs):
        chamadas.append((metodo, url))
        return RespostaFalsa(200)

    monkeypatch.setattr(requests, "request", request_falso)
    resposta = cliente.get("/api/cursos/1")
    assert resposta.status_code == 200
    assert chamadas == [("GET", "http://localhost:5001/cursos/1")]


def test_servico_desconhecido_retorna_404(cliente):
    assert cliente.get("/api/financeiro").status_code == 404


def test_servico_fora_do_ar_retorna_503(cliente, monkeypatch):
    def request_falha(*args, **kwargs):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "request", request_falha)
    assert cliente.get("/api/alunos").status_code == 503


def test_painel_compoe_alunos_e_avaliacoes(cliente, monkeypatch):
    def get_falso(url, timeout):
        if "/alunos/" in url:
            return RespostaFalsa(200, {"id": 1, "nome": "Maria Oliveira"})
        return RespostaFalsa(200, {"media": 8.75, "situacao": "aprovado"})

    monkeypatch.setattr(requests, "get", get_falso)
    dados = cliente.get("/api/painel/1").get_json()
    assert dados == {
        "aluno": {"id": 1, "nome": "Maria Oliveira"},
        "media": 8.75,
        "situacao": "aprovado",
    }
