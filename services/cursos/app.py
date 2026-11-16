"""Microsserviço de Cursos — camada de aplicação/API (Flask)."""
from flask import Flask, jsonify, request

from domain import Modulo, RegraDeNegocioError, RepositorioCursos


def criar_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False  # mantém acentos legíveis no JSON
    repo = RepositorioCursos()

    # Dados iniciais para demonstração
    curso = repo.criar("Desenvolvimento de Microsserviços", "Prof. Ana Souza")
    curso.adicionar_modulo(Modulo("Introdução ao DDD", 8))
    curso.adicionar_modulo(Modulo("API Gateway", 6))

    @app.get("/health")
    def health():
        return jsonify(servico="cursos", status="ok")

    @app.get("/cursos")
    def listar():
        return jsonify([c.to_dict() for c in repo.listar()])

    @app.get("/cursos/<int:curso_id>")
    def buscar(curso_id: int):
        curso = repo.buscar(curso_id)
        if curso is None:
            return jsonify(erro="Curso não encontrado"), 404
        return jsonify(curso.to_dict())

    @app.post("/cursos")
    def criar():
        dados = request.get_json(silent=True) or {}
        try:
            novo = repo.criar(dados.get("titulo", ""), dados.get("professor", ""))
        except RegraDeNegocioError as erro:
            return jsonify(erro=str(erro)), 422
        return jsonify(novo.to_dict()), 201

    @app.post("/cursos/<int:curso_id>/modulos")
    def adicionar_modulo(curso_id: int):
        curso = repo.buscar(curso_id)
        if curso is None:
            return jsonify(erro="Curso não encontrado"), 404
        dados = request.get_json(silent=True) or {}
        try:
            curso.adicionar_modulo(Modulo(dados.get("titulo", ""), int(dados.get("horas", 0))))
        except RegraDeNegocioError as erro:
            return jsonify(erro=str(erro)), 422
        return jsonify(curso.to_dict()), 201

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
