import subprocess
import time
import os
import sys
import urllib.request
import signal

STAGING_PORT = 8502
HEALTH_URL = f"http://localhost:{STAGING_PORT}/_stcore/health"

def run_staging_test():
    print(f"🚀 Iniciando Deploy em STAGING (Porta {STAGING_PORT})...")
    
    # Configurar ambiente
    env = os.environ.copy()
    env["APP_ENV"] = "staging"
    env["headless"] = "true"
    
    # Comando para iniciar Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(STAGING_PORT),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    # Iniciar processo
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print(f"⏳ Aguardando inicialização (PID: {process.pid})...")
    
    # Smoke Test Loop
    max_retries = 30
    success = False
    
    for i in range(max_retries):
        try:
            time.sleep(1)
            with urllib.request.urlopen(HEALTH_URL) as response:
                if response.getcode() == 200:
                    print(f"✅ Smoke Test PASS: Endpoint {HEALTH_URL} respondeu 200 OK")
                    print("✅ Aplicação iniciada corretamente.")
                    success = True
                    break
        except Exception:
            print(f"   ...tentativa {i+1}/{max_retries}...")
            
    # Verificar Feature Flag no log (simulação)
    # Como não podemos interagir com a UI facilmente aqui, validamos pelo config_manager
    # Mas o smoke test principal é o health check
    
    # Coletar logs iniciais
    try:
        outs, errs = process.communicate(timeout=2)
    except subprocess.TimeoutExpired:
        # Processo ainda rodando (o que é bom), vamos matar
        process.terminate()
        try:
            outs, errs = process.communicate(timeout=2)
        except:
            process.kill()
            outs, errs = process.communicate()
            
    print("\n📜 Logs do Deploy (Staging):")
    if outs: print(outs)
    if errs: print(errs)
    
    if success:
        print("\n🏆 RESULTADO: STAGING DEPLOY SUCCESS")
        return 0
    else:
        print("\n❌ RESULTADO: SMOKE TEST FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(run_staging_test())
