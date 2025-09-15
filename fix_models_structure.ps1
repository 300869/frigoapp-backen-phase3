\
# fix_models_structure.ps1
# 1) Renomme app\models.py s'il existe
if (Test-Path ".\app\models.py") {
  Rename-Item ".\app\models.py" "models_legacy.py"
  Write-Host "Renommé app\models.py -> app\models_legacy.py"
} else {
  Write-Host "app\models.py n'existe pas — rien à renommer."
}

# 2) Crée app\models\__init__.py à partir du fichier fourni
$destDir = ".\app\models"
if (!(Test-Path $destDir)) { New-Item -ItemType Directory $destDir | Out-Null }

$src = "$PSScriptRoot\app_models__init__.py"
$dst = "$destDir\__init__.py"
Copy-Item $src $dst -Force
Write-Host "Copié __init__.py dans app\models\__init__.py"

Write-Host "OK — structure des modèles prête."
