FreshKeeper – Pack d’intégration (Points 1→5)
============================================

Contenu:
- src/services/inventory_logic.py
- src/services/alerts_logic.py
- src/services/shopping_logic.py
- src/api/shopping.py
- PATCH_main_snippet.txt

Pré-requis:
- Votre backend existe déjà (FastAPI + SQLAlchemy)
- Les modèles Product, History, Alert, StorageLocation existent (ou adaptez les noms de colonnes dans le code)

Installation (Windows PowerShell):
----------------------------------
1) Copier/coller le contenu du dossier 'src' à la racine de votre projet backend:
   C:\Users\henry\Desktop\freshkeeper-backend-phase3\src\...

2) Ouvrir votre fichier d'entrypoint (ex: freshkeeper\main.py) et ajouter ces lignes (voir PATCH_main_snippet.txt):

   from src.api.shopping import router as shopping_router
   app.include_router(shopping_router)

3) Nettoyer les __pycache__ (optionnel):
   Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

4) Démarrer l’API:
   cd "C:\Users\henry\Desktop\freshkeeper-backend-phase3"
   $env:PYTHONPATH = "."
   .\.venv\Scripts\uvicorn.exe freshkeeper.main:app --host 0.0.0.0 --port 8080 --reload

Tests rapides (PowerShell):
---------------------------
# Création produit (inventaire)
Invoke-RestMethod -Method POST http://127.0.0.1:8080/shopping/inventory/create `
  -ContentType "application/json" `
  -Body (@{
    name="Lait demi-écrémé";
    quantity=2;
    expiry_date=(Get-Date).AddDays(8).ToString("yyyy-MM-dd");
    location_id=1
  } | ConvertTo-Json)

# Analyse (couleurs + purge des périmés)
Invoke-RestMethod -Method POST http://127.0.0.1:8080/shopping/analyze/refresh

# Construire AA (base + saisies utilisateur)
$rows = @(
  @{ name="lait demi-écrémé"; qty=1 },
  @{ name="banane"; qty=6 }
)
Invoke-RestMethod -Method POST http://127.0.0.1:8080/shopping/aa/build `
  -ContentType "application/json" `
  -Body (@{ rows = $rows } | ConvertTo-Json)

# AA -> BB (achat réel)
$purchases = @(
  @{ name="lait demi-écrémé"; qty=2; expiry_date=(Get-Date).AddDays(15).ToString("yyyy-MM-dd") },
  @{ name="banane"; qty=6; expiry_date=(Get-Date).AddDays(5).ToString("yyyy-MM-dd") }
)
Invoke-RestMethod -Method POST http://127.0.0.1:8080/shopping/bb/checkout `
  -ContentType "application/json" `
  -Body (@{ purchases = $purchases } | ConvertTo-Json)

# BB -> CC (classement des achats)
$placements = @(
  @{ name="lait demi-écrémé"; place="Frigo" },
  @{ name="banane"; place="Cuisine" }
)
Invoke-RestMethod -Method POST http://127.0.0.1:8080/shopping/cc/classify `
  -ContentType "application/json" `
  -Body (@{ bb = $purchases; placements = $placements } | ConvertTo-Json)

Notes:
- Adaptez les imports DB et les noms de colonnes si nécessaire (expiry_date, location_id, etc.).
- Si vous avez une colonne Product.color, dé-commentez la mise à jour correspondante.
