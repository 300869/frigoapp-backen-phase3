
Param(
  [Parameter(Mandatory=$true)][string]$ProjectRoot
)

# Stop on error
$ErrorActionPreference = "Stop"

Write-Host "== FreshKeeper rename helper =="

# 1) Run Python rename (assumes python on PATH)
python "$PSScriptRoot\bulk_rename_to_freshkeeper.py" "$ProjectRoot"

# 2) Common places to check/fix
$files = @(
  Join-Path $ProjectRoot "alembic.ini",
  Join-Path $ProjectRoot "README.md",
  Join-Path $ProjectRoot ".env",
  Join-Path $ProjectRoot "pyproject.toml",
  Join-Path $ProjectRoot "requirements.txt",
  Join-Path $ProjectRoot "requirements-dev.txt"
)
foreach ($f in $files) {
  if (Test-Path $f) { Write-Host "Check -> $f" }
}

Write-Host "Done. Next:"
Write-Host " - Update Alembic env.py imports to use 'freshkeeper' package"
Write-Host " - Run: pytest -q"
Write-Host " - Run: black . && isort --profile=black ."
