# Initialisation du projet vscodiumbench

## Présentation

`vscodiumbench` est un dépôt de configuration et d'outillage pour VSCode/VSCodium. Il fournit :

- Des scripts d'installation de la configuration VSCode/VSCodium sur de nouveaux projets
- Des scripts de gestion des extensions recommandées
- Un script d'installation de Prince XML (rendu PDF)
- Un script de status line pour Claude Code
- Des exemples de diagrammes (PlantUML, Mermaid, Graphviz)

---

## Prérequis

| Outil | Version minimale | Notes |
|---|---|---|
| Anaconda / Miniconda | 3.x | Gestionnaire d'environnements Python |
| VSCodium | 1.109+ | Editeur principal |
| Git | 2.x | Gestion de version |
| Java (JRE/JDK) | 11+ | Requis par PlantUML |
| Graphviz | 2.x | Requis pour les diagrammes DOT |
| Prince XML | 15.3 | Requis pour generation PDF (optionnel) |

---

## Création de l'environnement conda

### 1. Créer l'environnement

```bash
conda create -n vscodiumbench python=3.11 -y
```

### 2. Activer l'environnement

```bash
conda activate vscodiumbench
```

### 3. Installer les dépendances

Les scripts du projet n'utilisent que la bibliothèque standard Python, à l'exception de `commitizen` (gestion des versions) :

```bash
pip install commitizen
```

> **Note** : Le script `install_prince.py` utilise `urllib.request` (bibliothèque standard) — aucune dépendance externe n'est requise pour ce script.

### 4. Vérifier l'installation

```bash
python --version          # Python 3.11.x
cz version                # commitizen x.x.x
```

---

## Clonage du dépôt

```bash
git clone <URL_DU_REPO> vscodiumbench
cd vscodiumbench
```

---

## Structure du projet

```
vscodiumbench/
├── .claude/                        # Configuration Claude Code
│   ├── GUIDELINES.md               # Directives générales de développement
│   ├── PROJECT.md                  # Documentation du projet Ambulon (référence)
│   └── settings.json               # Paramètres Claude Code (hooks, UI, permissions)
├── .vscode/
│   └── settings.json               # Configuration VSCode/VSCodium du workspace
├── _diagrams/
│   ├── multidiagrams.md            # Exemples PlantUML / Mermaid / Graphviz
│   └── multidiagrams.pdf           # PDF généré
├── docs/
│   └── initialisation.md           # Ce fichier
├── scripts/
│   ├── activate_with_vscodium.bat  # Active conda + ajoute VSCodium au PATH
│   ├── install_prince.bat          # Installe Prince XML (bat wrapper)
│   ├── install_prince.py           # Télécharge et installe Prince XML 15.3
│   ├── install_vscode_config.py    # Copie la config VSCode dans un projet cible
│   ├── settings.json.template      # Template de config VSCode à distribuer
│   ├── statusline.py               # Status line Claude Code (tokens, coût, temps)
│   └── vscode/
│       ├── install_vscode_extensions.py    # Installe les extensions recommandées
│       └── uninstall_vscode_extensions.py  # Désinstalle les extensions redondantes
├── .gitignore
├── CHANGELOG.md                    # Généré par commitizen
└── pyproject.toml                  # Configuration commitizen
```

---

## Utilisation des scripts

### Installer la config VSCode dans un projet

```bash
python scripts/install_vscode_config.py <chemin_vers_le_projet>
```

Copie `settings.json.template` et `activate_with_vscodium.bat` dans le dossier `.vscode/` du projet cible.

### Installer les extensions VSCode recommandées

```bash
# Mode 1 : extensions ESSENTIELLES seulement
python scripts/vscode/install_vscode_extensions.py --mode 1

# Mode 2 : ESSENTIELLES + FORTEMENT RECOMMANDÉES (défaut)
python scripts/vscode/install_vscode_extensions.py --mode 2

# Mode 3 : TOUTES les extensions
python scripts/vscode/install_vscode_extensions.py --mode 3
```

### Installer Prince XML

```bash
python scripts/install_prince.py
```

### Activer conda + VSCodium dans un terminal

```bat
scripts\activate_with_vscodium.bat <nom_env_conda>
```

---

## Workflow Git (selon GUIDELINES.md)

Ce projet suit le workflow **Option B - Production First** :

```
feature/xxx  →  preprod/vX.X.X-stable  →  prod/vX.X.X-stable  →  main
```

### Développement d'une nouvelle fonctionnalité

```bash
# 1. Créer une feature branch depuis main
git checkout main
git checkout -b feature/ma-fonctionnalite

# 2. Développer et commiter avec commitizen
git add .
cz commit

# 3. Bump de version avant merge en preprod
cz bump --changelog

# 4. Créer la branche preprod
git checkout -b preprod/v0.2.0-stable
git push origin preprod/v0.2.0-stable --tags
```

### Versioning (SemVer)

| Type de changement | Incrément |
|---|---|
| Correctif / fix | PATCH (0.1.0 → 0.1.1) |
| Nouvelle fonctionnalité | MINOR (0.1.0 → 0.2.0) |
| Rupture de compatibilité | MAJOR (0.1.0 → 1.0.0) |

---

## Adaptation des chemins locaux

Les fichiers suivants contiennent des chemins absolus spécifiques à l'environnement local. Ils doivent être adaptés lors du déploiement sur une nouvelle machine :

| Fichier | Chemin à adapter |
|---|---|
| `scripts/activate_with_vscodium.bat` | Chemin Anaconda et VSCodium |
| `scripts/install_prince.py` | `INSTALL_DIR` (ligne 19) |
| `.vscode/settings.json` | Chemins Python, PlantUML JAR, Graphviz |
| `scripts/settings.json.template` | Chemin PlantUML JAR |

> Le template `scripts/settings.json.template` est la version à distribuer — adaptez-le avant de l'utiliser sur une nouvelle machine via `install_vscode_config.py`.
