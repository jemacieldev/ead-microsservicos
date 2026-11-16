"""Bounded Context: Gestão de Alunos (matrícula, progresso e certificação)."""
from dataclasses import dataclass, field
from datetime import date


class RegraDeNegocioError(ValueError):
    """Erro levantado quando uma regra do domínio é violada."""


@dataclass(frozen=True)
class Certificado:
    """Objeto de Valor: documento imutável que valida a conclusão de um curso."""

    aluno: str
    curso_id: int
    emitido_em: date

    def to_dict(self) -> dict:
        return {
            "aluno": self.aluno,
            "curso_id": self.curso_id,
            "emitido_em": self.emitido_em.isoformat(),
        }


@dataclass
class Aluno:
    """Entidade: identificada pelo id e responsável pelas próprias matrículas."""

    id: int
    nome: str
    email: str
    progresso: dict[int, int] = field(default_factory=dict)  # curso_id -> % concluído

    def matricular(self, curso_id: int) -> None:
        if curso_id in self.progresso:
            raise RegraDeNegocioError("Aluno já matriculado neste curso.")
        self.progresso[curso_id] = 0

    def atualizar_progresso(self, curso_id: int, percentual: int) -> None:
        if curso_id not in self.progresso:
            raise RegraDeNegocioError("Aluno não está matriculado neste curso.")
        if not 0 <= percentual <= 100:
            raise RegraDeNegocioError("O progresso deve estar entre 0 e 100.")
        self.progresso[curso_id] = percentual

    def emitir_certificado(self, curso_id: int, hoje: date | None = None) -> Certificado:
        # Regra de negócio central do contexto: só certifica quem concluiu 100%.
        if self.progresso.get(curso_id) != 100:
            raise RegraDeNegocioError("Certificado disponível apenas com 100% de conclusão.")
        return Certificado(self.nome, curso_id, hoje or date.today())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "matriculas": [
                {"curso_id": c, "progresso": p} for c, p in self.progresso.items()
            ],
        }


class RepositorioAlunos:
    """Repositório em memória do contexto de Alunos."""

    def __init__(self):
        self._alunos: dict[int, Aluno] = {}
        self._proximo_id = 1

    def criar(self, nome: str, email: str) -> Aluno:
        if "@" not in email:
            raise RegraDeNegocioError("E-mail inválido.")
        aluno = Aluno(id=self._proximo_id, nome=nome, email=email)
        self._alunos[aluno.id] = aluno
        self._proximo_id += 1
        return aluno

    def buscar(self, aluno_id: int) -> Aluno | None:
        return self._alunos.get(aluno_id)

    def listar(self) -> list[Aluno]:
        return list(self._alunos.values())
