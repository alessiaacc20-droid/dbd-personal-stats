import os
import requests
import json
import re
from datetime import datetime

def main():
    # 1. Definiamo gli URL base
    base_url = "https://stats.deadbydaylight.com"
    stats_page = f"{base_url}/statistics/"
    
    # Recupera il cookie sicuro memorizzato nei Secrets di GitHub
    cookie_session = os.environ.get("DBD_COOKIE")
    
    if not cookie_session:
        print("Errore: Il segreto DBD_COOKIE non è configurato su GitHub.")
        exit(1)
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie_session,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }
    
    try:
        # Visita la pagina principale per raccogliere il buildId dinamico
        print("Sincronizzazione della sessione e lettura della pagina principale...")
        session = requests.Session()
        response = session.get(stats_page, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Cerchiamo il buildId all'interno del tag __NEXT_DATA__ inserito nell'HTML
        html_content = response.text
        build_id_match = re.search(r'"buildId"\s*:\s*"([^"]+)"', html_content)
        
        if not build_id_match:
            print("Impossibile trovare il buildId dinamico nella pagina. Controllo fallback...")
            # Tentativo alternativo tramite pattern dell'URL degli script
            build_id_match = re.search(r'/_next/static/([^/]+)/_buildManifest\.js', html_content)
            
        if not build_id_match:
            print("Errore critico: Il sito ha cambiato struttura e il buildId non è stato individuato.")
            exit(1)
            
        build_id = build_id_match.group(1)
        print(f"Build ID rilevato con successo: {build_id}")
        
        # 2. Generiamo l'URL dell'API dinamicamente usando la build corretta
        dynamic_url = f"{base_url}/_next/data/{build_id}/statistics.json"
        print(f"Download dei dati dall'URL generato: {dynamic_url}")
        
        # Aggiorniamo l'header per richiedere il JSON puro
        headers["Accept"] = "application/json"
        api_response = session.get(dynamic_url, headers=headers, timeout=15)
        api_response.raise_for_status()
        
        raw_data = api_response.json()
        page_props = raw_data.get('pageProps', {})
        
        # Creiamo il file finale pulito con i tuoi dati reali
        output = {
            "last_updated_at": datetime.utcnow().isoformat() + "Z",
            "my_stats": page_props
        }
        
        with open("stats.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print("Statistiche aggiornate correttamente nel file stats.json!")
        
    except Exception as e:
        print(f"Errore durante il ciclo di tracciamento automatizzato: {e}")
        exit(1)

if __name__ == "__main__":
    main()
