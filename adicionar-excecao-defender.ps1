# Script para adicionar excecao do arquivo hosts no Windows Defender
# PRECISA SER EXECUTADO COMO ADMINISTRADOR

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"

Write-Host "=== Adicionar Excecao do Arquivo Hosts no Windows Defender ===" -ForegroundColor Cyan
Write-Host ""

# Verificar se esta como admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERRO: Precisa executar como Administrador!" -ForegroundColor Red
    Write-Host "Clique com botao direito no PowerShell e selecione 'Executar como administrador'" -ForegroundColor Yellow
    exit 1
}

try {
    Write-Host "Adicionando excecao para o arquivo hosts..." -ForegroundColor Cyan
    
    # Adicionar excecao de arquivo
    Add-MpPreference -ExclusionPath $hostsPath -ErrorAction Stop
    
    Write-Host "SUCCESS: Excecao adicionada com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Agora voce pode editar o arquivo hosts normalmente!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Abrindo arquivo hosts no Notepad..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "INSTRUCOES:" -ForegroundColor Yellow
    Write-Host "1. No Notepad, va ate o final do arquivo" -ForegroundColor White
    Write-Host "2. Adicione esta linha (em uma nova linha):" -ForegroundColor White
    Write-Host "   127.0.0.1    dashboard-ana" -ForegroundColor Cyan
    Write-Host "3. Salve o arquivo (Ctrl+S)" -ForegroundColor White
    Write-Host "4. Feche o Notepad" -ForegroundColor White
    Write-Host ""
    
    # Abrir notepad
    Start-Process notepad.exe -ArgumentList $hostsPath -Wait
    
    Write-Host ""
    Write-Host "Verificando se a entrada foi adicionada..." -ForegroundColor Cyan
    $content = Get-Content $hostsPath -ErrorAction SilentlyContinue
    if ($content -match "dashboard-ana") {
        Write-Host "SUCCESS: Entrada 'dashboard-ana' encontrada no arquivo hosts!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Reinicie o Streamlit e acesse: http://dashboard-ana:8501" -ForegroundColor Cyan
    } else {
        Write-Host "AVISO: Entrada 'dashboard-ana' nao encontrada." -ForegroundColor Yellow
        Write-Host "Verifique se voce salvou o arquivo corretamente." -ForegroundColor Yellow
    }
    
} catch {
    if ($_.Exception.Message -match "already exists") {
        Write-Host "AVISO: A excecao ja existe. Tentando abrir o arquivo..." -ForegroundColor Yellow
        
        try {
            Start-Process notepad.exe -ArgumentList $hostsPath -Wait
            Write-Host "Arquivo hosts aberto. Edite e salve normalmente." -ForegroundColor Green
        } catch {
            Write-Host "ERRO ao abrir arquivo: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "ERRO: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Tentando metodo alternativo - abrindo diretamente..." -ForegroundColor Yellow
        try {
            Start-Process notepad.exe -ArgumentList $hostsPath
            Write-Host "Notepad aberto. Tente editar manualmente." -ForegroundColor Yellow
        } catch {
            Write-Host "Nao foi possivel abrir o arquivo. Tente manualmente:" -ForegroundColor Red
            Write-Host "1. Abra Seguranca do Windows" -ForegroundColor White
            Write-Host "2. Protecao contra virus e ameacas" -ForegroundColor White
            Write-Host "3. Configuracoes -> Gerenciar configuracoes" -ForegroundColor White
            Write-Host "4. Exclusoes -> Adicionar ou remover exclusoes" -ForegroundColor White
            Write-Host "5. Adicione: $hostsPath" -ForegroundColor White
        }
    }
}

