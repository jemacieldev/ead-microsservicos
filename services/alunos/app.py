"""Microsserviço de Alunos — camada de aplicação/API (Flask)."""
from flask import Flask, jsonify, request

from domain import RegraDeNegocioError, RepositorioAlunos


def criar_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False  # mantém acentos legíveis no JSON
    repo = RepositorioAlunos()

    # Dados iniciais para demonstração
    aluno = repo.criar("Maria Oliveira", "maria@exemplo.com")
    aluno.matricular(1)
    aluno.atualizar_progresso(1, 100)

    def obter_aluno(aluno_id: int):
        aluno = repo.buscar(aluno_id)
        if aluno is None:
            return None, (jsonify(erro="Aluno não encontrado"), 404)
        return aluno, None

    @app.get("/health")
    def health():
        return jsonify(servico="alunos", status="ok")

    @app.get("/alunos")
    def listar():
        return jsonify([a.to_dict() for a in repo.listar()])

    @app.get("/alunos/<int:aluno_id>")
    def buscar(aluno_id: int):
        aluno, erro = obter_aluno(aluno_id)
        return erro or jsonify(aluno.to_dict())

    @app.post("/alunos")
    def criar():
        dados = request.get_json(silent=True) or {}
        try:
            novo = repo.criar(dados.get("nome", ""), dados.get("email", ""))
        except RegraDeNegocioError as e:
            return jsonify(erro=str(e)), 422
        return jsonify(novo.to_dict()), 201

    @app.post("/alunos/<int:aluno_id>/matriculas")
    def matricular(aluno_id: int):
        aluno, erro = obter_aluno(aluno_id)
        if erro:
            return erro
        dados = request.get_json(silent=True) or {}
        try:
            aluno.matricular(int(dados.get("curso_id", 0)))
        except RegraDeNegocioError as e:
            return jsonify(erro=str(e)), 422
        return jsonify(aluno.to_dict()), 201

    @app.patch("/alunos/<int:aluno_id>/matriculas/<int:curso_id>")
    def atualizar_progresso(aluno_id: int, curso_id: int):
        aluno, erro = obter_aluno(aluno_id)
        if erro:
            return erro
        dados = request.get_json(silent=True) or {}
        try:
            aluno.atualizar_progresso(curso_id, int(dados.get("progresso", -1)))
        except RegraDeNegocioError as e:
            return jsonify(erro=str(e)), 422
        return jsonify(aluno.to_dict())

    @app.post("/alunos/<int:aluno_id>/certificados/<int:curso_id>")
    def emitir_certificado(aluno_id: int, curso_id: int):
        aluno, erro = obter_aluno(aluno_id)
        if erro:
            return erro
        try:
            certificado = aluno.emitir_certificado(curso_id)
        except RegraDeNegocioError as e:
            return jsonify(erro=str(e)), 422
        return jsonify(certificado.to_dict()), 201

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
