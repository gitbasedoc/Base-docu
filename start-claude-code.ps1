# ============================================
# Script de lancement Claude Code
# Projet : KB Support Basedoc
# ============================================

# Configuration
$WorkDir = "F:\Claude_code\Base-de-connaissances"
$GitRepo = "https://github.com/gitbasedoc/Base-docu.git"
$GitBranch = "claude/it-knowledge-base-app-014pMzfzMdL8z4wxND1BWqb8"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Claude Code - KB Support Basedoc" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1 : Créer le répertoire si nécessaire
Write-Host "[1/5] Vérification du répertoire de travail..." -ForegroundColor Yellow
if (-Not (Test-Path $WorkDir)) {
    Write-Host "  → Création de $WorkDir" -ForegroundColor Gray
    New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null
    Write-Host "  ✓ Répertoire créé" -ForegroundColor Green
} else {
    Write-Host "  ✓ Répertoire existe" -ForegroundColor Green
}

# Aller dans le répertoire
Set-Location $WorkDir

# Étape 2 : Cloner ou mettre à jour le repository
Write-Host ""
Write-Host "[2/5] Synchronisation avec GitHub..." -ForegroundColor Yellow

if (-Not (Test-Path ".git")) {
    # Le repo n'existe pas, le cloner
    Write-Host "  → Clonage du repository..." -ForegroundColor Gray
    git clone $GitRepo .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Repository cloné" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Erreur lors du clonage" -ForegroundColor Red
        Read-Host "Appuyez sur Entrée pour quitter"
        exit 1
    }
} else {
    Write-Host "  ✓ Repository déjà cloné" -ForegroundColor Green
}

# Étape 3 : Checkout de la bonne branche
Write-Host ""
Write-Host "[3/5] Basculement sur la branche de travail..." -ForegroundColor Yellow
git checkout $GitBranch 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Branche $GitBranch active" -ForegroundColor Green
} else {
    Write-Host "  → Création de la branche locale..." -ForegroundColor Gray
    git checkout -b $GitBranch origin/$GitBranch
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Branche créée et active" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Erreur lors du checkout" -ForegroundColor Red
    }
}

# Étape 4 : Pull des dernières modifications
Write-Host ""
Write-Host "[4/5] Récupération des dernières modifications..." -ForegroundColor Yellow
git pull origin $GitBranch
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Code à jour" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Attention : Problème lors du pull" -ForegroundColor Yellow
}

# Étape 5 : Afficher le statut
Write-Host ""
Write-Host "[5/5] Statut du repository..." -ForegroundColor Yellow
Write-Host "  Répertoire : $WorkDir" -ForegroundColor Gray
Write-Host "  Branche    : " -NoNewline -ForegroundColor Gray
git branch --show-current
Write-Host "  Dernier commit : " -NoNewline -ForegroundColor Gray
git log -1 --oneline
Write-Host ""

# Afficher un résumé des fichiers importants
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Documentation disponible" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
$Docs = @(
    "DEPLOYMENT_STATUS.md",
    "DNS_CONFIGURATION.md",
    "EDITEUR_AVANCE.md",
    "README.md",
    "SUMMARY.md"
)

foreach ($doc in $Docs) {
    if (Test-Path $doc) {
        Write-Host "  ✓ $doc" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $doc (manquant)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Lancement de Claude Code" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vous pouvez dire à Claude Code :" -ForegroundColor Yellow
Write-Host '  "Lis DEPLOYMENT_STATUS.md et EDITEUR_AVANCE.md"' -ForegroundColor White
Write-Host '  "pour comprendre le contexte du projet"' -ForegroundColor White
Write-Host ""
Write-Host "Appuyez sur Entrée pour lancer Claude Code..." -ForegroundColor Cyan
Read-Host

# Lancer Claude Code
Write-Host "Lancement de Claude Code..." -ForegroundColor Green
claude

# Si Claude Code se termine
Write-Host ""
Write-Host "Session Claude Code terminée." -ForegroundColor Cyan
Write-Host ""
Write-Host "N'oubliez pas de pousser vos modifications vers GitHub :" -ForegroundColor Yellow
Write-Host "  git add ." -ForegroundColor Gray
Write-Host "  git commit -m 'Description des changements'" -ForegroundColor Gray
Write-Host "  git push origin $GitBranch" -ForegroundColor Gray
Write-Host ""
Read-Host "Appuyez sur Entrée pour fermer"
