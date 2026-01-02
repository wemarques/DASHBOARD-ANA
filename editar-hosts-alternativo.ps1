# Script alternativo: copia arquivo, edita, e copia de volta
# PRECISA SER EXECUTADO COMO ADMINISTRADOR

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$tempPath = "$env:TEMP\hosts_temp_$(Get-Date -Format 'yyyyMMddHHmmss')"
$entry = "127.0.0.1    dashboard-ana"

# Verificar se esta rodando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    exit 1
}

# Verificar se ja existe
try {
    $hostsContent = Get-Content $hostsPath -ErrorAction Stop
    if ($hostsContent -match "dashboard-ana") {
        Write-Host "OK: A entrada 'dashboard-ana' ja existe no arquivo hosts." -ForegroundColor Green
        exit 0
    }
} catch {
    Write-Host "Aviso: Nao foi possivel ler o arquivo hosts: $_" -ForegroundColor Yellow
}

try {
    # Copiar para temp
    Write-Host "Copiando arquivo hosts para area temporaria..." -ForegroundColor Cyan
    Copy-Item $hostsPath $tempPath -Force -ErrorAction Stop
    
    # Ler conteudo
    $content = Get-Content $tempPath -Raw
    
    # Adicionar entrada se nao existir
    if ($content -notmatch "dashboard-ana") {
        $newLine = "`r`n# Dashboard Ana - Configurado em $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`r`n$entry`r`n"
        $content = $content + $newLine
        
        # Salvar
        [System.IO.File]::WriteAllText($tempPath, $content, [System.Text.Encoding]::UTF8)
        Write-Host "Entrada adicionada ao arquivo temporario." -ForegroundColor Green
    }
    
    # Abrir no notepad para revisao
    Write-Host "`nAbrindo arquivo no Notepad para revisao..." -ForegroundColor Cyan
    Write-Host "Revise o arquivo e salve (Ctrl+S) quando estiver pronto." -ForegroundColor Yellow
    Start-Process notepad.exe -ArgumentList $tempPath -Wait
    
    # Perguntar se quer copiar de volta
    Write-Host "`nDeseja copiar o arquivo editado de volta? (S/N): " -ForegroundColor Cyan -NoNewline
    $resposta = Read-Host
    
    if ($resposta -eq "S" -or $resposta -eq "s") {
        # Fazer backup do original
        $backupPath = "$hostsPath.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $hostsPath $backupPath -Force
        Write-Host "Backup criado: $backupPath" -ForegroundColor Cyan
        
        # Copiar de volta
        Copy-Item $tempPath $hostsPath -Force -ErrorAction Stop
        Write-Host "SUCCESS: Arquivo hosts atualizado com sucesso!" -ForegroundColor Green
        Write-Host "`nVoce pode agora acessar: http://dashboard-ana:8501" -ForegroundColor Cyan
    } else {
        Write-Host "Operacao cancelada. O arquivo editado esta em: $tempPath" -ForegroundColor Yellow
    }
    
    # Limpar temp (opcional)
    Write-Host "`nDeseja remover o arquivo temporario? (S/N): " -ForegroundColor Cyan -NoNewline
    $limpar = Read-Host
    if ($limpar -eq "S" -or $limpar -eq "s") {
        Remove-Item $tempPath -Force -ErrorAction SilentlyContinue
    }
    
} catch {
    Write-Host "ERRO: $_" -ForegroundColor Red
    if (Test-Path $tempPath) {
        Write-Host "Arquivo temporario esta em: $tempPath" -ForegroundColor Yellow
    }
    exit 1
}

