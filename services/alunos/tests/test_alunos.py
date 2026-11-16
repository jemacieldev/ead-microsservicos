from datetime import date

import pytest

from app import criar_app
from domain import Aluno, RegraDeNegocioError


@pytest.fixture
def cliente():
    return criar_app().test_client()


# ---------- Testes de domínio ----------

def test_certificado_so_com_100_por_cento():
    aluno = Aluno(id=1, nome="João", email="joao@exemplo.com")
    aluno.matricular(10)
    aluno.atualizar_progresso(10, 80)
    with pytest.raises(RegraDeNegocioError):
        aluno.emitir_certificado(10)


def test_emite_certificado_ao_concluir():
    aluno = Aluno(id=1, nome="João", email="joao@exemplo.com")
    aluno.matricular(10)
    aluno.atualizar_progresso(10, 100)
    certificado = aluno.emitir_certificado(10, hoje=date(2026, 11, 16))
    assert certificado.to_dict() == {
        "aluno": "João",
        "curso_id": 10,
        "emitido_em": "2026-11-16",
    }


def test_progresso_fora_do_intervalo():
    aluno = Aluno(id=1, nome="João", email="joao@exemplo.com")
    aluno.matricular(10)
    with pytest.raises(RegraDeNegocioError):
        aluno.atualizar_progresso(10, 120)


# ---------- Testes da API ----------

def test_health(cliente):
    assert cliente.get("/health").get_json()["status"] == "ok"


def test_fluxo_matricula_progresso_certificado(cliente):
    novo = cliente.post("/alunos", json={"nome": "Ana", "email": "ana@exemplo.com"}).get_json()
    url = f"/alunos/{novo['id']}"
    assert cliente.post(f"{url}/matriculas", json={"curso_id": 1}).status_code == 201
    assert cliente.post(f"{url}/certificados/1").status_code == 422
    assert cliente.patch(f"{url}/matriculas/1", json={"progresso": 100}).status_code == 200
    assert cliente.post(f"{url}/certificados/1").status_code == 201


def test_email_invalido_retorna_422(cliente):
    resposta = cliente.post("/alunos", json={"nome": "Ana", "email": "sem-arroba"})
    assert resposta.status_code == 422
