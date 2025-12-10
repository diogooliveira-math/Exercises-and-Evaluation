Plan: FastAPI Integration for Exercises

Objetivo

Adicionar um micro-serviço FastAPI que expõe endpoints seguros para staging, preview headless, listagem de exercícios e geração de sebentas em background. O serviço deverá integrar programaticamente com os utilitários já existentes no repositório, nomeadamente `ExerciseDatabase._tools.add_exercise_safe.make_staged`, os helpers de preview e a classe `SebentaGenerator`, respeitando as regras de staging/preview (nunca escrever fora de `_staging` até confirmação) e as directrizes de agentes definidas em `AGENTS.md` e `copilot-instructions.md`.

MVP (visão geral)

- Endpoints read-only para listagem e visualização de exercícios (`GET /api/v1/exercises`, `GET /api/v1/exercises/{id}`).
- Endpoint seguro para criar um staged exercise (`POST /api/v1/exercises/stage`) que chama `make_staged(payload)` e devolve meta.
- Preview-as-data: endpoint para obter o preview de um staged (`GET /api/v1/staging/{staged_id}/preview`) que devolve o dicionário `{filename: content}` para UI clientes.
- Confirm/promote: endpoint para confirmar/promover staged items (`POST /api/v1/staging/{staged_id}/confirm`) que enfileira ou executa a promoção através de um wrapper seguro (promove apenas após auditoria/confirm).
- Geração de sebentas: `POST /api/v1/sebentas/generate` que cria um job background, invoca `SebentaGenerator` programaticamente com flags seguras (`--no-preview`/`--no-compile` por omissão) e salva logs em `temp/opencode_logs/`.

Design e decisões-chave

- Integração programática em vez de subprocessos: importar funções do pacote (`add_exercise_safe.make_staged`, helpers de preview, `SebentaGenerator`) e chamá-las internamente quando possível.
- Headless preview: nunca chamar `PreviewManager.show_and_confirm` com `auto_open=True` no servidor; em vez disso gerar e devolver os ficheiros de preview para o cliente. O cliente (ou operador) fará a revisão visual e chamará o endpoint de confirmação.
- Uso seguro do filesystem: escrever apenas em `ExerciseDatabase/_staging/` e em `temp/` para logs e outputs de job; não alterar `ExerciseDatabase/` definitivo sem promoção explícita.
- Jobs de longa duração (compilação PDF) correm em background e escrevem logs em `temp/opencode_logs/{job_id}.log` e metadados do job em `temp/jobs/{job_id}.json`.
- Autenticação/Autorizações: implementar um mecanismo simples de API key / token para controlar endpoints de escrita (staging, promotion, generation). Registrar auditoria para cada ação que altera o repositório.

Arquivos a criar

- `service/fastapi_app.py` - app FastAPI + middleware auth básica + inclusão de routers.
- `service/api_router.py` - definição dos endpoints listados acima, validações Pydantic e handlers.
- `service/jobs.py` - runner simples de jobs em background, store em `temp/jobs/` e logs em `temp/opencode_logs/`.
- `service/utils_wrappers.py` - wrappers light que importam `add_exercise_safe.make_staged`, `create_exercise_preview` e `SebentaGenerator` e os adaptam para uso HTTP (headless).
- `docs/fastapi.md` - documentação de utilização (exemplos PowerShell/uvicorn, endpoints, payloads).
- `tests/test_api_fastapi.py` - testes unitários/integrados que usam `tmp_path` e mockam/stubam FS para evitar alterações reais.

Endpoints propostos (resumo)

- POST `/api/v1/exercises/stage` — payload mínimo: `{discipline, module, concept, tipo, difficulty, statement, author?, tags?}`; chama `make_staged` e devolve `staged_id` e preview paths. Risco baixo; escrever só em `_staging`.
- GET `/api/v1/staging` — listar staged entries; leitura de `_staging`.
- GET `/api/v1/staging/{staged_id}/preview` — devolver `{filename:content}` do staging para UI review.
- POST `/api/v1/staging/{staged_id}/confirm` — ação: `promote` | `discard`; para `promote` chamar wrapper `promote_staged_exercise(staged_id)` (recomendo implementar) e escrever auditoria.
- GET `/api/v1/exercises` — filtrar por `discipline/module/concept/tipo/tag/difficulty` usando `ExerciseDatabase/index.json`.
- GET `/api/v1/exercises/{exercise_id}/preview` — devolver `.tex` e metadados do exercício.
- POST `/api/v1/sebentas/generate` — payload: filtros opcionais e flags (`no_preview`, `auto_approve`, `no_compile`); cria job que chama `SebentaGenerator` em modo programático; logs em `temp/opencode_logs/`.
- GET `/api/v1/sebentas/status/{job_id}` — estado do job e paths.

Fluxo recomendado para preview/promoção

1. Cliente chama `POST /exercises/stage` -> servidor cria staged entry via `make_staged` e devolve `staged_id`.
2. Cliente chama `GET /staging/{staged_id}/preview` -> servidor devolve ficheiros de preview (conteúdo) para UI.
3. Após revisão, cliente chama `POST /staging/{staged_id}/confirm` com `action: promote` -> servidor enfileira promoção ou executa wrapper para mover ficheiros e atualizar `ExerciseDatabase/index.json`. Operação auditada.

Considerações de deployment (Windows PowerShell)

- Recomendar execução com virtualenv: `.\.venv\Scripts\Activate.ps1` e comando uvicorn:

```powershell
uvicorn service.fastapi_app:app --host 127.0.0.1 --port 8000 ;
```

- Quando for necessário invocar scripts externos, usar `python SebentasDatabase\_tools\generate_sebentas.py --no-preview --auto-approve ...` (noteos escapes em PowerShell). Preferir import programático.
- Garantir `pdflatex` no PATH se for activar compilação PDF; senão, executar jobs com `--no-compile` por omissão e só compilar quando operador confirmar.

Riscos e mitigação

- `PreviewManager` e scripts interactivos: não executar `input()`/abrir VS Code no servidor. Transformar em preview-as-data + confirm API.
- Escritas diretas em `ExerciseDatabase/` e `SebentasDatabase/`: limitar e auditar; usar `_staging` e processos de promoção controlados.
- Jobs de compilação podem consumir recursos/tempo: enfileirar e limitar concorrência; começar com `BackgroundTasks` para MVP e migrar para RQ/Celery para produção.

Primeiros milestones

1) MVP read-only + staging
- Implementar `GET /exercises` e `GET /exercises/{id}` (ler `ExerciseDatabase/index.json` e ficheiros). 
- Implementar `POST /exercises/stage` que valida e chama `make_staged(payload)`.
- Testes unitários que usam `tmp_path` e mock filesystem.

2) Preview-as-service + promotion wrapper
- Implementar `GET /staging/{staged_id}/preview` e `POST /staging/{staged_id}/confirm` (promote/discard) via wrapper `promote_staged_exercise`.
- Testes de integração (staging -> preview -> confirm).

3) Sebenta generation (background jobs)
- `POST /sebentas/generate` enfileira job; job chama `SebentaGenerator` programaticamente com flags seguras.
- Implementar job status e logs.

4) Security e docs
- Adicionar API key/auth simples; RBAC para endpoints de escrita/geração; documentação em `docs/fastapi.md`.

Próximo passo imediato

Criar os ficheiros de esqueleto `service/fastapi_app.py`, `service/api_router.py` e `service/utils_wrappers.py`, e adicionar um teste básico que chama `POST /api/v1/exercises/stage` contra o handler de staging (mock `add_exercise_safe`).

---

Notas: Este documento serve de rascunho inicial. Se quiser, posso agora criar os ficheiros de esqueleto e os testes do MVP (implementando os wrappers que importam `add_exercise_safe.make_staged`) e executar os testes locais. Se preferir, diga se quer o fluxo: (A) headless preview (recomendado) ou (B) tentar usar `PreviewManager` para abrir VS Code do servidor (desaconselhado).