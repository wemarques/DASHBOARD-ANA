# Script para verificar qual processo esta usando o arquivo hosts
# PRECISA SER EXECUTADO COMO ADMINISTRADOR

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"

Write-Host "Verificando processos que podem estar bloqueando o arquivo hosts..." -ForegroundColor Cyan
Write-Host ""

# Tentar identificar processos que podem estar usando o arquivo
$processes = Get-Process | Where-Object {
    $_.ProcessName -like "*defender*" -or
    $_.ProcessName -like "*security*" -or
    $_.ProcessName -like "*avast*" -or
    $_.ProcessName -like "*kaspersky*" -or
    $_.ProcessName -like "*norton*" -or
    $_.ProcessName -like "*mcafee*" -or
    $_.ProcessName -like "*bitdefender*"
}

if ($processes) {
    Write-Host "Processos de seguranca encontrados:" -ForegroundColor Yellow
    $processes | Format-Table ProcessName, Id, Path -AutoSize
} else {
    Write-Host "Nenhum processo de seguranca obvio encontrado." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "SOLUCOES:" -ForegroundColor Cyan
Write-Host "1. Desabilite temporariamente o Windows Defender Real-time Protection" -ForegroundColor Yellow
Write-Host "2. Ou adicione uma excecao no seu antivirus para o arquivo hosts" -ForegroundColor Yellow
Write-Host "3. Ou tente editar usando o metodo manual abaixo" -ForegroundColor Yellow

