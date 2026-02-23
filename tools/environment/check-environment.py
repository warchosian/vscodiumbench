#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification de l'environnement pour vscodiumbench.

Vérifie la présence et les versions de :
- Python
- Java (PlantUML)
- Git
- Graphviz (optionnel)

Usage:
    python tools/environment/check-environment.py
"""

import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd):
    """Exécute une commande et retourne (success, stdout, stderr)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def check_python():
    """Vérifie Python."""
    expected = "3.14+"
    success, stdout, stderr = run_command("python --version")
    if success:
        version = stdout.split()[-1]
        major, minor = map(int, version.split('.')[:2])
        if major >= 3 and minor >= 14:
            print(f"✅ Python")
            print(f"   Attendu  : {expected}")
            print(f"   Obtenu   : {version}")
            return True
        else:
            print(f"❌ Python")
            print(f"   Attendu  : {expected}")
            print(f"   Obtenu   : {version}")
            return False
    else:
        print(f"❌ Python")
        print(f"   Attendu  : {expected}")
        print(f"   Obtenu   : Non trouvé")
        print("   → Installer : https://www.python.org/downloads/")
        return False


def check_java():
    """Vérifie Java."""
    expected = "21+ (OpenJDK Temurin)"
    success, stdout, stderr = run_command("java -version")
    if success:
        # La version est généralement sur stderr
        version_line = stderr.split('\n')[0] if stderr else stdout.split('\n')[0]
        version_line = version_line.strip()

        # Extraire la version majeure (ex: 21 de "openjdk 21.0.10")
        try:
            version_num = int(version_line.split()[-1].split('.')[0]) if version_line else 0
            if version_num >= 21:
                print(f"✅ Java")
                print(f"   Attendu  : {expected}")
                print(f"   Obtenu   : {version_line}")
                return True
        except (ValueError, IndexError):
            pass

        print(f"⚠️  Java")
        print(f"   Attendu  : {expected}")
        print(f"   Obtenu   : {version_line}")
        return False
    else:
        print(f"❌ Java")
        print(f"   Attendu  : {expected}")
        print(f"   Obtenu   : Non trouvé")
        print("   → Installer OpenJDK Temurin 21+ : https://adoptium.net/")
        return False


def check_git():
    """Vérifie Git."""
    expected = "2.x+"
    success, stdout, stderr = run_command("git --version")
    if success:
        print(f"✅ Git")
        print(f"   Attendu  : {expected}")
        print(f"   Obtenu   : {stdout.strip()}")
        return True
    else:
        print(f"❌ Git")
        print(f"   Attendu  : {expected}")
        print(f"   Obtenu   : Non trouvé")
        print("   → Installer : https://git-scm.com/downloads")
        return False


def check_graphviz():
    """Vérifie Graphviz (optionnel)."""
    expected = "2.x+ (optionnel pour les diagrammes DOT)"
    success, stdout, stderr = run_command("dot -V")
    if success:
        # dot affiche la version sur stderr
        version_line = stderr.strip() if stderr else stdout.strip()
        print(f"✅ Graphviz")
        print(f"   Attendu  : {expected}")
        print(f"   Obtenu   : {version_line}")
        return True
    else:
        print(f"⚠️  Graphviz")
        print(f"   Attendu  : {expected}")
        print(f"   Obtenu   : Non trouvé")
        print("   → Installer : https://graphviz.org/download/")
        return False


def check_commitizen():
    """Vérifie Commitizen."""
    expected = "3.0+ (optionnel pour versioning avec SemVer)"
    success, stdout, stderr = run_command("cz version")
    if success:
        print(f"✅ Commitizen")
        print(f"   Attendu  : {expected}")
        print(f"   Obtenu   : {stdout.strip()}")
        return True
    else:
        print(f"⚠️  Commitizen")
        print(f"   Attendu  : {expected}")
        print(f"   Obtenu   : Non trouvé")
        print("   → Installer : pip install commitizen")
        return False


def check_poetry():
    """Vérifie Poetry."""
    expected = "1.x+ (optionnel pour gestion des dépendances)"
    success, stdout, stderr = run_command("poetry --version")
    if success:
        print(f"✅ Poetry")
        print(f"   Attendu  : {expected}")
        print(f"   Obtenu   : {stdout.strip()}")
        return True
    else:
        print(f"⚠️  Poetry")
        print(f"   Attendu  : {expected}")
        print(f"   Obtenu   : Non trouvé")
        print("   → Installer : pip install poetry")
        return False


def check_vscode():
    """Vérifie VSCode/VSCodium."""
    expected = "1.109+ (optionnel — recommandé)"
    for cmd in ["codium --version", "code --version"]:
        success, stdout, stderr = run_command(cmd)
        if success:
            editor = "VSCodium" if "codium" in cmd else "VSCode"
            version = stdout.split()[0]
            print(f"✅ {editor}")
            print(f"   Attendu  : {expected}")
            print(f"   Obtenu   : {version}")
            return True

    print(f"⚠️  VSCode/VSCodium")
    print(f"   Attendu  : {expected}")
    print(f"   Obtenu   : Non trouvé")
    print("   → Installer VSCodium : https://vscodium.com/")
    print("   → Ou VSCode : https://code.visualstudio.com/")
    return False


def check_environment_vars():
    """Vérifie les variables d'environnement importantes."""
    print("\n--- Variables d'environnement ---")

    important_vars = {
        "PYTHONHOME": "Racine Python",
        "JAVA_HOME": "Racine Java",
        "PATH": "Chemin de recherche (exécutables)"
    }

    for var, desc in important_vars.items():
        value = Path(var).expandvars() if var in ("PYTHONHOME", "JAVA_HOME") else None
        if not value or value == var:
            value = sys.modules['os'].environ.get(var, "(non défini)")

        if var == "PATH":
            print(f"ℹ️  {var} : défini (contient {len(value.split(';'))} chemins)")
        else:
            if "(non défini)" in str(value):
                print(f"ℹ️  {var} : (non défini) — {desc}")
            else:
                print(f"✅ {var} : {value}")


def main():
    """Fonction principale."""
    print("=" * 70)
    print("Vérification de l'environnement pour vscodiumbench")
    print("=" * 70)
    print()

    results = {
        "Python": check_python(),
        "Java": check_java(),
        "Git": check_git(),
        "VSCode/VSCodium": check_vscode(),
        "Graphviz": check_graphviz(),
        "Commitizen": check_commitizen(),
        "Poetry": check_poetry(),
    }

    check_environment_vars()

    print("\n" + "=" * 70)
    print("Résumé")
    print("=" * 70)

    essential = ["Python", "Java", "Git"]
    recommended = ["VSCode/VSCodium", "Graphviz", "Commitizen", "Poetry"]

    essential_ok = all(results[k] for k in essential)
    recommended_ok = all(results[k] for k in recommended)

    print(f"\n✅ Essentiels : {sum(results[k] for k in essential)}/{len(essential)}")
    print(f"⚠️  Recommandés : {sum(results[k] for k in recommended)}/{len(recommended)}")

    if essential_ok:
        print("\n✅ Environnement prêt pour vscodiumbench !")
        if not recommended_ok:
            print("   → Installez les composants recommandés pour une meilleure expérience.")
        return 0
    else:
        print("\n❌ Environnement incomplet — installez les essentiels avant de continuer.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
