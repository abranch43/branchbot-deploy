param([string]$Cmd = "runbot")
$root = (Get-Location).Path
$logd = Join-Path $root "data\logs"; if (!(Test-Path $logd)) { New-Item -ItemType Directory -Force $logd | Out-Null }
$log  = Join-Path $logd ("task_" + (Get-Date -UFormat "%Y%m%dT%H%M%S") + ".log")
"[$(Get-Date -Format o)] Starting task: $Cmd" | Out-File -FilePath $log -Encoding utf8
try{
  & "$root\tasks.ps1" $Cmd 2>&1 | Tee-Object -FilePath $log -Append
  "[$(Get-Date -Format o)] Task completed." | Out-File -FilePath $log -Append -Encoding utf8
} catch {
  "[$(Get-Date -Format o)] ERROR: $_" | Out-File -FilePath $log -Append -Encoding utf8
  exit 1
}