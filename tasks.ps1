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
    python -m contracts_bot run --since 30
  }
  "scan_notify" {
    . .\.venv\Scripts\Activate.ps1
    $env:PYTHONPATH = (Resolve-Path .\bots\contracts-bot).Path
    $json = python -m contracts_bot run --since 30
    $csvPath = $json | python ops/notify.py
    "CSV => $csvPath"
  }
  "email_test" {
    . .\.venv\Scripts\Activate.ps1
    python ops/test_email.py
  }
  "health" {
    . .\.venv\Scripts\Activate.ps1
    python ops/healthcheck.py
  }
  default {
    Write-Host "Usage: .\tasks.ps1 [init|test|runbot]"
  }
}