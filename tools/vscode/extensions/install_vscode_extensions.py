#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'installation des extensions VS Code/VSCodium recommandées pour les diagrammes
Usage: python install_vscode_extensions.py [--mode 1|2|3]
  --mode 1 : Installer uniquement les extensions ESSENTIELLES
  --mode 2 : Installer ESSENTIELLES + FORTEMENT RECOMMANDÉES (défaut)
  --mode 3 : Installer TOUTES les extensions
"""

import subprocess
import sys
import os
import argparse
from typing import List, Dict

# Configuration de l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # Essayer de configurer le code page UTF-8
    try:
        os.system('chcp 65001 > nul 2>&1')
    except:
        pass

# Extensions recommandées (ID extension : description)
RECOMMENDED_EXTENSIONS = {
    # PlantUML - ESSENTIEL
    "jebbs.plantuml": {
        "description": "PlantUML - Le meilleur plugin pour diagrammes PlantUML",
        "category": "🌿 PlantUML",
        "priority": "ESSENTIEL"
    },

    # Mermaid - ESSENTIEL
    "bierner.markdown-mermaid": {
        "description": "Markdown Preview Mermaid Support - Officiel Microsoft",
        "category": "🌊 Mermaid",
        "priority": "ESSENTIEL"
    },

    # Graphviz/DOT - ESSENTIEL
    "tintinweb.graphviz-interactive-preview": {
        "description": "Graphviz Interactive Preview - Preview interactif pour DOT",
        "category": "🔗 Graphviz",
        "priority": "ESSENTIEL"
    },
    "geeklearningio.graphviz-markdown-preview": {
        "description": "Graphviz Markdown Preview - Support Graphviz dans Markdown",
        "category": "🔗 Graphviz",
        "priority": "ESSENTIEL"
    },

    # Kroki - FORTEMENT RECOMMANDÉ
    "pomdtr.vscode-kroki": {
        "description": "Kroki - Preview universel : C4, PlantUML, Mermaid, DOT, Excalidraw, etc. via kroki.io",
        "category": "🔷 Kroki",
        "priority": "FORTEMENT RECOMMANDÉ"
    },

    # Markdown tout-en-un - FORTEMENT RECOMMANDÉ
    "shd101wyy.markdown-preview-enhanced": {
        "description": "Markdown Preview Enhanced - Supporte PlantUML, Mermaid, Graphviz et +",
        "category": "📝 Markdown (tout-en-un)",
        "priority": "FORTEMENT RECOMMANDÉ"
    },

    # Compléments utiles - OPTIONNEL
    "vstirbu.vscode-mermaid-preview": {
        "description": "Mermaid Preview - Preview dédié Mermaid",
        "category": "🌊 Mermaid",
        "priority": "OPTIONNEL"
    },
    "gruntfuggly.mermaid-export": {
        "description": "Mermaid Export - Export diagrammes Mermaid",
        "category": "🌊 Mermaid",
        "priority": "OPTIONNEL"
    },
    "hediet.vscode-drawio": {
        "description": "Draw.io Integration - Éditeur de diagrammes visuel",
        "category": "🎨 Éditeur visuel",
        "priority": "OPTIONNEL"
    },
    "gera2ld.markmap-vscode": {
        "description": "Markmap - Mind maps depuis Markdown",
        "category": "🧠 Mind Map",
        "priority": "OPTIONNEL"
    },
}


def find_vscode_command(preferred_editor=None):
    """Trouve la commande VS Code ou VSCodium sur le système.

    Args:
        preferred_editor: 'code', 'codium', ou None pour auto-détection
    """
    # Si un éditeur spécifique est demandé
    if preferred_editor:
        # Essayer la commande dans le PATH
        try:
            subprocess.run([preferred_editor, "--version"], capture_output=True, check=True)
            print(f"✓ Utilisation de: {preferred_editor} (spécifié)")
            return preferred_editor
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Essayer les chemins Windows
        if preferred_editor == "code":
            paths = [
                r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
                r"C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd",
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"),
            ]
        elif preferred_editor == "codium":
            paths = [
                r"G:\WarchoLife\WarchoPortable\PortableCommon\VSCodium\vscodium-1.109.41146\bin\codium.cmd",
                r"C:\Program Files\VSCodium\bin\codium.cmd",
                r"C:\Program Files (x86)\VSCodium\bin\codium.cmd",
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\VSCodium\bin\codium.cmd"),
            ]
        else:
            paths = []

        for path in paths:
            if os.path.exists(path):
                print(f"✓ Utilisation de: {path} (spécifié)")
                return path

        print(f"❌ {preferred_editor} non trouvé.")
        sys.exit(1)

    # Auto-détection : essayer d'abord 'code' puis 'codium' dans le PATH
    for cmd in ["code", "codium"]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            print(f"✓ Utilisation de: {cmd} (auto-détecté)")
            return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Chemins d'installation courants sur Windows
    windows_paths = [
        # VS Code
        r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
        r"C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"),
        # VSCodium
        r"C:\Program Files\VSCodium\bin\codium.cmd",
        r"C:\Program Files (x86)\VSCodium\bin\codium.cmd",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\VSCodium\bin\codium.cmd"),
    ]

    for path in windows_paths:
        if os.path.exists(path):
            print(f"✓ Utilisation de: {path} (auto-détecté)")
            return path

    print("❌ VS Code/VSCodium non trouvé. Veuillez l'installer ou ajouter 'code'/'codium' au PATH.")
    print("   Chemins vérifiés:")
    for path in windows_paths:
        print(f"   - {path}")
    sys.exit(1)


def get_installed_extensions(vscode_cmd) -> set:
    """Récupère la liste des extensions installées."""
    try:
        result = subprocess.run(
            [vscode_cmd, "--list-extensions"],
            capture_output=True,
            text=True,
            check=True
        )
        return set(ext.strip() for ext in result.stdout.strip().split('\n') if ext.strip())
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la récupération des extensions: {e}")
        sys.exit(1)


def install_extension(extension_id: str, vscode_cmd: str) -> tuple[bool, str]:
    """Installe une extension VS Code."""
    try:
        result = subprocess.run(
            [vscode_cmd, "--install-extension", extension_id],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def main():
    """Fonction principale."""
    print("🔍 Vérification des extensions installées...\n")

    # Vérifier si --editor est passé en argument
    preferred_editor = None
    for i, arg in enumerate(sys.argv):
        if arg == "--editor" and i + 1 < len(sys.argv):
            preferred_editor = sys.argv[i + 1]
            break

    vscode_cmd = find_vscode_command(preferred_editor)
    installed = get_installed_extensions(vscode_cmd)

    # Grouper par catégorie et priorité
    essential = []
    recommended = []
    optional = []
    already_installed = []

    for ext_id, info in RECOMMENDED_EXTENSIONS.items():
        if ext_id in installed:
            already_installed.append((ext_id, info))
        elif info["priority"] == "ESSENTIEL":
            essential.append((ext_id, info))
        elif info["priority"] == "FORTEMENT RECOMMANDÉ":
            recommended.append((ext_id, info))
        else:
            optional.append((ext_id, info))

    # Afficher les extensions déjà installées
    if already_installed:
        print("✅ Extensions déjà installées:")
        for ext_id, info in already_installed:
            print(f"  • {ext_id}")
            print(f"    └─ {info['description']}")
        print()

    # Afficher les extensions à installer
    to_install = essential + recommended + optional

    if not to_install:
        print("🎉 Toutes les extensions recommandées sont déjà installées !")
        return

    print(f"📋 {len(to_install)} extension(s) recommandée(s) non installée(s):\n")

    if essential:
        print("⭐ ESSENTIELLES:")
        for ext_id, info in essential:
            print(f"  • {ext_id}")
            print(f"    └─ {info['description']}")
        print()

    if recommended:
        print("💡 FORTEMENT RECOMMANDÉES:")
        for ext_id, info in recommended:
            print(f"  • {ext_id}")
            print(f"    └─ {info['description']}")
        print()

    if optional:
        print("🔧 OPTIONNELLES:")
        for ext_id, info in optional:
            print(f"  • {ext_id}")
            print(f"    └─ {info['description']}")
        print()

    print("=" * 70)
    print("\nOptions d'installation:")
    print("  1 - Installer UNIQUEMENT les extensions ESSENTIELLES")
    print("  2 - Installer les ESSENTIELLES + FORTEMENT RECOMMANDÉES")
    print("  3 - Installer TOUTES les extensions")
    print("  0 - Annuler")

    # Vérifier si --mode est passé en argument
    choice = None
    for i, arg in enumerate(sys.argv):
        if arg == "--mode" and i + 1 < len(sys.argv):
            choice = sys.argv[i + 1]
            print(f"\n✓ Mode automatique: {choice}")
            break

    if not choice:
        try:
            choice = input("\nVotre choix (1/2/3/0): ").strip()
        except EOFError:
            print("\n❌ Impossible de lire l'entrée. Utilisez --mode 2 pour le mode recommandé.")
            return

    extensions_to_install = []

    if choice == "1":
        extensions_to_install = essential
    elif choice == "2":
        extensions_to_install = essential + recommended
    elif choice == "3":
        extensions_to_install = to_install
    elif choice == "0":
        print("\n❌ Installation annulée.")
        return
    else:
        print("\n❌ Choix invalide. Installation annulée.")
        return

    if not extensions_to_install:
        print("\n✅ Aucune extension à installer.")
        return

    print(f"\n📥 Installation de {len(extensions_to_install)} extension(s)...\n")

    success_count = 0
    failed_count = 0
    failed_extensions = []

    for ext_id, info in extensions_to_install:
        print(f"  Installation de {ext_id}... ", end='', flush=True)

        success, message = install_extension(ext_id, vscode_cmd)

        if success:
            print("✅ OK")
            success_count += 1
        else:
            print("❌ ÉCHEC")
            failed_count += 1
            failed_extensions.append((ext_id, message))

    print("\n" + "=" * 70)
    print(f"\n📊 Résumé:")
    print(f"  • Réussies: {success_count}")
    print(f"  • Déjà installées: {len(already_installed)}")
    print(f"  • Échouées: {failed_count}")

    if success_count > 0:
        print(f"\n✅ {success_count} extension(s) installée(s) avec succès !")
        print("💡 Redémarrez VS Code pour activer les extensions.")

    if failed_extensions:
        print(f"\n⚠️  Extensions échouées:")
        for ext_id, message in failed_extensions:
            print(f"  • {ext_id}")
            if message:
                print(f"    └─ {message}")


if __name__ == "__main__":
    main()
