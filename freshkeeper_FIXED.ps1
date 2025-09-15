
Param(
  [Parameter(Mandatory=$true)][string]$ProjectRoot
)

$ErrorActionPreference = "Stop"
Write-Host "== FreshKeeper rename helper (FIXED) =="

# Ensure we run from the script's folder
Set-Location -Path $PSScriptRoot

# Use python to run the fixed script
python ".\bulk_rename_to_freshkeeper_FIXED.py" "$ProjectRoot"

# Guidance
$files = @(
  Join-Path $ProjectRoot "alembic.ini",
  Join-Path $ProjectRoot "alembic\env.py",
  Join-Path $ProjectRoot "README.md",
  Join-Path $ProjectRoot ".env",
  Join-Path $ProjectRoot "pyproject.toml",
  Join-Path $ProjectRoot "requirements.txt",
  Join-Path $ProjectRoot "requirements-dev.txt"
)
Write-Host "Check the following files if present:"
$files | ForEach-Object { if (Test-Path $_) { Write-Host "  - $_" } }

Write-Host "`nNext steps:"
Write-Host "  1) Verify Alembic imports (env.py uses freshkeeper.*)"
Write-Host "  2) Run: pytest -q"
Write-Host "  3) Run: black . && isort --profile=black ."
