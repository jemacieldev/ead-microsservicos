import pytest

from app import criar_app
from domain import Avaliacao, Nota, RegraDeNegocioError, calcular_situacao


@pytest.fixture
def cliente():
    return criar_app().test_client()


# ---------- Testes de domínio ----------

def test_nota_fora_do_intervalo():
    with pytest.raises(RegraDeNegocioError):
        Nota(11)


def test_situacao_aprovado_e_reprovado():
    aprovado = [Avaliacao(1, 1, 1, "P1", Nota(7)), Avaliacao(2, 1, 1, "P2", Nota(6))]
    reprovado = [Avaliacao(3, 2, 1, "P1", Nota(4))]
    assert calcular_situacao(aprovado) == {"media": 6.5, "situacao": "aprovado"}
    assert calcular_situacao(reprovado)["situacao"] == "reprovado"


def test_sem_avaliacoes():
    assert calcular_situacao([])["situacao"] == "sem avaliações"


# ---------- Testes da API ----------

def test_health(cliente):
    assert cliente.get("/health").status_code == 200


def test_boletim_do_aluno_inicial(cliente):
    dados = cliente.get("/avaliacoes/aluno/1").get_json()
    assert dados["media"] == 8.75
    assert dados["situacao"] == "aprovado"


def test_registrar_nota_invalida_retorna_422(cliente):
    resposta = cliente.post("/avaliacoes", json={"aluno_id": 1, "curso_id": 1, "nota": 15})
    assert resposta.status_code == 422
