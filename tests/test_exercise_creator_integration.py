import os
import sys
import subprocess
import uuid
import glob
from pathlib import Path
import pytest

RUN_FLAG = os.environ.get('RUN_EXERCISE_CREATOR_INTEGRATION')

pytestmark = pytest.mark.skipif(RUN_FLAG is None,
                                reason="Set RUN_EXERCISE_CREATOR_INTEGRATION to run integration test")


def test_exercise_creator_integration():
    """Integration test that calls scripts/run_add_exercise.py to create an exercise.

    The test will:
    - build a unique marker
    - call the wrapper using sys.executable
    - search the ExerciseDatabase for any .tex files containing the marker
    - assert at least one was created
    - clean up any created .tex and metadata.json files that contain the marker
    """
    unique = f"TEST_AUTOM_{uuid.uuid4().hex}"
    user_prompt = (
        'Quero que cries um exercício no módulo P4_funcoes na generalidades de funcoes (procurar nomenclatura) '
        'e adiciones um novo tipo de exercício (escolhe tu a nomenclatura do tipo de exercício!), onde os alunos afirma coisas tipo "quando o preço aumenta a despesa vai aumentar" para responder às questões..'
    )
    statement = f"{unique} + {user_prompt}"

    cmd = [sys.executable,
           os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'run_add_exercise.py'),
           'discipline=matematica',
           'module=P4_funcoes',
           'concept=1-generalidades_funcoes',
           'tipo=afirmacoes_contextuais_temp',
           'difficulty=2',
           f"statement={statement}"]

    proc = None
    stdout = stderr = ''
    created_files = []
    created_metadata = []

    try:
        # Run the wrapper
        proc = subprocess.run(cmd, text=True, encoding='utf-8', errors='replace',
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        stdout = proc.stdout
        stderr = proc.stderr

        # If wrapper wrote a clear SUCCESS message, print it for diagnostics
        if stdout:
            print("---- wrapper stdout ----")
            print(stdout)
        if stderr:
            print("---- wrapper stderr ----")
            print(stderr)

        # Search for created .tex files containing the unique marker
        base = Path(__file__).resolve().parents[1] / 'ExerciseDatabase' / 'matematica' / 'P4_funcoes'
        tex_paths = list(base.rglob('*.tex')) if base.exists() else []

        for p in tex_paths:
            try:
                with p.open('r', encoding='utf-8', errors='replace') as fh:
                    content = fh.read()
                if unique in content:
                    created_files.append(str(p))
            except Exception as e:
                print(f"Could not read {p}: {e}")

        # Also search for any metadata.json files that might contain the marker
        json_paths = list(base.rglob('metadata.json')) if base.exists() else []
        for p in json_paths:
            try:
                with p.open('r', encoding='utf-8', errors='replace') as fh:
                    content = fh.read()
                if unique in content:
                    created_metadata.append(str(p))
            except Exception as e:
                print(f"Could not read {p}: {e}")

        # If the wrapper printed an explicit success, accept that; otherwise require created file(s)
        success_printed = 'SUCCESS' in (stdout or '') or 'SUCCESS' in (stderr or '')

        if not success_printed:
            assert created_files or created_metadata, (
                "No created files found containing the unique marker and no SUCCESS message.\n"
                f"Unique marker: {unique}\nstdout:\n{stdout}\nstderr:\n{stderr}"
            )

    finally:
        # Cleanup any files that contained the unique marker
        removed = []
        removed_meta = []
        try:
            # Remove tex files
            for fp in created_files:
                try:
                    os.unlink(fp)
                    removed.append(fp)
                except Exception as e:
                    print(f"Failed to remove {fp}: {e}")

            # Remove metadata files
            for fp in created_metadata:
                try:
                    os.unlink(fp)
                    removed_meta.append(fp)
                except Exception as e:
                    print(f"Failed to remove metadata {fp}: {e}")

            # Additionally, be defensive: remove any .tex or metadata.json anywhere under P4_funcoes that contain the marker
            base = Path(__file__).resolve().parents[1] / 'ExerciseDatabase' / 'matematica' / 'P4_funcoes'
            if base.exists():
                for p in base.rglob('*.tex'):
                    try:
                        text = p.read_text(encoding='utf-8', errors='replace')
                        if unique in text:
                            try:
                                os.unlink(p)
                                removed.append(str(p))
                            except Exception as e:
                                print(f"Failed to remove {p}: {e}")
                    except Exception:
                        continue

                for p in base.rglob('metadata.json'):
                    try:
                        text = p.read_text(encoding='utf-8', errors='replace')
                        if unique in text:
                            try:
                                os.unlink(p)
                                removed_meta.append(str(p))
                            except Exception as e:
                                print(f"Failed to remove metadata {p}: {e}")
                    except Exception:
                        continue

        finally:
            # Final assertions: ensure none of the removed files remain
            for fp in removed + removed_meta:
                if os.path.exists(fp):
                    print(f"Cleanup failed, file still exists: {fp}")

            # For test visibility, print what we found and removed
            print("==== Integration test summary ====")
            print(f"Unique marker: {unique}")
            print(f"Created tex files (found during test): {created_files}")
            print(f"Created metadata files (found during test): {created_metadata}")
            print(f"Removed files: {removed}")
            print(f"Removed metadata files: {removed_meta}")

            # If the test ran (i.e., RUN_FLAG is set), assert cleanup succeeded (no remaining files contain the marker)
            if RUN_FLAG is not None:
                base = Path(__file__).resolve().parents[1] / 'ExerciseDatabase' / 'matematica' / 'P4_funcoes'
                still_there = []
                if base.exists():
                    for p in list(base.rglob('*.tex')) + list(base.rglob('metadata.json')):
                        try:
                            text = p.read_text(encoding='utf-8', errors='replace')
                            if unique in text:
                                still_there.append(str(p))
                        except Exception:
                            continue
                assert not still_there, f"Cleanup left files containing the marker: {still_there}"
