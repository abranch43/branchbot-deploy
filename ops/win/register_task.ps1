param(
  [string]$RepoPath = "$PSScriptRoot\..\..",
  [string]$Python = "python",
  [string]$Time = "07:00"
)

$env:PYTHONPATH = "$RepoPath\bots\contracts-bot"
$Action = New-ScheduledTaskAction -Execute $Python -Argument "-m contracts_bot run --since 3" -WorkingDirectory $RepoPath
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType S4U -RunLevel Highest
Register-ScheduledTask -TaskName "BranchBot_Contracts_Daily" -Action $Action -Trigger $Trigger -Principal $Principal -Force
Write-Host "Scheduled task BranchBot_Contracts_Daily registered for $Time daily."