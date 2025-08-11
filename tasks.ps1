param([string]$Task)

switch ($Task) {
  "init" {
    . .\.venv\Scripts\Activate.ps1
    if (Test-Path requirements_branchbot.txt) { pip install -r requirements_branchbot.txt -U }
    if (Test-Path requirements.final.txt) { pip install -r requirements.final.txt -U }
  }
  "test" {
    . .\.venv\Scripts\Activate.ps1
    pytest -q
  }
  "runbot" {
    . .\.venv\Scripts\Activate.ps1
    $env:PYTHONPATH = (Resolve-Path .\bots\contracts-bot).Path
    python -m contracts_bot run --since 7
  }
  default {
    Write-Host "Usage: .\tasks.ps1 [init|test|runbot]"
  }
}