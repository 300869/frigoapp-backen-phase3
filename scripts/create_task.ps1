Param(
    [string]$ProjectDir = "C:\Users\henry\Desktop\freshkeeper-backend-phase3",
    [string]$TaskName = "FreshKeeper_RunScan_Every5min"
)

$batPath = Join-Path $ProjectDir "scripts\run_scan_cli.bat"

if (-not (Test-Path $batPath)) {
    Write-Error "Le fichier $batPath est introuvable."
    exit 1
}

$action = New-ScheduledTaskAction -Execute $batPath
$trigger = New-ScheduledTaskTrigger -Once (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::MaxValue)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName $TaskName -Description "Exécute le scan FreshKeeper toutes les 5 minutes" -Settings $settings
Write-Host "✅ Tâche planifiée '$TaskName' créée (toutes les 5 minutes)."
