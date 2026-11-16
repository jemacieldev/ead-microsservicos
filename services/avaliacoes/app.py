"""Microsserviço de Avaliações — camada de aplicação/API (Flask)."""
from flask import Flask, jsonify, request

from domain import RegraDeNegocioError, RepositorioAvaliacoes, calcular_situacao


def criar_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False  # mantém acentos legíveis no JSON
    repo = RepositorioAvaliacoes()

    # Dados iniciais para demonstração
    repo.registrar(aluno_id=1, curso_id=1, descricao="Prova 1", nota=8.5)
    repo.registrar(aluno_id=1, curso_id=1, descricao="Trabalho final", nota=9.0)

    @app.get("/health")
    def health():
        return jsonify(servico="avaliacoes", status="ok")

    @app.post("/avaliacoes")
    def registrar():
        dados = request.get_json(silent=True) or {}
        try:
            avaliacao = repo.registrar(
                aluno_id=int(dados.get("aluno_id", 0)),
                curso_id=int(dados.get("curso_id", 0)),
                descricao=dados.get("descricao", "Avaliação"),
                nota=float(dados.get("nota", -1)),
            )
        except RegraDeNegocioError as e:
            return jsonify(erro=str(e)), 422
        return jsonify(avaliacao.to_dict()), 201

    @app.get("/avaliacoes/aluno/<int:aluno_id>")
    def boletim(aluno_id: int):
        avaliacoes = repo.do_aluno(aluno_id)
        return jsonify(
            aluno_id=aluno_id,
            avaliacoes=[a.to_dict() for a in avaliacoes],
            **calcular_situacao(avaliacoes),
        )

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
