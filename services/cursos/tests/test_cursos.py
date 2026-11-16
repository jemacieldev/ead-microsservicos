import pytest

from app import criar_app
from domain import Curso, Modulo, RegraDeNegocioError


@pytest.fixture
def cliente():
    return criar_app().test_client()


# ---------- Testes de domínio (unitários puros) ----------

def test_carga_horaria_e_a_soma_dos_modulos():
    curso = Curso(id=1, titulo="Python", professor="Prof. X")
    curso.adicionar_modulo(Modulo("Básico", 10))
    curso.adicionar_modulo(Modulo("Avançado", 20))
    assert curso.carga_horaria == 30


def test_nao_permite_modulo_duplicado():
    curso = Curso(id=1, titulo="Python", professor="Prof. X")
    curso.adicionar_modulo(Modulo("Básico", 10))
    with pytest.raises(RegraDeNegocioError):
        curso.adicionar_modulo(Modulo("Básico", 5))


def test_modulo_com_horas_invalidas():
    with pytest.raises(RegraDeNegocioError):
        Modulo("Vazio", 0)


# ---------- Testes da API ----------

def test_health(cliente):
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    assert resposta.get_json()["servico"] == "cursos"


def test_lista_cursos_iniciais(cliente):
    resposta = cliente.get("/cursos")
    assert resposta.status_code == 200
    assert resposta.get_json()[0]["carga_horaria"] == 14


def test_cria_curso(cliente):
    resposta = cliente.post("/cursos", json={"titulo": "Cloud", "professor": "Prof. Y"})
    assert resposta.status_code == 201
    assert resposta.get_json()["titulo"] == "Cloud"


def test_curso_sem_titulo_retorna_422(cliente):
    resposta = cliente.post("/cursos", json={"titulo": "", "professor": "Prof. Y"})
    assert resposta.status_code == 422


def test_curso_inexistente_retorna_404(cliente):
    assert cliente.get("/cursos/999").status_code == 404
