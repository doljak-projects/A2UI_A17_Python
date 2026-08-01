---
issue: 1
title: "BE: Configurar provedor LLM via .env e pydantic-settings"
branch: chore/1-llm-config-via-env-and-pydantic-settings
status: closed
last_updated: 07-25-2026
---

# Issue #1 — Configurar provedor LLM via .env e pydantic-settings

## Status
Feita — configuração do provedor LLM integrada ao `Settings` com validação e testes.

## O que foi feito
- Adicionados campos em `Settings` (`app/core/config.py`): `llm_provider` (`openai|anthropic`), `llm_api_key` (`SecretStr`, obrigatório), `llm_model` (obrigatório), `llm_temperature` (0.0–2.0, default 0.7), `llm_max_tokens` (>0, default 1024).
- Validators Pydantic garantindo `llm_api_key`/`llm_model` presentes e não vazios na inicialização; provider restrito via `Literal`.
- `.env.example` atualizado com as novas variáveis (`LLM_*`), sem chave real.
- `tests/conftest.py` fornece credenciais fictícias para importar a app sem `.env`.
- `tests/test_config.py` cobre: carga da config de LLM, exigência de key/model, e rejeição de provider inválido.

## Como rastrear
- Branch: `chore/1-llm-config-via-env-and-pydantic-settings`
- Worktree: `1-worktree-llm-config`
- Arquivos principais: `apps/backend/app/core/config.py`, `apps/backend/.env.example`, `apps/backend/tests/conftest.py`, `apps/backend/tests/test_config.py`

## Notes
- `llm_api_key` usa `SecretStr` para evitar vazamento em logs/repr.
- Critério de conclusão atendido: `settings.llm_api_key` e `settings.llm_model` disponíveis e testados (4 testes passando).
