# Verifica se está executando como administrador
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Este script precisa ser executado como Administrador para configurar o Firewall." -ForegroundColor Red
    Write-Host "Por favor, clique com o botão direito neste arquivo e selecione 'Executar com o PowerShell' (se possível como admin) ou abra um PowerShell como Admin e execute este script." -ForegroundColor Yellow
    exit
}

Write-Host "Configurando Firewall do Windows..." -ForegroundColor Cyan

# Remove regra antiga se existir para evitar duplicatas
Remove-NetFirewallRule -DisplayName "Streamlit Dashboard" -ErrorAction SilentlyContinue

# Cria a regra de firewall
try {
    New-NetFirewallRule -DisplayName "Streamlit Dashboard" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8501 -ErrorAction Stop
    Write-Host "✅ Regra de Firewall 'Streamlit Dashboard' criada com sucesso para a porta 8501!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao criar regra de firewall: $_" -ForegroundColor Red
    exit
}

Write-Host "`nInformações de Rede:" -ForegroundColor Cyan
# Obtém endereços IP
$ips = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.PrefixOrigin -ne "WellKnown" }

foreach ($ip in $ips) {
    Write-Host "Interface: $($ip.InterfaceAlias)"
    Write-Host "Link de Acesso: http://$($ip.IPAddress):8501" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Teste acessar pelo celular agora." -ForegroundColor Yellow
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
