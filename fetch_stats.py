import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def main():
    url = "https://stats.deadbydaylight.com/statistics/"
    
    # Recupera il cookie sicuro memorizzato nei Secrets di GitHub
    cookie_session = os.environ.get("DBD_COOKIE")
    
    if not cookie_session:
        print("Errore: Il segreto DBD_COOKIE non è stato configurato correttamente.")
        exit(1)
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie_session
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Estrae i dati pre-caricati da Next.js nascosti nella pagina
        next_data_script = soup.find('script', id='__NEXT_DATA__')
        
        if next_data_script:
            raw_json = json.loads(next_data_script.string)
            stats_data = raw_json.get('props', {}).get('pageProps', {})
            
            if not stats_data:
                print("Attenzione: Pagina letta ma dati vuoti. Il cookie potrebbe essere scaduto.")
                exit(1)
        else:
            print("Errore: Impossibile trovare la struttura dati nella pagina.")
            exit(1)
        
        # Crea la struttura del JSON finale
        output = {
            "last_updated_at": datetime.utcnow().isoformat() + "Z",
            "my_stats": stats_data
        }
        
        # Salva il file JSON
        with open("stats.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print("Dati personali salvati con successo in stats.json!")
        
    except Exception as e:
        print(f"Errore durante lo scraping: {e}")
        exit(1)

if __name__ == "__main__":
    main()
