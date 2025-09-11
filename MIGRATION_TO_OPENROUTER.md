## OpenAI → OpenRouter Migration Guide

This document explains exactly how the codebase was migrated from OpenAI’s API to OpenRouter, while preserving OpenAI-related code as comments and maintaining OpenAI‑compatible endpoints for tooling like Open WebUI.

### Goals
- Switch LLM backend to OpenRouter.
- Keep OpenAI code paths commented out (do not delete).
- Maintain OpenAI‑compatible HTTP endpoints for clients (e.g., Open WebUI).
- Ensure minimal changes and avoid breaking existing workflows.

---

## High-level Architecture

- The app exposes first‑party REST endpoints and OpenAI‑compatible endpoints.
- LLM access is abstracted behind `BaseLLMProvider`. Concrete providers:
  - `OpenRouterProvider` (active)
  - `OpenAIProvider` (preserved but disabled/commented out)
- A factory (`LLMFactory`) selects the active provider based on settings.
- Medical workflow uses an OpenAI‑agents compatible runtime with a compatibility layer tuned for OpenRouter responses.

---

## Configuration Changes

File: `backend/app/core/config.py`
- OpenAI key setting is commented out.
- OpenRouter settings are the source of truth.

Key settings:
```python
openrouter_api_key: Optional[str] = None
openrouter_base_url: str = "https://openrouter.ai/api/v1"
default_llm_model: str = "openai/gpt-4o-mini"
default_llm_provider: str = "openrouter"
```

Environment files supported via `model_config.env_file` and Docker Compose variables (see below).

---

## Provider Factory

File: `backend/app/services/llm/factory.py`
- OpenAI branch is commented out (left in place for reference).
- OpenRouter branch is active and validated:
  - Reads API key from `openrouter_api_key` (or explicit param).
  - Constructs `OpenRouterProvider(api_key, base_url, default_model)`.
  - Raises configuration errors if missing.

---

## OpenRouter Provider

File: `backend/app/services/llm/openrouter.py`
- Uses `openai.AsyncOpenAI` client pointed at `openrouter_base_url`.
- Implements both `generate()` and `stream()`.
- Supports OpenRouter‑specific headers (optional):
  - `HTTP-Referer` via `http_referer` kwarg
  - `X-Title` via `x_title` kwarg

Core call path:
```python
await self.client.chat.completions.create(
  model=model or self.default_model,
  messages=self.format_messages(messages),
  temperature=temperature,
  max_tokens=max_tokens,
  extra_headers=extra_headers,
  **kwargs,
)
```

Streaming path mirrors the above with `stream=True` and incremental token yields.

---

## OpenAI Provider (Preserved, Disabled)

File: `backend/app/services/llm/openai.py`
- All imports and logic retained but commented out per request.
- Methods now raise `NotImplementedError` with guidance to use OpenRouter.

This prevents accidental re‑enablement while keeping a full reference for future use.

---

## Dependencies

File: `backend/requirements.txt`
- `openai` remains required because OpenRouter uses the OpenAI SDK client surface.
- `openai-agents` retained for the medical workflow runtime.

Key lines:
```text
openai>=1.96.1,<2.0.0
openai-agents>=0.1.0
```

---

## API Endpoints (including OpenAI‑compatible)

File: `backend/app/api/v1/chat.py`
- Regular chat endpoint remains unchanged.
- OpenAI‑compatible endpoints exposed for Open WebUI:
  - `GET /models`
  - `POST /chat/completions`

File: `backend/app/main.py`
- Exposes `GET /models` at the root for discovery.
- Mounts the OpenAI‑compatible router at multiple prefixes for client compatibility:
  - `/v1`, `/api`, and root `""`.

This allows Open WebUI to point to the backend using OpenAI API conventions without modification.

---

## Medical Workflow Runtime and Compatibility Layer

File: `backend/app/workflows/medical/runtime.py`

Purpose:
- The `openai-agents` library expects OpenAI response shapes (e.g., attributes like `.output`).
- The compatibility layer adapts OpenRouter responses to what `openai-agents` expects.

Key behaviors:
- Maps OpenRouter credentials to OpenAI environment variable names for the agents SDK:
  - Sets `OPENAI_API_KEY` from `OPENROUTER_API_KEY`.
  - Sets `OPENAI_BASE_URL` from `OPENROUTER_BASE_URL`.
- Applies patches to enhance response objects returned by `openai.AsyncOpenAI` calls so they include fields that the agents runtime reads.
- Adds an enhanced runner with robust error handling when invoking agents.

Why keep it:
- Required for compatibility with `openai-agents` without refactoring that library’s expectations.
- Zero change is required for workflow authors; the adapter smooths differences at runtime.

Minimalism note:
- If you do not use `openai-agents` features, you could remove the compatibility layer and call `OpenRouterProvider` directly from your workflows. In the current codebase it’s kept because the medical workflow relies on the agents interface.

---

## Docker and Environment Variables

File: `docker-compose.yml`

Backend service:
```yaml
environment:
  # OpenRouter configuration
  - OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}
  - OPENROUTER_BASE_URL=${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}

  # OpenAI‑compatible env vars for agents library
  - OPENAI_API_KEY=${OPENROUTER_API_KEY:-}
  - OPENAI_BASE_URL=${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}
```

Open WebUI service points to the backend using the OpenAI‑compatible surface:
```yaml
environment:
  - OPENAI_BASE_URL=http://backend:8000
  - OPENAI_API_KEY=sk-dummy-key-for-openwebui
  - ENABLE_OPENAI_API=true
  - BACKEND_URL=http://backend:8000
```

Local `.env` example:
```bash
OPENROUTER_API_KEY=sk-or-v1-xxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

---

## Models and Agents

File: `backend/app/workflows/medical/agents.py`
- Models updated to OpenRouter namespace (still OpenAI‑compatible strings):
  - `model="openai/gpt-4o-mini"`

This is the recommended style for OpenRouter when targeting OpenAI‑family models via their routing.

---

## Testing the Migration

1) Run the backend locally:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2) Health checks and model discovery:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/models
curl http://localhost:8000/v1/models
```

3) OpenAI‑compatible chat completion (Open WebUI syntax):
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "openai/gpt-4o-mini",
        "messages": [
          {"role": "user", "content": "Say hello"}
        ]
      }'
```

4) With Docker Compose:
```bash
docker compose up --build
```
Open WebUI at `http://localhost:3001` and set base URL to the backend (already wired in `docker-compose.yml`).

---

## Rollback Strategy

To revert to OpenAI as the active provider:
1) Uncomment the OpenAI branch in `LLMFactory` and comment out the OpenRouter branch.
2) Re‑enable `openai_api_key` in `config.py` and set it via environment variables.
3) Replace model ids (if needed) with OpenAI’s native names (e.g., `gpt-4o-mini`).
4) Ensure `OPENAI_BASE_URL` is the default OpenAI URL and remove OpenRouter headers.

Note: The code for OpenAI is preserved and ready to be re‑enabled.

---

## FAQ

- "Do we still need the OpenAI SDK?" — Yes, the OpenRouter surface is compatible with the OpenAI SDK (`AsyncOpenAI`) and relies on it. That’s why `openai` remains in `requirements.txt`.

- "Why keep the compatibility layer?" — The medical workflow uses `openai-agents`, which expects OpenAI response shapes. The layer adapts responses from OpenRouter so you don’t have to fork or refactor the agents library now.

- "Can we simplify further?" — If you discontinue `openai-agents` usage and call the provider directly from workflows, you can remove the compatibility layer entirely and use only `OpenRouterProvider`.

---

## Migration Checklist (applied)

- Comment out OpenAI provider code, keep it in repo.
- Set defaults to OpenRouter (provider, base URL, model names).
- Ensure factory initializes OpenRouter only.
- Configure Docker env to map OpenRouter credentials to OpenAI env vars for agents.
- Keep OpenAI‑compatible HTTP endpoints for Open WebUI.
- Verify streaming and non‑streaming paths work.

This completes a minimal, reversible migration to OpenRouter with OpenAI compatibility preserved at the boundary.


