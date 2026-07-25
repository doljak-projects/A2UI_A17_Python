# A2UI Backend

Backend em Python usando **FastAPI**. Por enquanto contém apenas a estrutura base
com um endpoint de health check.

## Requisitos

- Python 3.11+

## Setup

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
```

## Executar

```bash
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000/api/health
- Docs (Swagger): http://localhost:8000/docs

## Testes

```bash
pytest
```

## Estrutura

```
apps/backend/
├── app/
│   ├── api/
│   │   ├── router.py          # agregador de rotas
│   │   └── routes/
│   │       └── health.py      # endpoint /health
│   ├── core/
│   │   └── config.py          # settings (pydantic-settings)
│   ├── models/                # modelos de domínio / ORM (futuro)
│   ├── schemas/               # schemas Pydantic
│   │   └── health.py
│   ├── services/              # regras de negócio (futuro)
│   └── main.py                # criação da app FastAPI
└── tests/
    └── test_health.py
```
