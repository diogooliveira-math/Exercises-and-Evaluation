AGENTS - Recomendações para subagentes

Objetivo
- Evitar falhas ao tentar criar exercícios através de escrita de ficheiros e subprocessos em ambientes restritos (ex.: agentes que não têm permissão para escrever no workspace ou executar subprocessos).

Regra principal
- Sempre que possível, prefira a API programática oferecida pelo repositório em vez de escrever ficheiros e invocar scripts via subprocesso.

API programática (preferida)
- Módulo: `ExerciseDatabase._tools.add_exercise_safe`
- Função: `make_staged(payload: dict) -> dict`
  - Uso: importe o módulo e chame `make_staged(payload)` com um dicionário Python contendo as chaves obrigatórias.
  - Chaves obrigatórias: `discipline`, `module`, `concept`, `tipo`, `difficulty`, `statement`.
  - Retorno: um dicionário com pelo menos `status`, `staged_id`, `staged_path`, `created`.

Exemplo de uso (Python, programático)

```py
from ExerciseDatabase._tools.add_exercise_safe import make_staged

payload = {
  'discipline': 'matematica',
  'module': 'P2_tests',
  'concept': 'conceito_agent',
  'tipo': 'exercicios_simples',
  'difficulty': '2',
  'statement': 'Demonstre que 1+1=2.'
}

meta = make_staged(payload)
# meta['staged_id'], meta['staged_path'] disponíveis aqui
```

Fallback (se a importação falhar)
- Se a importação automática do módulo falhar (por restrições do ambiente), o agente deve:
  1. Não tentar gravar ficheiros no workspace sem verificar permissão.
  2. Em vez disso, devolver o `payload` e um comando sugerido para o operador humano executar localmente, por exemplo:
     `python ExerciseDatabase/_tools/add_exercise_safe.py --payload-file=ExerciseDatabase/temp/payload.json`
  3. Indicar explicitamente `staged_id: null` e `staged_path: null` na resposta e explicar que o staging precisa de execução local.

Deteção de capacidades do ambiente
- Antes de tentar gravar ficheiros ou chamar subprocessos, o agente deve tentar importar `ExerciseDatabase._tools.add_exercise_safe` e chamar `make_staged`.
- Se a importação for possível, executar `make_staged`. Se lançar exceção relacionada com permissões de escrita, tratar como fallback.

Boas práticas
- Não altere ficheiros fora de `ExerciseDatabase/_staging` e `ExerciseDatabase/temp` sem autorização explícita.
- Registe no log (stdout) apenas um pequeno JSON de resultado quando fizer staging automático, por exemplo: `{'status':'staged','staged_id':..., 'staged_path':...}`.
- Se for necessário criar ficheiros temporários, crie-os sob `ExerciseDatabase/temp/`.

Notas para desenvolvedores
- O repositório já contém `ExerciseDatabase/_tools/add_exercise_safe.py` com a função `make_staged(payload)` usada internamente. Favoreça essa API para evitar falhas por falta de permissões em ambientes de agente.

---
Última actualização: automática pelo assistant
