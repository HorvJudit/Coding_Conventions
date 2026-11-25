coding-conventions/
├── conventions/
│   ├── core_conventions.md
│   └── [language]_conventions.md
└── src/
    ├── config.py              # Környezeti változók és konstansok
    ├── github_client.py       # GitHub API hívások (diff, fájlok, komment)
    ├── convention_loader.py   # Releváns .md szabályok betöltése
    ├── llm_client.py          # Prompt összeállítása és LLM API hívás
    ├── reporting.py           # Komment formázása és naplózás
    └── main.py                # Belépési pont (a folyamat vezérlése)