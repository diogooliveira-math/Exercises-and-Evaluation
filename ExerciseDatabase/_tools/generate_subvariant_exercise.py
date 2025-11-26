#!/usr/bin/env python3
"""
Generic template generator for exercises with sub-variants (alíneas).

This script generates LaTeX content for exercises that have multiple sub-expressions
or sub-questions (alíneas) that can be any type of content: mathematical expressions,
text questions, problems, etc.

The exercise description is configurable to serve different pedagogical purposes.
"""

import json
import os
from typing import List, Dict, Any


def generate_subvariant_exercise_folder(
    exercise_id: str,
    title: str,
    subvariant_texts: List[str],
    exercise_description: str,
    metadata: Dict[str, Any],
    output_dir: str
) -> str:
    """
    Generate a folder structure for an exercise with sub-variants.

    Creates:
    - main.tex: Main exercise file that includes sub-variants
    - subvariant_1.tex, subvariant_2.tex, etc.: Individual sub-variant files

    Args:
        exercise_id: Unique exercise identifier
        title: Exercise title
        subvariant_texts: List of text content for each sub-variant (can be math expressions, text, etc.)
        exercise_description: The main exercise question/description text
        metadata: Exercise metadata dictionary
        output_dir: Directory to create the exercise folder in

    Returns:
        Path to the created exercise folder
    """
    # Create exercise folder
    exercise_folder = os.path.join(output_dir, exercise_id)
    os.makedirs(exercise_folder, exist_ok=True)

    # Generate main.tex
    main_content = generate_main_tex(exercise_id, title, subvariant_texts, exercise_description, metadata)
    main_file = os.path.join(exercise_folder, "main.tex")
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(main_content)

    # Generate individual sub-variant files
    for i, text in enumerate(subvariant_texts, 1):
        subvariant_content = generate_subvariant_tex(exercise_id, text, i, metadata)
        subvariant_file = os.path.join(exercise_folder, f"subvariant_{i}.tex")
        with open(subvariant_file, 'w', encoding='utf-8') as f:
            f.write(subvariant_content)

    return exercise_folder


def load_metadata_for_type(type_path: str) -> Dict[str, Any]:
    """
    Load metadata.json for a given type directory.

    Args:
        type_path: Path to the type directory (e.g., determinacao_analitica)

    Returns:
        Metadata dictionary
    """
    metadata_file = os.path.join(type_path, "metadata.json")
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def generate_main_tex(exercise_id: str, title: str, subvariant_texts: List[str], exercise_description: str, metadata: Dict[str, Any]) -> str:
    """Generate the main.tex file that includes all sub-variants."""
    
    latex_content = f"""% meta:
% id: {exercise_id}
% title: "{title}"
% difficulty: {metadata.get('difficulty', 3)}
% tags: {', '.join(metadata.get('tags', []))}
% author: {metadata.get('author', 'Generated')}
% has_subvariants: true

\\section{{{title}}}

\\exercicio{{
{exercise_description}
}}

\\begin{{enumerate}}[label=\\alph*)]"""

    # Include each sub-variant
    for i in range(1, len(subvariant_texts) + 1):
        latex_content += f"""
\\item \\input{{subvariant_{i}}}"""

    latex_content += """
\\end{enumerate}

"""

    return latex_content


def generate_subvariant_tex(exercise_id: str, text: str, index: int, metadata: Dict[str, Any]) -> str:
    """Generate an individual sub-variant .tex file."""
    return f"""% Sub-variant {index} for {exercise_id}
% Content: {text}

{text}
"""


if __name__ == "__main__":
    # Example usage
    import tempfile
    metadata = {
        "difficulty": 2,
        "tags": ["funcao_inversa", "determinacao_analitica"],
        "author": "Test"
    }

    # Example 1: Function inverse (original use case)
    subvariant_texts = ["f(x) = x + 4", "f(x) = 2x - 1", "f(x) = \\frac{1}{x-1}"]
    exercise_description = "Determina analiticamente a função inversa das seguintes expressões:"

    # Create temporary directory for example
    with tempfile.TemporaryDirectory() as temp_dir:
        folder = generate_subvariant_exercise_folder(
            "MAT_P4FUNCOE_4FIN_ANA_TEST",
            "Determinação Analítica da Função Inversa",
            subvariant_texts,
            exercise_description,
            metadata,
            temp_dir
        )

        print(f"Created exercise folder: {folder}")
        print("Contents:")
        for file in os.listdir(folder):
            print(f"  - {file}")