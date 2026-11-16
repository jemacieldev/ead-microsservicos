"""Bounded Context: Avaliação de Desempenho (provas, notas e aprovação)."""
from dataclasses import dataclass

MEDIA_MINIMA = 6.0


class RegraDeNegocioError(ValueError):
    """Erro levantado quando uma regra do domínio é violada."""


@dataclass(frozen=True)
class Nota:
    """Objeto de Valor: uma nota só é válida entre 0 e 10."""

    valor: float

    def __post_init__(self):
        if not 0 <= self.valor <= 10:
            raise RegraDeNegocioError("A nota deve estar entre 0 e 10.")


@dataclass
class Avaliacao:
    """Entidade: uma prova/trabalho realizado por um aluno em um curso."""

    id: int
    aluno_id: int
    curso_id: int
    descricao: str
    nota: Nota

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "aluno_id": self.aluno_id,
            "curso_id": self.curso_id,
            "descricao": self.descricao,
            "nota": self.nota.valor,
        }


def calcular_situacao(avaliacoes: list[Avaliacao]) -> dict:
    """Serviço de domínio: calcula média e situação do aluno."""
    if not avaliacoes:
        return {"media": None, "situacao": "sem avaliações"}
    media = round(sum(a.nota.valor for a in avaliacoes) / len(avaliacoes), 2)
    return {"media": media, "situacao": "aprovado" if media >= MEDIA_MINIMA else "reprovado"}


class RepositorioAvaliacoes:
    """Repositório em memória do contexto de Avaliações."""

    def __init__(self):
        self._avaliacoes: list[Avaliacao] = []

    def registrar(self, aluno_id: int, curso_id: int, descricao: str, nota: float) -> Avaliacao:
        avaliacao = Avaliacao(len(self._avaliacoes) + 1, aluno_id, curso_id, descricao, Nota(nota))
        self._avaliacoes.append(avaliacao)
        return avaliacao

    def do_aluno(self, aluno_id: int) -> list[Avaliacao]:
        return [a for a in self._avaliacoes if a.aluno_id == aluno_id]
