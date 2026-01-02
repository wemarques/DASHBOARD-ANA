# Script para desabilitar temporariamente Windows Defender
# PRECISA SER EXECUTADO COMO ADMINISTRADOR
# ATENCAO: Reative a protecao apos editar o hosts!

Write-Host "=== Desabilitar Windows Defender Temporariamente ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "ATENCAO: Este script desabilita a protecao em tempo real." -ForegroundColor Red
Write-Host "IMPORTANTE: A protecao sera reativada automaticamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Deseja continuar? (S/N): " -ForegroundColor Cyan -NoNewline
$confirmar = Read-Host

if ($confirmar -ne "S" -and $confirmar -ne "s") {
    Write-Host "Operacao cancelada." -ForegroundColor Yellow
    exit 0
}

try {
    # Verificar se esta como admin
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) {
        Write-Host "ERRO: Precisa executar como Administrador!" -ForegroundColor Red
        Write-Host "Clique com botao direito no PowerShell e selecione 'Executar como administrador'" -ForegroundColor Yellow
        exit 1
    }
    
    # Desabilitar
    Write-Host "Desabilitando protecao em tempo real..." -ForegroundColor Cyan
    Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction Stop
    
    Write-Host "SUCCESS: Protecao desabilitada!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Abrindo arquivo hosts no Notepad..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "INSTRUCOES:" -ForegroundColor Yellow
    Write-Host "1. No Notepad que abrir, va ate o final do arquivo" -ForegroundColor White
    Write-Host "2. Adicione esta linha (em uma nova linha):" -ForegroundColor White
    Write-Host "   127.0.0.1    dashboard-ana" -ForegroundColor Cyan
    Write-Host "3. Salve o arquivo (Ctrl+S)" -ForegroundColor White
    Write-Host "4. Feche o Notepad" -ForegroundColor White
    Write-Host ""
    
    # Abrir notepad
    $hostsPath = "C:\Windows\System32\drivers\etc\hosts"
    Start-Process notepad.exe -ArgumentList $hostsPath -Wait
    
    Write-Host ""
    Write-Host "Reativando protecao em tempo real..." -ForegroundColor Cyan
    Set-MpPreference -DisableRealtimeMonitoring $false -ErrorAction Stop
    Write-Host "SUCCESS: Protecao reativada!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verificando se a entrada foi adicionada..." -ForegroundColor Cyan
    $content = Get-Content $hostsPath -ErrorAction SilentlyContinue
    if ($content -match "dashboard-ana") {
        Write-Host "SUCCESS: Entrada 'dashboard-ana' encontrada no arquivo hosts!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Agora reinicie o Streamlit e acesse: http://dashboard-ana:8501" -ForegroundColor Cyan
    } else {
        Write-Host "AVISO: Entrada 'dashboard-ana' nao encontrada." -ForegroundColor Yellow
        Write-Host "Verifique se voce salvou o arquivo corretamente." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "ERRO: $_" -ForegroundColor Red
    Write-Host "Tentando reativar protecao..." -ForegroundColor Yellow
    try {
        Set-MpPreference -DisableRealtimeMonitoring $false -ErrorAction SilentlyContinue
        Write-Host "Protecao reativada." -ForegroundColor Green
    } catch {
        Write-Host "ERRO ao reativar. Reative manualmente em Seguranca do Windows!" -ForegroundColor Red
    }
    exit 1
}
