# ===========================================
# GIT SECURITY REPAIR SCRIPT
# ===========================================
# This script will:
# 1. Remove all .gitignore files from sub-folders (Bronze, Silver, Gold, Platinum)
# 2. Reset Git index completely
# 3. Re-add files based ONLY on the root .gitignore
# 4. Create a clean commit excluding secrets
#
# Run from repository root: .\fix_git_security.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "GIT SECURITY & .GITIGNORE REPAIR" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Find and remove all sub-folder .gitignore files
Write-Host "[Step 1] Finding sub-folder .gitignore files..." -ForegroundColor Yellow
$subfolderGitignores = Get-ChildItem -Path ".\Bronze_Tier", ".\Silver_Tier", ".\Gold_Tier", ".\Platinum_Tier" -Recurse -Filter ".gitignore" -ErrorAction SilentlyContinue

if ($subfolderGitignores.Count -gt 0) {
    Write-Host "Found $($subfolderGitignores.Count) .gitignore file(s) in sub-folders:" -ForegroundColor Yellow
    foreach ($file in $subfolderGitignores) {
        Write-Host "  - $($file.FullName)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "Removing sub-folder .gitignore files..." -ForegroundColor Yellow
    foreach ($file in $subfolderGitignores) {
        Remove-Item -Path $file.FullName -Force
        Write-Host "  [REMOVED] $($file.FullName)" -ForegroundColor Red
    }
} else {
    Write-Host "No sub-folder .gitignore files found." -ForegroundColor Green
}

Write-Host ""

# Step 2: Remove .gitignore from Git tracking (if it was tracked in subfolders)
Write-Host "[Step 2] Removing sub-folder .gitignore files from Git index..." -ForegroundColor Yellow
git rm --cached Bronze_Tier\.gitignore 2>$null | Out-Null
git rm --cached Silver_Tier\.gitignore 2>$null | Out-Null
git rm --cached Gold_Tier\.gitignore 2>$null | Out-Null
git rm --cached Platinum_Tier\.gitignore 2>$null | Out-Null
Write-Host "  Done." -ForegroundColor Green

Write-Host ""

# Step 3: Reset Git index completely
Write-Host "[Step 3] Resetting Git index (unstaging everything)..." -ForegroundColor Yellow
git reset HEAD
Write-Host "  Git index cleared." -ForegroundColor Green

Write-Host ""

# Step 4: Clean Git cache
Write-Host "[Step 4] Cleaning Git cache..." -ForegroundColor Yellow
git rm -r --cached . 2>$null
Write-Host "  Cache cleared." -ForegroundColor Green

Write-Host ""

# Step 5: Re-add everything based on root .gitignore
Write-Host "[Step 5] Re-adding files based on root .gitignore..." -ForegroundColor Yellow
git add .
Write-Host "  Files re-added according to root .gitignore rules." -ForegroundColor Green

Write-Host ""

# Step 6: Show what will be committed
Write-Host "[Step 6] Files that will be committed:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Step 7: Show what's being ignored (security check)
Write-Host "[Step 7] Files being IGNORED (security check):" -ForegroundColor Yellow
git status --ignored | Select-String "Ignored files" -Context 0,50
Write-Host ""

# Step 8: Verify secrets are excluded
Write-Host "[Step 8] Security Verification - Checking for secrets..." -ForegroundColor Yellow
$secretsToCheck = @(
    "**/credentials.json",
    "**/token.pickle",
    "**/token.json",
    "**/.env",
    "**/client_secret.json"
)

$secretsFound = $false
foreach ($secret in $secretsToCheck) {
    $found = Get-ChildItem -Path . -Include $secret -Recurse -File -ErrorAction SilentlyContinue
    if ($found) {
        foreach ($file in $found) {
            $gitStatus = git check-ignore -v $file.FullName 2>$null
            if ($gitStatus) {
                Write-Host "  [PROTECTED] $($file.FullName) - Correctly ignored" -ForegroundColor Green
            } else {
                Write-Host "  [WARNING] $($file.FullName) - NOT ignored!" -ForegroundColor Red
                $secretsFound = $true
            }
        }
    }
}

if (-not $secretsFound) {
    Write-Host "  All secrets are properly protected." -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "READY FOR COMMIT" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps (run manually):" -ForegroundColor Yellow
Write-Host "  git commit -m `"security: centralized .gitignore, excluded secrets`"" -ForegroundColor White
Write-Host ""
Write-Host "Or run the companion script: .\commit_git_fix.ps1" -ForegroundColor White
Write-Host ""
