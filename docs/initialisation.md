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

L'environnement a été créé avec un chemin absolu (`-p`) pour l'intégrer directement dans le répertoire Anaconda portable :

```bash
conda create -p G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\vscodiumbench python=3.14
```

> **Note** : L'option `-p` installe l'environnement à un chemin précis plutôt que dans le répertoire conda par défaut. Adaptez le chemin à votre installation Anaconda.

### 2. Activer l'environnement

```bash
conda activate G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\vscodiumbench
```

### 3. Installer les dépendances

Les scripts du projet n'utilisent que la bibliothèque standard Python, à l'exception de `commitizen` (gestion des versions) :

```bash
pip install commitizen
```

> **Note** : Le script `install_prince.py` utilise `urllib.request` (bibliothèque standard) — aucune dépendance externe n'est requise pour ce script.

### 4. Vérifier l'installation

```bash
python --version          # Python 3.14.x
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

## Status Line Claude Code

`scripts/statusline.py` affiche en temps réel dans la barre de statut de Claude Code : modèle actif, tokens utilisés, coût estimé, cache et durée de session.

### Configuration

La status line est activée dans `.claude/settings.json` :

```json
{
  "statusLine": {
    "type": "command",
    "command": "python G:\\WarchoLife\\WarchoDevplace\\Gitlab_Applications\\vscodiumbench\\scripts\\statusline.py"
  }
}
```

> **Important** : utilisez toujours un **chemin absolu**. Un chemin relatif est résolu depuis le répertoire de travail courant de la session Claude Code — s'il change en cours de session, le script ne sera plus trouvé et la status line disparaîtra silencieusement.

Claude Code pipe automatiquement un JSON de session vers le script via `stdin` à chaque mise à jour. Le script lit ce JSON et retourne une ligne formatée.

### Activer sur un autre projet

Copiez la section `statusLine` dans le `.claude/settings.json` de votre projet cible avec le chemin absolu vers `statusline.py` :

```json
{
  "statusLine": {
    "type": "command",
    "command": "python G:\\WarchoLife\\WarchoDevplace\\Gitlab_Applications\\vscodiumbench\\scripts\\statusline.py"
  }
}
```

Ou copiez directement `scripts/statusline.py` dans le projet cible et utilisez son chemin absolu.

### Prérequis

Aucune dépendance externe — le script utilise uniquement `json`, `sys` et `io` (bibliothèque standard Python).

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

Tous les chemins ci-dessous sont spécifiques à l'environnement d'origine et **doivent être adaptés** sur toute nouvelle machine.

---

### `.claude/settings.json` — Status Line

```json
"command": "G:\\WarchoLife\\WarchoPortable\\PortableWork\\Anaconda\\anaconda-3\\envs\\vscodiumbench\\python.exe G:\\WarchoLife\\WarchoDevplace\\Gitlab_Applications\\vscodiumbench\\scripts\\statusline.py"
```

| Partie | Valeur à remplacer | Description |
|---|---|---|
| `python.exe` | Chemin complet vers `python.exe` du conda env | Trouver avec `where python` après activation |
| `statusline.py` | Chemin absolu vers le script | Chemin de clonage du dépôt |

> **Pourquoi le chemin absolu est obligatoire** : Claude Code exécute la commande depuis un shell dont le `PATH` ne contient pas forcément l'environnement conda actif. Un chemin relatif ou la commande `python` seule échouera silencieusement.

---

### `scripts/activate_with_vscodium.bat`

```bat
call "G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\Scripts\activate.bat" %1
set "PATH=G:\WarchoLife\WarchoPortable\PortableCommon\VSCodium\vscodium-1.109.41146\bin;%PATH%"
```

| Ligne | Valeur à remplacer |
|---|---|
| `activate.bat` | Chemin vers le dossier `Scripts` de votre Anaconda |
| `vscodium-...` | Chemin vers le dossier `bin` de votre VSCodium |

---

### `scripts/install_prince.py` — ligne 19

```python
INSTALL_DIR = Path(r"G:\WarchoLife\WarchoPortable\PortableCommon\PrinceXml")
```

Remplacez par le chemin d'installation souhaité pour Prince XML.

---

### `.vscode/settings.json`

```json
"python.defaultInterpreterPath": "G:\\...\\python.exe",
"plantuml.jar": "G:\\...\\plantuml-x.x.jar",
"graphviz.dot": "G:\\...\\dot.exe"
```

| Clé | Valeur à remplacer |
|---|---|
| `python.defaultInterpreterPath` | Chemin vers `python.exe` du conda env du projet |
| `plantuml.jar` | Chemin vers le fichier `.jar` PlantUML téléchargé |
| `graphviz.dot` | Chemin vers l'exécutable `dot.exe` de Graphviz |

---

### `scripts/settings.json.template`

Même structure que `.vscode/settings.json` — c'est la version à distribuer sur d'autres projets. Adaptez le chemin `plantuml.jar` avant utilisation via `install_vscode_config.py`.

---

> **Astuce** : après avoir adapté tous les chemins, lancez un `Reload Window` dans VSCodium pour appliquer les changements de `.claude/settings.json`.
