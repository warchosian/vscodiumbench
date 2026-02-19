#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de désinstallation des extensions VS Code/VSCodium redondantes et inutiles
Usage: python uninstall_vscode_extensions.py [--yes]
  --yes : Désinstaller sans confirmation
"""

import subprocess
import sys
import os
import argparse
from typing import List, Tuple

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

# Extensions à désinstaller (ID extension : raison)
EXTENSIONS_TO_REMOVE = {
    # Doublons PlantUML (garder seulement jebbs.plantuml)
    "clysto.plantuml": "Doublon PlantUML - jebbs.plantuml est meilleur",
    "mebrahtom.plantumlpreviewer": "Doublon PlantUML - jebbs.plantuml est meilleur",
    "well-ar.plantuml": "Doublon PlantUML - version ancienne",

    # Assistants IA redondants (vous avez déjà Claude Code officiel + Copilot)
    "saoudrizwan.claude-dev": "Ancien - remplacé par anthropic.claude-code",
    "continue.continue": "Assistant IA redondant",
    "codeium.codeium": "Assistant IA redondant",
    "captainstack.captain-stack": "Recherche Stack Overflow - peu utilisé",
    "sst-dev.opencode": "Assistant IA redondant",

    # Doublons HTML Preview
    "ty4z2008.html-preview": "Doublon - garder george-alisson.html-preview-vscode",

    # Doublons LaTeX
    "manhen.latex-workshop-2": "Doublon - garder james-yu.latex-workshop",

    # Doublons Kotlin
    "mathiassoeholm.kotlin": "Doublon - garder fwcd.kotlin",

    # Graphviz redondant (vous en avez 3)
    "prinorange.markdown-graphviz-preview": "Redondant avec geeklearningio.graphviz-markdown-preview",

    # Mind map en trop (garder gera2ld.markmap-vscode)
    "souche.vscode-mindmap": "Mind map redondant",
    "season-studio.vsc-nano-mindmap": "Mind map redondant",

    # Extensions très spécifiques/peu utilisées
    "wpilibsuite.vscode-wpilib": "Robotique FRC - très spécifique",
    "nopeslide.vscode-drawio-plugin-mermaid": "Plugin DrawIO Mermaid - peu utile",
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


def get_installed_extensions(vscode_cmd) -> List[str]:
    """Récupère la liste des extensions installées."""
    try:
        result = subprocess.run(
            [vscode_cmd, "--list-extensions"],
            capture_output=True,
            text=True,
            check=True
        )
        return [ext.strip() for ext in result.stdout.strip().split('\n') if ext.strip()]
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la récupération des extensions: {e}")
        sys.exit(1)


def uninstall_extension(extension_id: str, vscode_cmd: str) -> bool:
    """Désinstalle une extension VS Code."""
    try:
        result = subprocess.run(
            [vscode_cmd, "--uninstall-extension", extension_id],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


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
    installed_set = set(installed)

    extensions_to_uninstall = [
        (ext_id, reason)
        for ext_id, reason in EXTENSIONS_TO_REMOVE.items()
        if ext_id in installed_set
    ]

    if not extensions_to_uninstall:
        print("✅ Aucune extension redondante trouvée. Votre configuration est optimale !")
        return

    print(f"📋 {len(extensions_to_uninstall)} extension(s) redondante(s) détectée(s):\n")

    for ext_id, reason in extensions_to_uninstall:
        print(f"  • {ext_id}")
        print(f"    └─ Raison: {reason}")

    print("\n" + "=" * 70)

    # Vérifier si --yes est passé en argument
    auto_confirm = "--yes" in sys.argv or "-y" in sys.argv

    if auto_confirm:
        print("\n✓ Mode automatique activé (--yes)")
        response = "o"
    else:
        try:
            response = input("\n⚠️  Voulez-vous désinstaller ces extensions ? (o/N): ").strip().lower()
        except EOFError:
            print("\n❌ Impossible de lire l'entrée. Utilisez --yes pour confirmer automatiquement.")
            return

    if response not in ['o', 'oui', 'y', 'yes']:
        print("\n❌ Désinstallation annulée.")
        return

    print("\n🗑️  Désinstallation en cours...\n")

    success_count = 0
    failed_count = 0

    for ext_id, reason in extensions_to_uninstall:
        print(f"  Désinstallation de {ext_id}... ", end='', flush=True)

        if uninstall_extension(ext_id, vscode_cmd):
            print("✅ OK")
            success_count += 1
        else:
            print("❌ ÉCHEC")
            failed_count += 1

    print("\n" + "=" * 70)
    print(f"\n📊 Résumé:")
    print(f"  • Réussies: {success_count}")
    print(f"  • Échouées: {failed_count}")

    if success_count > 0:
        print(f"\n✅ {success_count} extension(s) désinstallée(s) avec succès !")
        print("💡 Redémarrez VS Code pour finaliser les changements.")

    if failed_count > 0:
        print(f"\n⚠️  {failed_count} extension(s) n'ont pas pu être désinstallées.")


if __name__ == "__main__":
    main()
