param(
  [string]$RepoPath = "$PSScriptRoot\..\..",
  [string]$Python = "python"
)

Push-Location $RepoPath
try {
  & $Python -m venv .venv
  . .venv\Scripts\Activate.ps1
  pip install -r requirements_branchbot.txt
  $env:PYTHONPATH = "$RepoPath\bots\contracts-bot"
  python -m contracts_bot run --since 7
  python ops/notify.py
}
finally {
  Pop-Location
}