"""Bounded Context: Gestão de Cursos.

Camada de domínio (DDD): regras de negócio sem dependência de framework web.
"""
from dataclasses import dataclass, field


class RegraDeNegocioError(ValueError):
    """Erro levantado quando uma regra do domínio é violada."""


@dataclass(frozen=True)
class Modulo:
    """Objeto de Valor: identificado pelos seus atributos, não por um id."""

    titulo: str
    horas: int

    def __post_init__(self):
        if not self.titulo.strip():
            raise RegraDeNegocioError("O módulo precisa de um título.")
        if self.horas <= 0:
            raise RegraDeNegocioError("A carga horária do módulo deve ser positiva.")


@dataclass
class Curso:
    """Entidade: tem identidade própria (id) e ciclo de vida."""

    id: int
    titulo: str
    professor: str
    modulos: list[Modulo] = field(default_factory=list)

    @property
    def carga_horaria(self) -> int:
        return sum(m.horas for m in self.modulos)

    def adicionar_modulo(self, modulo: Modulo) -> None:
        if any(m.titulo == modulo.titulo for m in self.modulos):
            raise RegraDeNegocioError("Já existe um módulo com esse título no curso.")
        self.modulos.append(modulo)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "professor": self.professor,
            "carga_horaria": self.carga_horaria,
            "modulos": [{"titulo": m.titulo, "horas": m.horas} for m in self.modulos],
        }


class RepositorioCursos:
    """Repositório em memória (em produção seria um banco de dados próprio do serviço)."""

    def __init__(self):
        self._cursos: dict[int, Curso] = {}
        self._proximo_id = 1

    def criar(self, titulo: str, professor: str) -> Curso:
        if not titulo.strip():
            raise RegraDeNegocioError("O curso precisa de um título.")
        curso = Curso(id=self._proximo_id, titulo=titulo, professor=professor)
        self._cursos[curso.id] = curso
        self._proximo_id += 1
        return curso

    def buscar(self, curso_id: int) -> Curso | None:
        return self._cursos.get(curso_id)

    def listar(self) -> list[Curso]:
        return list(self._cursos.values())
