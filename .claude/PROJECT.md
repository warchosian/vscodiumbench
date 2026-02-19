# vscodiumbench — Documentation du projet

## Présentation

`vscodiumbench` est un dépôt de configuration et d'outillage pour VSCode/VSCodium.
Il fournit des scripts réutilisables, une configuration standard et des outils de développement
pour bootstrapper rapidement tout nouveau projet Python.

**Dépôt GitHub** : https://github.com/warchosian/vscodiumbench
**Version actuelle** : `0.1.0` (définie dans `pyproject.toml`)
**Licence** : MIT

---

## Architecture des modules

```
vscodiumbench/
├── src/
│   └── app/
│       └── conversion/
│           ├── __init__.py
│           └── commands/
│               ├── __init__.py
│               └── md2mmd.py          ← Convertisseur PlantUML/Graphviz → Mermaid
├── scripts/
│   ├── statusline.py                  ← Status line Claude Code
│   ├── install_vscode_config.py       ← Copie config VSCode dans un projet cible
│   ├── install_prince.py              ← Installation Prince XML (PDF)
│   ├── install_prince.bat             ← Wrapper bat pour install_prince.py
│   └── vscode_extensions/
│       ├── install_vscode_extensions.py    ← Installation extensions recommandées
│       └── uninstall_vscode_extensions.py  ← Désinstallation extensions redondantes
├── tests/
│   └── unit/
│       └── conversion/
│           └── commands/
│               └── test_md2mmd.py     ← Tests unitaires md2mmd.py (85% couverture)
├── _diagrams/
│   ├── multidiagrams.md               ← Exemples PlantUML / Mermaid / Graphviz
│   └── multidiagrams.mmd.md           ← Version convertie (généré par md2mmd.py)
├── .vscode/
│   ├── settings.json                  ← Config VSCode/VSCodium du workspace
│   └── activate_with_vscodium.bat     ← Active conda + ajoute VSCodium au PATH
├── docs/
│   └── initialisation.md              ← Guide setup complet du projet
├── .claude/
│   ├── GUIDELINES.md                  ← Directives générales de développement
│   ├── PROJECT.md                     ← Ce fichier
│   └── settings.json                  ← Paramètres Claude Code
├── .gitignore
├── LICENSE                            ← MIT
├── pytest.ini                         ← Configuration pytest
└── pyproject.toml                     ← Config Commitizen (SemVer)
```

---

## Commandes disponibles

### Conversion de diagrammes

```bash
# Convertir PlantUML/Graphviz → Mermaid dans un fichier Markdown
python src/app/conversion/commands/md2mmd.py <fichier.md>
# Génère : <fichier>.mmd.md dans le même répertoire

# Tester avec les exemples fournis
python src/app/conversion/commands/md2mmd.py _diagrams/multidiagrams.md
```

**Diagrammes supportés :**
| Source | Détection | Cible |
|--------|-----------|-------|
| PlantUML séquence | `actor`, `participant`, `->` | `sequenceDiagram` |
| PlantUML classe | `class X {` | `classDiagram` |
| PlantUML état | `[*]` | `stateDiagram-v2` |
| Graphviz digraph | `digraph {` | `flowchart TD/LR` |
| Graphviz graph | `graph {` | `flowchart TD` + warning |

### Configuration VSCode

```bash
# Copier la config VSCode dans un autre projet
python scripts/install_vscode_config.py <chemin_projet>

# Installer les extensions recommandées
python scripts/vscode_extensions/install_vscode_extensions.py --mode 2

# Désinstaller les extensions redondantes
python scripts/vscode_extensions/uninstall_vscode_extensions.py
```

### Installation outils

```bash
# Installer Prince XML (rendu PDF)
python scripts/install_prince.py
```

---

## Environnement conda

```bash
# Création (chemin absolu de l'env)
conda create -p G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\vscodiumbench python=3.14

# Activation
conda activate G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\vscodiumbench

# Dépendances
pip install commitizen pytest pytest-cov
```

---

## Tests

```bash
# Lancer tous les tests
python -m pytest

# Avec couverture
python -m pytest --cov=src --cov-report=term-missing

# Tests md2mmd uniquement
python -m pytest tests/unit/conversion/commands/test_md2mmd.py -v
```

**Couverture actuelle :** 85% (minimum requis : 80%)

---

## Workflow Git (GUIDELINES.md)

```
feature/xxx  →  preprod/v0.X.X-stable  →  prod/v0.X.X-stable  →  main
```

```bash
# Nouveau commit conventionnel
cz commit

# Bump de version + changelog
cz bump --changelog

# Push avec tags
git push origin main --follow-tags
```

---

## Chemins locaux à adapter

| Fichier | Ce qui change |
|---------|---------------|
| `.claude/settings.json` | `python.exe` absolu + chemin `statusline.py` |
| `scripts/activate_with_vscodium.bat` | Chemins Anaconda et VSCodium |
| `scripts/install_prince.py` ligne 19 | `INSTALL_DIR` |
| `.vscode/settings.json` | `python.defaultInterpreterPath`, `plantuml.jar`, `graphviz.dot` |
| `scripts/settings.json.template` | `plantuml.jar` |

---

## Dépendances externes

| Outil | Rôle | Requis par |
|-------|------|------------|
| Anaconda | Gestionnaire environnements Python | Tous les scripts |
| VSCodium | Éditeur principal | `activate_with_vscodium.bat` |
| Java JRE 11+ | Rendu PlantUML | Extension `jebbs.plantuml` |
| Graphviz | Rendu DOT | Extension `tintinweb.graphviz-interactive-preview` |
| Prince XML 15.3 | Génération PDF | `install_prince.py` |
| Git | Gestion de version | Workflow Git |
