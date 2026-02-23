#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'installation de la configuration VSCode/VSCodium
Copie settings.json et activate_with_vscodium.bat dans un projet cible
"""

import os
import sys
import shutil
from pathlib import Path


def install_config(target_project_path):
    """
    Installe la configuration VSCode dans le projet cible

    Args:
        target_project_path: Chemin vers le projet cible
    """
    # Chemins sources (dans vscodiumbench/scripts)
    script_dir = Path(__file__).parent
    settings_template = script_dir / "settings.json.template"
    activate_bat = script_dir / "activate_with_vscodium.bat"

    # Chemins cibles
    target_dir = Path(target_project_path)
    vscode_dir = target_dir / ".vscode"
    settings_target = vscode_dir / "settings.json"
    activate_target = vscode_dir / "activate_with_vscodium.bat"

    print("=" * 60)
    print("Installation de la configuration VSCode/VSCodium")
    print("=" * 60)
    print()

    # Vérifier que le projet cible existe
    if not target_dir.exists():
        print(f"[ERREUR] Le projet cible n'existe pas: {target_dir}")
        return False

    print(f"Projet cible: {target_dir}")
    print()

    # Créer le dossier .vscode si nécessaire
    if not vscode_dir.exists():
        print(f"[INFO] Création du dossier .vscode...")
        vscode_dir.mkdir(parents=True, exist_ok=True)
        print("[OK] Dossier créé")

    # Vérifier si settings.json existe déjà
    if settings_target.exists():
        print(f"[ATTENTION] settings.json existe déjà")
        response = input("Voulez-vous le remplacer ? (o/N): ").strip().lower()
        if response not in ['o', 'oui', 'y', 'yes']:
            print("Installation de settings.json annulée")
        else:
            # Faire une sauvegarde
            backup = settings_target.with_suffix('.json.backup')
            print(f"[INFO] Sauvegarde dans {backup.name}")
            shutil.copy2(settings_target, backup)

            # Copier le nouveau fichier
            shutil.copy2(settings_template, settings_target)
            print("[OK] settings.json installé")
    else:
        # Copier directement
        shutil.copy2(settings_template, settings_target)
        print("[OK] settings.json installé")

    # Installer activate_with_vscodium.bat
    if activate_target.exists():
        print(f"[ATTENTION] activate_with_vscodium.bat existe déjà")
        response = input("Voulez-vous le remplacer ? (o/N): ").strip().lower()
        if response not in ['o', 'oui', 'y', 'yes']:
            print("Installation de activate_with_vscodium.bat annulée")
        else:
            shutil.copy2(activate_bat, activate_target)
            print("[OK] activate_with_vscodium.bat installé")
    else:
        shutil.copy2(activate_bat, activate_target)
        print("[OK] activate_with_vscodium.bat installé")

    print()
    print("=" * 60)
    print("Installation terminée !")
    print("=" * 60)
    print()
    print("Fichiers installés dans:")
    print(f"  {vscode_dir}")
    print()
    print("Pour appliquer les changements:")
    print("  1. Fermez tous les terminaux VSCode")
    print("  2. Ouvrez un nouveau terminal")
    print("  3. La commande 'codium' devrait fonctionner")
    print()

    return True


def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        print("Usage: python install_vscode_config.py <chemin_projet>")
        print()
        print("Exemple:")
        print("  python install_vscode_config.py G:\\WarchoLife\\WarchoDevplace\\Gitlab_Applications\\mon_projet")
        print()
        return 1

    target_path = sys.argv[1]

    if install_config(target_path):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
