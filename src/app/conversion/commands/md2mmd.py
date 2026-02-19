#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convertisseur de diagrammes PlantUML et Graphviz/DOT vers Mermaid

Lit un fichier Markdown (.md) et génère un fichier (.mmd.md)
avec les blocs plantuml et dot/graphviz convertis en mermaid.

Usage:
    python md2mmd.py <fichier.md>

Sortie:
    <fichier>.mmd.md dans le même répertoire que le fichier source
"""

import sys
import io
import re
import unicodedata
from pathlib import Path


def _fix_stdout_encoding():
    """Corrige l'encodage UTF-8 de stdout sur Windows (à appeler uniquement depuis main)."""
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


# ---------------------------------------------------------------------------
# Extraction des blocs de code
# ---------------------------------------------------------------------------

CODE_BLOCK_RE = re.compile(
    r'^```([\w]+)\s*\n(.*?)^```[ \t]*$',
    re.MULTILINE | re.DOTALL
)

SUPPORTED_TYPES = {'plantuml', 'dot', 'graphviz'}


def extract_code_blocks(content):
    """
    Extrait les blocs de code PlantUML et Graphviz/DOT depuis un contenu Markdown.

    Args:
        content: Contenu texte du fichier Markdown

    Returns:
        Liste de dicts : [{'type': str, 'content': str, 'start': int, 'end': int}, ...]
    """
    blocks = []
    for match in CODE_BLOCK_RE.finditer(content):
        lang = match.group(1).lower()
        if lang in SUPPORTED_TYPES:
            blocks.append({
                'type': lang,
                'content': match.group(2),
                'start': match.start(),
                'end': match.end(),
            })
    return blocks


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

def sanitize_node_id(label):
    """
    Convertit un label DOT quelconque en identifiant Mermaid valide.

    Règles appliquées :
    - Suppression des accents
    - Espaces et caractères spéciaux → underscore
    - Début par une lettre (sinon préfixe N_)
    - Underscores consécutifs réduits à un seul

    Args:
        label: Nom de nœud original (peut contenir espaces, accents, etc.)

    Returns:
        Identifiant valide pour Mermaid
    """
    # Supprimer les accents
    nfkd = unicodedata.normalize('NFKD', label)
    without_accents = ''.join(c for c in nfkd if not unicodedata.combining(c))

    # Remplacer les caractères non alphanumériques par des underscores
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', without_accents)

    # Réduire les underscores consécutifs
    sanitized = re.sub(r'_+', '_', sanitized).strip('_')

    # Assurer que l'identifiant commence par une lettre
    if not sanitized or not sanitized[0].isalpha():
        sanitized = 'N_' + sanitized

    return sanitized or 'node'


def detect_plantuml_type(content):
    """
    Détecte le type de diagramme PlantUML par heuristique sur les mots-clés.

    Returns:
        'sequence' | 'class' | 'state'
    """
    if 'class ' in content and '{' in content:
        return 'class'
    if '[*]' in content:
        return 'state'
    # Par défaut : séquence (couvre actor, participant, ->)
    return 'sequence'


# ---------------------------------------------------------------------------
# Convertisseurs PlantUML
# ---------------------------------------------------------------------------

def convert_plantuml_sequence(content):
    """
    Convertit un diagramme de séquence PlantUML vers Mermaid.

    Conversions appliquées :
    - @startuml / @enduml supprimés
    - actor X → participant X
    - participant "Nom" as Alias → participant Alias as Nom
    - database "Nom" as Alias → participant Alias as Nom (approximatif)
    - -> → ->>
    - --> → -->>

    Returns:
        (mermaid_code: str, warning: str | None)
    """
    lines = []
    warnings = []
    has_database = False

    for raw_line in content.splitlines():
        line = raw_line.strip()

        # Ignorer les délimiteurs PlantUML
        if line in ('@startuml', '@enduml'):
            continue

        # database → participant (approximatif)
        if line.startswith('database '):
            line = line.replace('database ', 'participant ', 1)
            has_database = True

        # actor → participant
        if line.startswith('actor '):
            line = line.replace('actor ', 'participant ', 1)

        # participant "Nom long" as Alias → participant Alias as Nom long
        alias_match = re.match(r'participant\s+"([^"]+)"\s+as\s+(\w+)(.*)', line)
        if alias_match:
            nom, alias, reste = alias_match.groups()
            line = f'participant {alias} as {nom}{reste}'

        # Conversion des flèches : -> → ->> et --> → -->>
        # Ordre important : traiter --> avant ->
        line = re.sub(r'([\w\"\'])\s*-->\s*([\w\"\'])', r'\1 -->> \2', line)
        line = re.sub(r'([\w\"\'])\s*->\s*([\w\"\'])', r'\1 ->> \2', line)

        if line:
            lines.append('    ' + line)

    if has_database:
        warnings.append(
            '<!-- ATTENTION: type "database" converti en participant (non supporté nativement par Mermaid) -->'
        )

    mermaid = 'sequenceDiagram\n' + '\n'.join(lines)
    return mermaid, '\n'.join(warnings) if warnings else None


def convert_plantuml_class(content):
    """
    Convertit un diagramme de classes PlantUML vers Mermaid.

    Conversions appliquées :
    - @startuml / @enduml supprimés
    - Relations : "1" -- "0..*" → "1" --> "0..*"
    - Trailing > supprimé dans les labels de relation

    Returns:
        (mermaid_code: str, warning: str | None)
    """
    lines = []

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if line in ('@startuml', '@enduml'):
            continue

        # Relation avec cardinalité : Membre "1" -- "0..*" Livre : emprunte >
        # Convertir -- en --> et supprimer le > final
        line = re.sub(r'"\s*--\s*"', '" --> "', line)
        # Supprimer le > terminal dans les labels de relation
        line = re.sub(r'\s*>\s*$', '', line)

        if line:
            lines.append('    ' + line)

    mermaid = 'classDiagram\n' + '\n'.join(lines)
    return mermaid, None


def convert_plantuml_state(content):
    """
    Convertit un diagramme d'états PlantUML vers Mermaid.

    La syntaxe est quasi-identique : seuls @startuml/@enduml sont supprimés.

    Returns:
        (mermaid_code: str, None)
    """
    lines = []

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if line in ('@startuml', '@enduml'):
            continue

        if line:
            lines.append('    ' + line)

    mermaid = 'stateDiagram-v2\n' + '\n'.join(lines)
    return mermaid, None


# ---------------------------------------------------------------------------
# Convertisseurs Graphviz/DOT
# ---------------------------------------------------------------------------

_DOT_EDGE_DIRECTED_RE = re.compile(
    r'"([^"]+)"\s*->\s*"([^"]+)"(?:\s*\[[^\]]*\])?(?:\s*;)?'
)
_DOT_EDGE_UNDIRECTED_RE = re.compile(
    r'"([^"]+)"\s*--\s*"([^"]+)"(?:\s*\[[^\]]*\])?(?:\s*;)?'
)
_DOT_RANKDIR_RE = re.compile(r'rankdir\s*=\s*(\w+)', re.IGNORECASE)
_DOT_GLOBAL_NODE_STYLE_RE = re.compile(r'node\s*\[([^\]]+)\]', re.DOTALL)


def _detect_dot_direction(content):
    """Retourne la direction Mermaid depuis rankdir DOT."""
    match = _DOT_RANKDIR_RE.search(content)
    if match:
        rankdir = match.group(1).upper()
        mapping = {'TB': 'TD', 'TD': 'TD', 'LR': 'LR', 'RL': 'RL', 'BT': 'BT'}
        return mapping.get(rankdir, 'TD')
    return 'TD'


def convert_dot_digraph(content):
    """
    Convertit un graphe orienté DOT (digraph) vers Mermaid flowchart.

    Conversions appliquées :
    - digraph Name { } → flowchart TD|LR
    - "Node A" -> "Node B"; → NodeA[Node A] --> NodeB[Node B]
    - rankdir → direction Mermaid
    - Avertissement si styles globaux détectés

    Returns:
        (mermaid_code: str, warning: str | None)
    """
    direction = _detect_dot_direction(content)
    lines = []
    warnings = []

    for match in _DOT_EDGE_DIRECTED_RE.finditer(content):
        from_label, to_label = match.group(1), match.group(2)
        from_id = sanitize_node_id(from_label)
        to_id = sanitize_node_id(to_label)
        lines.append(f'    {from_id}["{from_label}"] --> {to_id}["{to_label}"]')

    # Avertissement si styles globaux présents
    if _DOT_GLOBAL_NODE_STYLE_RE.search(content):
        warnings.append(
            '<!-- ATTENTION: Styles globaux DOT (fillcolor, shape, etc.) '
            'non traduits — utilisez des classDef Mermaid si nécessaire -->'
        )

    mermaid = f'flowchart {direction}\n' + '\n'.join(lines)
    return mermaid, '\n'.join(warnings) if warnings else None


def convert_dot_graph(content):
    """
    Convertit un graphe non-orienté DOT (graph) vers Mermaid flowchart.

    Conversion approximative : les arêtes non-orientées sont représentées
    par des flèches bidirectionnelles (<-->).

    Returns:
        (mermaid_code: str, warning: str)
    """
    lines = []
    warnings = [
        '<!-- ATTENTION: Conversion approximative depuis graphe non-orienté DOT -->',
        '<!-- Les flèches bidirectionnelles (<-->) représentent les arêtes non-orientées -->',
    ]

    for match in _DOT_EDGE_UNDIRECTED_RE.finditer(content):
        from_label, to_label = match.group(1), match.group(2)
        from_id = sanitize_node_id(from_label)
        to_id = sanitize_node_id(to_label)
        lines.append(f'    {from_id}["{from_label}"] <--> {to_id}["{to_label}"]')

    if 'layout=' in content:
        warnings.append(
            '<!-- ATTENTION: Attribut layout= DOT (neato, circo, etc.) '
            'non supporté par Mermaid —  disposition automatique appliquée -->'
        )

    mermaid = 'flowchart TD\n' + '\n'.join(lines)
    return mermaid, '\n'.join(warnings)


# ---------------------------------------------------------------------------
# Routeur de conversion
# ---------------------------------------------------------------------------

def convert_diagram(diagram_type, content):
    """
    Route la conversion vers la fonction spécifique selon le type de diagramme.

    Args:
        diagram_type: 'plantuml' | 'dot' | 'graphviz'
        content: Contenu brut du bloc de code

    Returns:
        (mermaid_code: str | None, warning: str | None)
    """
    if diagram_type == 'plantuml':
        subtype = detect_plantuml_type(content)
        if subtype == 'class':
            return convert_plantuml_class(content)
        elif subtype == 'state':
            return convert_plantuml_state(content)
        else:
            return convert_plantuml_sequence(content)

    elif diagram_type in ('dot', 'graphviz'):
        if re.search(r'\bdigraph\b', content):
            return convert_dot_digraph(content)
        elif re.search(r'\bgraph\b', content):
            return convert_dot_graph(content)
        else:
            # Fallback : supposer digraph
            return convert_dot_digraph(content)

    return None, f'<!-- Type de diagramme non supporté: {diagram_type} -->'


# ---------------------------------------------------------------------------
# Orchestrateur principal
# ---------------------------------------------------------------------------

def convert_file(input_path):
    """
    Convertit un fichier Markdown en remplaçant les diagrammes PlantUML/DOT par Mermaid.

    Le fichier de sortie est créé dans le même répertoire avec l'extension .mmd.md.

    Args:
        input_path: Chemin vers le fichier .md source (str ou Path)

    Returns:
        True si la conversion réussit, False sinon
    """
    try:
        path = Path(input_path)

        if not path.exists():
            print(f"[ERREUR] Fichier introuvable : {path}")
            return False

        if not path.is_file():
            print(f"[ERREUR] Chemin invalide (pas un fichier) : {path}")
            return False

        if path.suffix.lower() != '.md':
            print(f"[ERREUR] Extension invalide (attendu .md) : {path.suffix}")
            return False

        print(f"[INFO] Lecture : {path}")
        content = path.read_text(encoding='utf-8')

        blocks = extract_code_blocks(content)

        if not blocks:
            print("[INFO] Aucun diagramme PlantUML/DOT trouvé — fichier copié tel quel")
            output_path = path.parent / (path.stem + '.mmd.md')
            output_path.write_text(content, encoding='utf-8')
            print(f"[OK] Créé : {output_path}")
            return True

        print(f"[INFO] {len(blocks)} diagramme(s) détecté(s)")

        # Traiter les blocs en ordre inverse pour préserver les indices
        converted_content = content
        conversion_count = 0
        warning_count = 0

        for block in reversed(blocks):
            mermaid_code, warning = convert_diagram(block['type'], block['content'])

            if mermaid_code is None:
                continue

            replacement = f'```mermaid\n{mermaid_code}\n```'
            if warning:
                replacement = warning + '\n' + replacement
                warning_count += 1

            converted_content = (
                converted_content[:block['start']]
                + replacement
                + converted_content[block['end']:]
            )
            conversion_count += 1
            print(f"[OK] Converti : {block['type']} → mermaid")

        output_path = path.parent / (path.stem + '.mmd.md')
        output_path.write_text(converted_content, encoding='utf-8')

        print(f"[OK] {conversion_count} diagramme(s) converti(s)")
        if warning_count:
            print(f"[ATTENTION] {warning_count} conversion(s) approximative(s) — vérifiez les commentaires dans le fichier")
        print(f"[OK] Fichier créé : {output_path}")
        return True

    except PermissionError:
        print(f"[ERREUR] Permission refusée lors de l'écriture du fichier de sortie")
        return False
    except UnicodeDecodeError as e:
        print(f"[ERREUR] Problème d'encodage lors de la lecture : {e}")
        return False
    except Exception as e:
        print(f"[ERREUR] Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# Point d'entrée CLI
# ---------------------------------------------------------------------------

def main():
    """Point d'entrée principal."""
    _fix_stdout_encoding()
    if len(sys.argv) < 2:
        print("Usage : python md2mmd.py <fichier.md>")
        print()
        print("Convertit les diagrammes PlantUML et Graphviz/DOT en Mermaid.")
        print("Génère <fichier>.mmd.md dans le même répertoire.")
        print()
        print("Exemple :")
        print("  python md2mmd.py _diagrams/multidiagrams.md")
        return 1

    result = convert_file(sys.argv[1])
    return 0 if result else 1


if __name__ == '__main__':
    sys.exit(main())
