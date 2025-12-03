import sys
import builtins
from types import ModuleType
from pathlib import Path
import json

import pytest


def test_create_research_project_noninteractive(monkeypatch, tmp_path):
    # Prepare a fake add_exercise_safe module with make_staged_project
    called = {}

    def fake_make_staged_project(payload):
        called['payload'] = payload
        return {
            'status': 'staged',
            'staged_id': 'STG_PROJ_TEST123',
            'staged_path': str(tmp_path / 'staging' / 'STG_PROJ_TEST123')
        }

    fake_module = ModuleType('add_exercise_safe')
    fake_module.make_staged_project = fake_make_staged_project
    monkeypatch.setitem(sys.modules, 'add_exercise_safe', fake_module)

    # Ensure preview_system module is available as top-level name used by the tool
    import importlib
    preview_mod = importlib.import_module('ExerciseDatabase._tools.preview_system')
    import sys as _sys
    _sys.modules['preview_system'] = preview_mod

    # Monkeypatch PreviewManager used in add_exercise_with_types to avoid opening
    import ExerciseDatabase._tools.add_exercise_with_types as at

    class DummyPreview:
        def __init__(self, auto_open=True, consolidated_preview=True):
            self.auto_open = auto_open
            self.consolidated_preview = consolidated_preview

        def show_and_confirm(self, content, title):
            # Simulate user confirming the preview
            assert 'STG_PROJ_TEST123' in title or isinstance(content, dict)
            return True

    monkeypatch.setattr(at, 'PreviewManager', DummyPreview)

    # Prepare sequence of inputs for input() calls
    inputs = iter([
        'Test Project',      # title
        'Dr. Test',          # responsavel
        'Short summary',     # summary line 1
        '',                  # end multiline
        '',                  # extra to end
        'n',                 # associate discipline? -> no
        '',                  # tags
        '',                  # visibility -> default
        '',                  # start_date
        '',                  # end_date
    ])

    monkeypatch.setattr(builtins, 'input', lambda *args, **kwargs: next(inputs))

    # Run the wizard function
    at.create_research_project()

    # Assert staging was called and payload contains expected keys
    assert 'payload' in called
    assert called['payload']['titulo'] == 'Test Project'
    assert 'responsavel' in called['payload']
