# Script para configurar o arquivo hosts do Windows
# PRECISA SER EXECUTADO COMO ADMINISTRADOR

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$entry = "127.0.0.1    dashboard-ana"

# Verificar se esta rodando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Clique com botao direito no PowerShell e selecione 'Executar como administrador'" -ForegroundColor Yellow
    exit 1
}

# Verificar se a entrada ja existe
try {
    $hostsContent = Get-Content $hostsPath -ErrorAction Stop
    if ($hostsContent -match "dashboard-ana") {
        Write-Host "OK: A entrada 'dashboard-ana' ja existe no arquivo hosts." -ForegroundColor Green
        Write-Host "Conteudo encontrado:" -ForegroundColor Yellow
        $hostsContent | Select-String -Pattern "dashboard-ana"
        exit 0
    }
} catch {
    Write-Host "ERRO ao ler arquivo hosts: $_" -ForegroundColor Red
    exit 1
}

# Fazer backup
$backupPath = "$hostsPath.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
try {
    Copy-Item $hostsPath $backupPath -Force -ErrorAction Stop
    Write-Host "Backup criado: $backupPath" -ForegroundColor Cyan
} catch {
    Write-Host "ERRO ao criar backup: $_" -ForegroundColor Red
    exit 1
}

# Adicionar entrada usando metodo alternativo
try {
    # Ler conteudo atual
    $currentContent = Get-Content $hostsPath -Raw -ErrorAction Stop
    
    # Preparar nova entrada
    $newEntry = "`r`n# Dashboard Ana - Configurado em $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`r`n$entry`r`n"
    
    # Adicionar ao final do conteudo
    $newContent = $currentContent + $newEntry
    
    # Escrever usando .NET para evitar problemas de encoding
    [System.IO.File]::WriteAllText($hostsPath, $newContent, [System.Text.Encoding]::UTF8)
    
    Write-Host "SUCCESS: Entrada adicionada com sucesso!" -ForegroundColor Green
    Write-Host "`nVoce pode agora acessar: http://dashboard-ana:8501" -ForegroundColor Cyan
    Write-Host "`nReinicie o Streamlit para aplicar as mudancas." -ForegroundColor Yellow
    
} catch {
    Write-Host "ERRO ao adicionar entrada: $_" -ForegroundColor Red
    Write-Host "Revertendo backup..." -ForegroundColor Yellow
    try {
        Copy-Item $backupPath $hostsPath -Force -ErrorAction Stop
        Write-Host "Backup restaurado com sucesso." -ForegroundColor Green
    } catch {
        Write-Host "ERRO ao restaurar backup: $_" -ForegroundColor Red
        Write-Host "Por favor, restaure manualmente de: $backupPath" -ForegroundColor Yellow
    }
    exit 1
}
