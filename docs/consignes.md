Voici le contenu complet du repertoire .claude :

  ---
  Structure

  .claude/
  ├── GUIDELINES.md        # Consignes generales de developpement
  ├── PROJECT.md           # Documentation specifique au projet Ambulon
  ├── settings.json        # Configuration active Claude Code
  ├── settings.json.bak    # Sauvegarde config hooks (inactifs)
  └── hooks.bak/           # Scripts hooks (inactifs)
      ├── event_logger.py
      ├── protect_sensitive_files.py
      └── python_validator.py

  ---
  settings.json (config active)

  - Permissions auto-approuvees : python3:*, git add:*, git commit:*
  - Status line : script tools/statusline.py
  - UI : compact desactive, suggestions desactivees

  ---
  GUIDELINES.md - Regles de developpement

  | Domaine     | Regle                                                   |
  |-------------|---------------------------------------------------------|
  | CLI         | argparse obligatoire — Typer interdit                   |
  | Entrypoint  | Pattern main(argv=None) + sys.exit(main())              |
  | Logs        | Fichiers timestampes logs/app_YYYY-MM-DD_HHhMMmSSs.log  |
  | Dependances | Gestion via Poetry                                      |
  | Git         | feature → preprod/vX.X.X → prod/vX.X.X → main           |
  | Versioning  | SemVer + Commitizen (cz commit, cz bump --changelog)    |
  | Config      | CLI > YAML > Env vars > Defauts                         |
  | Tests       | Couverture min 80%, cible 90%+, 100% pour securite/auth |

  ---
  PROJECT.md - Projet Ambulon

  - Version actuelle : 2.0.3
  - Architecture : CLI modulaire (cli/, piag/, ocr/, scan/, conversion/, processing/, encoding/, wikisi/, gitlab/)
  - API externe : PIAG RAG (preprod.api.piag.e2.rie.gouv.fr)
  - Dependances : Tesseract, Git, requests, PyYAML, pypdf, Pillow, bs4

  ---
  hooks.bak/ (inactifs — a reactiver si besoin)

  | Hook                       | Evenement                | Role                                                 |
  |----------------------------|--------------------------|------------------------------------------------------|
  | protect_sensitive_files.py | PreToolUse (Edit/Write)  | Bloque .env, .key, .pem, poetry.lock, etc. (exit 2)  |
  | python_validator.py        | PostToolUse (Edit/Write) | Verifie la syntaxe Python apres modif (non-bloquant) |
  | event_logger.py            | Tous evenements          | Affiche icones/logs pour chaque evenement Claude     |