Phase 6 — Automatisation persistante du scan (Windows)

1) Copier ce dossier "scripts" dans ton projet.
2) Vérifier le chemin dans run_scan_cli.bat (PROJECT_DIR).
3) Créer la tâche Windows :
   - Ouvrir PowerShell en Administrateur
   - cd "C:\Users\henry\Desktop\freshkeeper-backend-phase3\scripts"
   - .\create_task.ps1
4) Tester manuellement :
   .\scripts\run_scan_cli.bat
