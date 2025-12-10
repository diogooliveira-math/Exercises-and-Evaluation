**FastAPI Service**

Este ficheiro documenta o micro-serviço FastAPI adicionado ao repositório para suportar staging, preview headless, promoção auditada e geração de sebentas em background.

**Run (PowerShell)**
- Ativar virtualenv:

```powershell
.\.venv\Scripts\Activate.ps1
```

- Executar o servidor local (uvicorn):

```powershell
uvicorn service.fastapi_app:app --host 127.0.0.1 --port 8000 ;
```

**Endpoints principais**
- `POST /api/v1/exercises/stage` — Criar um staged exercise (escreve apenas em `ExerciseDatabase/_staging/`).
  - Payload mínimo (JSON):

```json
{
  "discipline": "matematica",
  "module": "P1_tests",
  "concept": "test_concept",
  "tipo": "exercicios_simples",
  "difficulty": 2,
  "statement": "Enunciado do exercício",
  "author": "Autor",
  "tags": ["unit","exemplo"]
}
```

- `GET /api/v1/staging/{staged_id}/preview` — Devolve um dicionário `{filename: content}` com os ficheiros do staged para o UI apresentar (headless preview).

- `POST /api/v1/staging/{staged_id}/confirm` — Confirmar ação sobre um staged: `{"action":"promote"}` ou `{"action":"discard"}`. A promoção move o staged para `ExerciseDatabase/<discipline>/<module>/<concept>/<tipo>/<staged_id>` e actualiza `ExerciseDatabase/index.json`.

- `POST /api/v1/sebentas/generate` — Enfileira um job para gerar sebentas. Payload opcional para filtros (module/discipline/concept/tipo). Retorna `{job_id}`.

- `GET /api/v1/sebentas/status/{job_id}` — Estado do job (metadata em `temp/jobs/{job_id}.json`).

**Fluxo recomendado (staging → preview → confirm)**
1. `POST /api/v1/exercises/stage` -> recebes `staged_id`.
2. `GET /api/v1/staging/{staged_id}/preview` -> cliente apresenta pré-visualização ao operador.
3. Após revisão, `POST /api/v1/staging/{staged_id}/confirm` com `action=promote` para mover e registar o exercício de forma atómica.

**Jobs & Logging**
- Ficheiros de log e metadados de job:
  - `temp/opencode_logs/{job_id}.log` — output textual do job.
  - `temp/jobs/{job_id}.json` — metadata do job (status, created_at, finished_at, error).
- O JobManager é intencionalmente minimalista e usa threads para o MVP. Para produção considere migrar para RQ/Celery.

**Testes**
- Executar a suite de testes (unit + integration):

```powershell
.\.venv\Scripts\python -m pytest -q
```

- Tests relevantes criados:
  - `tests/test_stage_flow.py` — fluxo stage/preview/confirm (unit, com monkeypatch)
  - `tests/test_promote_flow.py` — promoção real para `ExerciseDatabase/` em `tmp_path`
  - `tests/test_jobs.py` — JobManager unit test usando FakeGen
  - `tests/integration/test_jobs_integration.py` — JobManager end-to-end com FakeGen
  - `tests/integration/test_sebenta_api_integration.py` — API integration: `POST /sebentas/generate` + `GET /sebentas/status/{job_id}`

**Boas práticas e considerações**
- Cabe sempre confirmar manualmente a promoção — o servidor só escreve em `_staging/` até promoção explícita.
- Evitar executar funções interactivas no servidor: `PreviewManager.show_and_confirm` não é usado — o serviço gera e devolve ficheiros de preview para o cliente.
- Para chamadas a `SebentaGenerator` o serviço usa flags não-interactivas (`no_preview`, `no_compile`, `auto_approve`) por omissão. O operador pode pedir compilação manual depois.
- Logs e ficheiros temporários seguem a convenção: `temp/opencode_logs/` e `temp/jobs/` — não comitar estes ficheiros.

**Exemplo rápido (PowerShell) — criar e confirmar**

```powershell
# 1) Criar staged
$payload = '{"discipline":"matematica","module":"P1_tests","concept":"cx","tipo":"exercicios_simples","difficulty":2,"statement":"Enunciado"}' 
$resp = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/exercises/stage -Body $payload -ContentType 'application/json'
$staged_id = $resp.meta.staged_id

# 2) Obter preview
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/v1/staging/$staged_id/preview"

# 3) Confirmar promoção
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/staging/$staged_id/confirm" -Body '{"action":"promote"}' -ContentType 'application/json'
```

**Autenticação (MVP)**
- O serviço inclui actualmente apenas um stub de autenticação mínima (recomenda-se adicionar API-key middleware para proteger endpoints de escrita). Documente e gere chaves para utilizadores/operadores.
 
**API-Key Example**
- Header name: `X-API-Key`
- Set the `API_KEY` environment variable on the server process to enable middleware enforcement.

Exemplo `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/exercises/stage" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: secret123" \
  -d '{"discipline":"matematica","module":"P1_tests","concept":"cx","tipo":"exercicios_simples","difficulty":2,"statement":"Enunciado"}'
```

Exemplo PowerShell (Invoke-RestMethod):

```powershell
# On the client issuing the request (server must have API_KEY set):
$headers = @{ 'X-API-Key' = 'secret123' }
$payload = '{"discipline":"matematica","module":"P1_tests","concept":"cx","tipo":"exercicios_simples","difficulty":2,"statement":"Enunciado"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/exercises/stage -Body $payload -ContentType 'application/json' -Headers $headers
```

**Contribuir / Desenvolvimento**
- Workflow TDD: testes foram escritos antes das funcionalidades principais. Se adicionares novos endpoints, escreve primeiro os testes em `tests/` usando `tmp_path` e `monkeypatch`.

**Contactos & notas**
- Logs opencode e outros ficheiros temporários não devem ser comitados — ver `PREVIEW_SYSTEM.md` e `copilot-instructions.md` para políticas de preview e staging.
