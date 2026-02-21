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
| Python | 3.14+ | Langage de base (inclus dans Python) |
| VSCodium | 1.109+ | Editeur principal |
| Git | 2.x | Gestion de version |
| Java (JRE/JDK) | 21+ | Requis par PlantUML (OpenJDK Temurin 21.0.10+) |
| Graphviz | 2.x | Requis pour les diagrammes DOT |
| Prince XML | 15.3 | Requis pour generation PDF (optionnel) |

---

## Création de l'environnement virtuel

Deux approches sont possibles. Choisissez celle qui correspond à votre installation.

### Option A : Avec `python -m venv` (standard)

Créez un environnement virtuel isolé :

```bash
python -m venv venv
```

Ou dans un répertoire contrôlé :

```bash
python -m venv G:\MyEnvs\vscodiumbench
```

Cela crée un dossier contenant l'environnement virtuel Python avec `Scripts/python.exe`.

### Option B : Avec Conda (Anaconda/Miniconda portable)

Créez un environnement dans un chemin absolu pour l'intégrer au portable :

```bash
conda create -p G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\vscodiumbench python=3.14
```

Adaptez le chemin à votre installation Anaconda — l'important est que l'env soit dans un **répertoire contrôlé et portable**.

### 2. Activer l'environnement

**Avec venv (Option A) — Windows cmd :**
```bash
venv\Scripts\activate.bat
```

**Avec venv (Option A) — Windows PowerShell :**
```powershell
venv\Scripts\Activate.ps1
```

**Avec venv (Option A) — Linux/macOS :**
```bash
source venv/bin/activate
```

**Avec Conda (Option B) — Tous les OS :**
```bash
conda activate G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\vscodiumbench
```

Vous devriez voir `(venv)` ou le nom de l'env Conda au début de votre prompt.

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
│   ├── install_prince.bat          # Installe Prince XML (bat wrapper)
│   ├── install_prince.py           # Télécharge et installe Prince XML 15.3
│   ├── install_vscode_config.py    # Copie la config VSCode dans un projet cible
│   ├── settings.json.template      # Template de config VSCode à distribuer
│   ├── statusline.py               # Status line Claude Code (tokens, coût, temps)
│   └── vscode_extensions/
│       ├── install_vscode_extensions.py    # Installe les extensions recommandées
│       └── uninstall_vscode_extensions.py  # Désinstalle les extensions redondantes
├── src/
│   └── app/                        # Code source (md2mmd, conversion, CLI)
├── tests/                          # Tests unitaires
├── venv/ (optionnel)               # Environnement virtuel Python (python -m venv)
├── .gitignore
├── CHANGELOG.md                    # Généré par commitizen
├── LICENSE                         # MIT
└── pyproject.toml                  # Configuration Poetry et commitizen
```

---

## Utilisation des scripts

### Installer la config VSCode dans un projet

```bash
python scripts/install_vscode_config.py <chemin_vers_le_projet>
```

Copie `settings.json.template` et `activate_with_vscodium.bat` dans le dossier `.vscode/` du projet cible.

### Installer les extensions VSCode/VSCodium pour les diagrammes

Le script `scripts/vscode_extensions/install_vscode_extensions.py` installe les extensions nécessaires au rendu des diagrammes PlantUML, Mermaid et Graphviz.

```bash
# Mode 1 : extensions ESSENTIELLES seulement
python scripts/vscode_extensions/install_vscode_extensions.py --mode 1

# Mode 2 : ESSENTIELLES + FORTEMENT RECOMMANDÉES (défaut)
python scripts/vscode_extensions/install_vscode_extensions.py --mode 2

# Mode 3 : TOUTES les extensions
python scripts/vscode_extensions/install_vscode_extensions.py --mode 3
```

**Extensions installées par priorité :**

| Priorité | Extension | Rôle |
|---|---|---|
| ESSENTIEL | `jebbs.plantuml` | Rendu PlantUML |
| ESSENTIEL | `bierner.markdown-mermaid` | Rendu Mermaid dans Markdown |
| ESSENTIEL | `tintinweb.graphviz-interactive-preview` | Preview interactif Graphviz |
| ESSENTIEL | `geeklearningio.graphviz-markdown-preview` | Graphviz dans Markdown |
| FORTEMENT RECOMMANDÉ | `shd101wyy.markdown-preview-enhanced` | Preview tout-en-un (PlantUML + Mermaid + Graphviz) |
| OPTIONNEL | `vstirbu.vscode-mermaid-preview` | Preview dédié Mermaid |
| OPTIONNEL | `hediet.vscode-drawio` | Éditeur Draw.io intégré |
| OPTIONNEL | `gera2ld.markmap-vscode` | Mind maps depuis Markdown |

### Tester les extensions avec `_diagrams/multidiagrams.md`

Après installation, vérifiez que tout fonctionne en ouvrant le fichier de test :

```bash
# Ouvrir dans VSCodium
codium _diagrams/multidiagrams.md
```

1. Ouvrez `_diagrams/multidiagrams.md` dans VSCodium
2. Ouvrez la preview (`Ctrl+Shift+V` ou clic droit → *Open Preview*)
3. Vérifiez que les **9 diagrammes** s'affichent correctement :
   - 3 diagrammes **PlantUML** (séquence, classes, états)
   - 3 diagrammes **Mermaid** (flowchart, séquence, gantt)
   - 3 diagrammes **Graphviz/DOT** (graphe orienté, non orienté, arbre)

> Si un type de diagramme n'apparaît pas, relancez le mode 2 ou 3 du script d'installation et faites un **Reload Window**.

### Installer Prince XML

```bash
python scripts/install_prince.py
```

### Activer l'environnement virtuel + VSCodium dans un terminal

**Depuis cmd :**
```bat
venv\Scripts\activate.bat && codium .
```

**Depuis PowerShell :**
```powershell
venv\Scripts\Activate.ps1; codium .
```

**Depuis bash (Git Bash, WSL, etc.) :**
```bash
source venv/Scripts/activate && codium .
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

### Trouver le chemin python exact

Après activation de votre environnement (venv ou Conda), utilisez :

```bash
where python
```

Cela retourne le chemin complet vers `python.exe` dans votre environnement. Copiez ce chemin dans les configurations.

**Exemple :**
```
G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\vscodiumbench\python.exe
```

Utilisez ce chemin pour :

---

### `.claude/settings.json` — Status Line

**Avec venv :**
```json
"command": "C:\\Users\\username\\vscodiumbench\\venv\\Scripts\\python.exe C:\\Users\\username\\vscodiumbench\\scripts\\statusline.py"
```

**Avec Conda :**
```json
"command": "G:\\WarchoLife\\WarchoPortable\\PortableWork\\Anaconda\\anaconda-3\\envs\\vscodiumbench\\python.exe G:\\WarchoLife\\WarchoDevplace\\Gitlab_Applications\\vscodiumbench\\scripts\\statusline.py"
```

| Partie | Valeur à remplacer | Description |
|---|---|---|
| `python.exe` | Chemin complet vers python.exe | Obtenu via `where python` après activation |
| `statusline.py` | Chemin absolu vers le script | Chemin de clonage du dépôt |

**Pour trouver le chemin Python après activation :**
```bash
where python
```

> **Pourquoi le chemin absolu est obligatoire** : Claude Code exécute la commande depuis un shell dont le `PATH` ne contient pas forcément l'environnement actif. Un chemin relatif ou la commande `python` seule échouera silencieusement.

---

### Activation manuelle de l'environnement

**Avec venv — Windows cmd :**
```bat
venv\Scripts\activate.bat
```

**Avec venv — Windows PowerShell :**
```powershell
venv\Scripts\Activate.ps1
```

**Avec Conda — Tous les OS :**
```bash
conda activate G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\vscodiumbench
```

Après activation, utilisez simplement `python` ou `pip` sans chemin absolu.

Pour trouver le chemin exact du python activé :
```bash
where python
```

---

### `scripts/install_prince.py` — ligne 19

```python
INSTALL_DIR = Path(r"G:\WarchoLife\WarchoPortable\PortableCommon\PrinceXml")
```

Remplacez par le chemin d'installation souhaité pour Prince XML.

---

### `.vscode/settings.json`

**Avec venv :**
```json
"python.defaultInterpreterPath": "C:\\Users\\username\\vscodiumbench\\venv\\Scripts\\python.exe",
"plantuml.jar": "G:\\...\\plantuml-x.x.jar",
"graphviz.dot": "G:\\...\\dot.exe"
```

**Avec Conda :**
```json
"python.defaultInterpreterPath": "G:\\WarchoLife\\WarchoPortable\\PortableWork\\Anaconda\\anaconda-3\\envs\\vscodiumbench\\python.exe",
"plantuml.jar": "G:\\...\\plantuml-x.x.jar",
"graphviz.dot": "G:\\...\\dot.exe"
```

| Clé | Valeur à remplacer |
|---|---|
| `python.defaultInterpreterPath` | Chemin retourné par `where python` après activation |
| `plantuml.jar` | Chemin vers le fichier `.jar` PlantUML téléchargé |
| `graphviz.dot` | Chemin vers l'exécutable `dot.exe` de Graphviz |

---

### `scripts/settings.json.template`

Même structure que `.vscode/settings.json` — c'est la version à distribuer sur d'autres projets. Adaptez le chemin `plantuml.jar` avant utilisation via `install_vscode_config.py`.

---

> **Astuce** : après avoir adapté tous les chemins, lancez un `Reload Window` dans VSCodium pour appliquer les changements de `.claude/settings.json`.
