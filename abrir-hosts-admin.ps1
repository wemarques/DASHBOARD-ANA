# Script para abrir o arquivo hosts no Notepad como Administrador
# PRECISA SER EXECUTADO COMO ADMINISTRADOR

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"

# Verificar se esta rodando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Clique com botao direito no PowerShell e selecione 'Executar como administrador'" -ForegroundColor Yellow
    exit 1
}

# Abrir o arquivo hosts no Notepad
try {
    notepad $hostsPath
    Write-Host "`nArquivo hosts aberto no Notepad." -ForegroundColor Green
    Write-Host "`nINSTRUCOES:" -ForegroundColor Cyan
    Write-Host "1. Vá ate o final do arquivo" -ForegroundColor Yellow
    Write-Host "2. Adicione esta linha:" -ForegroundColor Yellow
    Write-Host "   127.0.0.1    dashboard-ana" -ForegroundColor White
    Write-Host "3. Salve o arquivo (Ctrl+S)" -ForegroundColor Yellow
    Write-Host "4. Feche o Notepad" -ForegroundColor Yellow
} catch {
    Write-Host "ERRO ao abrir arquivo: $_" -ForegroundColor Red
    exit 1
}

