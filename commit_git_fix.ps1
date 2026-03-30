# ===========================================
# COMMIT GIT FIX SCRIPT
# ===========================================
# Run after fix_git_security.ps1 to create the clean commit

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "COMMITTING GIT SECURITY FIX" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Create the commit
Write-Host "Creating security commit..." -ForegroundColor Yellow
git commit -m "security: centralized .gitignore, excluded credentials and secrets

- Created master root .gitignore with **/ patterns for all tiers
- Removed sub-folder .gitignore files (Bronze/Silver/Gold/Platinum)
- Excluded sensitive files:
  - credentials.json, token.pickle, token.json
  - .env files with API keys
  - logs/, inbox/, linkedin_drafts/
  - __pycache__/, *.pyc
  - IDE configs (.vscode/, .idea/)
  - Local settings (settings.local.json, settings.json)
- Prevents accidental credential commits across all tiers"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Commit successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verifying commit..." -ForegroundColor Yellow
    git log -1 --stat
} else {
    Write-Host ""
    Write-Host "Commit failed or nothing to commit." -ForegroundColor Red
    Write-Host "Run 'git status' to check what's happening." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "DONE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
