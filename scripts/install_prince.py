#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'installation automatique de Prince XML
Télécharge et installe Prince 15.3 (version non-commerciale)
"""

import os
import sys
import shutil
import zipfile
import urllib.request
import subprocess
from pathlib import Path

# Configuration
PRINCE_VERSION = "15.3"
PRINCE_URL = f"https://www.princexml.com/download/prince-{PRINCE_VERSION}-win64.zip"
INSTALL_DIR = Path(r"G:\WarchoLife\WarchoPortable\PortableCommon\PrinceXml")
TEMP_ZIP = Path(os.environ.get("TEMP", "/tmp")) / f"prince-{PRINCE_VERSION}-win64.zip"


def print_header(message):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 60)
    print(message)
    print("=" * 60 + "\n")


def check_existing_installation():
    """Vérifie si Prince est déjà installé"""
    try:
        result = subprocess.run(
            ["prince", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version_line = result.stdout.strip().split('\n')[0]
        print(f"[INFO] {version_line} est déjà installé")

        # Demander si on veut réinstaller
        response = input("Voulez-vous réinstaller ? (o/N): ").strip().lower()
        if response not in ['o', 'oui', 'y', 'yes']:
            print("Installation annulée.")
            return False
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return True


def download_prince():
    """Télécharge Prince"""
    print(f"[1/3] Téléchargement de Prince {PRINCE_VERSION}...")
    print(f"URL: {PRINCE_URL}")

    try:
        # Créer un hook de progression
        def reporthook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 / total_size, 100)
                sys.stdout.write(f"\r  Progression: {percent:.1f}% ({downloaded // 1024 // 1024} MB)")
                sys.stdout.flush()

        urllib.request.urlretrieve(PRINCE_URL, TEMP_ZIP, reporthook)
        print("\n[OK] Téléchargement terminé")
        return True
    except Exception as e:
        print(f"\n[ERREUR] Échec du téléchargement: {e}")
        return False


def extract_prince():
    """Extrait l'archive ZIP"""
    print(f"[2/3] Extraction de l'archive...")

    try:
        # Créer le dossier d'installation si nécessaire
        INSTALL_DIR.mkdir(parents=True, exist_ok=True)

        # Extraire l'archive
        with zipfile.ZipFile(TEMP_ZIP, 'r') as zip_ref:
            zip_ref.extractall(INSTALL_DIR)

        print("[OK] Extraction terminée")
        return True
    except Exception as e:
        print(f"[ERREUR] Échec de l'extraction: {e}")
        return False
    finally:
        # Nettoyer le fichier temporaire
        if TEMP_ZIP.exists():
            TEMP_ZIP.unlink()


def verify_installation():
    """Vérifie que l'installation a réussi"""
    print(f"[3/3] Vérification de l'installation...")

    prince_exe = INSTALL_DIR / f"prince-{PRINCE_VERSION}-win64" / "bin" / "prince.exe"

    if not prince_exe.exists():
        print(f"[ERREUR] Prince n'a pas été installé correctement")
        print(f"Fichier attendu: {prince_exe}")
        return False

    try:
        result = subprocess.run(
            [str(prince_exe), "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version_info = result.stdout.strip().split('\n')[0]
        print(f"[OK] {version_info}")

        print_header("Installation réussie !")
        print("Prince est installé dans:")
        print(f"  {INSTALL_DIR / f'prince-{PRINCE_VERSION}-win64'}\n")
        print("Exécutable:")
        print(f"  {prince_exe}\n")

        # Vérifier si prince est dans le PATH
        try:
            subprocess.run(["prince", "--version"], capture_output=True, check=True)
            print("[OK] Prince est accessible via le PATH")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[ATTENTION] Prince n'est pas dans le PATH")
            print("Ajoutez ce chemin au PATH système:")
            print(f"  {INSTALL_DIR / f'prince-{PRINCE_VERSION}-win64' / 'bin'}")

        return True
    except Exception as e:
        print(f"[ERREUR] Impossible de vérifier l'installation: {e}")
        return False


def main():
    """Point d'entrée principal"""
    print_header(f"Installation de Prince XML {PRINCE_VERSION}")

    # Vérifier l'installation existante
    if not check_existing_installation():
        return 0

    # Télécharger
    if not download_prince():
        return 1

    # Extraire
    if not extract_prince():
        return 1

    # Vérifier
    if not verify_installation():
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
