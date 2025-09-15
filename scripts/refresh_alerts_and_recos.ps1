$base = "http://127.0.0.1:8000"
Invoke-RestMethod -Method Post "$base/admin/alerts/scan"    | Out-Null
Invoke-RestMethod -Method Post "$base/admin/reco/refresh"   | Out-Null
