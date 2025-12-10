from pathlib import Path
import json
import tempfile

import pytest

from ExerciseDatabase._tools import preview_system as ps


def test_create_project_preview_and_tempdir(tmp_path):
    # Prepare a small project content dict
    project_id = 'PROJ_TEST_001'
    files = {
        'README.md': '# Projeto de Teste\n\nDescrição breve.',
        'proposal.md': 'Proposta do projecto',
        'materials/data.csv': 'a,b,c\n1,2,3'
    }
    metadata = {
        'id': project_id,
        'titulo': 'Projeto de Teste',
        'responsavel': 'Prof. Teste',
        'summary': 'Resumo breve',
        'created_at': '2025-12-02T10:00:00Z',
        'status': 'draft'
    }

    preview_content = ps.create_project_preview(project_id, files, metadata)
    assert isinstance(preview_content, dict)
    # Ensure keys include README and metadata file
    assert any('README' in k or 'README.md' in k for k in preview_content.keys())
    assert any('metadata' in k for k in preview_content.keys())

    # Use PreviewManager to create temp preview directory (auto_open disabled)
    pm = ps.PreviewManager(auto_open=False, consolidated_preview=False)
    temp_dir = pm.create_temp_preview(preview_content, title='Project Preview Test')
    assert temp_dir.exists()
    # README_PREVIEW.txt should exist
    assert (temp_dir / 'README_PREVIEW.txt').exists()

    # Cleanup
    pm.cleanup()
    assert pm.temp_dir is None or not (temp_dir.exists())


def test_show_project_folder_preview_creates_preview(tmp_path, monkeypatch):
    # Create a fake project folder with files
    proj_folder = tmp_path / 'projectA'
    proj_folder.mkdir()
    (proj_folder / 'README.md').write_text('# Test Project')
    (proj_folder / 'metadata.json').write_text(json.dumps({
        'id': 'PROJ_TMP', 'titulo': 'Tmp', 'responsavel': 'R', 'summary': 'S', 'created_at': '2025-12-02T10:00:00Z', 'status': 'draft'
    }, ensure_ascii=False))

    pm = ps.PreviewManager(auto_open=False, consolidated_preview=False)
    # show_project_folder_preview should create a preview temp dir and return it
    temp_dir = ps.show_project_folder_preview(proj_folder, metadata=None, pm=pm)
    assert temp_dir is not None
    assert Path(temp_dir).exists()
    assert (Path(temp_dir) / 'README_PREVIEW.txt').exists()
    pm.cleanup()
