param(
  [ValidateSet("install","uninstall")] [string]$Action = "install",
  [string]$Root = (Get-Location).Path
)

$hourly = "BranchBot - Hunt (Hourly)"
$daily  = "BranchBot - Daily Alert (8AM)"

if ($Action -eq "uninstall") {
  if (Get-ScheduledTask -TaskName $hourly -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $hourly -Confirm:$false }
  if (Get-ScheduledTask -TaskName $daily  -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $daily  -Confirm:$false }
  "Uninstalled tasks."; exit 0
}

& .\.venv\Scripts\activate
if (-not $?) { throw "Activate venv before running schedule.ps1" }

$act1 = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Root\ops\logwrap.ps1`" runbot"
$trg1 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Minutes 60) -RepetitionDuration (New-TimeSpan -Days 30)

$act2 = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Root\ops\logwrap.ps1`" scan_notify"
$trg2 = New-ScheduledTaskTrigger -Daily -At 8:00am

if (Get-ScheduledTask -TaskName $hourly -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $hourly -Confirm:$false }
if (Get-ScheduledTask -TaskName $daily  -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $daily  -Confirm:$false }

Register-ScheduledTask -TaskName $hourly -Action $act1 -Trigger $trg1 -Description "Scan portals and write results"
Register-ScheduledTask -TaskName $daily  -Action $act2 -Trigger $trg2 -Description "Email/CSV daily summary"
"Installed tasks: `$hourly, `$daily"