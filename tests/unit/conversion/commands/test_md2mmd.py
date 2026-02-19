#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour src/app/conversion/commands/md2mmd.py
"""

import pytest
from pathlib import Path

from src.app.conversion.commands.md2mmd import (
    extract_code_blocks,
    sanitize_node_id,
    detect_plantuml_type,
    convert_plantuml_sequence,
    convert_plantuml_class,
    convert_plantuml_state,
    convert_dot_digraph,
    convert_dot_graph,
    convert_diagram,
    convert_file,
)


# ===========================================================================
# Fixtures
# ===========================================================================

PLANTUML_SEQUENCE = """\
@startuml
actor Utilisateur
participant "Interface Web" as Web
participant "Service Auth" as Auth
database "Base de données" as DB

Utilisateur -> Web : Saisit identifiants
Web -> Auth : Envoie requête
Auth -> DB : Vérifie les données
DB --> Auth : Résultat
Auth --> Web : Jeton d'authentification
Web --> Utilisateur : Accès autorisé
@enduml
"""

PLANTUML_CLASS = """\
@startuml
class Livre {
  -String titre
  -String ISBN
  +emprunter()
  +rendre()
}

class Membre {
  -String nom
  -String idMembre
  +emprunterLivre(Livre)
}

Membre "1" -- "0..*" Livre : emprunte >
@enduml
"""

PLANTUML_STATE = """\
@startuml
[*] --> Créée
Créée --> Payée : paiement reçu
Payée --> Expédiée : préparation terminée
Expédiée --> Livrée : colis reçu
Livrée --> [*]
@enduml
"""

DOT_DIGRAPH = """\
digraph Dépendances {
    rankdir=TB;
    node [shape=box, style=filled, fillcolor="#e0f7fa"];

    "Frontend" -> "API Gateway";
    "API Gateway" -> "Service Utilisateurs";
    "Service Utilisateurs" -> "Base de données";
}
"""

DOT_DIGRAPH_LR = """\
digraph Projet {
    rankdir=LR;
    "A" -> "B";
    "B" -> "C";
}
"""

DOT_GRAPH = """\
graph Réseau {
    layout=neato;
    node [shape=circle, style=filled, fillcolor="#fff3e0"];

    "Jean" -- "Marie";
    "Jean" -- "Pierre";
    "Marie" -- "Sandrine";
}
"""


# ===========================================================================
# Tests : extract_code_blocks
# ===========================================================================

class TestExtractCodeBlocks:
    """Tests pour l'extraction des blocs de code Markdown."""

    def test_extract_plantuml_block(self):
        content = "# Titre\n```plantuml\n@startuml\nactor A\n@enduml\n```\n"
        blocks = extract_code_blocks(content)
        assert len(blocks) == 1
        assert blocks[0]['type'] == 'plantuml'
        assert '@startuml' in blocks[0]['content']

    def test_extract_dot_block(self):
        content = "```dot\ndigraph { \"A\" -> \"B\"; }\n```\n"
        blocks = extract_code_blocks(content)
        assert len(blocks) == 1
        assert blocks[0]['type'] == 'dot'

    def test_extract_graphviz_block(self):
        content = "```graphviz\ngraph { \"A\" -- \"B\"; }\n```\n"
        blocks = extract_code_blocks(content)
        assert len(blocks) == 1
        assert blocks[0]['type'] == 'graphviz'

    def test_ignore_python_block(self):
        content = "```python\nprint('hello')\n```\n"
        blocks = extract_code_blocks(content)
        assert len(blocks) == 0

    def test_extract_multiple_blocks(self):
        content = (
            "```plantuml\n@startuml\n[*]-->S1\n@enduml\n```\n\n"
            "```dot\ndigraph { \"A\" -> \"B\"; }\n```\n"
        )
        blocks = extract_code_blocks(content)
        assert len(blocks) == 2
        assert blocks[0]['type'] == 'plantuml'
        assert blocks[1]['type'] == 'dot'

    def test_block_has_start_end_positions(self):
        content = "```plantuml\n@startuml\n@enduml\n```\n"
        blocks = extract_code_blocks(content)
        assert 'start' in blocks[0]
        assert 'end' in blocks[0]
        assert blocks[0]['start'] == 0
        assert blocks[0]['end'] == len(content) - 1

    def test_empty_content(self):
        blocks = extract_code_blocks("")
        assert blocks == []


# ===========================================================================
# Tests : sanitize_node_id
# ===========================================================================

class TestSanitizeNodeId:
    """Tests pour la sanitization des identifiants de nœuds DOT."""

    def test_spaces_to_underscores(self):
        assert sanitize_node_id("API Gateway") == "API_Gateway"

    def test_special_chars_to_underscores(self):
        result = sanitize_node_id("Node-1.5")
        assert 'Node' in result
        assert '-' not in result
        assert '.' not in result

    def test_accents_removed(self):
        result = sanitize_node_id("Données")
        assert 'é' not in result
        assert 'Donn' in result

    def test_starts_with_number_gets_prefix(self):
        result = sanitize_node_id("1-First")
        assert result.startswith('N_')

    def test_starts_with_underscore_gets_prefix(self):
        result = sanitize_node_id("_private")
        assert result[0].isalpha()

    def test_no_consecutive_underscores(self):
        result = sanitize_node_id("A  B")
        assert '__' not in result

    def test_simple_label_unchanged(self):
        result = sanitize_node_id("Frontend")
        assert result == "Frontend"

    def test_service_with_space(self):
        result = sanitize_node_id("Service Auth")
        assert result == "Service_Auth"


# ===========================================================================
# Tests : detect_plantuml_type
# ===========================================================================

class TestDetectPlantumlType:
    """Tests pour la détection heuristique du type de diagramme PlantUML."""

    def test_detect_class_diagram(self):
        assert detect_plantuml_type("class Foo {\n  +method()\n}") == 'class'

    def test_detect_state_diagram(self):
        assert detect_plantuml_type("[*] --> Active") == 'state'

    def test_detect_sequence_diagram(self):
        assert detect_plantuml_type("actor User\nUser -> Web : message") == 'sequence'

    def test_default_to_sequence(self):
        assert detect_plantuml_type("@startuml\n@enduml") == 'sequence'

    def test_class_takes_precedence_over_state(self):
        content = "class Foo { }\n[*] --> Foo"
        # class détecté en premier
        assert detect_plantuml_type(content) == 'class'


# ===========================================================================
# Tests : convert_plantuml_sequence
# ===========================================================================

class TestConvertPlantUMLSequence:
    """Tests pour la conversion des diagrammes de séquence PlantUML."""

    def test_header_added(self):
        mermaid, _ = convert_plantuml_sequence(PLANTUML_SEQUENCE)
        assert mermaid.startswith('sequenceDiagram')

    def test_startuml_removed(self):
        mermaid, _ = convert_plantuml_sequence(PLANTUML_SEQUENCE)
        assert '@startuml' not in mermaid
        assert '@enduml' not in mermaid

    def test_actor_converted_to_participant(self):
        mermaid, _ = convert_plantuml_sequence(PLANTUML_SEQUENCE)
        assert 'actor' not in mermaid
        assert 'participant Utilisateur' in mermaid

    def test_participant_alias_inverted(self):
        mermaid, _ = convert_plantuml_sequence(PLANTUML_SEQUENCE)
        assert 'participant Web as Interface Web' in mermaid

    def test_arrow_sync_converted(self):
        mermaid, _ = convert_plantuml_sequence(PLANTUML_SEQUENCE)
        assert '->>' in mermaid

    def test_arrow_return_converted(self):
        mermaid, _ = convert_plantuml_sequence(PLANTUML_SEQUENCE)
        assert '-->>' in mermaid

    def test_database_warning(self):
        mermaid, warning = convert_plantuml_sequence(PLANTUML_SEQUENCE)
        assert warning is not None
        assert 'database' in warning.lower()

    def test_no_database_no_warning(self):
        content = "@startuml\nactor A\nA -> B : msg\n@enduml\n"
        _, warning = convert_plantuml_sequence(content)
        assert warning is None


# ===========================================================================
# Tests : convert_plantuml_class
# ===========================================================================

class TestConvertPlantUMLClass:
    """Tests pour la conversion des diagrammes de classes PlantUML."""

    def test_header_added(self):
        mermaid, _ = convert_plantuml_class(PLANTUML_CLASS)
        assert mermaid.startswith('classDiagram')

    def test_startuml_removed(self):
        mermaid, _ = convert_plantuml_class(PLANTUML_CLASS)
        assert '@startuml' not in mermaid
        assert '@enduml' not in mermaid

    def test_class_definition_preserved(self):
        mermaid, _ = convert_plantuml_class(PLANTUML_CLASS)
        assert 'class Livre' in mermaid
        assert '-String titre' in mermaid
        assert '+emprunter()' in mermaid

    def test_relationship_arrow_converted(self):
        mermaid, _ = convert_plantuml_class(PLANTUML_CLASS)
        assert '-->' in mermaid

    def test_trailing_chevron_removed(self):
        mermaid, _ = convert_plantuml_class(PLANTUML_CLASS)
        # La ligne ne doit plus se terminer par >
        lines = mermaid.splitlines()
        for line in lines:
            stripped = line.strip()
            if 'emprunte' in stripped:
                assert not stripped.endswith('>')

    def test_no_warning(self):
        _, warning = convert_plantuml_class(PLANTUML_CLASS)
        assert warning is None


# ===========================================================================
# Tests : convert_plantuml_state
# ===========================================================================

class TestConvertPlantUMLState:
    """Tests pour la conversion des diagrammes d'états PlantUML."""

    def test_header_added(self):
        mermaid, _ = convert_plantuml_state(PLANTUML_STATE)
        assert mermaid.startswith('stateDiagram-v2')

    def test_startuml_removed(self):
        mermaid, _ = convert_plantuml_state(PLANTUML_STATE)
        assert '@startuml' not in mermaid
        assert '@enduml' not in mermaid

    def test_initial_state_preserved(self):
        mermaid, _ = convert_plantuml_state(PLANTUML_STATE)
        assert '[*]' in mermaid

    def test_transitions_preserved(self):
        mermaid, _ = convert_plantuml_state(PLANTUML_STATE)
        assert 'Créée --> Payée : paiement reçu' in mermaid

    def test_no_warning(self):
        _, warning = convert_plantuml_state(PLANTUML_STATE)
        assert warning is None


# ===========================================================================
# Tests : convert_dot_digraph
# ===========================================================================

class TestConvertDotDigraph:
    """Tests pour la conversion des graphes orientés DOT."""

    def test_header_flowchart_td(self):
        mermaid, _ = convert_dot_digraph(DOT_DIGRAPH)
        assert mermaid.startswith('flowchart TD')

    def test_header_flowchart_lr(self):
        mermaid, _ = convert_dot_digraph(DOT_DIGRAPH_LR)
        assert mermaid.startswith('flowchart LR')

    def test_edges_converted(self):
        mermaid, _ = convert_dot_digraph(DOT_DIGRAPH)
        assert '-->' in mermaid

    def test_node_labels_preserved(self):
        mermaid, _ = convert_dot_digraph(DOT_DIGRAPH)
        assert '"Frontend"' in mermaid
        assert '"API Gateway"' in mermaid

    def test_sanitized_ids_used(self):
        mermaid, _ = convert_dot_digraph(DOT_DIGRAPH)
        assert 'Frontend[' in mermaid
        assert 'API_Gateway[' in mermaid

    def test_warning_for_global_styles(self):
        _, warning = convert_dot_digraph(DOT_DIGRAPH)
        assert warning is not None
        assert 'Styles globaux' in warning or 'fillcolor' in warning

    def test_no_warning_without_styles(self):
        content = 'digraph { "A" -> "B"; }'
        _, warning = convert_dot_digraph(content)
        assert warning is None

    def test_simple_digraph(self):
        content = 'digraph { "A" -> "B"; "B" -> "C"; }'
        mermaid, _ = convert_dot_digraph(content)
        assert 'A["A"] --> B["B"]' in mermaid
        assert 'B["B"] --> C["C"]' in mermaid


# ===========================================================================
# Tests : convert_dot_graph (non-orienté)
# ===========================================================================

class TestConvertDotGraph:
    """Tests pour la conversion des graphes non-orientés DOT."""

    def test_header_flowchart(self):
        mermaid, _ = convert_dot_graph(DOT_GRAPH)
        assert mermaid.startswith('flowchart TD')

    def test_bidirectional_arrows(self):
        mermaid, _ = convert_dot_graph(DOT_GRAPH)
        assert '<-->' in mermaid

    def test_node_labels_preserved(self):
        mermaid, _ = convert_dot_graph(DOT_GRAPH)
        assert '"Jean"' in mermaid
        assert '"Marie"' in mermaid

    def test_approximation_warning_present(self):
        _, warning = convert_dot_graph(DOT_GRAPH)
        assert warning is not None
        assert 'approximative' in warning.lower()

    def test_layout_warning_present(self):
        _, warning = convert_dot_graph(DOT_GRAPH)
        assert 'layout' in warning.lower() or 'neato' in warning.lower()

    def test_no_layout_no_layout_warning(self):
        content = 'graph { "A" -- "B"; }'
        _, warning = convert_dot_graph(content)
        # Warning approximatif toujours présent mais pas de warning layout
        assert warning is not None
        assert 'layout' not in warning.lower()


# ===========================================================================
# Tests : convert_diagram (routeur)
# ===========================================================================

class TestConvertDiagram:
    """Tests pour le routeur de conversion."""

    def test_routes_plantuml_state(self):
        content = "@startuml\n[*] --> Active\nActive --> [*]\n@enduml\n"
        mermaid, _ = convert_diagram('plantuml', content)
        assert 'stateDiagram-v2' in mermaid

    def test_routes_plantuml_class(self):
        content = "@startuml\nclass Foo {\n  +method()\n}\n@enduml\n"
        mermaid, _ = convert_diagram('plantuml', content)
        assert 'classDiagram' in mermaid

    def test_routes_plantuml_sequence(self):
        content = "@startuml\nactor A\nA -> B : msg\n@enduml\n"
        mermaid, _ = convert_diagram('plantuml', content)
        assert 'sequenceDiagram' in mermaid

    def test_routes_dot_digraph(self):
        content = 'digraph { "A" -> "B"; }'
        mermaid, _ = convert_diagram('dot', content)
        assert 'flowchart' in mermaid
        assert '-->' in mermaid

    def test_routes_dot_graph(self):
        content = 'graph { "A" -- "B"; }'
        mermaid, _ = convert_diagram('dot', content)
        assert '<-->' in mermaid

    def test_routes_graphviz_type(self):
        content = 'digraph { "X" -> "Y"; }'
        mermaid, _ = convert_diagram('graphviz', content)
        assert 'flowchart' in mermaid

    def test_unknown_type_returns_none(self):
        mermaid, warning = convert_diagram('unknown', 'some content')
        assert mermaid is None
        assert 'non supporté' in warning

    def test_dot_fallback_to_digraph(self):
        # Contenu DOT sans mot-clé digraph ni graph → fallback digraph
        content = '{ "A" -> "B"; }'
        mermaid, _ = convert_diagram('dot', content)
        assert mermaid is not None


# ===========================================================================
# Tests : convert_file (I/O)
# ===========================================================================

class TestConvertFile:
    """Tests pour les opérations de lecture/écriture de fichiers."""

    def test_creates_mmd_md_output(self, tmp_path):
        input_file = tmp_path / "test.md"
        input_file.write_text(
            "# Titre\n```plantuml\n@startuml\n[*] --> Active\n@enduml\n```\n",
            encoding='utf-8'
        )
        result = convert_file(str(input_file))
        assert result is True
        output_file = tmp_path / "test.mmd.md"
        assert output_file.exists()

    def test_output_contains_mermaid(self, tmp_path):
        input_file = tmp_path / "test.md"
        input_file.write_text(
            "```plantuml\n@startuml\n[*] --> S1\n@enduml\n```\n",
            encoding='utf-8'
        )
        convert_file(str(input_file))
        output = (tmp_path / "test.mmd.md").read_text(encoding='utf-8')
        assert 'stateDiagram-v2' in output
        assert '@startuml' not in output

    def test_output_filename_format(self, tmp_path):
        input_file = tmp_path / "diagram.md"
        input_file.write_text("no diagrams here", encoding='utf-8')
        convert_file(str(input_file))
        assert (tmp_path / "diagram.mmd.md").exists()

    def test_preserves_non_diagram_content(self, tmp_path):
        input_file = tmp_path / "mixed.md"
        input_file.write_text(
            "# Titre\n\nTexte normal.\n\n"
            "```python\nprint('code')\n```\n\n"
            "```plantuml\n@startuml\n[*] --> S1\n@enduml\n```\n\n"
            "Fin du document.\n",
            encoding='utf-8'
        )
        convert_file(str(input_file))
        output = (tmp_path / "mixed.mmd.md").read_text(encoding='utf-8')
        assert '# Titre' in output
        assert 'Texte normal.' in output
        assert "print('code')" in output
        assert 'Fin du document.' in output

    def test_missing_file_returns_false(self):
        result = convert_file("/chemin/inexistant/fichier.md")
        assert result is False

    def test_wrong_extension_returns_false(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("contenu", encoding='utf-8')
        result = convert_file(str(f))
        assert result is False

    def test_no_diagrams_copies_file(self, tmp_path):
        input_file = tmp_path / "plain.md"
        input_file.write_text("# Juste du texte\n", encoding='utf-8')
        result = convert_file(str(input_file))
        assert result is True
        output = (tmp_path / "plain.mmd.md").read_text(encoding='utf-8')
        assert '# Juste du texte' in output

    def test_mixed_plantuml_and_dot(self, tmp_path):
        input_file = tmp_path / "multi.md"
        input_file.write_text(
            "```plantuml\n@startuml\n[*] --> S1\n@enduml\n```\n\n"
            '```dot\ndigraph { "A" -> "B"; }\n```\n',
            encoding='utf-8'
        )
        convert_file(str(input_file))
        output = (tmp_path / "multi.mmd.md").read_text(encoding='utf-8')
        assert 'stateDiagram-v2' in output
        assert 'flowchart' in output


# ===========================================================================
# Tests : gestion des erreurs
# ===========================================================================

class TestErrorHandling:
    """Tests pour la robustesse face aux entrées invalides."""

    def test_malformed_plantuml_still_produces_output(self):
        """Un PlantUML invalide ne doit pas lever d'exception."""
        content = "@startuml\nINVALID SYNTAX HERE\n@enduml\n"
        mermaid, _ = convert_plantuml_sequence(content)
        assert mermaid is not None
        assert 'sequenceDiagram' in mermaid

    def test_empty_digraph_produces_flowchart(self):
        content = 'digraph Empty { }'
        mermaid, _ = convert_dot_digraph(content)
        assert 'flowchart' in mermaid

    def test_empty_graph_produces_flowchart(self):
        content = 'graph Empty { }'
        mermaid, _ = convert_dot_graph(content)
        assert 'flowchart' in mermaid

    def test_directory_path_returns_false(self, tmp_path):
        result = convert_file(str(tmp_path))
        assert result is False

    def test_plantuml_without_delimiters(self):
        """PlantUML sans @startuml doit quand même produire un résultat."""
        content = "actor A\nA -> B : message\n"
        mermaid, _ = convert_plantuml_sequence(content)
        assert 'sequenceDiagram' in mermaid
