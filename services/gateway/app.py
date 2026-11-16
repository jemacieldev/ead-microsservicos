"""API Gateway da plataforma EAD.

Ponto único de entrada para o cliente (site/app). Responsabilidades:
  1. Roteamento: /api/<servico>/... -> microsserviço correspondente.
  2. Composição: /api/painel/<aluno_id> junta dados de Alunos + Avaliações.
  3. Resiliência: timeout e resposta 503 quando um serviço está fora do ar.
  4. Health check agregado de todos os serviços.
"""
import os

import requests
from flask import Flask, Response, jsonify, request

TIMEOUT_SEGUNDOS = 3


def criar_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False  # mantém acentos legíveis no JSON
    servicos = {
        "cursos": os.getenv("CURSOS_URL", "http://localhost:5001"),
        "alunos": os.getenv("ALUNOS_URL", "http://localhost:5002"),
        "avaliacoes": os.getenv("AVALIACOES_URL", "http://localhost:5003"),
    }

    @app.get("/health")
    def health():
        estado = {}
        for nome, url in servicos.items():
            try:
                ok = requests.get(f"{url}/health", timeout=TIMEOUT_SEGUNDOS).ok
            except requests.RequestException:
                ok = False
            estado[nome] = "ok" if ok else "indisponivel"
        geral = "ok" if all(v == "ok" for v in estado.values()) else "degradado"
        return jsonify(gateway="ok", status=geral, servicos=estado), (200 if geral == "ok" else 503)

    @app.route("/api/<servico>", defaults={"caminho": ""}, methods=["GET", "POST", "PATCH"])
    @app.route("/api/<servico>/<path:caminho>", methods=["GET", "POST", "PATCH"])
    def rotear(servico: str, caminho: str):
        if servico not in servicos:
            return jsonify(erro=f"Serviço '{servico}' não existe"), 404
        destino = f"{servicos[servico]}/{servico}" + (f"/{caminho}" if caminho else "")
        try:
            resposta = requests.request(
                request.method,
                destino,
                json=request.get_json(silent=True),
                params=request.args,
                timeout=TIMEOUT_SEGUNDOS,
            )
        except requests.RequestException:
            return jsonify(erro=f"Serviço '{servico}' indisponível"), 503
        return Response(
            resposta.content,
            status=resposta.status_code,
            content_type=resposta.headers.get("Content-Type", "application/json"),
        )

    @app.get("/api/painel/<int:aluno_id>")
    def painel_do_aluno(aluno_id: int):
        """Composição de APIs: uma chamada do cliente, duas chamadas internas."""
        try:
            aluno = requests.get(
                f"{servicos['alunos']}/alunos/{aluno_id}", timeout=TIMEOUT_SEGUNDOS
            )
            if aluno.status_code == 404:
                return jsonify(erro="Aluno não encontrado"), 404
            boletim = requests.get(
                f"{servicos['avaliacoes']}/avaliacoes/aluno/{aluno_id}",
                timeout=TIMEOUT_SEGUNDOS,
            )
        except requests.RequestException:
            return jsonify(erro="Não foi possível montar o painel agora"), 503
        dados_boletim = boletim.json()
        return jsonify(
            aluno=aluno.json(),
            media=dados_boletim.get("media"),
            situacao=dados_boletim.get("situacao"),
        )

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
