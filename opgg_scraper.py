import requests
from bs4 import BeautifulSoup

def get_player_rank(summoner_name):
    """
    Obtiene el rango, LP, victorias, derrotas y win rate de un jugador desde OP.GG.
    """
    base_url = "https://www.op.gg/summoners/euw/"
    summoner_url = f"{base_url}{summoner_name.replace(' ', '%20').replace('#', '-')}"
    
    try:
        
        response = requests.get(summoner_url)
        response.raise_for_status()  # Levantar error si la respuesta no es 200
        print(summoner_url+ " "+str(response.status_code))
        soup = BeautifulSoup(response.text, 'html.parser')
        content_divs = soup.find_all('div', class_='content')

        # Verificar si el contenido esperado existe
        if len(content_divs) > 1:
            content = content_divs[1]

            # Extraer tier, lp, win-lose y win-rate
            tier = content.find('div', class_='tier').text.strip() if content.find('div', class_='tier') else "No Rank"
            lp = content.find('div', class_='lp').text.strip() if content.find('div', class_='lp') else "0 LP"
            win_lose = content.find('div', class_='win-lose').text.strip() if content.find('div', class_='win-lose') else "0W 0L"
            win_rate = content.find('div', class_='ratio').text.strip() if content.find('div', class_='ratio') else "Win rate 0%"

            return {
                "tier": tier,
                "lp": lp,
                "win_lose": win_lose,
                "win_rate": win_rate
            }
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con OP.GG: {e}")
        return None
