# Plataforma EAD — Microsserviços com DDD + API Gateway

![CI/CD](https://github.com/jemacieldev/ead-microsservicos/actions/workflows/ci-cd.yml/badge.svg)

Projeto acadêmico da disciplina **Desenvolvimento de Serviços e Microsserviços** (Centro Universitário Belas Artes).
Case 7 da Atividade 01: **Sistema de Gestão de Educação à Distância (EAD)**.

## Arquitetura

- **Planejamento da solução: DDD (Domain Driven Design).** Cada *bounded context* do case virou um microsserviço independente, com suas próprias entidades e objetos de valor.
- **Estilo arquitetural: API Gateway.** O cliente fala com um único ponto de entrada, que roteia, compõe respostas e trata falhas.

```
             Cliente (site / app)
                     │
             ┌───────▼────────┐
             │  API Gateway   │  :8000  roteamento · composição · health check
             └──┬─────┬─────┬─┘
        ┌───────┘     │     └────────┐
 ┌──────▼─────┐ ┌─────▼──────┐ ┌─────▼───────┐
 │   Cursos   │ │   Alunos   │ │ Avaliações  │
 │ Curso (E)  │ │ Aluno (E)  │ │ Avaliação(E)│
 │ Módulo(VO) │ │Certificado │ │  Nota (VO)  │
 └────────────┘ │    (VO)    │ └─────────────┘
                └────────────┘
 E = Entidade · VO = Objeto de Valor
```

| Serviço | Bounded context | Principais rotas (via gateway) |
|---|---|---|
| `cursos` | Gestão de Cursos | `GET /api/cursos`, `POST /api/cursos` |
| `alunos` | Gestão de Alunos | `POST /api/alunos/{id}/matriculas`, `POST /api/alunos/{id}/certificados/{curso}` |
| `avaliacoes` | Avaliação de Desempenho | `POST /api/avaliacoes`, `GET /api/avaliacoes/aluno/{id}` |
| `gateway` | API Gateway | `GET /health`, `GET /api/painel/{aluno_id}` (composição) |

## Workflow de CI/CD (`.github/workflows/ci-cd.yml`)

1. **Lint + testes** de cada serviço em paralelo (ruff + pytest), com relatório salvo como artefato.
2. **Teste de integração**: sobe os 4 containers com Docker Compose e testa as rotas pelo gateway.
3. **Publicação**: só na branch `main`, gera as imagens Docker e publica no GitHub Container Registry.

## Como rodar

```bash
# Com Docker
docker compose up --build
curl http://localhost:8000/health
curl http://localhost:8000/api/painel/1

# Sem Docker (um terminal por serviço)
cd services/cursos      && pip install -r requirements.txt && flask --app app run --port 5001
cd services/alunos      && flask --app app run --port 5002
cd services/avaliacoes  && flask --app app run --port 5003
cd services/gateway     && pip install -r requirements.txt && flask --app app run --port 8000

# Testes de um serviço
cd services/alunos && pip install -r requirements-dev.txt && pytest -v
```

## Referências pesquisadas no GitHub

- [GoogleCloudPlatform/microservices-demo](https://github.com/GoogleCloudPlatform/microservices-demo) — aplicação de referência com vários microsserviços, containers e CI.
- [microservices-patterns/ftgo-application](https://github.com/microservices-patterns/ftgo-application) — exemplo do livro *Microservices Patterns* (Chris Richardson), incluindo API Gateway.
- [Padrão API Gateway — microservices.io](https://microservices.io/patterns/apigateway.html)
